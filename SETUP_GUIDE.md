# Setup Guide — AI Study & Code Documentation Assistant

Complete step-by-step instructions to provision Azure resources, configure credentials, and run the application.

---

## Session Summary — What Was Completed

| Step | Status | Details |
|---|---|---|
| Azure Subscription | ✅ | Azure subscription 1 — Kanini (kanini.com) |
| Azure OpenAI Resource | ✅ | `study-assistant-openai` — East US — Standard S0 |
| gpt-4o Deployment | ✅ | Version 2024-11-20 — Succeeded |
| text-embedding-ada-002 Deployment | ✅ | Version 2 — Succeeded |
| Azure AI Search Resource | ✅ | `study-assistant-search` — Central US — Standard |
| `.env` Configuration | ✅ | All credentials set |
| Python Dependencies | ✅ | `pip install -r requirements.txt` — 56 packages installed |

---

## Prerequisites

- An active **Azure subscription**
- **Python 3.9+** installed locally
- **Git** installed locally

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/AkhilaSweetie-12/study-assistant.git
cd study-assistant
```

---

## Step 2 — Create Azure OpenAI Resource

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **"Azure OpenAI"** in the top search bar → select it
3. Click **+ Create** → choose **"Azure OpenAI"** (not Foundry)
4. Fill in the form:

   | Field | Value used |
   |---|---|
   | Subscription | Azure subscription 1 |
   | Resource group | `study-assistant-rg` (create new) |
   | Region | `East US` |
   | Name | `study-assistant-openai` |
   | Pricing tier | Standard S0 |

5. **Network tab:** Keep default — *"All networks, including the internet"*
6. Skip **Tags** tab
7. Click **Review + Create** → **Create**
8. Wait ~2 minutes for deployment to complete

### Get Azure OpenAI Credentials

1. Open the created resource → left sidebar → **Keys and Endpoint**
2. Copy **KEY 1** → this is your `AZURE_OPENAI_API_KEY`
3. Copy the **Endpoint** URL → this is your `AZURE_OPENAI_ENDPOINT`

> **Tip:** If you accidentally expose KEY 1, regenerate it from the same page and use KEY 2 in the meantime.

**Actual resource endpoint used:**
```
https://study-assistant-openai.openai.azure.com/
```

---

## Step 3 — Deploy Models in Azure OpenAI Studio

1. Go to [oai.azure.com](https://oai.azure.com) → select resource `study-assistant-openai`
2. If redirected to Microsoft Foundry (ai.azure.com) → click **"Open in Foundry Classic"**
3. Left sidebar → **Deployments** (under Shared resources) → **+ Deploy model** → **Deploy base model**

### Deploy Chat Model

| Field | Value |
|---|---|
| Model | `gpt-4o` |
| Deployment name | `gpt-4o` *(exact — must match `.env`)* |
| Version | 2024-11-20 |
| Type | Standard |

### Deploy Embedding Model

| Field | Value |
|---|---|
| Model | `text-embedding-ada-002` |
| Deployment name | `text-embedding-ada-002` *(exact — must match `.env`)* |
| Version | 2 |
| Type | Standard |

Both deployments show **Provisioning state: Succeeded** when ready.

---

## Step 4 — Create Azure AI Search Resource

1. Go to [portal.azure.com](https://portal.azure.com)
2. Navigate to **Microsoft Foundry** → left sidebar → **AI Search**
3. Click **+ Create**
4. Fill in the form:

   | Field | Value used |
   |---|---|
   | Subscription | Azure subscription 1 |
   | Resource group | `study-assistant-rg` |
   | Service name | `study-assistant-search` |
   | Location | `Central US` |
   | Pricing tier | Standard |

5. Click **Review + Create** → **Create**

### Get Azure AI Search Credentials

1. Open the created resource → **Overview** page → copy the **Url** field → `AZURE_SEARCH_ENDPOINT`
2. Left sidebar → **Search management** → **Keys**
3. Copy **Primary admin key** → `AZURE_SEARCH_API_KEY`

> **Important:** Use the **Admin key**, not the Query key — the app needs write access to create indexes automatically.

**Actual resource endpoint used:**
```
https://study-assistant-search.search.windows.net
```

---

## Step 5 — Configure Environment Variables

Create a `.env` file in the project root. The file is gitignored and will not be committed.

```env
# ── Azure OpenAI ──────────────────────────────────────────────────────────────
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-azure-openai-key>
AZURE_OPENAI_API_VERSION=2024-02-01

