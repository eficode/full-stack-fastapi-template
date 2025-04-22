
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

- Create `.github/copilot-instructions.md`
- Ask Copilot for Python best practices and add those to instructions file
- Review suggested changes and fix accordingly.

### Initialize a MCP server for PostgreSQL

- Explain the concept of MCP servers
    - MCP (Model Context Protocol) servers provide a standardized way to interact with various tools, services, and systems.
    - MCP server is run locally on the developer's workstation e.g. as a docker container
    - Developers can initialize and manage MCP servers directly from their IDE or command-line tools.
    - They allow seamless integration with Copilot for managing and interacting with external resources.
    - They support multiple types of integrations, including databases, APIs, and cloud services.
    - MCP servers enable real-time exploration, execution, and interaction with connected resources.
- Show the list of available MCP servers
    -  Talk about the [wide variety of available MCP servers](https://mcp.so/)
    -  Show specifically the page for [PostgreSQL MCP server](https://mcp.so/server/postgres/modelcontextprotocol)
- Initialize a MCP server for PostgreSQL
    - VS Code => Shift+CMD+P
    - \> MCP: Add server...
    - Docker image => `mcp/postgres`
    - Select "Allow"
    - Postgres URL: `postgresql://postgres:changethis@host.docker.internal:5432/app`
    - Select "Workspace"
    - Start the server by clicking on the play button in mcp.json
- Show that the query tool is available in the tools menu in the agent mode prompt box
- Demo how to query, e.g. "What is the schema of my database #query"

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

## Exercises For Training Session

- Real DB is used in unit tests --> Mock
