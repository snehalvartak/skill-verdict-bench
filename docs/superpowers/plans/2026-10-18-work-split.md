# Work split: local agent and cloud agent

Date: 2026-10-18. Two Claude sessions work on this repo at once. The local session has Ollama, `clef-flash` and the `runs/` directories. The cloud session has GitHub and a clone of [SkillScreen](https://github.com/JerroldH/SkillScreen), but no model. Each side changes only the files it owns, and both merge through PRs.

## Who owns which files

| Local (needs the model or run dirs) | Cloud (no model needed) |
|---|---|
| `svb/run.py`, `svb/score.py`, `svb/heldout.py`, `svb/compare.py`, `svb/methods.py`, `svb/checks.py` | `svb/data.py`, `svb/skillscreen.py` |
| `docs/experiments/003-*`, `004-*` and later | README "Related work" section, this file |
| Everything under `runs/` | Reviewing local PRs, write-ups drafted from pasted results |

If a change needs a file the other side owns, say so in the PR description and keep the edit small.

## Local agent

1. **Finish experiment 003.** If the pre-registration is not committed yet, consider these changes. If it is, add them as labelled exploratory analyses.
   - Sample benign skills more heavily in the test part, or make it larger. AUC, TPR and FPR do not depend on class balance, and 46 benign skills cannot resolve a +0.03 AUC difference.
   - Besides Youden's J, choose two more thresholds on validation: TPR ≥ 0.95, and FPR ≤ 0.05. Report test TPR and FPR at each. These match SkillScreen's high-recall framing and the second-stage use.
   - Fix the logistic regression before scoring: logit-transformed and standardised features, the L2 strength, the steps and the threshold tie-break.
   - Choose one rule for missing test scores: drop them from AUC and count them, or count them as flagged (SkillScreen's rule).
   - Record `--exclude` in `config.json` only when it is used. Old configs then still pass the resume check.
2. **After pulling the cloud PR,** run `uv run python -m svb.data verify` and record in the 003 write-up which dataset revision runs 001 to 003 used. Downloads are now pinned to `d4b42ce`, the revision SkillScreen uses. Files already cached are not re-checked, so running experiments are unaffected.
3. **SkillHarm probe, exp 004a, about an hour.** This decides which paper to write. On the source-disjoint test set, zero-shot TypeSafe catches 0 of 728 SkillHarm skills and SkillScreen flags all 90 SkillFortifyBench benign skills.
   - Add a `--ids FILE` option to `svb.run` that restricts the loaded part to the listed IDs, like `--exclude`.
   - Run:
     ```bash
     uv run python -m svb.skillscreen probe --skillscreen ../SkillScreen --out probe-ids.txt   # 100 SkillHarm + 90 SkillFortifyBench benign
     uv run python -m svb.run --split source_disjoint --part test --ids probe-ids.txt --methods ast10 naive-llm
     uv run python -m svb.skillscreen compare runs/<id> --method ast10 --skillscreen ../SkillScreen --protocol sd --threshold 0.1
     ```
   - Report AUROC on the probe set and the score distributions only. `--threshold` is required, but its recall and FPR columns mean nothing here; choose no threshold from the probe. Say in the write-up that this looked at test data.
4. **Experiment 004.** Fit on `m_structural_disjoint` and `source_disjoint` validation, then score SkillScreen's full test cohorts with `svb.skillscreen compare`. Batched `ast10` costs one call per skill; experiment 002 found batching does not change AUC. Use `ast10-split` only if 003 shows the learned combination helps.

## Cloud agent

1. PR: pin the dataset revision and check hashes (`svb.data verify`); add `svb.skillscreen` (SkillScreen's metric rules, CSV export, comparison and cascade against its released predictions, probe sample); add a README section on SkillScreen with citation and comparability.
2. Review each local PR as it lands, and watch CI.
3. Draft the 004 plan once 003's results are in, and write up results from the tables `svb.skillscreen compare` prints.
4. Keep the comparison page on SkillScreen up to date.

## Contract

- **Merging:** merge `main` into your branch before pushing, and keep PRs small.
- **Resume compatibility:** do not add keys to `config.json` that existing runs lack. If one is needed, write it only when the new option is used.
- **Licensing:** SkillScreen's predictions (CC BY 4.0) are read from a local clone and never committed here.
