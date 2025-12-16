#gitlab server and runner
resource "kubernetes_namespace_v1" "gitlab" {
  metadata {
    name = "gitlab"
  }
}
resource "helm_release" "gitlab" {
  depends_on = [ 
    kubernetes_namespace_v1.gitlab,
    # kubernetes_manifest.selfsigned_issuer
    ]

  name = "gitlab"
  repository = "https://charts.gitlab.io/"
  chart = "gitlab"
  namespace = kubernetes_namespace_v1.gitlab.metadata[0].name

  values = [
    file("${path.module}/values/gitlab.yaml")
  ]
  timeout = 600
}