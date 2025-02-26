# AlphaSwarm Architecture

## Introduction

AlphaSwarm is currently built with the [smolagents](https://github.com/huggingface/smolagents) framework. AlphaSwarm adds value on top of this in the form of customizable services, tools, and agent configurations geared for trading and DeFi.

### About `CodeAgent`

AlphaSwarm agents are currently based on the `CodeAgent` from `smolagents`. AlphaSwarm additionally provides specialized tools and configurations for crypto trading. The key benefit of adopting the `CodeAgent` has to do with the way it uses tools:

- Instead of using structured JSON for tool invocation (the industry standard), agents generate and execute Python code directly
- This Python-based approach enables greater flexibility - agents can write additional code before/after tool invocations
- Evidence suggests that planning in code (vs. JSON tool sequences) leads to more accurate execution on the first attempt

For code execution, we are currently relying on smolagents' [local Python code execution](https://huggingface.co/docs/smolagents/v1.6.0/en/tutorials/secure_code_execution#local-python-interpreter) framework. Secured, remote execution is part of the roadmap.

## Version Support (Initially Planned)

- Uniswap: V2 and V3 protocols
- Chains: Ethereum, Base, Solana
- Test Networks: Ethereum Sepolia

## Security

- Private keys and API credentials must be handled via environment variables
- Code execution is sandboxed via `smolagents`
- See SECURITY.md for vulnerability reporting procedures

## Architecture Overview

```mermaid
graph LR
    subgraph Services[**Services**]
        direction LR
        s1[Alchemy APIs]
        s2[Chain Clients]
        s3[Exchange Clients]
        s4[API Services]
    end

    subgraph Tools[**Tools**]
        direction LR

        subgraph Action
            t1[Trade Proposal]
            t2[Trade Execution]
            t3[Alert System]
        end 
        
        subgraph Analysis
            t4[Strategy Analysis]
            t5[Price Analysis]
        end

        subgraph Observation
            t6[Historical Prices]
            t7[Price Momentum]
            t8[Portfolio Positions]
        end
        
    end

    subgraph Core[**Core Components**]
        c1[CodeAgent]
        c2[Agent Config]
        c3[Utils]
    end

    subgraph Interfaces[**Interfaces**]
        i1[Telegram]
        i2[CLI]
        i3[Cron]
    end

    Services --> Tools
    Tools <--> Core
    Core <--> Interfaces
```

The architecture consists of three main components:

1. **Observation Layer** - Tools and services for data collection and monitoring
2. **Cognitive Layer** - Strategy analysis and decision making
3. **Action Layer** - Trade execution and notifications

### Core Components

#### Tools
Tools define interfaces for how the agent interacts with services and certain interface functions. A tool can be:
- A thin wrapper around a service
- A composite tool combining multiple services
- A standalone implementation

#### Services
Services contain the core implementation logic decoupled from any specific tool:
- API clients
- Chain interfaces
- Exchange interfaces

#### Interfaces
*Possible* interfaces for interacting with the agent:
- CLI
- Telegram
- Cron Runner
- Infinity Studio

### Current Directory Structure

```
alphaswarm/
├── agent/       # Agent and agent clients implementation
├── core/        # Core framework components
├── services/    # Service implementations
├── tools/       # Tool definitions
├── utils/       # Utility functions and helpers
└── config.py    # Configuration management
```