resource "kubernetes_namespace_v1" "cert_manager" {
  metadata {
    name = "cert-manager"
  }
}

resource "helm_release" "cert_manager" {
  depends_on = [kubernetes_namespace_v1.cert_manager]
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  namespace  = kubernetes_namespace_v1.cert_manager.metadata[0].name

  values = [
    file("${path.module}/values/cert-manager.yaml")
  ]
}

resource "time_sleep" "wait_for_crds" {
  depends_on = [helm_release.cert_manager]

  create_duration = "30s" # waiting for CRD to create
}

resource "kubernetes_manifest" "selfsigned_issuer" {
  depends_on = [time_sleep.wait_for_crds]

  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "ClusterIssuer"
    metadata = {
      name = "selfsigned-issuer"
    }
    spec = {
      selfSigned = {}
    }
  }
}