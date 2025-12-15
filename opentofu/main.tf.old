terraform {
  required_providers {
    k8s = {
      version = ">= 0.9.1"
      source  = "hashicorp/kubernetes"
    }
  }
}

provider "k8s" {
  host = "https://192.168.67.2:8443"
  config_path = "/home/nakedredd/.kube/config"
} 

resource "kubernetes_pod_v1" "nginx" {
  metadata {
    name = "nginx"
  }
  spec {
    container {
       name = "nginx"
       image = "nginx:1.14.2"
       port {
         container_port = 80
       }
    }
  }
}