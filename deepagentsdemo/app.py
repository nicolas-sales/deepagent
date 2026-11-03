"""Chatbot Streamlit basé sur deepagents.

Lancer depuis le dossier deepagentsdemo :
    streamlit run app.py
"""

import uuid

import streamlit as st
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from agent_factory import (
    BACKENDS,
    MODELS,
    AgentConfig,
    build_agent,
    build_input,
    fill_store,
    message_text,
)

st.set_page_config(page_title="Deep Agent Chatbot", page_icon="🤖", layout="wide")


# ---------------------------------------------------------------- Mémoire partagée entre les reruns

@st.cache_resource
def get_checkpointer():
    """Checkpointer = mémoire de conversation (court terme), une par thread_id."""
    return MemorySaver()


@st.cache_resource
def get_store():
    """Store = mémoire long terme partagée entre threads (utilisée par StoreBackend)."""
    return InMemoryStore()


checkpointer = get_checkpointer()
store = get_store()

if "threads" not in st.session_state:
    st.session_state.threads = {}          # thread_id -> liste de messages affichés
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"chat-{uuid.uuid4().hex[:8]}"
if "filled_namespaces" not in st.session_state:
    st.session_state.filled_namespaces = set()


def new_thread():
    st.session_state.thread_id = f"chat-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------- Barre latérale : toutes les variables

with st.sidebar:
    st.title("⚙️ Configuration")

    st.subheader("1. Type d'agent")
    agent_type = st.radio(
        "Agent",
        ["deep", "simple"],
        format_func=lambda x: "Deep agent (create_deep_agent)" if x == "deep" else "Agent simple (create_agent)",
        help="Agent simple = LLM + outils en boucle. Deep agent = + planification, fichiers, sous-agents, mémoire, skills.",
    )
    is_deep = agent_type == "deep"

    st.subheader("2. Modèle")
    model = st.selectbox("model", MODELS, index=0)
    if model.startswith("groq:"):
        st.caption("⚠️ Groq gratuit : 8k tokens/min et 200k tokens/jour. Un deep agent dépasse vite ces limites.")

    st.subheader("3. System prompt")
    system_prompt = st.text_area(
        "system_prompt",
        "You are a research assistant specializing in scientific literature. Always cite sources.",
        height=100,
    )

    st.subheader("4. Outils")
    use_web_search = st.checkbox("internet_search (Tavily)", value=True)

    st.subheader("5. Backend")
    backend = st.radio(
        "backend", list(BACKENDS), format_func=BACKENDS.get, disabled=not is_deep,
    )
    store_namespace = "demo-user"
    if backend == "store":
        store_namespace = st.text_input("namespace", "demo-user",
                                        help="Le 'dossier' du store. Un namespace par utilisateur = une mémoire par utilisateur.")
    elif backend == "filesystem":
        st.caption("CompositeBackend : `/AGENTS.md` → projects/, `/skills/` → skills/. L'agent ne voit pas les notebooks.")

    st.subheader("6. Contexte")
    use_memory = st.checkbox("memory = AGENTS.md (projects/AGENTS.md)", value=True, disabled=not is_deep)
    use_skills = st.checkbox("skills (python, langgraph, aws, report-writer)", value=True, disabled=not is_deep)
    force_skills = st.checkbox("Forcer l'utilisation des skills (règle dans le system prompt)",
                               value=True, disabled=not (is_deep and use_skills))

    st.subheader("7. Sous-agents")
    use_research = st.checkbox("research-agent (recherche web)", value=False, disabled=not is_deep)
    research_model = ""
    if use_research:
        research_model = st.selectbox("model du sous-agent", ["(même que l'agent principal)"] + MODELS)
        research_model = "" if research_model.startswith("(") else research_model
    use_structured = st.checkbox("researcher (sortie structurée ResearchFinding)", value=False, disabled=not is_deep)

    st.subheader("8. Exécution")
    recursion_limit = st.slider("recursion_limit", 10, 150, 50, step=5,
                                help="Nombre max d'étapes du graphe, pour éviter les boucles.")

    cfg = AgentConfig(
        agent_type=agent_type,
        model=model,
        system_prompt=system_prompt,
        use_web_search=use_web_search,
        backend=backend,
        store_namespace=store_namespace,
        use_memory=use_memory,
        use_skills=use_skills,
        force_skills=force_skills,
        use_research_subagent=use_research,
        research_subagent_model=research_model,
        use_structured_subagent=use_structured,
        recursion_limit=recursion_limit,
    )

    # Mémoire et skills sont chargés une fois par thread : nouvelle config -> nouvelle conversation
    if st.session_state.get("cfg_key") not in (None, cfg.key()):
        new_thread()
        st.toast("Configuration modifiée : nouvelle conversation (nouveau thread_id)")
    st.session_state.cfg_key = cfg.key()

    st.subheader("9. Conversation")
    st.code(f"thread_id = {st.session_state.thread_id}", language="python")
    st.button("➕ Nouvelle conversation", on_click=new_thread, use_container_width=True)


