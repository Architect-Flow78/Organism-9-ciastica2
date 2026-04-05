# Morphological Autopoietic Swarm

**Organism 8 + Organism 9 — Unified Two-Layer System**

> *Agents do not obey rules. They crystallise from conditions.*

---

## Overview

This repository implements a two-layer autopoietic swarm system in which agents
**spontaneously emerge** from a continuous phase field when local conditions
exceed the Kuramoto critical threshold K_c = 1.019.

### Layer 1 — Phase Field (Organism 9)
A discretised **sine-Gordon** equation runs on a 1-D ring:

```
φ_tt = φ_xx − g·sin(φ) + ξ(t)
```

Topological solitons (kinks) self-organise from asymmetric initial seeds.
Wherever |φ(x)| > K_c, the field can **birth an agent**.

### Layer 2 — Autopoietic Agents (Organism 8)
Each agent carries an **InvariantCell** with frequency parameter K.
Through Hurwitz self-tuning it seeks the maximally irrational point
φ = 1.618..., which minimises inter-rational tension.

Agents orbit in an arithmetic-fractal potential V(r) built from
divisor counts d(n). Each generation inherits talent and orbits
progressively closer to the deepest prime valley.

---

## Mathematical Constants

| Symbol | Value | Meaning |
|--------|-------|---------|
| K_c | 1.019 | Kuramoto critical threshold for U[1.2, 2.8] |
| φ | 1.618... | Hurwitz optimal — maximum irrationality |
| g | 1.4 | Sine-Gordon nonlinearity constant |

---

## Three Axioms (Necessary + Sufficient for Life)

1. **Phase** — θ = (w·K) mod 1 ∈ [0,1): cyclic potential exists
2. **Asymmetry** — δ > 0: a seed breaks the uniform field
3. **Nonlinearity** — K > K_c: coupling forces phase into a closed orbit

Below K_c: phases drift randomly, no stable agent.  
Above K_c: coherence C = |⟨e^{2πiθ}⟩| > 0, the agent is born.  
K = φ: maximum stability by Hurwitz theorem (1891).

---

## Coupling (Two-Layer Feedback Loop)

```
Field → birth candidates → Agents → death → field injection → Field
```

When an agent dies it deposits phase energy back into the substrate
(`field.inject()`), which can trigger new births nearby.
This closes the autopoietic loop: the swarm produces the conditions
for its own reproduction.

---

## Testable Predictions

1. Agents born near K = φ outlive agents born near rational K (1.5, 2.0, 2.5)
2. Population mean K converges toward φ without explicit optimisation
3. Mean orbital radius decreases monotonically with lineage (prime valley drift)
4. System coherence shows phase transitions at K_c = 1.019 and K = φ = 1.618

---

## Installation

```bash
pip install numpy matplotlib
python organism_unified.py
```

Outputs polar swarm plots and K→φ convergence chart every 1000 steps.

---

## File Structure

```
organism_unified.py   — complete unified simulation
README.md             — this file
```

---

## Citation

If you use this code or ideas in academic work, please cite:

```
Pascal, N. (2026). Morphological Autopoietic Swarm: Spontaneous Agent Birth
from Phase Fields via the Kuramoto Threshold. Preprint, Zenodo.
```

---

## License

CC BY 4.0 — Nicolae Pascal, Renazzo (Fe), Italy  
`pascalnicolae78@gmail.com`
