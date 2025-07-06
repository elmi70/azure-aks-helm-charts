# Cert-Manager Chart Configuration

This directory contains configuration files for deploying cert-manager to Kubernetes clusters.

## Files

- `cert-manager-values.yaml`: Helm values for cert-manager deployment (custom values file)
- `cluster-issuer.yaml`: Template for Let's Encrypt Production ClusterIssuer configuration
- `cluster-issuer-staging.yaml`: Template for Let's Encrypt Staging ClusterIssuer configuration (for testing)

## Usage

These files are used by the GitHub workflow in `.github/workflows/deploy-cert-manager.yaml` to deploy cert-manager with standardized configurations. The workflow is configured for manual triggering only to ensure all necessary inputs are provided.

### cert-manager-values.yaml

This custom values file configures cert-manager with:

- Prometheus metrics enabled
- Azure Workload Identity integration
- Resource requests and limits for all components
- Proper CRD management

### ClusterIssuer Templates

These template files get populated with environment-specific values during deployment:

### cluster-issuer.yaml

Configures the production Let's Encrypt issuer:

- Let's Encrypt production issuer with rate limits for live environments
- Azure DNS for DNS01 challenge validation
- Azure Workload Identity for authentication

### cluster-issuer-staging.yaml

Configures the staging Let's Encrypt issuer:

- Let's Encrypt staging issuer with higher rate limits for testing
- Uses test certificates that won't be trusted by browsers
- Ideal for testing certificate issuance before using production

## Customization

To customize the deployment for different environments, modify these files rather than the workflow file. This ensures consistent configuration across deployments.

## Testing

To verify that your cert-manager deployment is working correctly, you can create a test certificate:

1. First update the test-certificate.yaml with your domain:
   ```bash
   export AZURE_DNS_ZONE="your-domain.com"
   envsubst < ./test-certificate.yaml > ./test-certificate-rendered.yaml
   ```

2. Apply the test certificate:
   ```bash
   kubectl apply -f ./test-certificate-rendered.yaml
   ```

3. Check the certificate status:
   ```bash
   kubectl describe certificate test-certificate
   ```

4. Once issued, check the created secret:
   ```bash
   kubectl describe secret test-cert-tls
   ```

The certificate should go through these phases:
1. Initial processing
2. DNS01 challenge creation
3. Waiting for DNS propagation
4. Challenge validation
5. Certificate issuance

A sample test certificate configuration is provided in `test-certificate.yaml`.

## Azure Identity Configuration

This deployment uses the same Azure Managed Identity for two purposes:

1. **GitHub Actions Authentication**: Used by the workflow to authenticate to Azure and deploy cert-manager
2. **cert-manager DNS01 Challenge**: Used by cert-manager to create DNS records for certificate validation

The identity requires these permissions:

- Contributor role on the AKS cluster for deploying resources
- DNS Zone Contributor access to the specified Azure DNS zone

For production environments, consider using separate identities to follow the principle of least privilege.

## Troubleshooting

### Common Issues

1. **Certificate Issuance Failures**:
   - Verify the ClusterIssuer status with: `kubectl describe clusterissuer letsencrypt-prod`
   - Check cert-manager logs: `kubectl logs -n cert-manager -l app=cert-manager`
   - Ensure the managed identity has DNS Zone Contributor permissions

2. **Workload Identity Setup**:
   - Verify identity binding with: `kubectl get serviceaccount -n cert-manager cert-manager -o yaml`
   - Check federated identity credentials in Azure portal or with Azure CLI

3. **Rate Limiting**:
   - If hitting Let's Encrypt production rate limits, switch to staging environment
   - Use `kubectl get challenges` to see any failed ACME challenges

4. **DNS Propagation Delays**:
   - Certificate issuance may take time due to DNS propagation
   - You can use the `dns01-recursiveNameservers` option in the ClusterIssuer to speed up validation
