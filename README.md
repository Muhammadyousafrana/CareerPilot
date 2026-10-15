# CareerPilot

CareerPilot is an experimental, command-line job-search assistant built with Python and the Claude Agent SDK. It starts an interactive Claude session and gives the model four project prompts for resume profiling, job research, application preparation, and workflow coordination.

The prompt files describe a broader human-reviewed job-application workflow. The Python package is an early prototype: it wires the prompts and MCP servers into an agent session, but it does not itself implement a job-board crawler, resume parser, application database, dashboard, or end-to-end application submitter. Review the generated information and any proposed application materials yourself. Never submit an application without checking it.

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run CareerPilot](#run-careerpilot)
- [Agent prompts and workflow](#agent-prompts-and-workflow)
- [MCP integrations](#mcp-integrations)
- [Project layout](#project-layout)
- [Development](#development)
- [Privacy and safe use](#privacy-and-safe-use)
- [Troubleshooting](#troubleshooting)
- [Current limitations](#current-limitations)

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) for dependency and environment management
- An Anthropic API key with access to the models used by the Claude Agent SDK
- Node.js and `npx` if you want to start the configured Gmail and Playwright MCP servers
- A working Claude Agent SDK runtime in the environment

The Gmail and Playwright MCP servers are configured when the agent starts. They are not required to install the Python package, but the corresponding server commands and any account setup they require must work for those integrations to be useful.

## Installation

Clone the repository and enter its directory, then install the project and development dependencies:

```bash
uv sync
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set `ANTHROPIC_API_KEY` to your key. Keep `.env` private; it is excluded from Git.

## Configuration

### Anthropic API key

The application loads environment variables from `.env` with `python-dotenv`. Set:

```dotenv
ANTHROPIC_API_KEY=your-anthropic-api-key
```

You can instead provide the variable through your shell or secret manager. Do not commit a real API key or paste one into prompts, issues, or logs.

### MCP servers

The current agent configuration starts two stdio MCP servers through `npx`:

- `gmail`: `@anthropic-ai/mcp-server-gmail`
- `playwright`: `@playwright/mcp`

The server definitions live in `src/autonomous_job_system/agent.py`. Check each server's own documentation for installation, authentication, and supported tools. MCP server availability and account authorization are separate from setting the Anthropic API key.

## Run CareerPilot

Start the interactive agent from the project root:

```bash
uv run agent
```

Enter a request at the `You:` prompt. For example:

```text
Help me review my resume and identify roles that fit my experience.
```

When finished, type `exit` to close the session. The console application streams assistant text and tool-use summaries. Give it access only to files and accounts you intend it to use, and review any actions before allowing them to proceed.

## Agent prompts and workflow

The main prompt coordinates three specialized agent definitions. Prompt files are loaded from the installed package when available, with a project-tree fallback for development.

| Role | Prompt file | Intended responsibility |
| --- | --- | --- |
| Orchestrator | `prompts/job-application-orchestrator.md` | Coordinate the job-search workflow and checkpoints |
| Profile Architect | `prompts/profile-architect.md` | Turn resume information into a structured candidate profile |
| Job Intelligence | `prompts/job-intelligence.md` | Research and assess job opportunities |
| Application Engine | `prompts/application-engine.md` | Prepare tailored application materials and guide application steps |

The prompts are instructions to the agents, not standalone implementations of every capability they describe. Results depend on the model, available tools, MCP server configuration, and the information you provide. Verify job details, salary information, resume edits, and recipient addresses independently.

## MCP integrations

The application enables Playwright and Gmail MCP tools for the relevant agents. These integrations can give the agent access to browser activity or email actions, depending on the servers and accounts you configure.

- Use Playwright only on sites and accounts you are authorized to access, and comply with site terms.
- Review browser form contents before submitting them.
- Review the recipient, subject, body, and attachments before sending email.
- Keep account credentials in the MCP server's supported credential store; do not add them to this repository.

## Project layout

```text
.
├── .claude/skills/                 # Claude Code skill documentation
├── prompts/                        # Agent prompts; copied into the wheel at build time
├── src/autonomous_job_system/
│   ├── agent.py                    # Agent setup and interactive entry point
│   ├── main.py                     # Small placeholder module
│   └── utils.py                    # Console rendering helpers
├── .env.example                    # Environment variable template
├── QUICKSTART.md                   # Short setup guide
├── SUMMARY.md                      # Original project and workflow notes
├── pyproject.toml                  # Package metadata and dependencies
└── uv.lock                         # Locked Python dependency versions
```

## Development

Install the development dependency group with `uv sync`, then run the agent with `uv run agent`.

The project configures Ruff for linting and pytest for tests. Run them from the repository root:

```bash
uv run ruff check .
uv run pytest
```

The console entry point is declared in `pyproject.toml` as `agent = "autonomous_job_system.agent:run"`. Packaged prompt files are included in the wheel through the Hatch configuration in that file.

## Privacy and safe use

- `.env`, virtual environments, build output, and local session or application artifacts are ignored by Git.
- Resume files and job-search data may contain personal information. Share only the minimum needed with external models and services.
- Treat resumes, job listings, websites, and emails as untrusted input. Check links and claims before acting on them.
- Do not fabricate qualifications, employment history, references, or other application details.
- Keep a human in control of application decisions and final submissions.

Review `.gitignore` before committing if you add new local data or credential files.

## Troubleshooting

### `ANTHROPIC_API_KEY` is missing or rejected

Check that `.env` exists in the directory where the command is started, that the variable name is spelled correctly, and that the key is valid for your Anthropic account.

### `npx` or an MCP server cannot start

Confirm Node.js and `npx` are installed and available on `PATH`. Then consult the MCP server's documentation for package changes, permissions, and authentication setup.

### A prompt file cannot be found

Run the command from an installed environment created with `uv sync`. In a source checkout, confirm the prompt exists under `prompts/`. If you are using a built wheel, reinstall it after changing prompt files.

### A tool is unavailable or an action fails

Check the agent's tool permissions and the corresponding MCP server logs and account authorization. The Python package does not provide independent implementations of external search, email, or browser services.

## Current limitations

- This is an early prototype and has no dedicated automated test suite in the repository.
- Job-search coverage, scoring, and resume extraction depend on the prompts and available external tools; they are not implemented as deterministic Python services here.
- There is no built-in persistent campaign database or dashboard.
- Email and browser workflows depend on external MCP servers and need their own setup and verification.
- Human review is essential. Do not assume that an agent-generated job listing, match score, resume edit, or application is correct.

## License

The package metadata declares the MIT License. See `pyproject.toml` for the project metadata.
