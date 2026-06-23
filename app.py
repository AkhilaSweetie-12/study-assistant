import os

import gradio as gr

from config import Config
from indexing.processor import DocumentProcessor
from llm.azure_openai import AzureOpenAIClient
from search.azure_search import AzureSearchClient

# ------------------------------------------------------------------ #
#  Initialise                                                          #
# ------------------------------------------------------------------ #

config = Config()
processor = DocumentProcessor(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
search_client = AzureSearchClient(config)
llm_client = AzureOpenAIClient(config)

try:
    search_client.create_study_index()
    search_client.create_code_index()
    print("Azure AI Search indexes ready.")
except Exception as e:
    print(f"Index initialisation warning (may already exist): {e}")


# ------------------------------------------------------------------ #
#  Study Assistant handlers                                            #
# ------------------------------------------------------------------ #

def index_study_files(files):
    if not files:
        return "⚠️ No files uploaded."

    total_chunks = 0
    results = []

    for file in files:
        try:
            chunks = processor.process_study_document(file.name)
            docs_to_upload = []
            for chunk in chunks:
                chunk["content_vector"] = llm_client.get_embedding(chunk["content"])
                docs_to_upload.append(chunk)

            search_client.upload_documents(docs_to_upload, index_type="study")
            total_chunks += len(chunks)
            results.append(f"✅ {os.path.basename(file.name)} — {len(chunks)} chunks indexed")
        except Exception as e:
            results.append(f"❌ {os.path.basename(file.name)} — Error: {e}")

    return f"**Total chunks indexed: {total_chunks}**\n\n" + "\n".join(results)


def study_chat(message: str, history: list):
    if not message.strip():
        return history, ""

    try:
        query_vector = llm_client.get_embedding(message)
        results = search_client.search(message, query_vector, index_type="study", top_k=config.TOP_K)

        if not results:
            response = "No relevant study materials found. Please upload and index some documents first."
        else:
            response = llm_client.study_rag_response(message, results)

    except Exception as e:
        response = f"⚠️ Error: {e}"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return history, ""


def generate_quiz(topic: str):
    if not topic.strip():
        return "⚠️ Please enter a topic."

    try:
        query_vector = llm_client.get_embedding(topic)
        results = search_client.search(topic, query_vector, index_type="study", top_k=3)

        if not results:
            return "No study materials found for this topic. Please index documents first."

        return llm_client.generate_quiz(topic, results)
    except Exception as e:
        return f"⚠️ Error: {e}"


def generate_summary(topic: str):
    if not topic.strip():
        return "⚠️ Please enter a topic or keyword."

    try:
        query_vector = llm_client.get_embedding(topic)
        results = search_client.search(topic, query_vector, index_type="study", top_k=5)

        if not results:
            return "No relevant study material found. Please index documents first."

        return llm_client.generate_summary(results)
    except Exception as e:
        return f"⚠️ Error: {e}"


# ------------------------------------------------------------------ #
#  Code Documentation handlers                                         #
# ------------------------------------------------------------------ #

def index_code_files(files):
    if not files:
        return "⚠️ No files uploaded."

    total_chunks = 0
    results = []

    for file in files:
        try:
            chunks = processor.process_code_document(file.name)
            docs_to_upload = []
            for chunk in chunks:
                chunk["content_vector"] = llm_client.get_embedding(chunk["content"])
                docs_to_upload.append(chunk)

            search_client.upload_documents(docs_to_upload, index_type="code")
            total_chunks += len(chunks)
            results.append(f"✅ {os.path.basename(file.name)} — {len(chunks)} chunks indexed")
        except Exception as e:
            results.append(f"❌ {os.path.basename(file.name)} — Error: {e}")

    return f"**Total chunks indexed: {total_chunks}**\n\n" + "\n".join(results)


def code_chat(message: str, history: list):
    if not message.strip():
        return history, ""

    try:
        query_vector = llm_client.get_embedding(message)
        results = search_client.search(message, query_vector, index_type="code", top_k=config.TOP_K)

        if not results:
            response = "No relevant code documentation found. Please upload and index files first."
        else:
            response = llm_client.code_rag_response(message, results)

    except Exception as e:
        response = f"⚠️ Error: {e}"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return history, ""


# ------------------------------------------------------------------ #
#  Gradio UI                                                           #
# ------------------------------------------------------------------ #

with gr.Blocks(
    title="AI Study & Code Assistant",
) as demo:

    gr.Markdown(
        """
        # 🧠 AI Study & Code Documentation Assistant
        **Powered by Azure OpenAI (GPT-4o) + Azure AI Search**
        Upload your materials, then chat — or generate quizzes and summaries on the fly.
        """
    )

    with gr.Tabs():

        # ── Tab 1: Study Assistant ──────────────────────────────────── #
        with gr.Tab("📚 Study Assistant"):
            with gr.Row():

                # Left panel — upload & tools
                with gr.Column(scale=1, min_width=300):
                    gr.Markdown("### 📂 Upload Study Materials")
                    study_upload = gr.File(
                        label="Drop files here",
                        file_count="multiple",
                        file_types=[".pdf", ".txt", ".md"],
                    )
                    index_study_btn = gr.Button("⚡ Index Documents", variant="primary")
                    index_study_status = gr.Markdown(label="Status")

                    gr.Markdown("---")
                    gr.Markdown("### 🛠️ Study Tools")

                    with gr.Accordion("📝 Quiz Generator", open=False):
                        quiz_topic = gr.Textbox(
                            label="Topic",
                            placeholder="e.g. neural networks, recursion, photosynthesis",
                        )
                        quiz_btn = gr.Button("Generate Quiz", variant="secondary")
                        quiz_output = gr.Markdown(label="Quiz")

                    with gr.Accordion("📋 Topic Summary", open=False):
                        summary_topic = gr.Textbox(
                            label="Topic / keyword",
                            placeholder="e.g. gradient descent",
                        )
                        summary_btn = gr.Button("Generate Summary", variant="secondary")
                        summary_output = gr.Markdown(label="Summary")

                # Right panel — chat
                with gr.Column(scale=2):
                    gr.Markdown("### 💬 Ask Questions")
                    study_chatbot = gr.Chatbot(elem_classes="chatbot", show_label=False, type="messages")
                    study_input = gr.Textbox(
                        placeholder="e.g. Explain the concept of backpropagation...",
                        lines=2,
                        label="Your question",
                    )
                    with gr.Row():
                        study_send_btn = gr.Button("Send", variant="primary")
                        study_clear_btn = gr.Button("Clear Chat")

            # Events — Study
            index_study_btn.click(index_study_files, inputs=study_upload, outputs=index_study_status)
            study_send_btn.click(study_chat, inputs=[study_input, study_chatbot], outputs=[study_chatbot, study_input])
            study_input.submit(study_chat, inputs=[study_input, study_chatbot], outputs=[study_chatbot, study_input])
            study_clear_btn.click(lambda: ([], ""), outputs=[study_chatbot, study_input])
            quiz_btn.click(generate_quiz, inputs=quiz_topic, outputs=quiz_output)
            summary_btn.click(generate_summary, inputs=summary_topic, outputs=summary_output)

        # ── Tab 2: Code Documentation Search ───────────────────────── #
        with gr.Tab("💻 Code Documentation Search"):
            with gr.Row():

                # Left panel — upload
                with gr.Column(scale=1, min_width=300):
                    gr.Markdown("### 📂 Upload Code / Docs")
                    code_upload = gr.File(
                        label="Drop files here",
                        file_count="multiple",
                        file_types=[
                            ".py", ".js", ".ts", ".java", ".cs",
                            ".go", ".rs", ".md", ".txt", ".yaml",
                            ".yml", ".json",
                        ],
                    )
                    index_code_btn = gr.Button("⚡ Index Files", variant="primary")
                    index_code_status = gr.Markdown(label="Status")

                    gr.Markdown("---")
                    gr.Markdown(
                        "**Supported languages:**\n"
                        "Python · JavaScript · TypeScript · Java · C# · Go · Rust · Markdown · YAML · JSON"
                    )

                # Right panel — chat
                with gr.Column(scale=2):
                    gr.Markdown("### 🔍 Search Your Codebase")
                    code_chatbot = gr.Chatbot(elem_classes="chatbot", show_label=False, type="messages")
                    code_input = gr.Textbox(
                        placeholder="e.g. How does authentication work? Show me the database connection setup...",
                        lines=2,
                        label="Your question",
                    )
                    with gr.Row():
                        code_send_btn = gr.Button("Search", variant="primary")
                        code_clear_btn = gr.Button("Clear Chat")

            # Events — Code
            index_code_btn.click(index_code_files, inputs=code_upload, outputs=index_code_status)
            code_send_btn.click(code_chat, inputs=[code_input, code_chatbot], outputs=[code_chatbot, code_input])
            code_input.submit(code_chat, inputs=[code_input, code_chatbot], outputs=[code_chatbot, code_input])
            code_clear_btn.click(lambda: ([], ""), outputs=[code_chatbot, code_input])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True, theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"), css=".chatbot {height: 460px;}")
