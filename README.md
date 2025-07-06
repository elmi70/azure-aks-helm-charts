# Azure AKS Helm Charts

Automated deployment of official Helm charts to Azure Kubernetes Service (AKS) using GitHub Actions.

## Overview

This repository contains GitHub Actions workflows and configuration files for deploying and managing common infrastructure components on Azure Kubernetes Service using Helm charts. It serves as a centralized location for AKS infrastructure management, ensuring consistent deployment patterns and security practices across all your clusters.

Each chart deployment is configured with:

- Secure authentication using Azure Workload Identity
- Standardized deployment patterns
- Environment-specific configurations
- Clear documentation and usage examples

## Included Charts

Currently, this repository includes the following infrastructure components:

- **cert-manager**: Automates certificate management with Let's Encrypt integration and Azure DNS for DNS01 challenges

*More charts will be added in the future.*

## Repository Structure

```plaintext
/
├── .github/workflows/    # GitHub Actions workflows
│   └── deploy-cert-manager.yaml
│
└── charts/               # Helm chart configurations 
    └── cert-manager/     # cert-manager specific configurations
        ├── cert-manager-values.yaml
        ├── cluster-issuer.yaml
        ├── cluster-issuer-staging.yaml
        ├── test-certificate.yaml
        └── README.md
```

## Azure Identity Configuration

This repository uses Azure Managed Identity for secure authentication:

1. **GitHub Actions Workflow Authentication**: Uses the identity to authenticate to Azure for deploying applications
2. **Application-Specific Authentication**: The same identity is used by applications (e.g., cert-manager) for Azure resource access

For production environments, consider using separate identities for workflow authentication and application-specific authentication.

## Usage

All deployment workflows in this repository follow a similar pattern:

1. Workflows are triggered manually to ensure required inputs are provided
2. Each workflow is specific to a chart and targets a single AKS cluster
3. Configuration is maintained in the `charts/[chart-name]` directory
4. Workflows use Azure Workload Identity for secure authentication

### General Deployment Steps

To deploy any chart:

1. Go to the Actions tab in the GitHub repository
2. Select the desired workflow
3. Click "Run workflow"
4. Enter the required parameters
5. Click "Run workflow" to start the deployment

### Available Charts

#### cert-manager

**Purpose:** Automated TLS certificate management with Let's Encrypt integration

**Required Inputs:**

- AKS cluster name
- cert-manager version (optional, defaults to latest stable)
- Environment: production or staging (optional, determines which ClusterIssuer to use)

**Features:**

- Configurable Let's Encrypt production/staging environments
- Azure DNS integration for DNS-01 challenges
- Azure Workload Identity for secure DNS management

For detailed information on each chart, see the respective README files in the chart directories.
