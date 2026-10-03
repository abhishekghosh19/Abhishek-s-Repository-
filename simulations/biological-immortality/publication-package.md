# Preprint and journal-submission preparation package

## Current status

**Not submitted; not peer reviewed; no external preprint DOI has been issued.** The report is merged into the public GitHub repository. The Pages workflow is also merged, but the site is not live: the first deployment failed because Pages has not been enabled for the repository. A repository owner must select **Settings → Pages → Build and deployment → Source: GitHub Actions** and then rerun the Pages workflow. The repository license is CC0 1.0; the responsible human author should confirm that the public-domain dedication fits the intended deposit and any journal's terms.

The manuscript is best framed as a **Perspective / research synthesis**, not as original experimental research. It is not a systematic review: the report does not document a reproducible database search, screening protocol or risk-of-bias assessment. Its simulations are illustrative toy models, not validated biological or demographic forecasts. The public version must be disclosed to any repository or journal, and the target venue's preprint/previous-dissemination policy must be checked.

## Proposed title

**Can Human Biological Function Be Maintained Indefinitely? A Systems Perspective on Cancer Risk, Somatic Mutation, Neural Continuity, and Longevity Limits**

## Draft abstract

Biological immortality, defined here as indefinite preservation of the same biological brain without irreversible age-related functional decline, is considered as a systems-maintenance problem. This narrative synthesis reviews three barriers: cancer risk during telomere-supported renewal, somatic mutation accumulation, and preservation of neuronal function and identity. It proposes conditional renewal, reference-guided lineage replacement, and neuronal repair in place as research directions, with organoid and animal experiments designed to include explicit support and falsification criteria. Standard-library simulations illustrate the compounding of hypothetical residual hazards, idealized mutation-count resets, and repeated imperfect neural-state transfer. These simulations are not calibrated to human survival, mutation impact, cognition, or identity. No currently demonstrated intervention achieves strict biological immortality, and no consensus hard maximum lifespan is established. Jeanne Calment’s verified record is 122 years and 164 days; demographic forecasts of possible 126–130-year records this century are conditional population projections, not physiological limits. The report distinguishes observed evidence from plausible mechanisms, speculation, and unresolved questions.

## Keywords

Aging; longevity; telomeres; somatic mutation; cancer; neuronal maintenance; healthspan; biological immortality.

## Manuscript source and supplementary material

- **Canonical manuscript/report:** [`report.md`](report.md). This is the single source of truth; it includes inline DOI/source links, evidence labels, methods proposals, limitations, and conclusions.
- **Code and synthetic outputs:** [`simulate.py`](simulate.py), [`outputs/results.md`](outputs/results.md), and the CSV files in [`outputs/`](outputs/).
- **Reproducibility note:** Python standard library; seed `20261003`. The toy models are not fitted to human lifespan data.

## Author and declarations — complete and verify before deposit

- **Author name(s), order, affiliations, and corresponding author:** `[human author(s) to supply and approve]`
- **ORCID and contact details:** `[author to supply directly to the selected platform; do not publish private email in this repository]`
- **Authorship responsibility:** a human author must review the complete text, independently verify claims and references, approve the final version, and accept responsibility for it. Disclose AI assistance according to the selected repository and journal policies.
- **Funding:** `[author to verify; state funding or no external funding as appropriate]`
- **Competing interests:** `[author to verify and declare]`
- **Acknowledgments:** `[author to complete, if applicable]`
- **Ethics:** the report analyzes published literature and synthetic toy-model outputs; proposed future organoid/mouse experiments were not conducted here. Confirm the selected venue's required statement.
- **Data availability:** no new empirical participant or animal data are reported. Simulation code and generated synthetic outputs are in the public repository linked above.
- **Prior dissemination:** disclose the public GitHub report and Pages edition. Whether this qualifies as a preprint or affects eligibility is venue-specific.

## Draft cover letter (venue and author fields intentionally left open)

Dear Editor,

Please consider the accompanying Perspective, “Can Human Biological Function Be Maintained Indefinitely? A Systems Perspective on Cancer Risk, Somatic Mutation, Neural Continuity, and Longevity Limits,” for consideration at **[journal]**. It presents a source-linked narrative synthesis of three interdependent maintenance challenges, proposes falsifiable experiments, and clearly separates established evidence from speculative mechanisms and forecasts. The included simulations are explicitly illustrative and are not presented as clinical evidence or validated lifespan predictions.

A public version of the report and its code are available at **[GitHub repository / Pages URL]**. We will follow the journal's policy for preprints and prior public dissemination and will provide any required disclosure. **[Before sending, confirm the manuscript is not under review elsewhere and complete all journal-specific declarations.]**

Sincerely,

**[Corresponding human author, affiliation, contact details]**

## Remaining steps before any external submission

1. A human author supplies author order, affiliations, ORCID/contact details, funding, conflicts and acknowledgments, and verifies every reference and factual statement.
2. Select the preprint repository and target journal; verify current scope, manuscript category, word/reference limits, AI-use rules, license, and preprint/previous-publication policy.
3. Format the manuscript and bibliography to the selected venue. Current in-text links are not a substitute for a journal-formatted reference list.
4. Obtain the human author's approval of the final files and declarations. Only then deposit or submit using that author's own account; no external submission has been made by this agent.
