# Simulation results: biological-maintenance thought experiments

> **Caution:** These are toy models, not biological forecasts, clinical advice, or evidence that any intervention works. Parameter values are illustrative unless explicitly identified as an observed scale. The mutation model uses an approximate rate reported in selected adult stem-cell populations, but linear extrapolation and ideal archive resets are assumptions. The neuronal state model is an information-loss illustration, not a model of human memory.

Seed: `20261003`. Hazard trials per row: `50,000`. Toy-network trials per strategy: `1,000`.

## 1. Residual-hazard thought experiment

Assume a constant residual failure rate λ per year. The probability of no event through time T is exp(−λT). This simulation checks that calculation by sampling exponential event times. The rates below are hypothetical and are not estimates of cancer or biological failure rates.

| Hypothetical λ/year | 100 y | 500 y | 1,000 y |
|---:|---:|---:|---:|
| 1e-06 | 99.990% | 99.950% | 99.900% |
| 1e-05 | 99.900% | 99.501% | 99.005% |
| 1e-04 | 99.005% | 95.123% | 90.484% |
| 1e-03 | 90.484% | 60.653% | 36.788% |

The central lesson is mathematical: a small positive hazard compounds over long horizons. Under this model, no finite positive λ gives a nonzero probability of surviving forever. This does not prove that the biological hazards in question have any particular value; it shows why ‘extremely low’ and ‘zero’ are different claims.

### One-pass cancer-surveillance thought experiment

Assume each abnormal clone is independently detected with the same hypothetical sensitivity in one surveillance round. The probability of no missed clone among N clones is sensitivity^N. This assumes independent errors and is optimistic; a shared sensor blind spot would invalidate that assumption.

| Hypothetical clones | 99% sensitivity | 99.9% sensitivity | 99.99% sensitivity |
|---:|---:|---:|---:|
| 1 | 99.000% | 99.900% | 99.990% |
| 10 | 90.438% | 99.004% | 99.900% |
| 100 | 36.603% | 90.479% | 99.005% |
| 1000 | 0.004% | 36.770% | 90.483% |

This does not estimate how many premalignant clones a person has or how sensitive a future system could be. It shows that surveillance requirements scale with the number of opportunities for escape, and that correlated misses would be worse than this independent model.

### Three-channel interaction

For three independent channels with the same illustrative rate λ, the combined no-failure probability is exp(−3λT). Real cancer, mutation and neural risks are neither independent nor constant; this is a deliberately simple interaction check.

| λ per channel/year | 100 y | 1,000 y |
|---:|---:|---:|
| 1e-06 | 99.970% | 99.700% |
| 1e-05 | 99.700% | 97.045% |
| 1e-04 | 97.045% | 74.082% |

## 2. Mutation accumulation versus ideal archive refresh

The model adds a Poisson-distributed number of mutation events each year to 500 renewing lineages. It uses 40 events per lineage-year as an illustrative scale reported in sampled human intestinal and liver stem cells (Blokzijl et al., Nature, 2016; DOI: 10.1038/nature19768); it is not a universal rate. The archive is assumed to be perfectly clean and to restore every lineage at the chosen interval. No event is classified as harmful, and no functional consequence is inferred.

| Ideal refresh interval | Mean current count across lineage-years | Mean at year 100 | 95th percentile at year 100 |
|---:|---:|---:|---:|
| Never | 2021.2 | 4002.0 | 4115.0 |
| 50 y | 1019.7 | 1997.8 | 2065.1 |
| 10 y | 219.8 | 399.8 | 436.0 |
| 1 y | 40.0 | 40.5 | 51.0 |

Ideal replacement sharply limits the number of mutations present in an individual lineage at a given time. It does **not** imply that function is restored: most counted variants may be neutral, while a small subset may matter greatly. Nor does it model bank contamination, epigenetic drift, immune rejection, bottlenecks, or the possibility that the reference itself is wrong. Those omissions make the archive result an optimistic upper bound.

## 3. Neuronal-state transfer thought experiment

Represent a memory-relevant circuit by 10,000 abstract binary states. Each state has an illustrative 10⁻⁵ annual probability of changing. Compare no repair, in-place repair with 99% success after a damage event, and replacement every ten years with varying per-state mapping fidelity. These rates are chosen for demonstration, not measured biology. The in-place model generously assumes the original state is locally recoverable; the replacement model charges a new independent mapping error at every replacement.

| Toy strategy | Expected fraction of original states retained after 100 y | MC 5th–95th percentile |
|---|---:|---:|
| no_maintenance | 99.900% | 99.840%–99.950% |
| in_place_repair_99pct | 99.999% | 99.990%–100.000% |
| replacement_map_fidelity_0.5 | 0.098% | 0.050%–0.150% |
| replacement_map_fidelity_0.99 | 90.348% | 89.890%–90.850% |
| replacement_map_fidelity_0.999 | 98.906% | 98.720%–99.080% |
| replacement_map_fidelity_0.9999 | 99.800% | 99.720%–99.870% |

This is not a claim that memories are binary synapse lists. It is a thought experiment about repeated imperfect copying: even high per-transfer fidelity can compound, while successful repair in place avoids a full re-mapping step. A real brain has plasticity, redundancy and distributed representations that this model omits; those may improve robustness, but they do not establish that exact personal identity can be reconstructed after neuron loss.

## Interpretation and next experiments

1. Measure real clone escape and safety-switch performance in organoids before assigning a cancer-risk reduction factor.
2. Sequence archived and refreshed lineages over serial passages; separately measure tissue function so mutation count is not mistaken for damage.
3. For neuronal work, preregister memory-specificity and cell-identity endpoints. A general behavioural improvement is insufficient if the original memory becomes less specific.
4. Fit parameter ranges only after experimental data exist. Until then, sensitivity analysis is more honest than a single numerical forecast.

## Reproducibility

Run `python3 simulations/biological-immortality/simulate.py --seed 20261003`. All outputs use Python's standard library and are written beside this report in `outputs/`.
