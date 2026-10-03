#!/usr/bin/env python3
"""Transparent toy simulations for the biological-immortality discussion.

These models illustrate sensitivity and information-loss ideas. They are NOT
biological forecasts, validated mechanistic models, or clinical decision tools.
Only the illustrative stem-cell mutation-rate scale is anchored to a published
measurement (about 40 new mutations/year in selected sampled tissues); all
other model rates and intervention efficiencies are explicitly hypothetical.

Run:
    python3 simulations/biological-immortality/simulate.py

Outputs are written to simulations/biological-immortality/outputs/.
Python standard library only.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
DEFAULT_SEED = 20261003


def quantile(values: Sequence[float], q: float) -> float:
    """Linear-interpolated sample quantile."""
    if not values:
        return float("nan")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def wilson(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson interval for a simulated Bernoulli proportion."""
    if trials <= 0:
        return float("nan"), float("nan")
    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def poisson_knuth(rng: random.Random, lam: float) -> int:
    """Poisson draw; adequate for the small/moderate lambdas used here."""
    if lam < 0:
        raise ValueError("lambda must be nonnegative")
    if lam == 0:
        return 0
    threshold = math.exp(-lam)
    product = 1.0
    count = 0
    while product > threshold:
        count += 1
        product *= rng.random()
    return count - 1


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def hazard_simulation(rng: random.Random, trials: int) -> list[dict[str, object]]:
    """Simulate survival from a constant, hypothetical Poisson failure hazard."""
    rates = (1e-6, 1e-5, 1e-4, 1e-3)
    horizons = (100, 500, 1000)
    rows: list[dict[str, object]] = []
    for rate in rates:
        for years in horizons:
            p_exact = math.exp(-rate * years)
            survived = sum(rng.expovariate(rate) > years for _ in range(trials))
            p_sim = survived / trials
            low, high = wilson(survived, trials)
            rows.append({
                "annual_residual_hazard_illustrative": rate,
                "horizon_years": years,
                "analytic_no_failure_probability": p_exact,
                "monte_carlo_no_failure_probability": p_sim,
                "mc_95_wilson_low": low,
                "mc_95_wilson_high": high,
                "trials": trials,
            })
    return rows


def cancer_screening_simulation(rng: random.Random, trials: int) -> list[dict[str, object]]:
    """Toy calculation of misses across many independently screened clones.

    Sensitivities and clone counts are hypothetical. Independence is optimistic:
    correlated sensor failures, antigen loss, inaccessible tumours, or shared
    blind spots would make the true miss probability larger.
    """
    clone_counts = (1, 10, 100, 1000)
    sensitivities = (0.99, 0.999, 0.9999)
    rows: list[dict[str, object]] = []
    for count in clone_counts:
        for sensitivity in sensitivities:
            p_no_missed = sensitivity ** count
            successes = 0
            for _ in range(trials):
                all_detected = all(rng.random() < sensitivity for _ in range(count))
                successes += all_detected
            low, high = wilson(successes, trials)
            rows.append({
                "hypothetical_independent_clones_screened": count,
                "hypothetical_per_clone_sensitivity": sensitivity,
                "analytic_probability_no_missed_clone": p_no_missed,
                "analytic_probability_at_least_one_missed": 1 - p_no_missed,
                "mc_probability_no_missed_clone": successes / trials,
                "mc_95_wilson_low": low,
                "mc_95_wilson_high": high,
                "trials": trials,
            })
    return rows


def mutation_refresh_simulation(rng: random.Random) -> list[dict[str, object]]:
    """Track mutation-count units in stem-cell lineages with ideal archive resets.

    A rate of 40/year is an approximate published rate in selected human adult
    stem-cell populations, not a universal rate. The 100-year linear extension,
    perfect archive, and refresh intervals are model assumptions. The model does
    not assign functional consequence to a mutation.
    """
    lineages = 500
    years = 100
    mutation_rate = 40.0
    intervals: tuple[int | None, ...] = (None, 50, 10, 1)
    rows: list[dict[str, object]] = []
    for interval in intervals:
        burdens = [0] * lineages
        annual_means: list[float] = []
        for year in range(1, years + 1):
            if interval is not None and year > 1 and (year - 1) % interval == 0:
                burdens = [0] * lineages  # ideal, mutation-free archive reset
            for i in range(lineages):
                burdens[i] += poisson_knuth(rng, mutation_rate)
            annual_means.append(sum(burdens) / lineages)
        label = "never" if interval is None else str(interval)
        rows.append({
            "ideal_archive_refresh_interval_years": label,
            "mean_current_mutation_count_across_lineage_years": sum(annual_means) / years,
            "mean_current_mutation_count_at_year_100": sum(burdens) / lineages,
            "p95_current_mutation_count_at_year_100": quantile(burdens, 0.95),
            "lineages": lineages,
            "horizon_years": years,
            "assumed_mutation_events_per_lineage_year": mutation_rate,
        })
    return rows


