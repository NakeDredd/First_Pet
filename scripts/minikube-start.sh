#!/bin/bash

minikube stop --profile=first-pet 2>/dev/null

echo "Starting Minikube with 2 nodes..."
minikube start \
  --cpus=4 \
  --memory=6144 \
  --disk-size=30g \
  --nodes=2 \
  --driver=docker \
  --profile=first-pet \
  --addons=ingress,csi-hostpath-driver,metrics-server

echo "Checking Minikube status..."
minikube status --profile=first-pet

echo "Setting csi-hostpath-sci as default storage class..."
kubectl patch storageclass csi-hostpath-sc -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

MINIKUBE_IP=$(minikube ip --profile=first-pet)
echo "Minikube IP: $MINIKUBE_IP"

echo "Add these lines to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows):"
echo "$MINIKUBE_IP gitlab.local"
echo "$MINIKUBE_IP registry.gitlab.local"
echo "$MINIKUBE_IP grafana.local"
echo "$MINIKUBE_IP prometheus.local"