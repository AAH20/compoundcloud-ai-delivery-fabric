terraform {
  required_version = ">= 1.6.0"
}

locals {
  architecture_decision = {
    candidate_id          = "azure-premium-low-latency"
    cloud                 = "azure"
    region                = "eastus2"
    compute               = "AKS multi-zone"
    network_topology      = "private-hub-spoke-frontdoor"
    estimated_monthly_usd = 43707.99
    estimated_margin      = 0.8786
  }
}

output "architecture_decision" {
  value = local.architecture_decision
}
