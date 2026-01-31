# Documentation, note-taking and planning
- Always create a docs/ folder in the project directory 
- Create a docs/NOTES.md file with a running, append-only log of the current state of the task, any learnings or discoveries, next steps and more
- Create a docs/CHANGELOG.md file with a running, append-only log of any code changes. 
- Make a git commit at each logical step. Use Conventional Commits spec to structure commit messages
- Create a logs/ folder in the project directory for any code/script generated output. Prefer JSONL structured logging

# Scripting
- Prefer python or typescript/javascript for scripting over bash scripts. Avoid bash unless absolutely necessary or its a very simple script
- When appropriate, create a Justfile with commonly used commands and keep it up to date.

### Python
- Prefer `uv` over other tools
- Prefer PEP 723 inline metadata for dependencies in small scripts, and use a `pyproject.toml` file for more complex projects

### Javascript
- Prefer `bun` and typescript over other tools
