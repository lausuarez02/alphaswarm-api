import json
from alphaswarm.tools.strategy_analysis.generic.generic_analysis import AnalyzeTradingStrategy
from alphaswarm.tools.strategy_analysis.strategy import Strategy


def test_generic_strategy_analysis() -> None:
    """Test the generic strategy analysis with basic WETH price data"""
    strategy = Strategy.from_file(filename="momentum_strategy_config.md")
    tool = AnalyzeTradingStrategy(strategy=strategy)

    # Sample token data with realistic price changes
    token_data = {
        "WETH": {
            "symbol": "WETH",
            "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "chain": "ethereum",
            "price_changes": {"5m": 0.3, "1h": 1.2, "24h": 3.5},
        }
    }

    result = tool.forward(json.dumps(token_data))

    # Basic verification
    assert result is not None
    assert result.summary is not None
    assert len(result.summary) > 0
