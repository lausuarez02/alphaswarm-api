# Contributing to AlphaSwarm

Thank you for your interest in contributing to AlphaSwarm! This guide focuses on contributions to the Tools and Services components of the project.

## Scope of Contributions

Currently, we are accepting contributions in the following areas:

- **Tools**: Located in `alphaswarm/tools/`, see [this guide](docs/tools.md) for more details
  - Utility functions and classes
  - Metrics collection and analysis
  - Helper tools and scripts

- **Services**: Located in `alphaswarm/services/`, see [this guide](docs/services.md) for more details
  - Service implementations
  - Client libraries
  - Service utilities

## Getting Started

1. Fork the repository
2. Create a new branch for your feature or fix
3. Make your changes
4. Write or update tests as needed
5. Submit a pull request

## Token Value Representation 

- Decimal are used to represent floating point token value in the codebase.
- int are used to represent integer token value in base units (wei for Eth, atomic for Sol, ...).
- float must be avoided for any token value representation because of there lack of precision.

## Code Style Guidelines

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Include type hints where appropriate

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting
- Include integration tests for services

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure the test suite passes
4. Update the `README.md` and `.env.example` if necessary
5. If you're introducing a new package, create an `__init__.py` file with appropriate imports
6. Submit the pull request with a clear description of changes
7. The pull request should pass all linters and static code checks, [see](https://github.com/chain-ml/alphaswarm?tab=readme-ov-file#code-quality)
8. The pull request needs to be reviewed and accepted by the core team

## Questions or Need Help?

If you have questions or need assistance, please:
1. Check existing issues
2. Create a new issue with a clear description
3. Tag it appropriately

Thank you for contributing to AlphaSwarm! 
