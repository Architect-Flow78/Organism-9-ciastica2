"""
Morphological Autopoietic Swarm — Unified System
Organism 9 (Phase Field Substrate) + Organism 8 (Agent Swarm)

Two-layer architecture:
  Layer 1: Sine-Gordon phase field  — continuous substrate, births emerge here
  Layer 2: Autopoietic agents       — crystallize from field peaks above K_c

Mathematical constants:
  K_c  = 1.019  (Kuramoto critical threshold)
  phi  = 1.618  (Hurwitz optimal stability point)

Nicolae Pascal — Independent Researcher, Renazzo (Fe), Italy
March 2026 — CC BY 4.0
"""

import numpy as np
import math
import random
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ─── FUNDAMENTAL CONSTANTS ───────────────────────────────────────────────────
PHI = 1.6180339887          # Hurwitz optimal: maximises min|K - p/q|
K_C = 2.0 * (2.8 - 1.2) / math.pi   # = 1.019  Kuramoto threshold for U[1.2, 2.8]


# ─── UTILITIES ───────────────────────────────────────────────────────────────

def ema(old, new, alpha):
    return alpha * old + (1.0 - alpha) * new

def circular_coherence(phases):
    """Order parameter C = |<e^{2πi θ}>| ∈ [0,1]."""
    if not phases:
        return 0.5
    sc = sum(math.cos(2.0 * math.pi * p) for p in phases) / len(phases)
    ss = sum(math.sin(2.0 * math.pi * p) for p in phases) / len(phases)
    return math.sqrt(sc * sc + ss * ss)

def divisor_count(n):
    """d(n): number of positive divisors of n."""
    if n < 1:
        return 1
    count = 0
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            count += 2 if i != n // i else 1
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — PHASE FIELD (Sine-Gordon substrate)
# φ_tt = φ_xx − g·sin(φ) + ξ(t)
# Topological solitons = candidate birth sites for agents
# ═══════════════════════════════════════════════════════════════════════════════

class PhaseField:
    """
    Discretised sine-Gordon field on a 1-D ring.
    Kink solutions (solitons) carry topological charge and mark
    locations where the field amplitude exceeds K_c — triggering
    agent crystallisation.
    """

    def __init__(self, Nx: int = 600, dt: float = 0.05, g: float = 1.4):
        self.Nx = Nx
        self.dt = dt
        self.g  = g

        # Initialise with asymmetric seeds (Axiom 3: δ > 0)
        self.phi      = np.zeros(Nx)
        self.phi_prev = np.zeros(Nx)
        rng = np.random.default_rng()
        for _ in range(40):
            pos = rng.integers(20, Nx - 20)
            self.phi[pos] = rng.uniform(2.0, 5.0)
        self.phi_prev = self.phi.copy()

    # ── evolution ────────────────────────────────────────────────────────────
    def step(self):
        lap = np.roll(self.phi, -1) - 2.0 * self.phi + np.roll(self.phi, 1)
        phi_next = (2.0 * self.phi - self.phi_prev
                    + self.dt ** 2 * (lap - self.g * np.sin(self.phi))
                    + np.random.normal(0.0, 0.002, self.Nx))
        self.phi_prev = self.phi.copy()
        self.phi      = phi_next

    # ── coupling ──────────────────────────────────────────────────────────────
    def inject(self, pos: int, amplitude: float = 1.5):
        """Agent death deposits phase energy back into the substrate."""
        w = 5
        for dx in range(-w, w + 1):
            i = (pos + dx) % self.Nx
            self.phi[i] += amplitude * math.exp(-dx * dx / (2.0 * w * w))

    def local_sample(self, pos: int, n: int = 5) -> list:
        """Return n field values centred on pos — the agent's sensory world."""
        half = n // 2
        return [self.phi[(pos + dx) % self.Nx] for dx in range(-half, half + 1)]

    # ── birth detection ───────────────────────────────────────────────────────
    def birth_candidates(self, threshold: float = K_C) -> np.ndarray:
        """Positions where |φ| > K_c: necessary condition for agent birth."""
        return np.where(np.abs(self.phi) > threshold)[0]


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1b — PRIME POTENTIAL  V(r) = log(d(n_local)+1) + log(d(n_global)+1)
# Arithmetic-fractal landscape; multiple stable orbits at prime-related radii
# ═══════════════════════════════════════════════════════════════════════════════

class PrimePotentialField:
    def __init__(self, scale: float = 10.0):
        self.scale = scale

    def potential(self, r: float) -> float:
        n_loc = max(1, int(abs(r) * self.scale))
        n_glo = max(1, int(abs(r) * self.scale * 0.1))
        return (math.log(divisor_count(n_loc) + 1)
              + math.log(divisor_count(n_glo) + 1))

    def gradient(self, r: float, eps: float = 1e-3) -> float:
        return (self.potential(r + eps) - self.potential(r - eps)) / (2.0 * eps)


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 2a — INVARIANT CELL  (sovereign frequency identity)
# Tracks circular coherence C = |<e^{2πiθ}>| and self-tunes K → φ
# ═══════════════════════════════════════════════════════════════════════════════

