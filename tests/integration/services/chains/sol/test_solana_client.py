import pytest
from solders.pubkey import Pubkey

from alphaswarm.config import ChainConfig, Config
from alphaswarm.services.chains.solana import SolSigner, SolanaClient


@pytest.fixture
def solana_config(default_config: Config) -> ChainConfig:
    return default_config.get_chain_config("solana")


@pytest.fixture
def client(solana_config: ChainConfig) -> SolanaClient:
    return SolanaClient(solana_config)


@pytest.mark.skip("Requires a valid Solana wallet")
@pytest.mark.parametrize(
    "token",
    [
        ("SOL"),
        ("GIGA"),
        ("USDC"),
    ],
)
def test_token_balance(token: str, client: SolanaClient, solana_config: ChainConfig) -> None:
    result = client.get_token_balance(token, solana_config.wallet_address)
    assert result is not None
    print(result)


@pytest.mark.skip("Requires a valid Solana wallet")
def test_sol_signer(solana_config: ChainConfig) -> None:
    signer = SolSigner(solana_config.private_key)

    assert signer.wallet_address == solana_config.wallet_address


@pytest.mark.skip("Requires a valid Solana wallet")
def test_get_all_token_balances(client: SolanaClient, solana_config: ChainConfig) -> None:
    result = client.get_all_token_balances(Pubkey.from_string(solana_config.wallet_address))
    assert len(result) > 0
    for item in result:
        assert item.value > 0, f"balance for token {item.token_info.symbol}"
