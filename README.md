# Deep Agents Demo

Notebooks and a Streamlit chatbot to learn [deepagents](https://github.com/langchain-ai/deepagents) (LangChain / LangGraph).

## Installation

From the project root:

```bash
python -m venv venvda
venvda\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file at the root with your keys:

```
OPENAI_API_KEY=...
GROQ_API_KEY=...
TAVILY_API_KEY=...
GOOGLE_API_KEY=...
```

## Run the chatbot

```bash
cd deepagentsdemo
streamlit run app.py
```

Every setting is in the sidebar: model, system prompt, tools, backend, memory, skills, subagents, `thread_id`.

## Structure

```
deepagent/
├── .env
├── requirements.txt
└── deepagentsdemo/
    ├── basicdeepagent.ipynb
    ├── backends.ipynb
    ├── contextengineering.ipynb
    ├── subagents.ipynb
    ├── app.py
    ├── agent_factory.py
    ├── projects/AGENTS.md
    └── skills/
```

| File / folder | Purpose |
|---|---|
| `basicdeepagent.ipynb` | Simple agent (`create_agent`) vs deep agent (`create_deep_agent`), web search tool |
| `backends.ipynb` | `StateBackend`, `FilesystemBackend`, `StoreBackend` |
| `contextengineering.ipynb` | System prompt, `AGENTS.md` memory, checkpointer, skills |
| `subagents.ipynb` | Subagents and structured output (`response_format`) |
| `app.py` | Streamlit chatbot UI |
| `agent_factory.py` | Builds the agent from the selected configuration |
| `projects/AGENTS.md` | Project memory, loaded on every call |
| `skills/` | `python`, `langgraph`, `aws`, `report-writer` skills (`SKILL.md`, `instructions.md`, `examples.md`) |

## Key concepts

- **Checkpointer + `thread_id`**: memory of one conversation (short term).
- **Backend + `memory=`**: project memory (`AGENTS.md`), long term depending on the backend.
- **Skills**: context loaded on demand; the model decides when to read them.
- **Subagents**: a task is delegated with the `task` tool, in an isolated context.

## Common pitfalls

- The path in `memory=` / `skills=` must be **exactly** the path where the file is stored, otherwise it is silently ignored.
- Memory and skills are loaded **once per thread**: after a change, use a new `thread_id`.
- With `FilesystemBackend`, restrict `root_dir` so the agent does not read the notebooks (context too large).
- Groq free tier: 8k tokens/min and 200k tokens/day, quickly reached with a deep agent.
