# LangGraph - Examples

## Example 1 - Workflow with nodes and edges
```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    question: str
    answer: str

def answer_node(state: State) -> dict:
    return {"answer": f"You asked: {state['question']}"}

graph = StateGraph(State)
graph.add_node("answer", answer_node)
graph.add_edge(START, "answer")
graph.add_edge("answer", END)
app = graph.compile()
print(app.invoke({"question": "Hello?"}))
```

## Example 2 - Deep agent with memory and skills
```python
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    model="groq:openai/gpt-oss-20b",
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    memory=["/AGENTS.md"],
    skills=["/skills/"],
    checkpointer=MemorySaver(),
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain checkpointers"}]},
    config={"configurable": {"thread_id": "demo-1"}},
)
```
