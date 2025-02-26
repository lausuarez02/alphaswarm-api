import asyncio
import logging
import random
from typing import Callable, List

import dotenv
from alphaswarm.agent.agent import AlphaSwarmAgent
from alphaswarm.agent.clients import CronJobClient
from alphaswarm.config import Config
from alphaswarm.core.tool import AlphaSwarmToolBase
from alphaswarm.tools.alchemy import GetAlchemyPriceHistoryBySymbol
from alphaswarm.tools.core import GetUsdPrice
from alphaswarm.tools.exchanges import GetTokenPrice

logging.getLogger("smolagents").setLevel(logging.ERROR)


async def main() -> None:
    dotenv.load_dotenv()
    config = Config()

    # Initialize tools for price-related operations
    # GetUsdPrice: General price queries
    # GetTokenPrice: Real-time token prices
    # GetAlchemyPriceHistoryBySymbol: Historical price data from Alchemy
    tools: List[AlphaSwarmToolBase] = [GetUsdPrice(), GetTokenPrice(config), GetAlchemyPriceHistoryBySymbol()]

    # Initialize the AlphaSwarm agent with the price tools
    agent = AlphaSwarmAgent(tools=tools, model_id="anthropic/claude-3-5-sonnet-20241022")

    def generate_message_cron_job1() -> str:
        # Randomly generate price queries for major cryptocurrencies
        # Returns "quit" occasionally to potentially terminate the job
        c = random.choice(["ETH", "BTC", "bitcoin", "weth", "quit"])
        return f"What's the value of {c}?" if c != "quit" else c

    def generate_message_cron_job2() -> str:
        # Generate queries for either ETH price history or GIGA/SOL pair price
        # Returns "quit" occasionally to potentially terminate the job
        c = random.choice(["What's the price history for ETH?", "What's the pair price of GIGA/SOL?", "quit"])
        return c

    def response_handler(prefix: str) -> Callable[[str], None]:
        # Creates a closure that prints responses with color formatting
        def handler(response: str) -> None:
            print(f"\033[94m[{prefix}] Received response: {response}\033[0m")

        return handler

    # Create a cron job client that runs every 60 seconds
    cron_client_1 = CronJobClient(
        agent=agent,
        client_id="AlphaSwarm1",
        interval_seconds=60,
        message_generator=generate_message_cron_job1,
        response_handler=response_handler("AlphaSwarm1"),
    )

    # Create a second cron job client that runs every 15 seconds
    cron_client_2 = CronJobClient(
        agent=agent,
        client_id="AlphaSwarm2",
        interval_seconds=15,
        message_generator=generate_message_cron_job2,
        response_handler=response_handler("AlphaSwarm2"),
    )

    # Run both cron jobs concurrently using asyncio
    await asyncio.gather(
        cron_client_1.start(),
        cron_client_2.start(),
    )


if __name__ == "__main__":
    asyncio.run(main())
