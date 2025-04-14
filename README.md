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

### Workspace index (Optional)

A workspace index helps Copilot better analyze and accurately search your codebase for relevant files when generating and answer.
The indexing might take a while, so it's good to do this early to speed up Copilot responses later on. However, once the index is done,
it doesn't need to be repeated as Copilot will automatically update the index with the new changes.

### Create a Copilot Instruction File

Generate an instruction file in freestyle markdown that will include information you want to add to all Copilot prompts.
The instruction file is simply a markdown file that resides in `.github/copilot-instructions.md`. The instructions can
include for example the language that you want Copilot to answer in, the structure of those answers, some coding best
practices or company policies, etc.

For example,

> All Python files must adhere to PEP 8 guidelines.
>
> Answer the prompt and only the prompt. Nothing else.

are just some lines you could add into your instruction file

### Create a Prompt File (Optional)

Create a prompt file to tell Copilot to follow specific instructions when generating new API endpoints. These instructions are:

- All methods must be under 30 lines in length.
- All method parameters must have proper type hints in place
- When raising a `HTTPException`, there must be `details` added to the raise.
- All new endpoints must have a sufficient docstring.

Like a `copilot-instructions.md` file, prompt files are custom instructions you can add to your prompts, but only for the
context of the current prompt. These files are named `<name>.prompt.md` and they need to be separately added as a context
to your prompts.

### Compare Agents And Edits

Prompt Copilot Edits and Copilot Agent mode to create a new API route to add an `Authors` model and compare the results.

We have our `books` model in place, but books don't have appropraite authors. Each book should have one author and any author may
have written more than one book. We need to refactor our codebase to address this change. Also, the new `Author` model needs to
tested with proper unit tests.

Consider the following questions:

- How do the responses differ from the each other?
- Which mode should you use in each scenario?

### Initialize a MCP server for PostgreSQL

- Initialize a MCP server for PostgreSQL

## Exercises For Training Session

- Real DB is used in unit tests --> Mock