def neuron_state_simulation(rng: random.Random, network_trials: int) -> list[dict[str, object]]:
    """Toy network-state retention experiment.

    Each abstract state bit stands for one identity-relevant synaptic state. It
    is NOT a claim that one synapse stores one bit or that memory is a binary
    vector. The damage rate, repair efficiency, and mapping fidelity are chosen
    for illustration only.
    """
    state_bits = 10_000
    years = 100
    damage_per_state_year = 1e-5
    repair_efficiency = 0.99
    transfer_interval = 10
    transfers = years // transfer_interval

    scenarios: list[tuple[str, float, str]] = []
    p_no_repair = (1 - damage_per_state_year) ** years
    scenarios.append(("no_maintenance", p_no_repair, "illustrative independent damage; no correction"))

    # Generous upper bound: every damaged state is recognized and recoverable
    # from a local reference, with the stated repair probability.
    p_in_place = (1 - damage_per_state_year * (1 - repair_efficiency)) ** years
    scenarios.append(("in_place_repair_99pct", p_in_place, "assumes original state is locally recoverable"))

    for fidelity in (0.5, 0.99, 0.999, 0.9999):
        p_transfer = ((1 - damage_per_state_year) ** transfer_interval * fidelity) ** transfers
        scenarios.append((f"replacement_map_fidelity_{fidelity:g}", p_transfer,
                          "each transfer has independent per-state mapping error"))

    rows: list[dict[str, object]] = []
    for name, expected, assumption in scenarios:
        retained_fractions: list[float] = []
        # Sample network-level binomial variation using independent state bits.
        for _ in range(network_trials):
            retained = sum(rng.random() < expected for _ in range(state_bits))
            retained_fractions.append(retained / state_bits)
        rows.append({
            "strategy": name,
            "expected_fraction_of_original_states_retained": expected,
            "mc_mean_fraction_retained": sum(retained_fractions) / network_trials,
            "mc_p05_fraction_retained": quantile(retained_fractions, 0.05),
            "mc_p95_fraction_retained": quantile(retained_fractions, 0.95),
            "state_bits_in_toy_network": state_bits,
            "network_trials": network_trials,
            "horizon_years": years,
            "assumption": assumption,
        })
    return rows


def integrated_hazard_simulation(rng: random.Random, trials: int) -> list[dict[str, object]]:
    """Three independent hypothetical failure channels, for arithmetic only."""
    rows: list[dict[str, object]] = []
    for each_rate in (1e-6, 1e-5, 1e-4):
        total_rate = 3 * each_rate
        for years in (100, 1000):
            p_exact = math.exp(-total_rate * years)
            survived = sum(rng.expovariate(total_rate) > years for _ in range(trials))
            low, high = wilson(survived, trials)
            rows.append({
                "hypothetical_rate_per_channel_per_year": each_rate,
                "independent_channels": 3,
                "horizon_years": years,
                "analytic_no_failure_probability": p_exact,
                "monte_carlo_no_failure_probability": survived / trials,
                "mc_95_wilson_low": low,
                "mc_95_wilson_high": high,
                "trials": trials,
            })
    return rows


def fmt_pct(x: float) -> str:
    return f"{100*x:.3f}%"


