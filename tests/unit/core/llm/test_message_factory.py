from dataclasses import asdict

from alphaswarm.core.llm import CacheControl, ImageURL, Message, TextContentBlock
from tests import get_data_filename


def test_message_basic() -> None:
    message = Message(role="system", content=[TextContentBlock.default("test message")])

    assert isinstance(message, Message)
    assert message.role == "system"
    assert len(message.content) == 1
    assert message.content[0].type == "text"
    assert message.content[0].text == "test message"
    assert message.content[0].cache_control is None
    assert message.to_dict() == {
        "role": "system",
        "content": [{"type": "text", "text": "test message"}],
    }


def test_cache_control_dict() -> None:
    message = Message.system("system test", cache=True)

    assert isinstance(message, Message)
    assert message.role == "system"
    assert message.content[0].type == "text"
    assert message.content[0].text == "system test"
    assert message.content[0].cache_control == CacheControl.ephemeral()
    assert asdict(CacheControl.ephemeral()) == {"type": "ephemeral"}
    assert message.to_dict() == {
        "role": "system",
        "content": [{"type": "text", "text": "system test", "cache_control": {"type": "ephemeral"}}],
    }


def test_system_message() -> None:
    message = Message.system("system test")

    assert isinstance(message, Message)
    assert message.role == "system"
    assert message.content[0].type == "text"
    assert message.content[0].text == "system test"


def test_system_message_with_cache() -> None:
    message = Message.system("system test", cache=True)

    assert isinstance(message, Message)
    assert message.role == "system"
    assert message.content[0].type == "text"
    assert message.content[0].text == "system test"
    assert message.content[0].cache_control == CacheControl.ephemeral()


def test_user_message() -> None:
    message = Message.user("user test")

    assert isinstance(message, Message)
    assert message.role == "user"
    assert message.content[0].type == "text"
    assert message.content[0].text == "user test"


def test_user_message_with_cache() -> None:
    message = Message.user("user test", cache=True)

    assert isinstance(message, Message)
    assert message.role == "user"
    assert message.content[0].type == "text"
    assert message.content[0].text == "user test"
    assert message.content[0].cache_control == CacheControl.ephemeral()


def test_assistant_message() -> None:
    message = Message.assistant("assistant test")

    assert isinstance(message, Message)
    assert message.role == "assistant"
    assert message.content[0].type == "text"
    assert message.content[0].text == "assistant test"


def test_assistant_message_with_cache() -> None:
    message = Message.assistant("assistant test", cache=True)

    assert isinstance(message, Message)
    assert message.role == "assistant"
    assert message.content[0].type == "text"
    assert message.content[0].text == "assistant test"
    assert message.content[0].cache_control == CacheControl.ephemeral()


def test_message_with_image_link() -> None:
    message = Message.create(role="user", content="user test", image_url=ImageURL("https://example.com/image.jpg"))

    assert isinstance(message, Message)
    assert message.role == "user"
    assert message.content[0].type == "image_url"
    assert message.content[0].image_url.url == "https://example.com/image.jpg"
    assert message.content[1].type == "text"
    assert message.content[1].text == "user test"


def test_message_with_image_path() -> None:
    path = get_data_filename("eth_sol_prices.png")
    message = Message.create(role="user", content="user test", image_url=ImageURL.from_path(path))

    assert isinstance(message, Message)
    assert message.role == "user"
    assert len(message.content) == 2
    assert message.content[0].type == "image_url"
    assert message.content[0].image_url.url.startswith("data:image/png;base64,iVBORw0KGgoAAAA")
    assert message.content[1].type == "text"
    assert message.content[1].text == "user test"
