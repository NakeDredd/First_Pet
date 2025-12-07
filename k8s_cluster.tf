terraform {
  required_providers {
    k8s = {
      version = ">= 0.8.0"
      source  = "banzaicloud/k8s"
    }
  }
}

provider "k8s" {
  config_context = "prod-cluster"
}
