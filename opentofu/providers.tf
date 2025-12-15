terraform {
  required_version = ">= 0.12"

  required_providers {
    kubernetes = {
        source  = "hashicorp/kubernetes"
    }
    helm = {
        source = "hashicorp/helm"
    }
  }
}
provider kubernetes {
    config_path = "~/.kube/config"
    config_context = "first-pet"
}

provider helm {
    kubernetes {
        config_path = "~/.kube/config"
        config_context = "first-pet"
    }
  }