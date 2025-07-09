# Grafana Helm Chart

This Helm chart deploys Grafana with optional Azure Key Vault integration for secure credential management.

## Features

- Grafana deployment with persistent storage
- Istio Gateway and VirtualService configuration
- TLS/SSL support with cert-manager
- Azure Key Vault integration for secure credential storage
- Pre-configured Prometheus datasource
- Dashboard provisioning for Kubernetes and Prometheus metrics

## Azure Key Vault Integration

This chart supports Azure Key Vault integration to securely store the Grafana admin password. The admin username is configured directly in the Helm values as it's not sensitive information.

### Prerequisites

1. **Azure Key Vault with Workload Identity**: Ensure you have:
   - An Azure Key Vault with the secret `grafana-admin-password`
   - A User Assigned Identity with Key Vault Secrets User permissions
   - A Federated Identity Credential linking the identity to the Grafana service account
   - AKS cluster with workload identity enabled

### Configuration

To enable Key Vault integration, update your values.yaml:

```yaml
keyVault:
  enabled: true
  name: "your-keyvault-name"
  tenantId: "your-azure-tenant-id"
  userAssignedClientID: "your-workload-identity-client-id"  
  secrets:
    adminPassword: "grafana-admin-password"  # Only password is stored in Key Vault

# Set admin username directly (not sensitive)
grafana:
  adminUser: "admin"  # Set your desired username here
  adminPassword: ""   # Will be overridden by Key Vault secret
```

### Security Benefits

- **No hardcoded credentials**: Admin credentials are stored securely in Azure Key Vault
- **Automatic rotation**: Credentials can be rotated in Key Vault without redeploying
- **Audit trail**: All secret access is logged in Azure Key Vault
- **RBAC**: Fine-grained access control through Azure RBAC and Key Vault policies

## Installation

```bash
# Install with hardcoded credentials (development only)
helm install grafana ./charts/grafana

# Install with Azure Key Vault integration (recommended for production)
helm install grafana ./charts/grafana \
  --set keyVault.enabled=true \
  --set keyVault.name=your-keyvault \
  --set keyVault.tenantId=your-tenant-id \
  --set keyVault.userAssignedClientID=your-client-id \
  --set grafana.adminUser=admin
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `keyVault.enabled` | bool | `false` | Enable Azure Key Vault integration |
| `keyVault.name` | string | `""` | Azure Key Vault name |
| `keyVault.tenantId` | string | `""` | Azure tenant ID |
| `keyVault.userAssignedClientID` | string | `""` | Workload Identity client ID |
| `keyVault.secrets.adminPassword` | string | `"grafana-admin-password"` | Key Vault secret name for admin password |
| `grafana.adminUser` | string | `"admin"` | Admin username (configured directly, not in Key Vault) |
| `grafana.adminPassword` | string | `"admin123"` | Default admin password (used when Key Vault is disabled) |
