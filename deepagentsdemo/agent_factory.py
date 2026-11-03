"""Construction des agents du chatbot, à partir des notions vues dans les notebooks.

- basicdeepagent.ipynb   : modèle, outil web_search (Tavily), create_agent vs create_deep_agent
- backends.ipynb         : StateBackend, FilesystemBackend, StoreBackend (namespace)
- contextengineering.ipynb : memory (AGENTS.md), skills, checkpointer, files, CompositeBackend
- subagents.ipynb        : sous-agents, modèle du sous-agent, response_format
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tavily import TavilyClient

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend, StoreBackend
from deepagents.backends.composite import CompositeBackend
from deepagents.backends.utils import create_file_data
from langchain.agents import create_agent

load_dotenv()

BASE_DIR = Path(__file__).parent
PROJECTS_DIR = BASE_DIR / "projects"
SKILLS_DIR = BASE_DIR / "skills"

# Chemins vus par l'agent (identiques pour tous les backends)
MEMORY_PATH = "/AGENTS.md"
SKILLS_PATH = "/skills/"

MODELS = [
    "openai:gpt-4o-mini",
    "openai:gpt-4o",
    "groq:openai/gpt-oss-20b",
    "groq:openai/gpt-oss-120b",
    "groq:llama-3.3-70b-versatile",
]

BACKENDS = {
    "state": "StateBackend - fichiers dans l'état du thread (éphémère)",
    "store": "StoreBackend - store partagé entre threads (mémoire long terme)",
    "filesystem": "FilesystemBackend - vrai disque (projects/ + skills/)",
}

SKILLS_RULE = (
    "Before answering ANY request, you MUST read_file the SKILL.md of every matching skill "
    "from the Skills list. For any code request, read /skills/python/SKILL.md first. "
    "Always finish by applying the report-writer skill."
)

SUBAGENTS_RULE = (
    "For any question that needs research or up-to-date information, do NOT answer from memory: "
    "delegate it with the task tool to the research subagent (research-agent or researcher), "
    "then write the final answer from its findings."
)


# ---------------------------------------------------------------- Outil (basicdeepagent / subagents)

_tavily_client = None


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# ---------------------------------------------------------------- Sortie structurée (subagents)

class ResearchFinding(BaseModel):
    """Structured findings from a research task"""
    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLS")


# ---------------------------------------------------------------- Configuration

@dataclass
class AgentConfig:
    agent_type: Literal["deep", "simple"] = "deep"
    model: str = "openai:gpt-4o-mini"
    system_prompt: str = "You are a helpful research assistant. Always cite sources."
    use_web_search: bool = True
    backend: Literal["state", "store", "filesystem"] = "state"
    store_namespace: str = "demo-user"
    use_memory: bool = True
    use_skills: bool = True
    force_skills: bool = True
    use_research_subagent: bool = False
    research_subagent_model: str = ""  # vide = même modèle que l'agent principal
    use_structured_subagent: bool = False
    recursion_limit: int = 50
    extra: dict = field(default_factory=dict)

    def key(self) -> tuple:
        """Identifie une configuration (pour savoir s'il faut une nouvelle conversation)."""
        return tuple(sorted((k, str(v)) for k, v in self.__dict__.items()))


# ---------------------------------------------------------------- Fichiers de contexte

def context_files() -> dict:
    """AGENTS.md + tous les fichiers des skills, au format attendu par les backends."""
    files = {}
    agents_md = PROJECTS_DIR / "AGENTS.md"
    if agents_md.exists():
        files[MEMORY_PATH] = create_file_data(agents_md.read_text(encoding="utf-8"))
    for p in SKILLS_DIR.glob("*/*.md"):
        files[f"{SKILLS_PATH}{p.parent.name}/{p.name}"] = create_file_data(p.read_text(encoding="utf-8"))
    return files


def fill_store(store, namespace: str) -> None:
    """StoreBackend : on dépose les fichiers une seule fois (store.put)."""
    for path, data in context_files().items():
        store.put((namespace,), path, data)


# ---------------------------------------------------------------- Construction

def build_backend(cfg: AgentConfig, store):
    if cfg.backend == "state":
        return StateBackend()
    if cfg.backend == "store":
        return StoreBackend(store=store, namespace=lambda rt: (cfg.store_namespace,))
    # FilesystemBackend limité à projects/ et skills/ (évite de lire les gros notebooks)
    return CompositeBackend(
        default=FilesystemBackend(root_dir=PROJECTS_DIR, virtual_mode=True),
        routes={SKILLS_PATH: FilesystemBackend(root_dir=SKILLS_DIR, virtual_mode=True)},
    )


def build_subagents(cfg: AgentConfig, tools: list) -> list:
    subagents = []
    if cfg.use_research_subagent:
        sub = {
            "name": "research-agent",
            "description": "Used to research more in depth questions",
            "system_prompt": (
                "You are a great researcher. Use the internet_search tool to find information, "
                "then summarize it with sources."
            ),
            "tools": tools or [internet_search],
        }
        if cfg.research_subagent_model:
            sub["model"] = cfg.research_subagent_model
        subagents.append(sub)
    if cfg.use_structured_subagent:
        subagents.append({
            "name": "researcher",
            "description": "Researches topics and returns structured findings (summary, confidence, sources)",
            "system_prompt": "Research the given topic thoroughly. Return your findings",
            "tools": tools or [internet_search],
            "response_format": ResearchFinding,
        })
    return subagents


def build_agent(cfg: AgentConfig, checkpointer, store):
    tools = [internet_search] if cfg.use_web_search else []

    if cfg.agent_type == "simple":
        # Agent classique : LLM + outils en boucle (create_agent)
        return create_agent(
            model=cfg.model,
            tools=tools,
            system_prompt=cfg.system_prompt or None,
            checkpointer=checkpointer,
        )

    system_prompt = cfg.system_prompt
    if cfg.use_skills and cfg.force_skills:
        system_prompt = f"{system_prompt}\n\n{SKILLS_RULE}".strip()
    if cfg.use_research_subagent or cfg.use_structured_subagent:
        system_prompt = f"{system_prompt}\n\n{SUBAGENTS_RULE}".strip()

    return create_deep_agent(
        model=cfg.model,
        tools=tools,
        system_prompt=system_prompt or None,
        backend=build_backend(cfg, store),
        memory=[MEMORY_PATH] if cfg.use_memory else None,
        skills=[SKILLS_PATH] if cfg.use_skills else None,
        subagents=build_subagents(cfg, tools) or None,
        store=store,
        checkpointer=checkpointer,
    )


def build_input(cfg: AgentConfig, user_text: str, first_message: bool) -> dict:
    """Avec StateBackend, AGENTS.md et les skills sont déposés dans "files" au 1er message du thread."""
    payload = {"messages": [{"role": "user", "content": user_text}]}
    if cfg.agent_type == "deep" and cfg.backend == "state" and first_message:
        files = context_files()
        if not cfg.use_memory:
            files.pop(MEMORY_PATH, None)
        if not cfg.use_skills:
            files = {k: v for k, v in files.items() if not k.startswith(SKILLS_PATH)}
        if files:
            payload["files"] = files
    return payload


def message_text(message) -> str:
    """Texte d'un message, que content soit une chaîne ou une liste de blocs (API Responses d'OpenAI)."""
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return str(content)
