# Personal Quantum Computer

**Status:** proposed
**Part of:** [7 — The City of Light](../../SPEC.md)
**Node type:** `personal_quantum_computer`
**Implementation repo:** none yet — see `creation.md` convention

## Purpose

The first *compute* node spec (as distinct from [muon_detector](../muon_detector/SPEC.md),
a *sensor* node). Where the muon detector establishes how a residence
contributes raw, real-world signal to 7, this spec establishes how a
residence contributes quantum-sourced entropy and/or quantum computation —
and, more importantly, establishes the pattern itself: **many small nodes,
in ordinary homes, rather than one large facility.**

## Physical form — deliberately undecided

This spec intentionally does not commit to hardware yet. What "quantum" means
physically for a residential node is an open question (see below) to be
resolved in a future spec pass, once the node protocol and network are
further along. Options already on the table, none chosen:

- A hardware quantum random number generator (QRNG) — genuinely exploits
  quantum indeterminacy (single-photon detection, vacuum noise), cheap,
  fully residentially buildable, no cloud dependency.
- A software client/orchestrator that submits real circuits to cloud
  quantum processors (IBM Quantum, AWS Braket, Azure Quantum) — real
  quantum computation, but the quantum hardware itself is not in the
  residence.
- Both together — local quantum entropy plus remote quantum compute,
  orchestrated from the house.
- A classically-simulated stand-in first, matching the MVP-before-hardware
  path used in `muon_detector/SPEC.md`.

Note for future passes: true gate-based quantum computers (superconducting
or trapped-ion) require dilution refrigerators at millikelvin temperatures
and are not residentially feasible as of this writing — whatever is chosen
here has to work within that real constraint.

## Why "personal" and why a residence

This node type is the direct modern instance of the pattern root
[SPEC.md](../../SPEC.md) already describes in "Precursors: The First
Networked Systems" — systems that were "plural, zoned, and interconnected
rather than singular and self-contained," each tuned to one different thing.
A personal quantum computer, sitting in someone's home rather than a data
center or national lab, is that precursor pattern instantiated at the
smallest possible scale: **distributed by construction, not centralized and
then federated.**

## Network role

- Registers as node type `personal_quantum_computer` under the shared node
  protocol (see [../INDEX.md](../INDEX.md#node-protocol)).
- Lives in a private residence: owner-operated, geographically arbitrary,
  not a data center — genuine distribution, not simulated distribution.
- Contributes whichever of {quantum-sourced entropy, quantum job execution,
  quantum job orchestration} the eventual hardware decision provides, once
  made.
- Alongside `muon_detector`, this is the second node type to use the shared
  node protocol — both specs exist in part to prove that protocol works
  across genuinely different device kinds (a passive sensor vs. an active
  compute node) before more node types are added.

## Open questions

- Which hardware path (see "Physical form" above) — and does the answer
  differ for an early adopter vs. a mature network?
- What's the minimum a residence needs (power, always-on network, physical
  space) to host a node in practice?
- How does a residential node authenticate/register itself as trustworthy
  within the network, given it's owner-operated and not physically secured
  the way a data center node would be?
- If the eventual answer includes a cloud QC bridge, how much of "personal"
  survives when the actual qubits are remote?
