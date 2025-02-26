from decimal import Decimal

import pytest

from alphaswarm.config import Config
from alphaswarm.services.exchanges import DEXFactory
from alphaswarm.services.exchanges.uniswap import UniswapClientV2


def test_get_markets_for_tokens_v2(default_config: Config) -> None:
    """Test getting markets between USDC and WETH on Uniswap V2."""
    chain = "ethereum"
    client: UniswapClientV2 = DEXFactory.create("uniswap_v2", default_config, chain)  # type: ignore

    # Get token info from addresses directly since they might not be in config
    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # Ethereum USDC
    weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # Ethereum WETH

    evm_client = client._evm_client
    usdc = evm_client.get_token_info(evm_client.to_checksum_address(usdc_address))
    weth = evm_client.get_token_info(evm_client.to_checksum_address(weth_address))

    tokens = [usdc, weth]
    markets = client.get_markets_for_tokens(tokens)

    assert markets is not None
    assert len(markets) > 0  # Should find at least one market

    # Check first market pair
    base_token, quote_token = markets[0]
    assert {base_token.symbol, quote_token.symbol} == {"USDC", "WETH"}
    assert base_token.chain == chain
    assert quote_token.chain == chain


@pytest.fixture
def client(default_config: Config, chain: str) -> UniswapClientV2:
    return UniswapClientV2.from_config(default_config, chain)


chains = [
    "ethereum",
    "ethereum_sepolia",
    "base",
    # "base_sepolia",
]


@pytest.mark.skip("Need a funded wallet.")
@pytest.mark.parametrize("chain", chains)
def test_swap_eth_sepolia(client: UniswapClientV2, chain: str) -> None:
    usdc = client.chain_config.get_token_info("USDC")
    weth = client.chain_config.get_token_info("WETH")

    quote = client.get_token_price(token_out=usdc, amount_in=weth.to_amount(Decimal("0.0001")))
    assert quote.amount_out > quote.amount_in

    result = client.swap(quote)
    print(result)
    assert result.amount_out == pytest.approx(quote.amount_out, rel=Decimal("0.05"))
