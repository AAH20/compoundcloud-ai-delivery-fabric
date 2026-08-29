# Architecture

```mermaid
flowchart LR
    A[Business workload contract] --> B[Architecture compiler]
    P[Versioned provider pricing] --> B
    T[Measured benchmark profiles] --> B
    B --> C1[Azure candidate]
    B --> C2[AWS candidate]
    B --> C3[GCP candidate]
    B --> C4[On-prem GPU candidate]
    C1 & C2 & C3 & C4 --> E[SLO and capacity gates]
    E --> U[Unit economics engine]
    U --> D[Signed architecture decision]
    D --> I[IaC and deployment plan]
    I --> R[Ephemeral benchmark environment]
    R --> M[Measured quality, latency, reliability, cost]
    M --> T
    I --> O[Production observability]
    O --> T
    I --> C[Derived control evidence]
```

## Control loop

The compiler does not claim that a spreadsheet estimate proves production fitness. It produces a versioned hypothesis. An ephemeral environment tests representative traffic; measured results update benchmark profiles; the compiler re-ranks candidates; a promotion decision records the exact inputs and evidence.

## Networking is a first-class decision variable

Each candidate describes a topology rather than treating networking as plumbing. The production implementation will model private endpoints, ingress and egress paths, DNS, cross-zone traffic, hybrid routing, service-to-service encryption, failure domains, and the latency/cost consequences of each choice.

## IaC to compliance-as-code

Infrastructure is the source of truth. Policy checks and evidence are generated from the compiled topology and deployed state. They cannot silently substitute for performance, reliability, or business outcomes.

