#!/bin/bash
# Quick deployment script

cd "$(dirname "$0")"

echo "🚀 Car Part Scraper - Quick Deploy"
echo ""

# Step 1: Build image
echo "Step 1: Building Docker image..."
echo "Run: ./build.sh"
echo ""

# Step 2: Update deployment
echo "Step 2: Update deployment.yaml with new image"
echo "File: ../homelab-gitops/k3s/apps/car-part-scraper/deployment.yaml"
echo "Change: image: nginx:alpine"
echo "To: image: ghcr.io/andydrag/car-part-scraper:latest"
echo ""

# Step 3: Push to git
echo "Step 3: Push changes"
echo "cd ../homelab-gitops"
echo "git add k3s/apps/car-part-scraper/deployment.yaml"
echo "git commit -m 'Deploy real car-part-scraper image'"
echo "git push"
echo ""

# Step 4: Monitor
echo "Step 4: Monitor deployment"
echo "ssh root@proxmox1.drag.rocks"
echo "pct exec 220 -- bash -c 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml && kubectl get pods -n car-scraper -w'"
echo ""

echo "✅ Follow these steps to deploy!"