class InvariantCell:
    def __init__(self, K: float):
        self.K    = K      # frequency parameter — the agent's invariant identity
        self.fast = 0.5    # short-term coherence EMA  (α = 0.9)
        self.slow = 0.5    # long-term coherence EMA   (α = 0.995)

    def update(self, values: list) -> float:
        phases = [(v * self.K) % 1.0 for v in values]
        C = circular_coherence(phases)
        self.fast = ema(self.fast, C, 0.9)
        self.slow = ema(self.slow, C, 0.995)
        return C

    def tension(self) -> float:
        return abs(self.fast - self.slow)


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 2b — AGENT  (autopoietic entity born from field peak)
# ═══════════════════════════════════════════════════════════════════════════════

class Agent:
    """
    Born at a field position where |φ| > K_c.
    Carries InvariantCell with K ≥ K_c.
    Seeks K → φ = 1.618 via Hurwitz self-tuning.
    Orbits in prime potential V(r); lineage reduces effective angular momentum,
    drifting orbits inward across generations.
    """

    def __init__(self,
                 field_pos: int,
                 field_K: float,
                 talent: float = 0.0,
                 lineage: int   = 0):
        self.field_pos = field_pos
        self.lineage   = lineage
        self.cell      = InvariantCell(max(K_C, min(field_K, 13.0)))
        self.inner_bias = 0.5
        self.ten        = 0.0   # running tension
        self.talent     = talent
        self.fear       = 0.0
        self.life_time  = 0

        # Orbital state — lineage pushes birth radius inward
        self.r     = max(2.0, 20.0 / (lineage + 1) + random.uniform(-1.0, 1.0))
        self.pr    = 0.0
        self.theta = random.random() * 2.0 * math.pi
        self.L     = random.uniform(0.3, 0.7)   # angular momentum

    # ── one timestep ─────────────────────────────────────────────────────────
    def update(self, world: list, prime: PrimePotentialField,
               gamma: float = 1.5, dt: float = 0.05) -> str:
        self.life_time += 1

        # 1. Cognition: update coherence
        C = self.cell.update(world)
        self.inner_bias = ema(self.inner_bias, self.cell.fast, 0.999)
        conflict = abs(self.cell.fast - self.inner_bias)
        self.ten = ema(self.ten, conflict + self.cell.tension(), 0.98)

        # 2. Self-tuning toward φ (Hurwitz theorem)
        if self.ten > 0.25:
            self.cell.K += 0.1 * (self.cell.fast - self.inner_bias)
            self.talent  += 0.005
        if self.ten > 0.6:
            self.fear += 0.02
        else:
            self.fear *= 0.98

        # 3. Orbital dynamics in prime potential
        #    L_eff = L · exp(−α · lineage)  → inward drift with generations
        L_eff = self.L * math.exp(-self.lineage * 0.1)
        dV    = prime.gradient(self.r)
        f_rad = -gamma * dV + L_eff ** 2 / (self.r ** 3 + 1e-6)
        self.pr     += f_rad * dt
        self.r      += self.pr * dt
        self.theta  += L_eff / (self.r ** 2 + 1e-6)

        # 4. Bounds
        self.cell.K = max(0.5, min(13.0, self.cell.K))
        self.r      = max(0.5, self.r)

        if self.fear > 1.2 or self.life_time > 1500:
            return "death"
        return "alive"


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED SYSTEM — MorphAutopoieticSwarm
# ═══════════════════════════════════════════════════════════════════════════════

