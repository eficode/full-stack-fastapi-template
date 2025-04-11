# Full Stack FastAPI Template

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test/badge.svg" alt="Test"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

## Notice About This Repository

This is a heavily reduced version of the [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
with just the backend remaining. The purpose of this repository is to be used as a lightweight app for GitHub Copilot
learning. Instructions to set up local environment is described in [backend/README.md](backend/README.md).

If you want to read the full instructions and latest version of the Full Stack FastAPI template, head over to the
original repository.

## Exercises For Planning Session

### Create a Copilot Instruction File

- Workspace index
- Generate an instruction file with Copilot
    - Method max length = x
    - Naming convention
    - Type hinting

### Create a Prompt File (Optional)

- Endpoint Conventions
    - Error details
    - Method docstring

### Compare Agents And Edits

- Refactoring Agents vs. Edits
    - Add Author model and relationship to Books model
        - Add Unit tests

### Postgres MCP server

- Initialize a MCP server for PostgreSQL

## Exercises For Training Session

- Real DB is used in unit tests --> Mock
