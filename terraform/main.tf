terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "studyassistate2"
    container_name       = "tfstate"
    key                  = "study-assistant.tfstate"
  }
}

provider "azurerm" {
  features {}
}

# ── Resource Group ─────────────────────────────────────────────────────────────

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# ── Azure OpenAI ───────────────────────────────────────────────────────────────

resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_name
  location            = var.openai_location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0"

  depends_on = [azurerm_resource_group.rg]
}

# ── Model Deployments ──────────────────────────────────────────────────────────

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-11-20"
  }

  scale {
    type     = "Standard"
    capacity = 10
  }
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "text-embedding-ada-002"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }

  scale {
    type     = "Standard"
    capacity = 10
  }

  depends_on = [azurerm_cognitive_deployment.gpt4o]
}

# ── Azure AI Search ────────────────────────────────────────────────────────────

resource "azurerm_search_service" "search" {
  name                = var.search_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = var.search_sku
}

# ── App Service ────────────────────────────────────────────────────────────────

resource "azurerm_service_plan" "app_plan" {
  name                = "${var.resource_group_name}-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = var.app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  service_plan_id     = azurerm_service_plan.app_plan.id

  site_config {
    application_stack {
      python_version = "3.12"
    }
    app_command_line = "pip install -r requirements.txt && python app.py"
    always_on       = true
  }

  app_settings = {
    "AZURE_OPENAI_ENDPOINT"             = azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_API_KEY"              = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_OPENAI_API_VERSION"          = "2024-02-01"
    "AZURE_OPENAI_CHAT_DEPLOYMENT"      = "gpt-4o"
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" = "text-embedding-ada-002"
    "AZURE_SEARCH_ENDPOINT"             = "https://${azurerm_search_service.search.name}.search.windows.net"
    "AZURE_SEARCH_API_KEY"              = azurerm_search_service.search.primary_key
    "AZURE_SEARCH_STUDY_INDEX"          = "study-materials"
    "AZURE_SEARCH_CODE_INDEX"           = "code-documentation"
    "CHUNK_SIZE"                        = "1000"
    "CHUNK_OVERLAP"                     = "200"
    "TOP_K"                             = "5"
    "WEBSITES_PORT"                     = "7860"
  }

  depends_on = [
    azurerm_cognitive_deployment.embedding,
    azurerm_search_service.search
  ]
}