# ---------------------------------------------------------------- Zone de chat

thread_id = st.session_state.thread_id
history = st.session_state.threads.setdefault(thread_id, [])
config = {"configurable": {"thread_id": thread_id}, "recursion_limit": cfg.recursion_limit}

st.title("🤖 Deep Agent Chatbot")
st.caption(
    f"{'Deep agent' if is_deep else 'Agent simple'} · `{cfg.model}`"
    + (f" · backend `{cfg.backend}`" if is_deep else "")
)

for msg in history:
    with st.chat_message(msg["role"]):
        if msg.get("steps"):
            with st.expander(f"🔧 {len(msg['steps'])} étape(s) de l'agent"):
                st.markdown("\n".join(msg["steps"]))
        st.markdown(msg["content"])


def describe_update(namespace, node, update) -> list[str]:
    """Transforme une mise à jour du stream en lignes lisibles (outils appelés, sous-agents)."""
    lines = []
    where = "sous-agent" if namespace else "agent"
    messages = (update or {}).get("messages", []) if isinstance(update, dict) else []
    messages = getattr(messages, "value", messages)  # Overwrite(...) -> liste
    for m in messages if isinstance(messages, list) else []:
        for tc in getattr(m, "tool_calls", None) or []:
            args = tc.get("args", {})
            if tc["name"] == "task":
                lines.append(f"- **{where}** délègue à `{args.get('subagent_type')}` : {str(args.get('description', ''))[:150]}")
            else:
                short = ", ".join(f"{k}={str(v)[:60]!r}" for k, v in args.items() if k != "content")
                lines.append(f"- **{where}** → `{tc['name']}`({short})")
        if getattr(m, "type", "") == "tool":
            status = "❌" if "Error" in message_text(m)[:80] else "✅"
            lines.append(f"  - {status} résultat `{getattr(m, 'name', '')}`")
    return lines


if prompt := st.chat_input("Posez votre question…"):
    first_message = len(history) == 0
    history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # StoreBackend : on remplit le store une seule fois par namespace
    if is_deep and cfg.backend == "store" and cfg.store_namespace not in st.session_state.filled_namespaces:
        fill_store(store, cfg.store_namespace)
        st.session_state.filled_namespaces.add(cfg.store_namespace)

    with st.chat_message("assistant"):
        steps: list[str] = []
        try:
            agent = build_agent(cfg, checkpointer, store)
            with st.status("L'agent travaille…", expanded=True) as status:
                for namespace, chunk in agent.stream(
                    build_input(cfg, prompt, first_message),
                    config=config,
                    stream_mode="updates",
                    subgraphs=True,
                ):
                    for node, update in chunk.items():
                        new_lines = describe_update(namespace, node, update)
                        steps.extend(new_lines)
                        for line in new_lines:
                            st.markdown(line)
                status.update(label=f"Terminé · {len(steps)} étape(s)", state="complete", expanded=False)

            final = agent.get_state(config).values["messages"][-1]
            answer = message_text(final) or "_(réponse vide)_"
        except Exception as exc:  # erreurs API (429 Groq, 400 outil inventé...)
            answer = f"❌ **Erreur** : `{type(exc).__name__}`\n\n```\n{str(exc)[:800]}\n```"
            if "rate_limit" in str(exc) or "429" in str(exc) or "413" in str(exc):
                answer += "\n\n💡 Limite de tokens atteinte : changez de modèle (ex. `openai:gpt-4o-mini`)."
        st.markdown(answer)

    history.append({"role": "assistant", "content": answer, "steps": steps})


# ---------------------------------------------------------------- Inspection de la mémoire

if is_deep and history:
    with st.expander("🗂️ Fichiers vus par l'agent"):
        if cfg.backend == "state":
            state = build_agent(cfg, checkpointer, store).get_state(config).values
            files = state.get("files", {})
            st.caption("StateBackend : fichiers dans l'état du thread (state['files']).")
            st.write(sorted(files))
        elif cfg.backend == "store":
            items = store.search((cfg.store_namespace,), limit=100)
            st.caption(f"StoreBackend : fichiers du namespace ('{cfg.store_namespace}',), partagés entre threads.")
            st.write(sorted(item.key for item in items))
        else:
            st.caption("FilesystemBackend : fichiers réels sur le disque (projects/ et skills/).")
