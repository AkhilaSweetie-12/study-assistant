output "openai_endpoint" {
  description = "Azure OpenAI endpoint — use as AZURE_OPENAI_ENDPOINT in .env"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_api_key" {
  description = "Azure OpenAI primary key — use as AZURE_OPENAI_API_KEY in .env"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "search_endpoint" {
  description = "Azure AI Search endpoint — use as AZURE_SEARCH_ENDPOINT in .env"
  value       = "https://${azurerm_search_service.search.name}.search.windows.net"
}

output "search_api_key" {
  description = "Azure AI Search primary admin key — use as AZURE_SEARCH_API_KEY in .env"
  value       = azurerm_search_service.search.primary_key
  sensitive   = true
}

output "resource_group_name" {
  description = "Resource group containing all resources"
  value       = azurerm_resource_group.rg.name
}

# output "app_url" {
#   description = "Public URL of the deployed Gradio app"
#   value       = "https://${azurerm_linux_web_app.app.default_hostname}"
# }
#
# output "app_name" {
#   description = "Azure App Service name (used for deployment)"
#   value       = azurerm_linux_web_app.app.name
# }
