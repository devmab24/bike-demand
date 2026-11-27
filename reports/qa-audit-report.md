# QA Audit Report — Bike Demand Investigation

**Auditor:** qa-auditor agent (independent)
**Date:** 2026-11-27
**Working directory:** `c:\Users\M.Faisal\Desktop\bike-demand-test\demo`
**Git branch:** master (8a729c5)

---

## 1. Scope

Full independent audit covering: repository structure, Python environment, dataset integrity, data loading, Context7 documentation gate, leakage prevention, chronological split, model training/evaluation, model artifact, inference contract, EDA deliverables, notebook structure, Streamlit application, tests, documentation, and git hygiene.

---

## 2. Methodology

1. Inspected all relevant files directly (no reliance on prior agent reports).
2. Executed commands independently and recorded exact outputs.
3. Verified SHA-256 checksum of raw dataset.
4. Loaded and queried model artifact to confirm inference.
5. Ran full pytest suite.
6. Compared FEATURE_ORDER in app against inference contract programmatically.
7. Inspected notebook Cell 4 for dataset loading correctness.

---

## 3. Commands Executed

```
ls demo/                                           # repo structure
ls demo/.claude/agents/                            # agent definitions
uv run python --version                            # Python version
Get-FileHash data/raw/hour.csv -Algorithm SHA256   # dataset checksum
uv run python -c "... pd.read_csv; df.shape ..."   # dataset shape/columns
uv run python -c "from src.data_pipeline.load import load_hour_csv; ..."  # data loading
uv run python -c "import joblib; p=joblib.load(...); ..."  # artifact steps
uv run python -c "... chronological_split ..."     # split verification
uv run python -m pytest tests/ -v --tb=short       # full test suite
git status && git log --oneline -5                 # git hygiene
```

---

## 4. Check Results

| ID | Check | Verdict | Evidence |
|----|-------|---------|----------|
| A1 | Required directories exist | PASS | All 10 required dirs confirmed: data/raw/, src/data_pipeline/, src/data_analysis/, src/modelling/, app/, notebooks/, modelling/artifacts/, artifacts/, reports/, tests/ |
| A2 | 11 agent definitions present | PASS | All 11 .md files in .claude/agents/: colab-notebook-engineer, data-scientist, documentation-researcher, git-supervisor, inference-ui-builder, ml-engineer, project-setup, qa-auditor, repository-architect, research-agent, ui-launcher |
| B1 | .python-version pins 3.12 | PASS | File contains "3.12" |
| B2 | pyproject.toml has required deps | PASS | numpy, pandas, scikit-learn, matplotlib, seaborn, joblib in dependencies; streamlit in optional-dependencies.ui; pytest in dev group. Note: scipy==1.15.3 also present (not prohibited, appears to be pinned transitive dep) |
| B3 | uv.lock present | PASS | File exists |
| B4 | Python 3.12 confirmed | PASS | `uv run python --version` → Python 3.12.16 |
| C1 | data/raw/hour.csv present | PASS | File exists |
| C2 | SHA-256 checksum | PASS | E03DE4EE4EF4DC376AC6E04BF829673C6269E8EBA5C60FA121640FA2F829504F matches expected (case-insensitive) |
| C3 | Row/column count | PASS | (17379, 17) confirmed |
| C4 | Required columns present | PASS | All 17 required columns present |
| D1 | load_hour_csv loads correctly | PASS | Returns (17379, 17) |
| E1 | context7-docs-evidence.json present | PASS | File present |
| E2 | Status "verified" | PASS | Top-level "status": "verified" |
| E3 | At least 5 libraries listed | PASS | 9 libraries listed: pandas, numpy, scikit-learn, matplotlib, seaborn, scikit-learn (run2), joblib, pytest, streamlit |
| F1 | FEATURE_COLS excludes leakage columns | PASS | FEATURE_COLS = [season, yr, mnth, hr, holiday, weekday, workingday, weathersit, temp, atemp, hum, windspeed] — cnt/casual/registered/instant absent |
| F2 | EXCLUDED_COLS includes all four | PASS | EXCLUDED_COLS = ("cnt", "casual", "registered", "instant", "dteday") |
| G1 | Chronological split uses instant sort | PASS | df.sort_values("instant").reset_index(drop=True) — no shuffle |
| G2 | No shuffle in split | PASS | Uses iloc slice only; no shuffle parameter |
| H1 | metrics.json present and readable | PASS | File present and parses correctly |
| H2 | RF R² > 0.85 | PASS | R² = 0.9003 |
| H3 | RF MAE < Baseline MAE | PASS | RF MAE = 45.02 vs Baseline MAE = 174.98 |
| H4 | Train+test sizes sum to 17,379 | PASS | 13903 + 3476 = 17379 |
| I1 | pipeline.joblib present | PASS | File exists at modelling/artifacts/pipeline.joblib |
| I2 | Artifact loads and has correct steps | PASS | steps: ['preprocessor', 'model'] |
| J1 | inference-contract.json present | PASS | File present |
| J2 | feature_names has exactly 12 entries | PASS | 12 features: season through windspeed |
| J3 | No leakage columns in feature_names | PASS | cnt/casual/registered/instant absent |
| K1 | eda-findings.md present | PASS | File present in reports/ |
| K2 | reports/figures/ has PNG files | PASS | 6 PNGs: 01_target_distribution.png through 06_demand_workingday_vs_weekend.png |
| K3 | src/data_analysis/eda.py present | PASS | File present |
| L1 | Notebook Cell 4 — no archive.ics.uci.edu | PASS | No reference to archive.ics.uci.edu in cell 4 |
| L2 | EXPECTED_SHA256 correct | PASS | 'e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f' present |
| L3 | _verify_csv_bytes function present | PASS | Function defined and verifies SHA-256 + shape + schema |
| L4 | files.upload() present (Colab path) | PASS | from google.colab import files; files.upload() present |
| L5 | Local path detection present | PASS | _local_candidates logic handles repo root and notebooks/ subdirectory |
| M1 | Notebook has at least 30 cells | PASS | 37 cells |
| M2 | Notebook covers required topics | PASS | Cells cover: imports (2,3), data loading (4), EDA (7-18), feature selection (20), baseline (22), random forest (24-25), evaluation (26-33), conclusions (34-36) |
| N1 | app/app.py present | PASS | File present |
| N2 | FEATURE_ORDER matches contract | PASS | Programmatic comparison: exact match — ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed'] |
| N3 | validate_inputs() present | PASS | Function defined with int_ranges and float_ranges validation |
| N4 | load_pipeline() uses correct path | PASS | PIPELINE_PATH = Path(__file__).resolve().parent.parent / "modelling" / "artifacts" / "pipeline.joblib" |
| N5 | Inference produces correct output | PASS | Contract example (season=3,hr=17,...) → 820.52, matches contract expected value exactly |
| O1 | All tests pass | PASS | 39/39 passed in 4.40s |
| P1 | README.md present | PASS | File present |
| P2 | repository-architecture.md present | PASS | File present in reports/ |
| P3 | inference-contract.json present | PASS | Already confirmed in J1 |
| Q1 | Working tree clean | PASS WITH NOTE | Tracked files are clean; one untracked file: reports/final-run-report.md (not staged, not committed) |
| Q2 | Notebook fix commit present | PASS | 8a729c5 fix(notebook): use canonical dataset with SHA-256 verification is in log |

