# FastAPI Exercise Application for Copilot Trainings
The purpose of this repository is to be used as an exercise application in GitHub Copilot trainings for Python developers.

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [DynamoDB](https://aws.amazon.com/dynamodb/) as the NoSQL database.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).

## How to get started
TODO: Simplified instructions of how to
- Install requirements (Docker, uv)
- Run the local development environment (docker compose)
- Run unit tests

# Exercises for the Copilot traning

## 1. Create a custom instructions file

Generate an instruction file in freestyle markdown that will include information you want to add to all Copilot prompts.
The instruction file is simply a markdown file that resides in `.github/copilot-instructions.md`. The instructions can
include for example the language that you want Copilot to answer in, the structure of those answers, some coding best
practices or company policies, etc.

For example,

> All Python files must adhere to PEP 8 guidelines.
>
> Answer the prompt and only the prompt. Nothing else.

are just some lines you could add into your instruction file

- Create `.github/copilot-instructions.md`
- Ask Copilot for Python best practices and add those to instructions file
- Review suggested changes and fix accordingly
- Think about what kind of contents would be useful in the file, e.g.
      - Project structure
      - Tehcnology stack, e.g. application and testing frameworks, data stores etc.
      - Design patterns
      - Description of the application purpose, business logic, use cases
      - Coding conventions
      - Instructions for building, running tests etc.
- In the following exercises, take notice how the file is automatically added to all prompts. See if the contests could be refined based on the effectiveness of the prompts.

## 2. Initialize a MCP server for DynamoDB

- Racap of MCP servers
    - MCP (Model Context Protocol) servers provide a standardized way to interact with various tools, services, and systems.
    - MCP server is run locally on the developer's workstation e.g. as a docker container
    - Developers can initialize and manage MCP servers directly from their IDE or command-line tools.
    - They allow seamless integration with Copilot for managing and interacting with external resources.
    - They support multiple types of integrations, including databases, APIs, and cloud services.
    - MCP servers enable real-time exploration, execution, and interaction with connected resources.
    -  [A wide variety of MCP servers are aldready available](https://mcp.so/)
    - In the following exercise [DynamoDB MCP server](https://github.com/imankamyabi/dynamodb-mcp-server) will be configured and used
- Exercise: Initialize a MCP server for dynamoDB (VS Code)
    - Clone the [GitHub repository](https://github.com/imankamyabi/dynamodb-mcp-server)
    - Navigate to the cloned repository
    - Build the Docker image and tag it as you see fit. E.g `docker build -t my-mcp-server .`

:exclamation: **NOTE!!** Since we're building the image ourselves and we haven't
pushed the image to Docker Hub we won't follow these steps, which would be the
standard way of adding an MCP server.

> - VS Code => Shift+CMD+P
> - \> MCP: Add server...
> - Docker image => `mcp/postgres`
> - Select "Allow"
> - Postgres URL: `postgresql://postgres:changethis@host.docker.internal:5432/app`
> - Select "Workspace"
> - Start the server by clicking on the play button in mcp.json
> - The query tool provided by the MCP server should be now available in the tools menu in the agent mode prompt box
> - Try out the tool e.g. with the following prompt: "What is the schema of my database #query"
> - Think about how the information provided by the MCP server could be utilised in prompts targeting the codebase

Instead, we'll continue by adding the server configuration manually to a file
called `.vscode/mcp.json`

```json
{
    "servers": {
        "dynamodb": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "--network=host",
                "-e", "AWS_ACCESS_KEY_ID=fakeMyKeyId",
                "-e", "AWS_SECRET_ACCESS_KEY=fakeSecretAccessKey",
                "-e", "AWS_REGION=local",
                "-e", "AWS_SESSION_TOKEN=fakeSessionToken",
                "my-mcp-server"
            ]
        }
    }
}
```

The `--network=host` is just to ensure the MCP server container is running in the same
network as the database container. You can try removing this or changing this to
another network depending on your Docker configurations.

Remember to rename `my-mcp-server` to whatever you tagged your instance.

## 3. Prompt files

Create a prompt file to tell Copilot to follow specific instructions when generating new API endpoints. These instructions are:

- All methods must be under 30 lines in length.
- All method parameters must have proper type hints in place
- When raising a `HTTPException`, there must be `details` added to the raise.
- All new endpoints must have a sufficient docstring.

Like a `copilot-instructions.md` file, prompt files are custom instructions you can add to your prompts, but only for the
context of the current prompt. These files are named `<name>.prompt.md` and they need to be separately added as a context
to your prompts.

## 4. Comparison: Agent mode vs Edits

Prompt Copilot Edits and Copilot Agent mode to create a new API route to add an `Authors` model and compare the results.

We have our `books` model in place, but books don't have appropraite authors. Each book should have one author and any author may
have written more than one book. We need to refactor our codebase to address this change. Also, the new `Author` model needs to
tested with proper unit tests.

Consider the following questions:

- How do the responses differ from the each other?
- Which mode should you use in each scenario?

# About This Repository
Forked from [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template). Frontend removed to make the project suitable for Python developers.
