# Can human biological function be maintained indefinitely?

## Executive conclusion and scope

**[Established]** No demonstrated technology prevents all age-related functional decline in humans, and no experiment can prove survival or perfect function over infinite time. The most defensible research direction is not to make every cell divide forever, but to selectively renew vulnerable tissues, remove dangerous clones, and preserve functioning neurons in place.

**[Plausible]** A future system combining screened cell renewal, targeted DNA correction, cancer surveillance and neuronal maintenance might greatly extend healthspan. **[Speculative]** That system could keep age-related failure rates low enough for very long life. It would not establish literal immortality: if an irreversible endogenous failure has any constant residual rate λ, the probability of avoiding it for time T is exp(−λT), which approaches zero as T grows without bound. This is a mathematical consequence of the assumption λ>0, not an estimate of any human risk.

“Biological immortality” here means preserving the same biological brain without irreversible age-related decline; uploading/emulation do not count. This differs from invulnerability to accidents or infection. Forecasts concern a human-grade maintenance platform—not living forever.

Labels distinguish evidence: **[Established]** direct evidence; **[Plausible]** extrapolation consistent with biology; **[Speculative]** proposed or unvalidated; **[Contradicted]** too-strong wording or premise.

## 1. Cancer–telomere trade-off

### Problem and architecture

