from .models import ArchitectureCandidate


def default_catalog() -> list[ArchitectureCandidate]:
    """Transparent reference assumptions; replace with live price adapters in production."""
    return [
        ArchitectureCandidate(
            id="azure-serverless-balanced", cloud="azure", region="eastus2",
            compute="Azure Container Apps", model="Azure OpenAI balanced model",
            model_class="managed", topology="private-hub-spoke",
            retrieval="Azure AI Search", unit_input_per_million=0.55,
            unit_output_per_million=2.20, fixed_monthly_cost=540,
            variable_platform_cost_per_request=0.00035, expected_quality=0.92,
            expected_p95_ms=1450, expected_availability=0.9995,
            max_sustained_rps=85, egress_cost_per_gb=0.087,
        ),
        ArchitectureCandidate(
            id="azure-premium-low-latency", cloud="azure", region="eastus2",
            compute="AKS multi-zone", model="Azure OpenAI premium model",
            model_class="managed", topology="private-hub-spoke-frontdoor",
            retrieval="Azure AI Search premium", unit_input_per_million=2.50,
            unit_output_per_million=10.0, fixed_monthly_cost=2650,
            variable_platform_cost_per_request=0.00065, expected_quality=0.97,
            expected_p95_ms=720, expected_availability=0.9999,
            max_sustained_rps=420, egress_cost_per_gb=0.087,
        ),
        ArchitectureCandidate(
            id="aws-serverless-throughput", cloud="aws", region="us-east-1",
            compute="ECS Fargate", model="Bedrock balanced model",
            model_class="managed", topology="transit-gateway-private-link",
            retrieval="OpenSearch Serverless", unit_input_per_million=0.60,
            unit_output_per_million=2.40, fixed_monthly_cost=610,
            variable_platform_cost_per_request=0.00032, expected_quality=0.91,
            expected_p95_ms=1380, expected_availability=0.9995,
            max_sustained_rps=95, egress_cost_per_gb=0.09,
        ),
        ArchitectureCandidate(
            id="gcp-global-balanced", cloud="gcp", region="us-central1",
            compute="Cloud Run", model="Vertex AI balanced model",
            model_class="managed", topology="global-load-balancer-private-service-connect",
            retrieval="Vertex AI Search", unit_input_per_million=0.50,
            unit_output_per_million=2.00, fixed_monthly_cost=585,
            variable_platform_cost_per_request=0.00030, expected_quality=0.91,
            expected_p95_ms=1320, expected_availability=0.9995,
            max_sustained_rps=105, egress_cost_per_gb=0.085,
        ),
        ArchitectureCandidate(
            id="onprem-gpu-sovereign", cloud="on-premises", region="customer-datacenter",
            compute="Kubernetes + 2x L40S", model="self-hosted open-weight 70B",
            model_class="self-hosted", topology="dual-edge-bgp-service-mesh",
            retrieval="Qdrant HA", unit_input_per_million=0,
            unit_output_per_million=0, fixed_monthly_cost=7900,
            variable_platform_cost_per_request=0.00018, expected_quality=0.90,
            expected_p95_ms=980, expected_availability=0.999,
            max_sustained_rps=55, egress_cost_per_gb=0.01,
        ),
    ]

