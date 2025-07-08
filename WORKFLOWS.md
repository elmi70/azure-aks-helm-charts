# Helm Charts CI/CD Workflows

This repository contains automated workflows for packaging and deploying Helm charts to Azure Kubernetes Service (AKS) using GitHub Container Registry (GHCR).

## Overview

The CI/CD setup consists of three main workflows:

1. **Package and Push Helm Charts to GHCR** (`package-helm-charts.yaml`) - Packages individual charts and pushes to GHCR
2. **Deploy Helm Chart** (`deploy-helm-chart.yaml`) - Deploys individual charts from GHCR to AKS
3. **Deploy cert-manager** (`deploy-cert-manager.yaml`) - Deploys cert-manager for TLS certificates

All workflows use **manual triggers only** for controlled, predictable operations.

## 🏗️ Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Source Code   │    │       GHCR       │    │   AKS Cluster   │
│                 │    │                  │    │                 │
│  charts/        │───▶│  Helm Charts     │───▶│  Running Apps   │
│  ├── grafana/   │    │  (OCI Format)    │    │  ├── Grafana    │
│  ├── prometheus/│    │                  │    │  ├── Prometheus │
│  └── kube-st... │    │                  │    │  └── cert-mgr   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

### Required Secrets

Configure these secrets in your GitHub repository (`Settings > Secrets and variables > Actions`):

```bash
# Azure Authentication
AZURE_CLIENT_ID                    # Managed Identity Client ID for GitHub Actions
AZURE_TENANT_ID                    # Azure Tenant ID
AZURE_SUBSCRIPTION_ID              # Azure Subscription ID

# cert-manager specific
AZURE_WORKLOAD_IDENTITY_CLIENT_ID  # Managed Identity for cert-manager DNS challenges
LETSENCRYPT_EMAIL                  # Email for Let's Encrypt certificates
```

### Required Variables

Configure these variables in your GitHub repository (`Settings > Secrets and variables > Actions > Variables`):

```bash
# AKS Configuration
RESOURCE_GROUP                     # Azure Resource Group containing AKS cluster

# DNS Configuration (for cert-manager)
AZURE_DNS_RESOURCE_GROUP          # Resource Group containing DNS Zone
AZURE_DNS_ZONE                    # DNS Zone name (e.g., example.com)
```

### Required Permissions

The managed identity needs:

1. **GitHub Actions Identity** (`AZURE_CLIENT_ID`):
   - `Contributor` role on the AKS cluster
   - `AcrPull` role on any container registries (if using private images)

2. **cert-manager Identity** (`AZURE_WORKLOAD_IDENTITY_CLIENT_ID`):
   - `DNS Zone Contributor` role on the DNS zone
   - Can be the same identity as above for simplicity

## 🚀 Workflows

### 1. Package and Push Helm Charts to GHCR

**File**: `.github/workflows/package-helm-charts.yaml`

**Purpose**: Packages individual Helm charts and pushes them to GitHub Container Registry.

**Triggers**:

- Manual trigger only (select specific chart from dropdown)

**Usage**:

```bash
# Manual trigger via GitHub UI
Go to Actions > Package and Push Helm Charts to GHCR > Run workflow

# Required inputs:
chart_name: grafana|prometheus|kube-state-metrics
```

**Features**:

- ✅ Single chart packaging per run
- ✅ Automatic version detection from Chart.yaml
- ✅ Skips packaging if version already exists in GHCR
- ✅ Chart validation and linting
- ✅ Clean, focused output and summary

### 2. Deploy Helm Chart

**File**: `.github/workflows/deploy-helm-chart.yaml`

**Purpose**: Deploys a single Helm chart from GHCR to AKS with verification.

**Triggers**:

- Manual trigger only (for controlled deployments)

**Usage**:

```bash
# Manual trigger via GitHub UI
Go to Actions > Deploy Helm Chart > Run workflow

# Required inputs:
cluster_name: "your-aks-cluster-name"
chart_name: grafana|prometheus|kube-state-metrics

# Optional inputs:
namespace: "grafana|prometheus|kube-state-metrics|monitoring"
create_namespace: true|false
wait_for_deployment: true|false
```

