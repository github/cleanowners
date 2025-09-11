# Copilot Instructions

This is a GitHub Action that is designed to help keep `CODEOWNERS` files current by removing users that are no longer a part of the organization. This is helpful for companies that are looking to remove outdated information in the `CODEOWNERS` file. This action can be paired with other `CODEOWNERS` related actions to suggest new owners or lint `CODEOWNERS` files to ensure accuracy.

## Code Standards

### Required Before Each Commit

- Run `make lint` before committing any changes to ensure proper code linting and formatting.

### Development Flow

- Lint: `make lint`
- Test: `make test`

## Repository Structure

- `Makefile`: Contains commands for linting, testing, and other tasks
- `requirements.txt`: Python dependencies for the project
- `requirements-test.txt`: Python dependencies for testing
- `README.md`: Project documentation and setup instructions
- `setup.py`: Python package setup configuration
- `test_*.py`: Python test files matching the naming convention for test discovery

## Key Guidelines

1. Follow Python best practices and idiomatic patterns
2. Maintain existing code structure and organization
3. Write unit tests for new functionality.
4. Document changes to environment variables in the `README.md` file.
