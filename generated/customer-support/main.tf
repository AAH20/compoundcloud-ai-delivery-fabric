terraform {
  required_version = ">= 1.6.0"
}

locals {
  architecture_decision = {
    candidate_id          = "gcp-global-balanced"
    cloud                 = "gcp"
    region                = "us-central1"
    compute               = "Cloud Run"
    network_topology      = "global-load-balancer-private-service-connect"
    estimated_monthly_usd = 28448.35
    estimated_margin      = 0.8682
  }
}

output "architecture_decision" {
  value = local.architecture_decision
}
