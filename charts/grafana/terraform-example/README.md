# Grafana Azure Key Vault Integration

This directory contains example Terraform configuration for integrating Grafana with Azure Key Vault for secure credential management.

## Overview

Instead of hardcoding Grafana admin credentials in your Helm values, this solution stores them securely in Azure Key Vault and uses the AKS CSI Secret Store driver to mount them as secrets in your pods.

**Important**: Only the admin **password** is stored in Key Vault. The admin **username** is configured directly in Helm values since usernames are not sensitive information.

## Prerequisites

1. **AKS cluster with CSI Secret Store driver enabled** (you already have this)
2. **Azure Key Vault** (you already have this)  
3. **Proper RBAC configuration** (you already have this)

## Setup Steps

### 1. Add Terraform Resources

Copy the contents of `grafana-keyvault.tf` to your existing Terraform configuration where you have your AKS and Key Vault setup.

The Terraform will:
- Generate a secure random password for Grafana admin
- Store only the password in your existing Key Vault (username stays in Helm values)
- Output the necessary values for Helm configuration

### 2. Apply Terraform Changes

```bash
terraform plan
terraform apply
```

### 3. Get Configuration Values

After applying Terraform, get the values needed for Helm:

```bash
# Get Key Vault name
terraform output grafana_key_vault_name

# Get tenant ID
terraform output grafana_tenant_id

# Get workload identity client ID
terraform output grafana_workload_identity_client_id

# Get the generated admin password (one-time retrieval for reference)
terraform output -raw grafana_admin_password
```

### 4. Update Helm Values

Update your `charts/grafana/values.yaml`:

```yaml
# Enable Key Vault integration with workload identity
keyVault:
  enabled: true
  name: "<output from terraform output grafana_key_vault_name>"
  tenantId: "<output from terraform output grafana_tenant_id>"
  userAssignedClientID: "<output from terraform output grafana_workload_identity_client_id>"
  secrets:
    adminPassword: "grafana-admin-password"  # Only password is stored in Key Vault

# Set admin username directly (not sensitive) and clear hardcoded password
grafana:
  adminUser: "admin"  # Set your desired username here
  adminPassword: ""   # Will be overridden by Key Vault secret
```

### 5. Deploy Grafana

```bash
helm upgrade --install grafana ./charts/grafana \
  --namespace monitoring \
  --create-namespace \
  --values ./charts/grafana/values.yaml
```

## How It Works

1. **SecretProviderClass**: Created by the Helm chart to define which secrets to fetch from Key Vault
2. **Pod Volume**: The CSI driver mounts secrets as files in `/mnt/secrets-store/`
3. **Environment Variables**: The deployment reads the secret files and sets them as environment variables
4. **Grafana**: Uses the environment variables for admin credentials

## Security Benefits

- ✅ No hardcoded credentials in Git
- ✅ Centralized secret management in Azure Key Vault
- ✅ Automatic secret rotation support (when enabled)
- ✅ Audit trail of secret access
- ✅ RBAC-controlled access to secrets

## Troubleshooting

### Check if secrets are mounted

```bash
kubectl exec -n monitoring deployment/grafana -- ls -la /mnt/secrets-store/
```

### Check SecretProviderClass

```bash
kubectl get secretproviderclass -n monitoring
kubectl describe secretproviderclass grafana-secrets -n monitoring
```

### Check CSI driver logs

```bash
kubectl logs -n kube-system -l app=secrets-store-csi-driver
```

### Verify Key Vault access

```bash
# Check if the kubelet identity has access to Key Vault
az keyvault secret show --vault-name "<your-keyvault>" --name "grafana-admin-password"
```
