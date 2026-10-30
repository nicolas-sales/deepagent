# LangGraph - Instructions

## Choose the right level
- **Fixed path known in advance** -> `StateGraph` with nodes + edges (workflow).
- **LLM decides, short task with tools** -> `create_agent(model, tools)`.
- **Long multi-step task (plan, files, subagents, memory)** -> `create_deep_agent(...)`.
Always say which level you chose and why.

## Core concepts to explain correctly
- **State**: a TypedDict shared by all nodes; nodes return partial updates.
- **Nodes**: Python functions `(state) -> dict`.
- **Edges**: `add_edge` (fixed) or `add_conditional_edges` (router function).
- **Checkpointer** (`MemorySaver`, Postgres...): short-term memory of ONE thread,
  selected with `config={"configurable": {"thread_id": "..."}}`.
- **Store** (`InMemoryStore`, `PostgresStore`): long-term memory shared across threads.

## deepagents specifics
- Backends: `StateBackend` (default, per thread), `StoreBackend` (shared store),
  `FilesystemBackend(root_dir=..., virtual_mode=True)` (real disk), `CompositeBackend` (routing).
- `memory=[path]` loads AGENTS.md into the system prompt; `skills=[dir]` exposes skills.
- The path in `memory=` must exactly match where the file is stored, otherwise it is silently ignored.

## Answer format
- Give a minimal runnable example, then explain each part.
- Mention token cost when relevant (deep agents use large prompts).