# Deployment names (must match exactly what you created in Step 3)
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# ── Azure AI Search ───────────────────────────────────────────────────────────
AZURE_SEARCH_ENDPOINT=https://<your-search-name>.search.windows.net
AZURE_SEARCH_API_KEY=<your-search-admin-key>

# Index names (auto-created on first run — no action needed)
AZURE_SEARCH_STUDY_INDEX=study-materials
AZURE_SEARCH_CODE_INDEX=code-documentation

# ── RAG Tuning (optional) ─────────────────────────────────────────────────────
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
```

> **Note:** The `.env` file is blocked from being read/edited by IDE tools (it is gitignored).
> To update it programmatically, use PowerShell:
> ```powershell
> (Get-Content ".env") -replace 'KEY=.*', 'KEY=new-value' | Set-Content ".env" -Encoding UTF8
> ```

### Credentials Reference Table

| Variable | Where to find it |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource → Keys and Endpoint → Endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI resource → Keys and Endpoint → KEY 1 |
| `AZURE_OPENAI_API_VERSION` | Keep as `2024-02-01` (no change needed) |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Deployment name given to gpt-4o in Step 3 |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Deployment name given to embedding model in Step 3 |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search → Overview → Url |
| `AZURE_SEARCH_API_KEY` | Azure AI Search → Search management → Keys → Primary admin key |

---

## Step 6 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Packages installed (56 total)** including: `gradio`, `openai`, `azure-search-documents`, `pypdf`, `langchain`, `uvicorn`, `httpx`, `pandas`, `tqdm`, and others.

> **PATH Warning:** On Windows, pip may show warnings like:
> ```
> WARNING: The script gradio.exe is installed in '...\Scripts' which is not on PATH.
> ```
> This is non-critical — `python app.py` will still work. To suppress: add the Scripts folder to your system PATH.

---

## Step 7 — Run the Application

```bash
python app.py
```

Open your browser and go to: **http://localhost:7860**

---

## Application Usage

### Tab 1 — Study Assistant
1. Click **"Upload Study Materials"** → upload PDF, TXT, or MD files
2. Click **"Index Materials"** to process and store them in Azure AI Search
3. Type a question in the chat box → get AI answers grounded in your documents
4. Use **"Generate Quiz"** to create 5 MCQs on any topic
5. Use **"Summarize Topic"** to get a bullet-point summary

### Tab 2 — Code Documentation Search
1. Upload source code files (`.py`, `.js`, `.ts`, `.java`, `.cs`, `.go`, etc.)
2. Click **"Index Code"** to process and store them
3. Ask natural language questions like *"How does authentication work?"*
4. Responses include filename citations and code snippets

---

## CI/CD — Automated Infrastructure Pipeline

Automate provisioning and teardown of all Azure resources using **Terraform + GitHub Actions**.

### Files Created

```
terraform/
├── main.tf          # All Azure resources (Resource Group, OpenAI, Search)
├── variables.tf     # Configurable values with defaults
└── outputs.tf       # Exports endpoint URLs and API keys

.github/workflows/
├── provision.yml    # Triggered on push to main or manually → terraform apply
└── destroy.yml      # Manual trigger only → terraform destroy
```

### Step 1 — Create a Service Principal

Run this in Azure CLI to create credentials for the pipeline:

```bash
az ad sp create-for-rbac \
  --name "study-assistant-pipeline" \
  --role Contributor \
  --scopes /subscriptions/<your-subscription-id> \
  --sdk-auth
