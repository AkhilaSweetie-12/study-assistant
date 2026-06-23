variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "study-assistant-rg"
}

variable "location" {
  description = "Azure region for most resources"
  type        = string
  default     = "East US"
}

variable "openai_name" {
  description = "Name of the Azure OpenAI resource"
  type        = string
  default     = "study-assistant-openai"
}

variable "openai_location" {
  description = "Azure region for OpenAI (gpt-4o availability varies by region)"
  type        = string
  default     = "East US"
}

variable "search_name" {
  description = "Name of the Azure AI Search resource (must be globally unique)"
  type        = string
  default     = "study-assistant-search"
}

variable "search_sku" {
  description = "Azure AI Search pricing tier: free, basic, standard"
  type        = string
  default     = "free"

  validation {
    condition     = contains(["free", "basic", "standard", "standard2", "standard3"], var.search_sku)
    error_message = "search_sku must be one of: free, basic, standard, standard2, standard3"
  }
}