**Features**:

- ✅ Single chart deployment per run
- ✅ Pre-deployment verification (checks if chart exists in GHCR)
- ✅ Automatic namespace management
- ✅ Deployment health verification
- ✅ Clear success/failure feedback

### 3. Deploy cert-manager

**File**: `.github/workflows/deploy-cert-manager.yaml`

**Purpose**: Deploys cert-manager with Let's Encrypt integration for automatic TLS certificates.

**Usage**:

```bash
# Manual trigger via GitHub UI
Go to Actions > Deploy cert-manager to AKS > Run workflow

# Required inputs:
cluster_name: "your-aks-cluster-name"

# Optional inputs:
cert_manager_version: "v1.18.0"
environment: "production|staging|development"
```

## 📦 Available Charts

| Chart | Description | Default Port |
|-------|-------------|--------------|
| `grafana` | Visualization and monitoring dashboards | 3000 |
| `prometheus` | Metrics collection and storage | 9090 |
| `kube-state-metrics` | Kubernetes cluster metrics | 8080 |

## 🔄 Workflow Examples

### Example 1: Package a Chart

```yaml
# Inputs for Package and Push Helm Charts to GHCR workflow:
chart_name: "grafana"
```

### Example 2: Deploy Chart to Production

```yaml
# Inputs for Deploy Helm Chart workflow:
cluster_name: "my-prod-cluster"
chart_name: "grafana"
namespace: "grafana"
create_namespace: true
wait_for_deployment: true
```

### Example 3: Deploy Chart to Custom Namespace

```yaml
# Inputs for Deploy Helm Chart workflow:
cluster_name: "my-dev-cluster"
chart_name: "prometheus"
namespace: "monitoring"
create_namespace: true
wait_for_deployment: false
```

## 🏥 Accessing Deployed Applications

After successful deployment, use port-forwarding to access applications:

### Grafana

```bash
kubectl port-forward -n <namespace> svc/grafana 3000:80
# Access: http://localhost:3000
```

### Prometheus

```bash
kubectl port-forward -n <namespace> svc/prometheus 9090:9090
# Access: http://localhost:9090
```

## 🔧 Troubleshooting

### Common Issues

1. **kubelogin not found**
   - Fixed automatically by `azure/use-kubelogin@v1` action

2. **Chart not found in GHCR**
   - Package the chart first using the Package workflow
   - Verify the chart was pushed successfully

3. **Authentication failures**
   - Verify Azure secrets and managed identity permissions
   - Check that `RESOURCE_GROUP` variable is set correctly

4. **Deployment timeouts**
   - Check AKS cluster resources
   - Review pod logs: `kubectl logs -n <namespace> <pod-name>`

### Debug Commands

```bash
# Check workflow authentication
az account show

# Verify AKS connection
kubectl get nodes

# Check Helm releases
helm list -A

# View pod status in specific namespace
kubectl get pods -n <namespace>

# Check events
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
```

## 🔒 Security Considerations

1. **Secrets Management**: All sensitive data is stored in GitHub Secrets
2. **Workload Identity**: Uses Azure AD integration for secure authentication
3. **RBAC**: Follows principle of least privilege
4. **Image Security**: Charts are stored in private GHCR repository

## 🚀 Extending the Workflows

### Adding New Charts

1. Create chart directory: `charts/new-chart/`
2. Add `Chart.yaml` and templates
3. Add the new chart to the dropdown options in both workflows
4. Test packaging and deployment

### Customizing Deployment Options

1. Add new input parameters to `deploy-helm-chart.yaml`
2. Add corresponding logic in the deployment steps
3. Update documentation

## 📊 Workflow Status

Monitor workflow status:

- GitHub Actions tab shows all workflow runs
- Each workflow provides detailed summaries
- Failed workflows include debugging information

---

**Note**: These workflows are designed for production use with proper secret management and RBAC. Always test in development environments first.
