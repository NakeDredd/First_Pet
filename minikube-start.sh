#!bin/bash

minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=50g \
  --nodes=2 \
  --driver=docker \
  --profile=first-pet \
#для днс доступа
minikube addons enable ingress
#для PVC
minikube addons enable storage-provisioner
#для настройки etc/hosts
minikube ip