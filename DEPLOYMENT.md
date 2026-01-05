# Deployment Guide

## Prerequisites

1. Docker installed locally
2. GitHub Container Registry (ghcr.io) access
3. kubectl access to K3s cluster

## Step-by-Step Deployment

### 1. Build the Docker Image

```bash
cd /Users/andydrag/Library/CloudStorage/OneDrive-DragCo/Documents/GitRepos/car-part-scraper

# Make build script executable
chmod +x build.sh

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u andydrag --password-stdin

# Build and push (replace 'andydrag' with your GitHub username in build.sh first!)
./build.sh v1.0.0

# This will:
# - Build the Docker image
# - Tag it as ghcr.io/andydrag/car-part-scraper:v1.0.0
# - Tag it as ghcr.io/andydrag/car-part-scraper:latest
# - Push both tags to GitHub Container Registry
```

**Note:** Update `REGISTRY` in `build.sh` to match your GitHub username!

### 2. Update Kubernetes Deployment

```bash
cd ../homelab-gitops/k3s/apps/car-part-scraper

# Edit deployment.yaml
nano deployment.yaml

# Change line 20 from:
        image: nginx:alpine

# To:
        image: ghcr.io/andydrag/car-part-scraper:latest
        # Or use specific version: ghcr.io/andydrag/car-part-scraper:v1.0.0

# Also change line 23 from:
        - containerPort: 80

# To:
        - containerPort: 8000
```

### 3. Update Service

```bash
# Edit service.yaml
nano service.yaml

# Change line 13 from:
    targetPort: 80

# To:
    targetPort: 8000
```

### 4. Commit and Push

```bash
cd ../../../homelab-gitops

git add k3s/apps/car-part-scraper/deployment.yaml
git add k3s/apps/car-part-scraper/service.yaml

git commit -m "Deploy real car-part-scraper FastAPI application

- Switch from nginx placeholder to actual app
- Image: ghcr.io/andydrag/car-part-scraper:latest
- FastAPI web UI with PostgreSQL integration
- REST API for parts search and management"

git push
```

### 5. Force Flux Reconciliation

```bash
# SSH to proxmox1
ssh root@proxmox1.drag.rocks

# Force reconcile
pct exec 220 -- bash -c "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml && /usr/local/bin/flux reconcile kustomization apps --with-source"
```

### 6. Monitor Deployment

```bash
# Watch pod restart
pct exec 220 -- bash -c "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml && kubectl get pods -n car-scraper -w"

# Expected output:
# car-part-scraper-xxxxx   1/1     Terminating   0          5m
# car-part-scraper-yyyyy   0/1     Pending       0          1s
# car-part-scraper-yyyyy   0/1     ContainerCreating   0     2s
# car-part-scraper-yyyyy   1/1     Running             0     30s

# Check logs
pct exec 220 -- bash -c "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml && kubectl logs -f -n car-scraper -l app=car-part-scraper"

# Should see:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Test the Application

```bash
# From browser
open https://4g63.drag.rocks

# Should see the 4G63 Head Finder dashboard!

# Test API
curl https://4g63.drag.rocks/health
# {"status":"healthy","database":"connected"}

curl https://4g63.drag.rocks/api/stats
# {statistics JSON}

# View interactive API docs
open https://4g63.drag.rocks/docs
```

## Troubleshooting

### Image Pull Errors

If you see `ImagePullBackOff`:

```bash
# Check if image exists
docker pull ghcr.io/andydrag/car-part-scraper:latest

# Make sure image is public or add imagePullSecrets to deployment
```

**To make GitHub Container Registry package public:**
1. Go to https://github.com/users/andydrag/packages
2. Find `car-part-scraper` package
3. Click "Package settings"
4. Scroll to "Danger Zone"
5. Click "Change visibility" → "Public"

### Database Connection Issues

```bash
# Check if postgres is running
kubectl get pods -n car-scraper -l app=postgres

# Check postgres logs
kubectl logs -n car-scraper -l app=postgres

# Test connection from app pod
kubectl exec -it -n car-scraper deployment/car-part-scraper -- \
  env | grep DATABASE
```

### Application Crashes

```bash
# Check pod logs
kubectl logs -n car-scraper -l app=car-part-scraper --previous

# Common issues:
# - Missing DATABASE_URL
# - Cannot connect to postgres
# - Python dependencies not installed
```

## Updating the Application

After making code changes:

```bash
cd car-part-scraper

# Build new version
./build.sh v1.0.1

# If using 'latest' tag, force pod restart
kubectl rollout restart deployment/car-part-scraper -n car-scraper

# Or update deployment with new version tag
# Then git commit + push
```

## Quick Reference

**App URL:** https://4g63.drag.rocks  
**API Docs:** https://4g63.drag.rocks/docs  
**Health:** https://4g63.drag.rocks/health  
**Namespace:** car-scraper  
**Database:** postgres.car-scraper.svc.cluster.local:5432  
**AI Service:** ollama.ai.svc.cluster.local:11434
