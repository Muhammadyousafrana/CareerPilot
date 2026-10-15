import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from claude_agent_sdk import (
    AgentDefinition, ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage
)

from .utils import display_message

load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
_BUNDLED_PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_DIR = (
    _BUNDLED_PROMPT_DIR
    if _BUNDLED_PROMPT_DIR.is_dir()
    else PROJECT_ROOT / "prompts"
)

def load_prompt(filename: str) -> str:
    prompt_path = PROMPT_DIR / filename
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Required prompt file not found: {prompt_path}. "
            "Reinstall CareerPilot with its bundled prompts."
        ) from exc
    
async def main():
    main_agent_prompt = load_prompt("job-application-orchestrator.md")
    profile_agent_prompt = load_prompt("profile-architect.md")
    job_agent_prompt = load_prompt("job-intelligence.md")
    application_agent_prompt = load_prompt("application-engine.md")

    agents = {
        "profile-architect": AgentDefinition(
            description = "Transforms raw resume files into structured, machine-readable profiles optimized for automated job applications and matching.",
            prompt = profile_agent_prompt,
            tools = ["Read", "Grep", "Glob", "Bash"],
            model = "haiku"
        ),
        "job-intelligence": AgentDefinition(
            description = "Multi-source job search, intelligent scoring, and application method classification system.",
            prompt = job_agent_prompt,
            tools = ["WebSearch", "WebFetch","Read","Write", "Bash", "mcp__playwright__*"],
            model = "haiku"
        ),
        "application-engine": AgentDefinition(
            description = "Intelligent resume tailoring and multi-method application submission system. Operates per-job with human checkpoints.",
            prompt = application_agent_prompt,
            tools = ["WebSearch", "Read", "Write", "Bash", "mcp__playwright__*", "mcp__gmail__*"],
            model = "haiku"
        )
    }

    # MCP, tools, subagents
    options = ClaudeAgentOptions(
        system_prompt = main_agent_prompt,
        mcp_servers={
            "gmail": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@anthropic-ai/mcp-server-gmail"]
        },
            "playwright": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@playwright/mcp"]
        }
        
        },
        allowed_tools = ["Task", "Skills", "Write", "Bash", "WebSearch", "WebFetch", "mcp__playwright__*", "mcp__gmail__*"],
        agents = agents
    )

    async with ClaudeSDKClient(options=options) as client:
        print("starting conversation")
        print("Type exit to quit\n")

        while True:
            user_input = input('\033[1m'+'You'+'\033[0m'+': ')
            print('')
            if user_input.lower() == 'exit':
                break
            await client.query(user_input)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    display_message(message)

def run():
    """Non-async wrapper for the script entry point"""
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