```

Copy the JSON output — it contains `clientId`, `clientSecret`, `tenantId`, `subscriptionId`.

### Step 2 — Add GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret name | Value |
|---|---|
| `AZURE_CLIENT_ID` | `clientId` from service principal JSON |
| `AZURE_CLIENT_SECRET` | `clientSecret` from service principal JSON |
| `AZURE_TENANT_ID` | `tenantId` from service principal JSON |
| `AZURE_SUBSCRIPTION_ID` | `subscriptionId` from service principal JSON |

### Step 3 — Run the Provision Pipeline

**Option A — Auto trigger:** Push any change to `terraform/` folder → pipeline runs automatically.

**Option B — Manual trigger:**
- GitHub repo → **Actions** tab → **Provision Azure Infrastructure** → **Run workflow**

### What the Pipeline Creates

| Resource | Name | Tier |
|---|---|---|
| Resource Group | `study-assistant-rg` | — |
| Azure OpenAI | `study-assistant-openai` | Standard S0 |
| gpt-4o deployment | `gpt-4o` | Standard, 10K TPM |
| text-embedding-ada-002 | `text-embedding-ada-002` | Standard, 10K TPM |
| Azure AI Search | `study-assistant-search` | Free (default) |

### Step 4 — Get Credentials After Pipeline Runs

After `terraform apply` completes, retrieve outputs:

```bash
cd terraform
terraform output openai_endpoint
terraform output -raw openai_api_key
terraform output search_endpoint
terraform output -raw search_api_key
```

Update your `.env` with these values (see Step 5 above).

### Destroy All Resources

**Manual trigger only** (requires typing `destroy` as confirmation):
- GitHub repo → **Actions** → **Destroy Azure Infrastructure** → **Run workflow**
- Input: type `destroy` → **Run workflow**

> ⚠️ This permanently deletes all Azure resources. Data in search indexes will be lost.

### Customize Variables

Edit `terraform/variables.tf` to change resource names, region, or search tier:

```hcl
variable "search_sku" {
  default = "free"    # Change to "basic" or "standard" as needed
}

variable "location" {
  default = "East US" # Change region here
}
```

---

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| `AuthenticationError` | Wrong API key | Double-check `AZURE_OPENAI_API_KEY` in `.env` |
| `ResourceNotFound` | Wrong deployment name | Verify deployment names in Azure OpenAI Studio match `.env` |
| `ServiceUnavailable` | Region capacity issue | Try a different region when creating the resource |
| `No results found` | Index is empty | Upload and index documents first before querying |
| Search index errors | Wrong search key | Ensure you're using the **Admin key**, not the Query key |

---

## Architecture Overview

```
User Uploads Files (PDF / Code / Markdown)
        │
        ▼
  Text Chunking (indexing/processor.py)
  CHUNK_SIZE=1000, CHUNK_OVERLAP=200
        │
        ▼
  Embedding Generation ──────────────► Azure OpenAI
  (text-embedding-ada-002)             text-embedding-ada-002 deployment
        │
        ▼
  Vector + Keyword Index ────────────► Azure AI Search
  (Hybrid search)                      study-materials / code-documentation
        │
   User Query
        │
        ▼
  Query Embedding ──► Top-K Retrieval (TOP_K=5)
                              │
                              ▼
                       Azure OpenAI GPT-4o
                              │
                              ▼
                      AI-Powered Response
```

---

## Project Structure

```
study-assistant/
├── app.py                  # Gradio UI + event handlers
├── config.py               # Environment variable loading
├── requirements.txt        # Python dependencies
├── .env                    # Your credentials (gitignored)
├── SETUP_GUIDE.md          # This file
├── README.md               # Project overview
├── indexing/
│   └── processor.py        # PDF/code loading + text chunking
├── search/
│   └── azure_search.py     # Azure AI Search index creation + hybrid search
└── llm/
    └── azure_openai.py     # Embeddings + RAG prompts + quiz/summary generation
```
