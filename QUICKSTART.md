# Quick Start Guide

## 1. Package Your Charts

**Manual packaging only** - controlled and predictable operations:

1. Go to **Actions** → **Package and Push Helm Charts to GHCR**
2. Click **Run workflow**
3. Select a chart from the dropdown: `grafana`, `prometheus`, or `kube-state-metrics`
4. Click **Run workflow**

The workflow will automatically detect the chart version from `Chart.yaml` and skip packaging if that version already exists in GHCR.

## 2. Deploy Charts to AKS

1. Go to **Actions** → **Deploy Helm Chart**
2. Click **Run workflow**
3. Fill in the form:

   ```yaml
   cluster_name: my-aks-cluster
   chart_name: grafana (or prometheus, kube-state-metrics)
   namespace: grafana (or prometheus, kube-state-metrics, monitoring)
   create_namespace: true
   wait_for_deployment: true
   ```

   **Notes**:
   - The workflow verifies the chart exists in GHCR before deployment
   - Chart version is automatically detected from GHCR
   - Charts are deployed with their packaged default values

4. Click **Run workflow**

**Note**: To deploy multiple charts, run the workflow multiple times with different chart selections.

## 3. Access Your Applications

After deployment completes:

```bash
# Access Grafana (if deployed)
kubectl port-forward -n <namespace> svc/grafana 3000:80
# Open: http://localhost:3000

# Access Prometheus (if deployed)
kubectl port-forward -n <namespace> svc/prometheus 9090:9090
# Open: http://localhost:9090

# Access kube-state-metrics (if deployed)
kubectl port-forward -n <namespace> svc/kube-state-metrics 8080:8080
# Open: http://localhost:8080/metrics
```

## 4. Deploy cert-manager (Optional)

1. Go to **Actions** → **Deploy cert-manager to AKS**
2. Click **Run workflow**
3. Enter your cluster name
4. Click **Run workflow**

That's it! Your charts are now running on AKS. 🎉