def make_report(
    hazard: list[dict[str, object]],
    cancer_screening: list[dict[str, object]],
    mutation: list[dict[str, object]],
    neuron: list[dict[str, object]],
    integrated: list[dict[str, object]],
    seed: int,
    trials: int,
    network_trials: int,
) -> str:
    lines = [
        "# Simulation results: biological-maintenance thought experiments",
        "",
        "> **Caution:** These are toy models, not biological forecasts, clinical advice, or evidence that any intervention works. Parameter values are illustrative unless explicitly identified as an observed scale. The mutation model uses an approximate rate reported in selected adult stem-cell populations, but linear extrapolation and ideal archive resets are assumptions. The neuronal state model is an information-loss illustration, not a model of human memory.",
        "",
        f"Seed: `{seed}`. Hazard trials per row: `{trials:,}`. Toy-network trials per strategy: `{network_trials:,}`.",
        "",
        "## 1. Residual-hazard thought experiment",
        "",
        "Assume a constant residual failure rate λ per year. The probability of no event through time T is exp(−λT). This simulation checks that calculation by sampling exponential event times. The rates below are hypothetical and are not estimates of cancer or biological failure rates.",
        "",
        "| Hypothetical λ/year | 100 y | 500 y | 1,000 y |",
        "|---:|---:|---:|---:|",
    ]
    by_rate: dict[float, dict[int, dict[str, object]]] = {}
    for row in hazard:
        by_rate.setdefault(float(row["annual_residual_hazard_illustrative"]), {})[int(row["horizon_years"])] = row
    for rate, horizon_rows in by_rate.items():
        vals = [fmt_pct(float(horizon_rows[t]["analytic_no_failure_probability"])) for t in (100, 500, 1000)]
        lines.append(f"| {rate:.0e} | " + " | ".join(vals) + " |")
    lines += [
        "",
        "The central lesson is mathematical: a small positive hazard compounds over long horizons. Under this model, no finite positive λ gives a nonzero probability of surviving forever. This does not prove that the biological hazards in question have any particular value; it shows why ‘extremely low’ and ‘zero’ are different claims.",
        "",
        "### One-pass cancer-surveillance thought experiment",
        "",
        "Assume each abnormal clone is independently detected with the same hypothetical sensitivity in one surveillance round. The probability of no missed clone among N clones is sensitivity^N. This assumes independent errors and is optimistic; a shared sensor blind spot would invalidate that assumption.",
        "",
        "| Hypothetical clones | 99% sensitivity | 99.9% sensitivity | 99.99% sensitivity |",
        "|---:|---:|---:|---:|",
    ]
    cancer_by_count: dict[int, dict[float, dict[str, object]]] = {}
    for row in cancer_screening:
        cancer_by_count.setdefault(int(row["hypothetical_independent_clones_screened"]), {})[float(row["hypothetical_per_clone_sensitivity"])] = row
    for count, sensitivity_rows in cancer_by_count.items():
        vals = [fmt_pct(float(sensitivity_rows[s]["analytic_probability_no_missed_clone"])) for s in (0.99, 0.999, 0.9999)]
        lines.append(f"| {count} | " + " | ".join(vals) + " |")
    lines += [
        "",
        "This does not estimate how many premalignant clones a person has or how sensitive a future system could be. It shows that surveillance requirements scale with the number of opportunities for escape, and that correlated misses would be worse than this independent model.",
        "",
        "### Three-channel interaction",
        "",
        "For three independent channels with the same illustrative rate λ, the combined no-failure probability is exp(−3λT). Real cancer, mutation and neural risks are neither independent nor constant; this is a deliberately simple interaction check.",
        "",
        "| λ per channel/year | 100 y | 1,000 y |",
        "|---:|---:|---:|",
    ]
    int_by_rate: dict[float, dict[int, dict[str, object]]] = {}
    for row in integrated:
        int_by_rate.setdefault(float(row["hypothetical_rate_per_channel_per_year"]), {})[int(row["horizon_years"])] = row
    for rate, horizon_rows in int_by_rate.items():
        lines.append(f"| {rate:.0e} | {fmt_pct(float(horizon_rows[100]['analytic_no_failure_probability']))} | {fmt_pct(float(horizon_rows[1000]['analytic_no_failure_probability']))} |")

    lines += [
        "",
        "## 2. Mutation accumulation versus ideal archive refresh",
        "",
        "The model adds a Poisson-distributed number of mutation events each year to 500 renewing lineages. It uses 40 events per lineage-year as an illustrative scale reported in sampled human intestinal and liver stem cells (Blokzijl et al., Nature, 2016; DOI: 10.1038/nature19768); it is not a universal rate. The archive is assumed to be perfectly clean and to restore every lineage at the chosen interval. No event is classified as harmful, and no functional consequence is inferred.",
        "",
        "| Ideal refresh interval | Mean current count across lineage-years | Mean at year 100 | 95th percentile at year 100 |",
        "|---:|---:|---:|---:|",
    ]
    for row in mutation:
        label = "Never" if row["ideal_archive_refresh_interval_years"] == "never" else f"{row['ideal_archive_refresh_interval_years']} y"
        lines.append(
            f"| {label} | {float(row['mean_current_mutation_count_across_lineage_years']):.1f} | "
            f"{float(row['mean_current_mutation_count_at_year_100']):.1f} | "
            f"{float(row['p95_current_mutation_count_at_year_100']):.1f} |"
        )
    lines += [
        "",
        "Ideal replacement sharply limits the number of mutations present in an individual lineage at a given time. It does **not** imply that function is restored: most counted variants may be neutral, while a small subset may matter greatly. Nor does it model bank contamination, epigenetic drift, immune rejection, bottlenecks, or the possibility that the reference itself is wrong. Those omissions make the archive result an optimistic upper bound.",
        "",
        "## 3. Neuronal-state transfer thought experiment",
        "",
        "Represent a memory-relevant circuit by 10,000 abstract binary states. Each state has an illustrative 10⁻⁵ annual probability of changing. Compare no repair, in-place repair with 99% success after a damage event, and replacement every ten years with varying per-state mapping fidelity. These rates are chosen for demonstration, not measured biology. The in-place model generously assumes the original state is locally recoverable; the replacement model charges a new independent mapping error at every replacement.",
        "",
        "| Toy strategy | Expected fraction of original states retained after 100 y | MC 5th–95th percentile |",
        "|---|---:|---:|",
    ]
    for row in neuron:
        lines.append(
            f"| {row['strategy']} | {fmt_pct(float(row['expected_fraction_of_original_states_retained']))} | "
            f"{fmt_pct(float(row['mc_p05_fraction_retained']))}–{fmt_pct(float(row['mc_p95_fraction_retained']))} |"
        )
    lines += [
        "",
        "This is not a claim that memories are binary synapse lists. It is a thought experiment about repeated imperfect copying: even high per-transfer fidelity can compound, while successful repair in place avoids a full re-mapping step. A real brain has plasticity, redundancy and distributed representations that this model omits; those may improve robustness, but they do not establish that exact personal identity can be reconstructed after neuron loss.",
        "",
        "## Interpretation and next experiments",
        "",
        "1. Measure real clone escape and safety-switch performance in organoids before assigning a cancer-risk reduction factor.",
        "2. Sequence archived and refreshed lineages over serial passages; separately measure tissue function so mutation count is not mistaken for damage.",
        "3. For neuronal work, preregister memory-specificity and cell-identity endpoints. A general behavioural improvement is insufficient if the original memory becomes less specific.",
        "4. Fit parameter ranges only after experimental data exist. Until then, sensitivity analysis is more honest than a single numerical forecast.",
        "",
        "## Reproducibility",
        "",
        "Run `python3 simulations/biological-immortality/simulate.py --seed 20261003`. All outputs use Python's standard library and are written beside this report in `outputs/`.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--trials", type=int, default=50_000, help="Monte Carlo trials per hazard row")
    parser.add_argument("--network-trials", type=int, default=1_000, help="Toy networks sampled per neuron strategy")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    if args.trials < 1 or args.network_trials < 1:
        parser.error("trial counts must be positive")

    rng = random.Random(args.seed)
    hazard = hazard_simulation(rng, args.trials)
    cancer_screening = cancer_screening_simulation(rng, args.trials)
    mutation = mutation_refresh_simulation(rng)
    neuron = neuron_state_simulation(rng, args.network_trials)
    integrated = integrated_hazard_simulation(rng, args.trials)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "residual_hazard.csv", hazard)
    write_csv(args.output_dir / "cancer_screening.csv", cancer_screening)
    write_csv(args.output_dir / "mutation_refresh.csv", mutation)
    write_csv(args.output_dir / "neuron_state_transfer.csv", neuron)
    write_csv(args.output_dir / "integrated_hazard.csv", integrated)
    report = make_report(hazard, cancer_screening, mutation, neuron, integrated, args.seed, args.trials, args.network_trials)
    (args.output_dir / "results.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWrote simulation outputs to {args.output_dir}")


if __name__ == "__main__":
    main()
