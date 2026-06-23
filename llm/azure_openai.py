from typing import Dict, List

from openai import AzureOpenAI

from config import Config


class AzureOpenAIClient:
    def __init__(self, config: Config):
        self.config = config
        self.client = AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
        )

    # ------------------------------------------------------------------ #
    #  Embeddings                                                          #
    # ------------------------------------------------------------------ #

    def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )
        return response.data[0].embedding

    # ------------------------------------------------------------------ #
    #  Base chat                                                           #
    # ------------------------------------------------------------------ #

    def _chat(self, messages: List[Dict[str, str]], max_tokens: int = 1500) -> str:
        response = self.client.chat.completions.create(
            model=self.config.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    # ------------------------------------------------------------------ #
    #  Study Assistant                                                     #
    # ------------------------------------------------------------------ #

    def study_rag_response(self, query: str, context_chunks: List[Dict]) -> str:
        context = "\n\n".join(
            f"[Source: {c.get('source', 'Unknown')}]\n{c['content']}"
            for c in context_chunks
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent study assistant. Use the provided context from "
                    "study materials to answer questions clearly and thoroughly.\n\n"
                    "Rules:\n"
                    "- Base your answers strictly on the provided context\n"
                    "- If the context does not contain the answer, say so clearly\n"
                    "- Use bullet points, headers, and examples to aid understanding\n"
                    "- Cite the source document when referencing specific facts"
                ),
            },
            {
                "role": "user",
                "content": f"Context from study materials:\n{context}\n\nQuestion: {query}",
            },
        ]
        return self._chat(messages)

    def generate_quiz(self, topic: str, context_chunks: List[Dict]) -> str:
        context = "\n\n".join(c["content"] for c in context_chunks[:3])

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert educator. Generate exactly 5 multiple-choice questions "
                    "based on the provided study material. For each question:\n"
                    "- Write 4 answer options labeled A, B, C, D\n"
                    "- Mark the correct answer at the end\n"
                    "- Keep questions factual and grounded in the material"
                ),
            },
            {
                "role": "user",
                "content": f"Study material:\n{context}\n\nGenerate a 5-question quiz on: {topic}",
            },
        ]
        return self._chat(messages, max_tokens=2000)

    def generate_summary(self, context_chunks: List[Dict]) -> str:
        context = "\n\n".join(c["content"] for c in context_chunks[:5])

        messages = [
            {
                "role": "system",
                "content": "You are a study assistant. Summarize the provided material concisely using bullet points grouped by key topics.",
            },
            {
                "role": "user",
                "content": f"Summarize the following study material:\n{context}",
            },
        ]
        return self._chat(messages, max_tokens=1000)

    # ------------------------------------------------------------------ #
    #  Code Documentation                                                  #
    # ------------------------------------------------------------------ #

    def code_rag_response(self, query: str, context_chunks: List[Dict]) -> str:
        context_parts = []
        for c in context_chunks:
            lang = c.get("language", "text")
            filename = c.get("filename", c.get("source", "Unknown"))
            context_parts.append(f"[File: {filename} | Language: {lang}]\n```{lang}\n{c['content']}\n```")

        context = "\n\n".join(context_parts)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer and code documentation assistant. "
                    "Answer developer questions using the provided code context.\n\n"
                    "Rules:\n"
                    "- Reference specific files and functions by name\n"
                    "- Include relevant code snippets in your answer\n"
                    "- Highlight important patterns, caveats, and best practices\n"
                    "- If the code context is insufficient, clearly state what is missing"
                ),
            },
            {
                "role": "user",
                "content": f"Code context:\n{context}\n\nDeveloper question: {query}",
            },
        ]
        return self._chat(messages)
