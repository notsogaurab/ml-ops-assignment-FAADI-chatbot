import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Chatbot", layout="wide")


def fetch_threads():
    try:
        resp = requests.get(f"{BACKEND_URL}/threads")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def create_new_thread():
    try:
        resp = requests.post(f"{BACKEND_URL}/threads", params={"title": "New Chat"})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def fetch_messages(thread_id):
    try:
        resp = requests.get(f"{BACKEND_URL}/threads/{thread_id}/messages")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def delete_thread(thread_id):
    try:
        requests.delete(f"{BACKEND_URL}/threads/{thread_id}")
    except Exception:
        pass


if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("💬 Chat Threads")

    if st.button("➕ New Chat", use_container_width=True):
        thread = create_new_thread()
        if thread:
            st.session_state.current_thread_id = thread["id"]
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    threads = fetch_threads()
    for thread in threads:
        col1, col2 = st.columns([4, 1])
        with col1:
            label = thread["title"][:30] + ("..." if len(thread["title"]) > 30 else "")
            is_active = st.session_state.current_thread_id == thread["id"]
            if st.button(
                f"{'▶ ' if is_active else ''}{label}",
                key=f"thread_{thread['id']}",
                use_container_width=True,
            ):
                st.session_state.current_thread_id = thread["id"]
                msgs = fetch_messages(thread["id"])
                st.session_state.messages = [
                    {
                        "role": m["role"],
                        "content": m["content"],
                        "sources": m.get("sources", []),
                    }
                    for m in msgs
                ]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{thread['id']}"):
                delete_thread(thread["id"])
                if st.session_state.current_thread_id == thread["id"]:
                    st.session_state.current_thread_id = None
                    st.session_state.messages = []
                st.rerun()

    st.markdown("---")
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

    if uploaded_file is not None:
        if st.button("Index Document"):
            with st.spinner("Indexing..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                    }
                    response = requests.post(f"{BACKEND_URL}/index", files=files)

                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "skipped":
                            st.info(
                                f"'{data['filename']}' is already indexed. Skipped."
                            )
                        else:
                            st.success(
                                f"Indexed {data['filename']} ({data['num_chunks']} chunks)!"
                            )
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    st.markdown("---")
    st.caption(f"Backend: {BACKEND_URL}")

st.title("📚 RAG Chatbot")

if not st.session_state.current_thread_id:
    st.info("Start a new chat or select an existing thread from the sidebar.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            with st.expander("📎 View Sources"):
                for idx, source in enumerate(message["sources"]):
                    src_text = (
                        source.get("text", "")
                        if isinstance(source, dict)
                        else str(source)
                    )
                    st.markdown(f"**[{idx + 1}]**")
                    st.caption(src_text)

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {"query": prompt}
                if st.session_state.current_thread_id:
                    payload["thread_id"] = st.session_state.current_thread_id

                response = requests.post(f"{BACKEND_URL}/chat", json=payload)

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data.get("sources", [])
                    thread_id = data.get("thread_id")

                    if thread_id and not st.session_state.current_thread_id:
                        st.session_state.current_thread_id = thread_id

                    st.write(answer)
                    if sources:
                        with st.expander("📎 View Sources"):
                            for idx, source in enumerate(sources):
                                st.markdown(f"**[{idx + 1}]**")
                                st.caption(source.get("text", ""))

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
                else:
                    st.error(f"Backend Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
