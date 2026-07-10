# Product Boundary

## Product Role

This repository is the Stage 1 synthetic proving ground for the evidence-bundle
contract. It owns:

- definition of the `source -> item -> chunk` bundle structure
- deterministic validation of schemas, content, references, provenance,
  sensitivity metadata, and checksums
- validation that synthetic evidence remains inside the public-safe boundary
- boundary-preserving checks that reject malformed, inconsistent, or unsafe
  bundles

Its primary question is whether synthetic evidence can be packaged as a
self-consistent, public-safe bundle that satisfies a deterministic contract and
is suitable for downstream analytical consumption.

## Core Invariant

Only synthetic, public-safe evidence that satisfies the declared bundle
structure, provenance, reference, content-integrity, sensitivity, and checksum
rules may be treated as a valid Stage 1 bundle; generated findings and reports
remain outside the evidence contract.

In practice, a bundle is not valid merely because its files parse. Its declared
records and counts must agree, references must resolve, content spans and hashes
must be self-consistent, provenance and sensitivity metadata must be present,
checksums must match, and the content must pass the repository's public-safety
checks.

## Product Object

The primary durable product object is the **contract-conforming evidence
bundle**. The schemas, synthetic generator, examples, and validator exist to
define and prove that object.

Findings, reports, and synthesis consume evidence downstream. They are not
evidence records and are not part of the current product contract. The local
synthesis stub exercises that boundary; it does not make analytical inference
part of Stage 1.

## Repository Boundaries

- **Acquisition belongs elsewhere.** Source records preserve acquisition
  provenance, but Stage 1 creates only deterministic synthetic inputs and does
  not connect to real source systems.
- **Retained knowledge belongs elsewhere.** The contract records sensitivity
  and retention metadata, but this repository does not operate a persistent
  knowledge base or approve retention of real data.
- **Publishing belongs elsewhere.** This repository defines public-safety
  checks for its synthetic bundle. It does not publish findings, reports, or
  real-data artifacts.
- **Production infrastructure belongs elsewhere.** Stage 1 does not provision
  LKE, storage, networks, model serving, retrieval, or serving systems.
- **Production analytical inference belongs elsewhere.** Findings, production
  synthesis, model-backed inference, and conclusions are downstream of the
  evidence contract.

These boundaries keep the repository focused on proving that evidence is
packaged consistently and remains inside its declared trust boundary before a
downstream system consumes it.

## Trust Philosophy

Trust in Stage 1 means that the bundle has inspectable provenance, structural
integrity, referential integrity, deterministic validation, and public-safety
boundaries. It does not mean that the evidence is true, that a conclusion is
correct, that an analysis is valid, or that retention has been approved.

## Product Decision Filter

For a proposed change, ask:

- Does it strengthen the evidence-bundle contract?
- Does it improve deterministic validation?
- Does it improve boundary-preserving trust?
- Does it strengthen validation of public-safe evidence?
- Does it begin performing analytical inference?
- Does it begin retaining knowledge?
- Does it begin acquiring knowledge from real systems?
- Does it begin owning production infrastructure?

The first four questions identify work that may belong here. A yes to any of
the last four indicates that the proposal crosses the current Stage 1 product
boundary.

## Non-Goals

Stage 1 does not own:

- truth verification or correctness of conclusions
- analytical findings or analytical validity
- production synthesis or model-backed inference
- retained knowledge or retention approval
- acquisition from real systems
- publication of findings, reports, or real-data artifacts
- production serving or retrieval
- general LKE platform ownership
- real-data processing
