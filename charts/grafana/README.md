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

### Terraform Setup (Recommended)

For a complete infrastructure-as-code approach, use the Terraform configuration in the `terraform-example/` directory. This will:

1. Generate a secure random password
2. Store it in your existing Azure Key Vault  
3. Provide outputs for your Helm configuration

See `terraform-example/README.md` for detailed instructions.

### Manual Setup

If you prefer manual setup:

1. **Azure Key Vault**: Create an Azure Key Vault and add the following secret:
   - `grafana-admin-password`: The admin password (username is configured in values.yaml)

2. **RBAC**: Ensure your AKS cluster's kubelet identity has access to the Key Vault:
   ```bash
   # Grant Key Vault access to AKS kubelet identity  
   az keyvault set-policy --name <your-keyvault> \
     --spn <kubelet-identity-client-id> \
     --secret-permissions get
   ```

### Configuration

To enable Key Vault integration, update your values.yaml:

```yaml
keyVault:
  enabled: true
  name: "your-keyvault-name"
  tenantId: "your-azure-tenant-id"
  userAssignedIdentityID: ""  # Leave empty to use kubelet identity
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
  --set grafana.adminUser=admin
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `keyVault.enabled` | bool | `false` | Enable Azure Key Vault integration |
| `keyVault.name` | string | `""` | Azure Key Vault name |
| `keyVault.tenantId` | string | `""` | Azure tenant ID |
| `keyVault.userAssignedIdentityID` | string | `""` | Managed Identity client ID |
| `keyVault.secrets.adminPassword` | string | `"grafana-admin-password"` | Key Vault secret name for admin password |
| `grafana.adminUser` | string | `"admin"` | Admin username (configured directly, not in Key Vault) |
| `grafana.adminPassword` | string | `"admin123"` | Default admin password (used when Key Vault is disabled) |
