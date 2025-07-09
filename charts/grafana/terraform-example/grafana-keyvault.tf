# grafana-keyvault.tf
# Add this to your existing Terraform configuration where you have the Key Vault setup

# Generate secure password for Grafana admin
resource "random_password" "grafana_admin_password" {
  length  = 16
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Store only the Grafana admin password in Key Vault (username is not sensitive)
resource "azurerm_key_vault_secret" "grafana_admin_password" {
  name         = "grafana-admin-password"
  value        = random_password.grafana_admin_password.result
  key_vault_id = azurerm_key_vault.aks_kv.id
  
  # Use your existing tags variable, or remove this line if not using tags
  # tags = var.tags
  
  depends_on = [
    azurerm_role_assignment.grafana_kv_secrets_user
  ]
}

# Create User Assigned Identity for Grafana workload identity
resource "azurerm_user_assigned_identity" "grafana_workload_identity" {
  name                = "grafana-workload-identity"  # Or use your naming convention
  location            = azurerm_resource_group.aks.location
  resource_group_name = azurerm_resource_group.aks.name
  
  # Use your existing tags variable, or remove this line if not using tags
  # tags = var.tags
}

# Grant Key Vault access to the workload identity
resource "azurerm_role_assignment" "grafana_kv_secrets_user" {
  scope                = azurerm_key_vault.aks_kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.grafana_workload_identity.principal_id
}

# Federate the workload identity with the AKS cluster
resource "azurerm_federated_identity_credential" "grafana_workload_identity" {
  name                = "grafana-federated-identity"
  resource_group_name = azurerm_resource_group.aks.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = azurerm_kubernetes_cluster.aks.oidc_issuer_url
  parent_id           = azurerm_user_assigned_identity.grafana_workload_identity.id
  subject             = "system:serviceaccount:default:grafana"  # Update namespace if different
}

# Optional: Add variable for configurable admin username
variable "grafana_admin_user" {
  description = "Grafana admin username"
  type        = string
  default     = "admin"
}

# Output the Key Vault name for Helm configuration
output "grafana_key_vault_name" {
  description = "Key Vault name for Grafana Helm configuration"
  value       = azurerm_key_vault.aks_kv.name
}

# Output tenant ID for Helm configuration
output "grafana_tenant_id" {
  description = "Azure tenant ID for Grafana Key Vault access"
  value       = data.azurerm_client_config.current.tenant_id
}

# Output the workload identity client ID for Helm configuration
output "grafana_workload_identity_client_id" {
  description = "Workload Identity Client ID for Grafana Key Vault access"
  value       = azurerm_user_assigned_identity.grafana_workload_identity.client_id
}

# Output the generated password (sensitive) - for initial setup reference only
output "grafana_admin_password" {
  description = "Generated Grafana admin password (retrieve once for reference)"
  value       = random_password.grafana_admin_password.result
  sensitive   = true
}

# Output the secret names for Helm configuration
output "grafana_keyvault_secret_names" {
  description = "Key Vault secret names for Grafana configuration"
  value = {
    admin_password = azurerm_key_vault_secret.grafana_admin_password.name
  }
}
