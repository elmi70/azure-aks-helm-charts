# Azure AKS Helm Charts

Automated packaging and deployment of Helm charts to Azure Kubernetes Service (AKS) using GitHub Actions and GitHub Container Registry (GHCR).

## Overview

This repository contains GitHub Actions workflows and Helm charts for deploying and managing monitoring and infrastructure components on Azure Kubernetes Service. It provides:

- **Manual-only workflows** for controlled operations
- **Single-chart operations** for simplicity and predictability
- **GHCR integration** for chart storage and distribution
- **Pre-deployment verification** to ensure charts exist before deployment

Each chart deployment includes:

- Secure authentication using Azure Workload Identity
- Automatic namespace management
- Health verification and status reporting
- Clear success/failure feedback

## Included Charts

This repository includes the following components:

- **grafana**: Visualization and monitoring dashboards (Port: 3000)
- **prometheus**: Metrics collection and storage (Port: 9090)
- **kube-state-metrics**: Kubernetes cluster metrics (Port: 8080)
- **cert-manager**: Automated certificate management with Let's Encrypt integration

## Repository Structure

```plaintext
/
├── .github/workflows/           # GitHub Actions workflows
│   ├── package-helm-charts.yaml    # Package charts to GHCR
│   ├── deploy-helm-chart.yaml      # Deploy charts from GHCR
│   └── deploy-cert-manager.yaml    # Deploy cert-manager
│
└── charts/                      # Helm charts
    ├── grafana/                 # Grafana chart and dashboards
    ├── prometheus/              # Prometheus chart and config
    ├── kube-state-metrics/      # kube-state-metrics chart
    └── cert-manager/            # cert-manager configurations
```

## Azure Identity Configuration

This repository uses Azure Managed Identity for secure authentication:

1. **GitHub Actions Workflow Authentication**: Uses the identity to authenticate to Azure for deploying applications
2. **Application-Specific Authentication**: The same identity is used by applications (e.g., cert-manager) for Azure resource access

For production environments, consider using separate identities for workflow authentication and application-specific authentication.

## Usage

This repository provides three main workflows:

1. **Package and Push Helm Charts to GHCR** - Packages individual charts and pushes to GitHub Container Registry
2. **Deploy Helm Chart** - Deploys individual charts from GHCR to AKS
3. **Deploy cert-manager** - Deploys cert-manager with Let's Encrypt integration

All workflows use **manual triggers only** for controlled, predictable operations.

### Quick Start

1. **Package a chart**: Go to Actions → "Package and Push Helm Charts to GHCR" → Select chart → Run
2. **Deploy a chart**: Go to Actions → "Deploy Helm Chart" → Enter cluster name and chart → Run

### Workflow Features

- ✅ **Single-chart operations**: One chart per workflow run
- ✅ **Pre-deployment verification**: Checks if chart exists in GHCR
- ✅ **Automatic version detection**: Uses version from Chart.yaml
- ✅ **Namespace management**: Creates namespaces if needed
- ✅ **Health verification**: Waits for deployment completion

### Available Workflows

#### Package and Push Helm Charts to GHCR

**Purpose:** Packages individual Helm charts and pushes to GitHub Container Registry

**Inputs:**

- Chart name (dropdown): grafana, prometheus, kube-state-metrics

#### Deploy Helm Chart

**Purpose:** Deploys a single chart from GHCR to AKS with verification

**Inputs:**

- AKS cluster name (required)
- Chart name (dropdown): grafana, prometheus, kube-state-metrics
- Namespace (optional): grafana, prometheus, kube-state-metrics, monitoring
- Create namespace (optional): true/false
- Wait for deployment (optional): true/false

#### Deploy cert-manager

**Purpose:** Deploys cert-manager with Let's Encrypt integration

**Inputs:**

- AKS cluster name (required)
- cert-manager version (optional)
- Environment (optional): production/staging

For detailed documentation, see [WORKFLOWS.md](./WORKFLOWS.md) and [QUICKSTART.md](./QUICKSTART.md).
