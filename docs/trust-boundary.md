# Trust Boundary

This public repository is only for generic tooling, schemas, fake data, and
documentation. It must remain safe to publish.

## Public Repository Boundary

Allowed in this repository:

- generic source code
- JSON Schemas
- synthetic examples
- fake corpus data
- public-safe documentation

Not allowed in this repository:

- employer data
- internal URLs
- real logs
- real tickets
- real incident data
- real service names
- proprietary documentation
- generated summaries derived from real work data
- work-specific overlays, configs, secrets, reports, or outputs

Generated reports from real data are work-derived artifacts. They must stay
inside the approved boundary for that data and must not be committed here.

## MVP Network Boundary

The MVP has no public ingress, no external model calls, and no real adapters.
All commands run locally against fake data.

## Future Operator-Access Constraint

Future LKE deployment work should preserve a private operator model:

- no public app ingress
- workload services internal-only
- initial operator access limited to two approved source IPs:
  - work Mac egress IP
  - work Linux VM egress IP

This is future work only. This repository does not provision LKE, networks,
model serving, storage, or access controls in Stage 1.

