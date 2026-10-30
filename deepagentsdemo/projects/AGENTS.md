# Deep Agents - Project Memory

## Role
You are a research assistant specializing in scientific literature and AI agent architectures.
- Always cite your sources. Never invent references; if a source cannot be verified, say so.
- Answer in a concise, structured way.

## What is Deep Agents?
`deepagents` is an open-source library from LangChain, built on top of LangGraph.
It creates agents that can handle long, multi-step tasks, going beyond a simple
"LLM calling tools in a loop" agent. It is created with `create_deep_agent(...)`,
which returns a compiled LangGraph graph (`invoke`, `stream`, ...).

## Architecture - the 4 pillars
1. **Detailed system prompt**
   A long built-in prompt explaining how to plan, use the files and delegate work.
   The user's `system_prompt` is added on top of it.
2. **Planning tool - `write_todos`**
   The agent writes and updates a todo list to break a task into steps and track progress.
3. **Filesystem - `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`**
   Used to offload large context (notes, results) out of the message history.
   The storage depends on the **backend**:
   - `StateBackend` (default): virtual files stored in the LangGraph state (ephemeral).
   - `FilesystemBackend`: real files on disk, under `root_dir`.
   - `StoreBackend`: persistent storage across threads (LangGraph Store).
   - `CompositeBackend`: routes path prefixes to different backends.
4. **Subagents - `task` tool**
   The main agent can spawn subagents with their own context window to isolate
   subtasks (context quarantine). A `general-purpose` subagent is always available;
   custom ones are passed with `subagents=[...]`.

## Middleware
Each capability is implemented as a LangChain agent middleware:
- `TodoListMiddleware` -> planning
- `FilesystemMiddleware` -> file tools
- `SubAgentMiddleware` -> `task` tool
- `SummarizationMiddleware` -> summarizes history when the context gets too long
- `MemoryMiddleware` -> loads `AGENTS.md` files (like this one) into the system prompt
- `HumanInTheLoopMiddleware` -> pauses on tools listed in `interrupt_on`

## Context engineering
- **Input context**: system prompt, `AGENTS.md` memory (always loaded), skills (loaded on demand).
- **Runtime context**: todos, files, summarization, subagent isolation.
- `AGENTS.md` = persistent memory, injected into the prompt at every invocation.
  The agent can update it with `edit_file` to remember things between sessions.

## Main parameters of `create_deep_agent`
`model`, `tools`, `system_prompt`, `subagents`, `backend`, `memory`, `skills`,
`interrupt_on`, `checkpointer`, `store`, `response_format`.
