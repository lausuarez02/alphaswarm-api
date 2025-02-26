from fastapi import FastAPI, HTTPException
from typing import List, Optional
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from alphaswarm.agent import AlphaSwarmAgent
from alphaswarm.config import Config
from alphaswarm.core.tool import AlphaSwarmToolBase
from alphaswarm.tools.core import GetTokenAddress
from alphaswarm.tools.alchemy import GetAlchemyPriceHistoryBySymbol
from alphaswarm.tools.forecasting import ForecastTokenPrice
from alphaswarm.tools.exchanges import ExecuteTokenSwap, GetTokenPrice
from alphaswarm.tools.cookie.cookie_metrics import GetCookieMetricsBySymbol, GetCookieMetricsPaged
# Initialize FastAPI app
load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

config = Config(network_env="test")

# Initialize config and tools (done once at startup)
tools: List[AlphaSwarmToolBase] = [
    GetAlchemyPriceHistoryBySymbol(),
    ForecastTokenPrice(),
    GetTokenPrice(config),
    ExecuteTokenSwap(config),
    GetCookieMetricsBySymbol(),
    GetCookieMetricsPaged(),
]

# Create the agent (done once at startup)
agent = AlphaSwarmAgent(tools=tools, model_id="openai/gpt-4o-mini")

# Define request model
class QuoteRequest(BaseModel):
    message: str

@app.post("/process")
async def process_message(request: QuoteRequest):
    try:
        response = await agent.process_message(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)