# Biological-maintenance simulations

- [Complete report: solution architecture, experiment plans, simulation results and conclusions](report.md)
- [Detailed simulation output tables](outputs/results.md)

This folder contains reproducible **toy simulations and thought experiments** for the three barriers discussed in the research response:

1. residual cancer / endogenous failure risk over long horizons, plus an independent clone-detection thought experiment;
2. somatic mutation accumulation with an idealized cell-bank reset;
3. loss of an abstract memory-relevant network state during repeated neuronal replacement.

They are for reasoning and experiment design—not biological forecasts, clinical advice, or validated models of aging, cancer, DNA repair, memory, or identity. Several parameters are deliberately hypothetical. The script prints assumptions alongside the results and writes small CSVs plus a Markdown summary into `outputs/`.

## Run

```bash
python3 simulations/biological-immortality/simulate.py --seed 20261003
```

Python 3.9+; standard library only. Change the seed to obtain a different Monte Carlo sample. `--trials` and `--network-trials` control simulation precision, not biological certainty.

## What each model does—and does not—say

### 1. Residual hazard

For a constant residual event rate `lambda` per year, the model samples event times from an exponential distribution and compares Monte Carlo results with `exp(-lambda * time)`. Rates from `1e-6` to `1e-3` per year are **illustrative, not estimates** of a person's cancer or failure risk. The calculation demonstrates only that any positive constant hazard compounds over unbounded time.

### 2. Mutation-count accumulation

The model adds Poisson mutation-count increments to 500 renewing lineages over 100 years. It uses 40 new mutations per lineage-year as an approximate published rate in selected adult human stem-cell populations (Blokzijl et al., *Nature*, 2016, [DOI](https://doi.org/10.1038/nature19768)). This is not a universal somatic mutation rate. Reset intervals of 1, 10, and 50 years assume an impossibly clean archive that perfectly resets every lineage. Mutations are **not** classified as harmful, and the simulation does not infer function from mutation count. Linear extrapolation and a perfect archive are intentionally optimistic assumptions.

### 3. Neuronal state transfer

A toy circuit has 10,000 independent binary state variables. This is **not** a claim that one synapse stores one bit or that memories are stored as a binary connectome. The annual state-change probability, repair success rate, and replacement fidelity are illustrative. The in-place repair case assumes the original state can be recovered locally; the replacement case incurs an independent mapping error at each transfer. This isolates the information-theory intuition that repeated imperfect copying can compound error. It is not a model of human memory or subjective identity.

## Source anchors

- Somatic mutations accumulate in human adult stem-cell populations at tissue-specific rates: Blokzijl et al., *Nature* (2016), [DOI](https://doi.org/10.1038/nature19768).
- Memory-associated neurons and circuit connectivity in mice: Ryan et al., *Science* (2015), [DOI](https://doi.org/10.1126/science.aaa5542).
- Partial reprogramming of mouse engram neurons: Berdugo-Vega et al., *Neuron* (2026), [DOI](https://doi.org/10.1016/j.neuron.2025.11.028).
- Sequencing errors can be reduced with duplex consensus: Schmitt et al., *PNAS* (2012), [DOI](https://doi.org/10.1073/pnas.1208715109).

## Appropriate use

Use these outputs to identify assumptions that dominate conclusions, derive thresholds for follow-up experiments, and communicate why very low risk is not the same as zero risk. Do not cite their numerical outputs as empirical biological probabilities. Replace hypothetical parameters with measured data only after preregistered experiments and independent replication.
