# Report Writer - Example

**User:** What is a checkpointer in LangGraph?

**Answer:**

# Report: Checkpointer in LangGraph

## Summary
A checkpointer saves the state of a graph after each step. It gives an agent short-term
memory of a conversation, identified by a `thread_id`.

## Details
- Created with `MemorySaver()` (RAM) or a database saver (Postgres, SQLite).
- Passed with `create_deep_agent(..., checkpointer=checkpointer)`.
- Same `thread_id` = same conversation; new `thread_id` = new conversation.

## Skills used
langgraph, report-writer

## Sources
- /skills/langgraph/instructions.md
- LangGraph documentation: https://langchain-ai.github.io/langgraph/concepts/persistence/

## Next steps
1. Call the agent twice with the same `thread_id` and check it remembers.
2. Compare with a `StoreBackend` for long-term memory.