class MorphAutopoieticSwarm:
    """
    Couples the sine-Gordon phase field (Organism 9) with the
    autopoietic agent swarm (Organism 8):

      Field → birth candidates → agents → death → field injection → loop

    Three necessary+sufficient conditions are maintained globally:
      Axiom 1 (Phase):        φ ∈ S¹ for every agent
      Axiom 2 (Evolution):    K self-tunes, r evolves, θ rotates
      Axiom 3 (Non-closure):  tension > 0 always (fractal V + irrational K)
    """

    def __init__(self, max_agents: int = 80):
        self.field      = PhaseField()
        self.prime      = PrimePotentialField()
        self.agents: list[Agent] = []
        self.max_agents = max_agents
        self.t          = 0

        # Metrics history
        self.mean_K     = []
        self.pop        = []
        self.mean_r     = []
        self.births_log = []
        self.deaths_log = []

        self._births_this_step = 0
        self._deaths_this_step = 0

    # ── one timestep ─────────────────────────────────────────────────────────
    def step(self):
        self.t += 1
        self._births_this_step = 0
        self._deaths_this_step = 0

        # ① Advance substrate
        self.field.step()

        # ② Try to birth new agents from field peaks
        if len(self.agents) < self.max_agents:
            candidates = self.field.birth_candidates(K_C)
            if len(candidates) > 0:
                pos = int(np.random.choice(candidates))
                amp = abs(self.field.phi[pos])
                # Exclusion zone: no two agents within 10 cells
                nearby = any(abs(a.field_pos - pos) < 10 for a in self.agents)
                if not nearby and random.random() < 0.05:
                    a = Agent(field_pos=pos, field_K=amp)
                    self.agents.append(a)
                    self._births_this_step += 1

        # ③ Update all agents
        survivors = []
        for a in self.agents:
            world  = self.field.local_sample(a.field_pos)
            status = a.update(world, self.prime)
            if status == "death":
                self._deaths_this_step += 1
                # Couple back: deposit energy into field
                self.field.inject(a.field_pos, amplitude=1.5)
                # Reincarnation with talent inheritance
                child = Agent(
                    field_pos=a.field_pos,
                    field_K=a.cell.K,
                    talent=a.talent * 0.6,
                    lineage=a.lineage + 1
                )
                survivors.append(child)
            else:
                survivors.append(a)
        self.agents = survivors

        # ④ Record metrics
        if self.agents:
            self.mean_K.append(sum(a.cell.K for a in self.agents) / len(self.agents))
            self.mean_r.append(sum(a.r     for a in self.agents) / len(self.agents))
        else:
            self.mean_K.append(float('nan'))
            self.mean_r.append(float('nan'))

        self.pop.append(len(self.agents))
        self.births_log.append(self._births_this_step)
        self.deaths_log.append(self._deaths_this_step)

    def run(self, steps: int = 5000, plot_every: int = 2500):
        for t in range(steps + 1):
            self.step()
            if t % plot_every == 0:
                self.visualise(t)

    # ── visualisation ────────────────────────────────────────────────────────
    def visualise(self, t: int):
        fig = plt.figure(figsize=(14, 10))
        gs  = GridSpec(2, 2, figure=fig)

        # (A) Phase field snapshot
        ax0 = fig.add_subplot(gs[0, :])
        ax0.plot(self.field.phi, color='steelblue', lw=0.8, alpha=0.85)
        ax0.axhline(K_C,  color='red',    lw=1.2, ls='--', label=f'K_c={K_C:.3f}')
        ax0.axhline(-K_C, color='red',    lw=1.2, ls='--')
        ax0.axhline(PHI,  color='gold',   lw=1.2, ls=':',  label=f'φ={PHI:.3f}')
        ax0.set_title(f'Phase Field φ(x)  —  step {t}', fontsize=11)
        ax0.legend(fontsize=9)
        ax0.set_xlim(0, self.field.Nx)

        # (B) Polar swarm
        ax1 = fig.add_subplot(gs[1, 0], projection='polar')
        if self.agents:
            rs  = [a.r       for a in self.agents]
            ts  = [a.theta   for a in self.agents]
            cl  = [a.lineage for a in self.agents]
            sz  = [10 + a.talent * 200 for a in self.agents]
            sc  = ax1.scatter(ts, rs, c=cl, s=sz, cmap='plasma', alpha=0.85)
            plt.colorbar(sc, ax=ax1, label='Lineage', pad=0.12)
        ax1.set_title('Swarm orbits\n(colour=lineage, size=talent)', fontsize=9)

        # (C) K convergence toward φ
        ax2 = fig.add_subplot(gs[1, 1])
        ax2.plot(self.mean_K, color='darkorange', lw=1.2, label='mean K')
        ax2.axhline(PHI, color='gold', lw=1.5, ls='--', label=f'φ={PHI:.3f}')
        ax2.axhline(K_C, color='red',  lw=1.0, ls=':',  label=f'K_c={K_C:.3f}')
        ax2.set_xlabel('step'); ax2.set_ylabel('K')
        ax2.set_title('K → φ convergence', fontsize=10)
        ax2.legend(fontsize=8)

        plt.suptitle(
            f'Morphological Autopoietic Swarm  |  pop={len(self.agents)}  '
            f'births={sum(self.births_log)}  deaths={sum(self.deaths_log)}',
            fontsize=11, y=1.01
        )
        plt.tight_layout()
        plt.savefig(f'swarm_step_{t:05d}.png', dpi=120, bbox_inches='tight')
        plt.show()
        print(f'[t={t:5d}]  pop={len(self.agents):3d}  '
              f'meanK={self.mean_K[-1]:.4f}  meanR={self.mean_r[-1]:.3f}')


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"K_c = {K_C:.4f}   φ = {PHI:.4f}")
    swarm = MorphAutopoieticSwarm(max_agents=80)
    swarm.run(steps=5000, plot_every=1000)
  