**[Established]** Telomeres are protective structures at chromosome ends; they tend to shorten as cells divide. Telomerase can extend them. Most human cancers use telomerase to maintain telomeres; a minority use alternative lengthening of telomeres (ALT), a recombination-based route. Thus, universal telomerase activation could aid tissue renewal while also helping an abnormal clone keep dividing. (Shay & Bacchetti, 1997, *European Journal of Cancer*, [DOI](https://doi.org/10.1016/S0959-8049(97)00062-2); Buseman et al., 2012, *Mutation Research*, [DOI](https://doi.org/10.1016/j.mrfmmm.2011.07.006); Mori et al., 2024, *Journal of Clinical Pathology*, [DOI](https://doi.org/10.1136/jcp-2023-209005).)

**[Speculative]** Use *restricted, conditional renewal*, not whole-body “immortalization”:

1. Measure telomere dysfunction in renewing stem-cell compartments; activate TERT only in screened cells when a prespecified dysfunction threshold is reached.
2. Use brief, reversible expression rather than permanent activation. Require intact genome-integrity and cell-identity checks before a pulse.
3. Monitor clonal expansion and chromosome abnormalities. Add an independent, inducible elimination switch to replaceable therapeutic cells; inducible caspase-9 has been used as a safety switch in engineered T-cell therapy, but extending it to tissue stem cells is unproven. (Di Stasi et al., 2011, *New England Journal of Medicine*, [DOI](https://doi.org/10.1056/NEJMoa1106152).)
4. Watch for ALT as well as telomerase. Remove an unsafe lineage and restore tissue, where feasible, from a separately screened autologous reserve.

### Readiness and uncertainty

**[Established]** TERT gene therapy extended lifespan in mice without a detected increase in cancer in one study, while telomerase-overexpressing mice in another model were more susceptible to chemically induced skin tumours. These results show context dependence, not human safety or a general cancer guarantee. (Bernardes de Jesus et al., 2012, *EMBO Molecular Medicine*, [DOI](https://doi.org/10.1002/emmm.201200245); González-Suárez et al., 2001, *The EMBO Journal*, [DOI](https://doi.org/10.1093/emboj/20.11.2619).) A 2024 TERT-activation study in primary human cells and aged mice remains preclinical (Shim et al., 2024, *Cell*, [DOI](https://doi.org/10.1016/j.cell.2024.05.048)). A 2025 ZSCAN4 study treated two patients with telomere biology disorders; it is limited disease-specific evidence, not systemic rejuvenation (Myers et al., 2025, *NEJM Evidence*, [DOI](https://doi.org/10.1056/EVIDoa2400252)).

**[Plausible]** Near-term research can test whether carefully restricted telomere maintenance preserves renewal with acceptable risk. **[Speculative]** No finite assay can certify that every cell is nonmalignant; absolute zero cancer risk is not demonstrated.

### Minimum viable experiment

**[Speculative]** Use donor-derived human colon organoids. Compare vehicle, transient unrestricted TERT, stem-cell-gated TERT, and gated TERT plus an inducible safety switch. Add a separate low-frequency, barcoded challenge with abnormal clones, including an ALT reference. Follow serial passages. Measure telomerase activity, shortest telomeres, organoid renewal and differentiation, barcode abundance, chromosome abnormalities and tumour-like growth.

**Support:** gated TERT maintains normal renewal without increasing challenge-clone expansion; the switch removes target cells without collapsing healthy organoids. **Falsify:** abnormal clones expand, ALT escapes, the switch fails, or renewal is substantially impaired. Even a clean result is not proof of zero human cancer risk.

## 2. Somatic DNA mutations

### Problem and architecture

**[Contradicted as written]** “Every cell division introduces a fixed mutation” is too absolute: polymerase proofreading and mismatch repair correct many copying errors (Manhart & Alani, 2017, *PNAS*, [DOI](https://doi.org/10.1073/pnas.1705971114)). **[Established]** Mutations nevertheless accumulate in human tissues. One study found about 40 new mutations per year in sampled adult stem-cell populations from selected tissues; rates are tissue-specific (Blokzijl et al., 2016, *Nature*, [DOI](https://doi.org/10.1038/nature19768)). Mutations also accumulate in post-mitotic human neurons, and some mutational processes can occur independently of division (Lodato et al., 2018, *Science*, [DOI](https://doi.org/10.1126/science.aao4426); 2024, *PLOS Biology*, [DOI](https://doi.org/10.1371/journal.pbio.3002678)). Mutation count is not equivalent to functional decline: some variants are neutral, while some can affect function or give a clone a growth advantage (Martincorena et al., 2015, *Science*, [DOI](https://doi.org/10.1126/science.aaa6806)).

**[Speculative]** Build a *reference-and-renewal system* rather than attempting to edit every cell:

1. In early adulthood, bank multiple aliquots of a person’s stem/progenitor cells and sequence them as a tissue-specific reference. Independent aliquots reduce dependence on a single sample.
2. Later, use error-corrected sequencing to identify concerning variants and clonal expansion. Duplex Sequencing improves detection of rare variants by comparing both DNA strands; it does not repair them (Schmitt et al., 2012, *PNAS*, [DOI](https://doi.org/10.1073/pnas.1208715109)).
3. Prefer selecting and replacing a risky lineage from a screened reserve when tissue turnover permits. Use targeted editing only for verified variants with a reliable reference; prime editing has demonstrated varied targeted changes in human cells, not whole-body correction (Anzalone et al., 2019, *Nature*, [DOI](https://doi.org/10.1038/s41586-019-1711-4)).
4. Do not correct every neutral mutation. Correct only changes with demonstrated or well-supported functional consequences.

### Readiness and minimum viable experiment

**[Established]** Sequencing and targeted editing are research tools; a system that surveys and repairs every human cell does not exist. **[Speculative]** Test the reference-and-renewal principle in intestinal organoids from several donors. Preserve early-passage aliquots; compare continuously passaged lines with lines refreshed periodically from the archive, lines refreshed after sequence-based selection, and a small targeted-editing arm for a predefined functional variant. Over serial passages, measure duplex-sequencing variants, broader genomic and chromosome integrity, organoid formation, differentiation and tissue-specific function.

**Support:** refreshing reduces concerning clone burden and restores function toward baseline without new genomic instability. **Falsify:** archived cells lose function after thawing and expansion, refreshing fails to restore tissue function, or editing introduces consequential collateral changes. This model cannot establish centuries-long archive integrity, reconstruct a cell’s epigenetic history, or directly solve mutation repair in every neuron.

## 3. Neurons, memory and identity

### Problem and architecture

**[Established, with uncertainty]** Many mature neurons do not divide. Rodent experiments show that memory-associated “engram” neurons have specific synaptic changes and connectivity related to recall, but do not prove that memory or identity is encoded only in synapses (Ryan et al., 2015, *Science*, [DOI](https://doi.org/10.1126/science.aaa5542)). The amount of adult human hippocampal neurogenesis remains disputed: studies reported both very low/undetectable levels and persistence into older age (Sorrells et al., 2018, *Nature*, [DOI](https://doi.org/10.1038/nature25975); Boldrini et al., 2018, *Cell Stem Cell*, [DOI](https://doi.org/10.1016/j.stem.2018.03.015)).

**[Plausible]** The identity-preserving priority is repair *in place*: maintain neuronal proteostasis, mitochondria and supporting glial, vascular and myelin environments. **[Speculative]** Brief, cell-targeted epigenetic rejuvenation could be tested in existing neurons, with expression shut off before loss of neuronal identity. OSK treatment improved visual function in mice in one study; a 2026 mouse study reported memory improvement after OSK was targeted to engram neurons. Neither establishes lifelong safety, human efficacy or preservation of personal identity (Lu et al., 2020, *Nature*, [DOI](https://doi.org/10.1038/s41586-020-2975-4); Berdugo-Vega et al., 2026, *Neuron*, [DOI](https://doi.org/10.1016/j.neuron.2025.11.028)).

If a neuron cannot be rescued, an exploratory fallback is “overlap-and-transfer”: integrate a replacement while the original remains, use activity-dependent plasticity to tune it, and test its contribution before removing the original. **[Speculative]** This may preserve some circuit functions; it cannot promise exact reconstruction of the original neuron’s state. Recent mouse connectomics covers limited tissue volumes, not a complete living human brain (MICrONS-related work, 2025, *Nature*, [article](https://www.nature.com/articles/s41586-025-08840-3)).

### Minimum viable experiment

**[Speculative]** Independently test engram-targeted OSK in aged mice using a memory task with context discrimination. Compare engram-targeted OSK, targeting vector without OSK, OSK in non-engram cells and a young reference group. Measure recall and memory specificity, locomotion and sensory controls, reactivation of tagged cells, neuronal identity and synaptic structure; follow animals for abnormal growth.

**Support:** recall and context discrimination improve without loss of neuronal identity or memory specificity. **Falsify:** no improvement versus controls, worsened memory specificity, loss of identity or unsafe growth. A behavioural improvement alone is insufficient evidence that a person’s identity would be preserved.

## 4. Integrated system and roadmap

**[Speculative]** The modules fit together as selective maintenance: screened cell reserves support renewal; telomere maintenance is restricted to screened renewing lineages; neurons are preserved in place wherever possible. This may reduce the need to make every cell divide indefinitely. Conflicts remain: telomerase could help a mutation-bearing clone persist; editing or reprogramming could create new errors; and neuronal replacement could preserve a task while altering the original circuit state. AI could prioritize measurements, but it cannot certify that every cell or failure mode has been observed.

- **2026–2036 — [Speculative].** Test gated TERT, mutation surveillance and neuronal rejuvenation in organoids/animals; proceed only without malignant escape, genomic instability or memory loss.
- **2036–2076 — [Speculative].** Conditional organ-specific clinical studies with long-term follow-up, not whole-body immortality claims.
- **2076 onward — [Speculative].** Combine only after independent safety/function evidence; decades of follow-up cannot prove infinite maintenance.

## 5. Feasibility and forecasts

**[Speculative forecast]** These are subjective central estimates with 90% uncertainty ranges, not statistical confidence intervals. “Working solution” means a credible human-grade platform that makes a barrier no longer a dominant age-related failure mechanism; it does not mean proof of infinite life. If success instead means a guarantee of zero endogenous failure forever, these practical estimates do not apply.

| Barrier | Verdict | By 2100 | By 2200 | Ever, under known physics |
|---|---|---:|---:|---:|
| Cancer–telomere control | Possibly solvable for substantial risk reduction; zero-risk guarantee not established | 8% (1–20%) | 25% (5–50%) | 40% (10–75%) |
| Somatic mutation burden | Possibly solvable for functionally important mutations; perfect correction unlikely | 4% (0–10%) | 15% (2–35%) | 30% (5–65%) |
| Neuronal continuity | Unlikely under exact identity requirements; preservation in place is more plausible | 2% (0–8%) | 10% (1–30%) | 25% (3–60%) |
| Integrated strict goal | Unlikely; solving components does not prove immortality | 0.5% (0–3%) | 4% (0.5–15%) | 12% (1–40%) |

## 6. Simulation results and thought experiments

The reproducible simulations are toy models, not biological forecasts. Full assumptions, code and CSVs are in [`outputs/results.md`](outputs/results.md) and this folder. Fixed seed: `20261003`.

### Residual-risk model

**[Established mathematics; hypothetical rates]** For a constant residual event rate λ, no-event probability is exp(−λT). The following rates are illustrative, not estimates of cancer or human failure risk.

| Hypothetical λ/year | 100 years | 500 years | 1,000 years |
|---:|---:|---:|---:|
| 10⁻⁶ | 99.990% | 99.950% | 99.900% |
| 10⁻⁵ | 99.900% | 99.501% | 99.005% |
| 10⁻⁴ | 99.005% | 95.123% | 90.484% |
| 10⁻³ | 90.484% | 60.653% | 36.788% |

**[Speculative thought experiment]** For one independent screening round, the probability of detecting every one of N clones is sᴺ, where s is hypothetical per-clone sensitivity. At N=1,000, 99.99% sensitivity yields a 90.5% chance of no miss; 99% yields about 0.004%. Real clone counts and detection sensitivities are not estimated here, and shared sensor blind spots would worsen performance.

With three independent failure channels each at a hypothetical 10⁻⁴/year, the no-event probability is 97.0% over 100 years and 74.1% over 1,000 years. Independence and constant rates are simplifications.

### Mutation-refresh model

**[Speculative model]** The simulation adds 40 mutation-count units per lineage-year to 500 lineages over 100 years, then assumes an ideally clean archive that resets each lineage at the chosen interval. It does not classify mutations as harmful.

| Ideal archive refresh | Mean current count across lineage-years | Mean at year 100 | 95th percentile at year 100 |
|---:|---:|---:|---:|
| Never | 2,021 | 4,002 | 4,115 |
| Every 50 years | 1,020 | 1,998 | 2,065 |
| Every 10 years | 220 | 400 | 436 |
| Every year | 40 | 41 | 51 |

**Interpretation:** ideal resets cap the count present in a lineage, but do not prove restored function. Archive contamination, epigenetic drift and the possibility of an incorrect reference are omitted; this is an optimistic bound.

### Neuronal-state transfer model

**[Speculative thought experiment]** A toy circuit contains 10,000 abstract state variables, each with an illustrative 10⁻⁵ annual chance of change. This is not a claim that one synapse stores one bit. After 100 years, expected fraction of original states retained:

| Strategy | Fraction retained |
|---|---:|
| No maintenance | 99.900% |
| In-place repair with 99% success, assuming state is recoverable | 99.999% |
| Replacement every decade, 99% mapping fidelity per state | 90.348% |
| Replacement every decade, 99.9% mapping fidelity | 98.906% |
| Replacement every decade, 99.99% mapping fidelity | 99.800% |

**Interpretation:** repeated imperfect copying compounds, while repair in place avoids a full remapping step in this deliberately simplified model. Actual brains have distributed representations and plasticity, which this model omits; it says nothing quantitative about human memory or identity.

## 7. Maximum lifespan: what research and these simulations can say

**[Established]** Jeanne Calment’s verified record is 122 years, 164 days; it is not a proven biological ceiling ([Guinness](https://www.guinnessworldrecords.com/world-records/oldest-person)). **[Contested]** Dong et al. argued that extreme-age survival gains had stalled ([2016, *Nature*](https://doi.org/10.1038/nature19793)); Barbi et al. found mortality approximately level after 105 in 3,836 documented Italian cases ([2018, *Science*](https://doi.org/10.1126/science.aat3119)). A mortality plateau is not immortality.

**[Speculative forecasts, not bounds]** Pearce and Raftery estimated >99% probability of breaking the record by 2100, with 89%, 44% and 13% probabilities of someone reaching at least 126, 128 and 130, respectively ([2021](https://doi.org/10.4054/demres.2021.44.52)). Pyrkov et al. extrapolated a loss of physiological resilience at 120–150 years from biomarkers; this is not an observed or settled limit ([2021](https://doi.org/10.1038/s41467-021-23014-1)).

**[Established] Conclusion:** no consensus establishes a maximum possible lifespan. Our simulations do **not** estimate one: they use hypothetical hazards, mutation counts and abstract neural-state errors, not age-specific human mortality data.

## 8. Pre-mortem: ten plausible failure modes

**[Speculative]** Failure modes: (1) TERT lets an undetected clone expand; (2) ALT evades surveillance; (3) safety switches miss targets or kill healthy cells; (4) archive mosaicism; (5) editing causes collateral damage; (6) epigenetic drift; (7) failed tissue integration; (8) neuronal treatment alters memory or identity; (9) late detection; or (10) monitoring, supply or governance failure.

## 9. Ethics and governance

**[Plausible governance proposals]** Neural interventions need revisable consent, advance directives and stopping rules; better behavioural scores do not prove identity preservation. Require independent review, adverse-event reporting and long-term follow-up before systemic trials; prohibit pay-to-play unvalidated interventions. Plan for unequal access and resource demand without coercive population policies, and keep somatic maintenance distinct from germline modification.

## 10. Open questions and falsifiable predictions

- **[Open question]** Can surveillance eliminate abnormal clones before they gain a clinically meaningful advantage, including ALT clones?
- **[Open question]** Which accumulating mutations actually impair tissue function, rather than simply marking lineage history?
- **[Open question]** Can neuronal epigenetic rejuvenation preserve memory specificity and neuronal identity over long follow-up?
- **[Falsifiable prediction]** In serially passaged organoids, refreshing from screened ancestral cells will lower concerning clone burden and restore function versus no refresh. Failure to restore function weakens the archive strategy.
- **[Falsifiable prediction]** Engram-targeted OSK will improve aged-mouse memory without loss of specificity or neuronal identity; failure on either criterion is a no-go.
- **[Falsifiable prediction]** Gated TERT will preserve normal renewal without increasing abnormal-clone expansion; reproducible clone escape falsifies the proposed safety architecture.

## Compact evidence table

| Major claim | Label | Principal sources |
|---|---|---|
| Most cancers use telomerase; a minority use ALT | [Established] | Shay & Bacchetti, 1997, *Eur. J. Cancer*, [DOI](https://doi.org/10.1016/S0959-8049(97)00062-2); Mori et al., 2024, *J. Clin. Pathol.*, [DOI](https://doi.org/10.1136/jcp-2023-209005) |
| TERT effects on cancer risk are context-dependent; aging work is preclinical | [Established] | González-Suárez et al., 2001, *EMBO J.*, [DOI](https://doi.org/10.1093/emboj/20.11.2619); Bernardes de Jesus et al., 2012, *EMBO Mol. Med.*, [DOI](https://doi.org/10.1002/emmm.201200245); Shim et al., 2024, *Cell*, [DOI](https://doi.org/10.1016/j.cell.2024.05.048) |
| Early human telomere extension evidence is disease-specific and very small | [Established] | Myers et al., 2025, *NEJM Evidence*, [DOI](https://doi.org/10.1056/EVIDoa2400252) |
| Inducible apoptosis can act as a safety switch in engineered T-cell therapy | [Established] | Di Stasi et al., 2011, *NEJM*, [DOI](https://doi.org/10.1056/NEJMoa1106152) |
| Human stem-cell mutations accumulate with age; tissue rates vary | [Established] | Blokzijl et al., 2016, *Nature*, [DOI](https://doi.org/10.1038/nature19768) |
| Post-mitotic neurons accumulate mutations | [Established] | Lodato et al., 2018, *Science*, [DOI](https://doi.org/10.1126/science.aao4426) |
| Duplex sequencing and prime editing are useful but limited tools | [Established] | Schmitt et al., 2012, *PNAS*, [DOI](https://doi.org/10.1073/pnas.1208715109); Anzalone et al., 2019, *Nature*, [DOI](https://doi.org/10.1038/s41586-019-1711-4) |
| Memory-related engram connectivity and human neurogenesis uncertainty | [Established] | Ryan et al., 2015, *Science*, [DOI](https://doi.org/10.1126/science.aaa5542); Sorrells et al., 2018, *Nature*, [DOI](https://doi.org/10.1038/nature25975); Boldrini et al., 2018, *Cell Stem Cell*, [DOI](https://doi.org/10.1016/j.stem.2018.03.015) |
| Partial reprogramming improves selected mouse neural outcomes, not proven human identity preservation | [Established] | Lu et al., 2020, *Nature*, [DOI](https://doi.org/10.1038/s41586-020-2975-4); Berdugo-Vega et al., 2026, *Neuron*, [DOI](https://doi.org/10.1016/j.neuron.2025.11.028) |
| A functional mouse cortical connectome has only been mapped at limited tissue scale | [Established] | MICrONS-related study, 2025, *Nature*, [article](https://www.nature.com/articles/s41586-025-08840-3) |
| Some age-associated mutation processes can occur independent of cell division | [Established] | 2024, *PLOS Biology*, [DOI](https://doi.org/10.1371/journal.pbio.3002678) |

## Bottom line

**[Established]** No current evidence shows that indefinite biological immortality is achievable in humans. **[Plausible]** A path to substantially longer healthspan could combine carefully controlled cell renewal, mutation surveillance and neuronal repair in place. The most critical breakthrough is a safe, repeatable way to preserve or rejuvenate memory-bearing neurons without losing their functional state—while simultaneously keeping cancer and genomic error rates extremely low. Literal zero risk forever remains unsupported and may be incompatible with any system that retains a nonzero residual failure rate.
