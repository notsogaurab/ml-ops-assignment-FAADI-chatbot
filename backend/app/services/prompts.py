SYSTEM_PROMPT = (
    "You are a helpful and precise assistant for Question Answering tasks.\n"
    "Your goal is to answer the user's question based ONLY on the provided context.\n\n"
    "Rules:\n"
    "1. Use ONLY the information from the provided context to answer.\n"
    "2. Cite your sources using inline references like [1], [2], etc. matching the source numbers.\n"
    '3. If the context does not contain enough information, say: "I don\'t have enough information in the provided documents to answer this question."\n'
    "4. Do NOT make up information or use outside knowledge.\n"
    "5. Be clear, structured, and comprehensive.\n"
    "6. When multiple sources support a claim, cite all of them, e.g. [1][3].\n"
)

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Context:\n[1] Python was created by Guido van Rossum in 1991.\n\nQuestion: Who created Python?",
    },
    {
        "role": "assistant",
        "content": "Python was created by Guido van Rossum in 1991 [1].",
    },
    {
        "role": "user",
        "content": "Context:\n[1] ML learns from data.\n\nQuestion: What is quantum computing?",
    },
    {
        "role": "assistant",
        "content": "I don't have enough information in the provided documents to answer this question.",
    },
]


def build_user_prompt(context_chunks, query, chat_history=None):
    numbered_context = []
    for i, chunk in enumerate(context_chunks, 1):
        numbered_context.append(f"[{i}] {chunk}")

    context_str = "\n\n".join(numbered_context)

    history_str = ""
    if chat_history:
        history_parts = []
        for msg in chat_history:
            role = msg["role"].capitalize()
            history_parts.append(f"{role}: {msg['content']}")
        history_str = "Previous conversation:\n" + "\n".join(history_parts) + "\n\n"

    return f"{history_str}Context:\n{context_str}\n\nQuestion: {query}"