---

## 5. Findings

### Finding QA-001 (Low) — Untracked file in working tree

- **File:** `reports/final-run-report.md`
- **Description:** `git status` shows one untracked file. No tracked file is modified or staged. This is cosmetically unclean but does not affect reproducibility or core functionality.
- **Impact:** Low. The file is a report artifact, not implementation code. The working tree is otherwise clean.
- **Expected:** No untracked files.
- **Actual:** One untracked file: `reports/final-run-report.md`.
- **Recommendation:** Stage and commit the file or add it to .gitignore if it is intentionally excluded.

### Finding QA-002 (Low) — scipy not in CLAUDE.md required deps list

- **File:** `pyproject.toml`
- **Description:** `scipy==1.15.3` is listed as a dependency but is not in the CLAUDE.md "Required dependencies" list. It appears to be a pinned transitive dependency of scikit-learn or seaborn.
- **Impact:** Low. It is not a prohibited package. The environment is functional. This is an undocumented direct pin.
- **Recommendation:** Confirm whether scipy is a direct dependency or should be left as an implicit transitive dep. If the latter, it can be removed from the direct dependencies list in pyproject.toml.

### Finding QA-003 (Low) — Branch not pushed to remote

- **File:** N/A
- **Description:** `git status` reports "Your branch is ahead of 'origin/master' by 1 commit." The notebook-fix commit (8a729c5) has not been pushed to remote.
- **Impact:** Low. Local functionality is unaffected.
- **Recommendation:** Push the branch to remote when ready.

---

## 6. Unverified Items

- **UI rendering in browser:** Streamlit app was not launched in a live browser session. App file, path resolution, feature ordering, validation logic, error handling, and pipeline integration were all verified statically and via the test suite (39 tests all pass, including test_inference.py). Live browser rendering is not feasible in a non-interactive CLI audit session.
- **Colab execution:** Notebook was not executed in Google Colab. Cell-by-cell logic was reviewed statically. The SHA-256 verification and upload path were confirmed correct against the canonical dataset.

---

## 7. Summary

All 17 required checks spanning repository structure, environment, dataset integrity, data loading, documentation gate, leakage prevention, chronological split, model quality, artifact, inference contract, EDA, notebook, Streamlit app, tests, and documentation return **PASS**. Three low-severity findings were identified (untracked file, undocumented scipy pin, unpushed commit). No critical or high-severity issues were found.

---

## FINAL VERDICT: PASS
