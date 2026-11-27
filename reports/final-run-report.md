# Final Run Report: GitHub-to-Local Reproducibility Test (Run 3)

**Execution date:** 2026-11-27
**Lead Agent:** Claude Sonnet 5.5 (Claude Code)
**Run type:** Fresh session. The local project was intentionally cleaned and then recovered from GitHub. The retained `.venv`, dataset and agent architecture were reused, and nothing was downloaded.

> This report replaces the previous run's report, which is still available in git history (commit `c016a4a`).

---

## A. Run identity

| Item | Value |
|---|---|
| GitHub repository | https://github.com/devmab24/bike-demand.git (`origin`) |
| Synchronized branch | `master` |
| Initial synchronized commit | `f6147930f42b1f3546e17942704f23ead21bd160` (= `origin/master`, 0 ahead / 0 behind) |
| Working branch for corrections | `fix/run3-reproducibility-corrections` (local only, **not pushed**) |
| Correction commits | `5b5c514` (docs and notebook corrections C1–C5); `7add08b` (notebook SHA-256 fix M-1, README m-2) |
| Final commit | This report is committed on the same branch in a follow-up commit (see section I) |

---

## B. Agent execution register

| Agent | Invoked (phase) | Verdict | Files changed | Report received |
|---|---|---|---|---|
| git-supervisor | Phase 0 sync; Phase 6 review ×2 and commits | PASS (sync, with CRLF warning); READY ×2 | none (restored 46 deleted tracked files; created 2 authorized commits) | Yes |
| repository-architect | Phase 1 inspection; correction C2 | PASS WITH FINDINGS | `reports/repository-architecture.md` (C2) | Yes |
| project-setup | Phase 1 environment and dataset; C1, m-2 | PASS WITH FINDINGS | `README.md` (C1, m-2) | Yes |
| research-agent | Phase 1 research verification | PASS WITH FINDINGS | none | Yes |
| documentation-researcher | Phase 1 Context7 evidence | PASS WITH FINDINGS | none | Yes |
| data-scientist | Phase 2 EDA reproduction; C3 | PASS WITH FINDINGS | `reports/eda-findings.md` (C3) | Yes |
| ml-engineer | Phase 3 ML reproduction; C4 | PASS WITH FINDINGS | `reports/ml-results.md` (C4) | Yes |
| colab-notebook-engineer | Phase 4 notebook; C5, M-1 | PASS WITH FINDINGS (Colab not executed) | `notebooks/bike_demand_investigation.ipynb` (C5, M-1) | Yes |
| inference-ui-builder | Phase 5 app verification | PASS WITH FINDINGS | none | Yes |
| qa-auditor | Phase 7 audit; re-audit | **FAIL** → **PASS WITH LIMITATIONS** | none | Yes |
| ui-launcher | Phase 8 launch | LAUNCHED, REACHABLE LOCALLY | none | Yes |

Regenerated outputs are not counted as changes. Running EDA and training rewrote the tracked outputs, but every one was byte-identical to HEAD (see section F).

---

## C. Repository recovery

- The cleanup left 46 tracked files deleted (` D`), with no other modified or untracked files.
- Restore command: `git ls-files -d -z | xargs -0 git restore --source=HEAD --`. Afterwards `git ls-files -d` was empty.
- `git fetch origin` ran. `git rev-list --left-right --count master...origin/master` gave `0 0`, so no merge was needed.
- `HEAD` = `origin/master` = `f6147930…`.
- No `reset --hard`, `clean`, force-push or history rewrite was used.
- **Warning (non-blocking):**
  - After the restore, `git status` lists files as ` M` purely because of line endings: 28 files initially, 24 after the correction commits.
  - Cause: `core.autocrlf=true` in the system gitconfig and no `.gitattributes` file, so git writes LF blobs to disk as CRLF.
  - Evidence that content is unchanged:
    - `git diff --quiet` exits 0.
    - `git diff --ignore-cr-at-eol` is empty.
    - `git hash-object` equals `HEAD:<file>` for every checked file.

---

## D. Environment verification

| Item | Value |
|---|---|
| Python (`.venv/Scripts/python.exe`) | 3.12.16 (`.python-version` = 3.12) |
| uv | 0.13.7 |
| Interpreter used by `uv run --no-sync` | project `.venv` (verified `sys.executable`) |
| numpy / pandas / scikit-learn | 2.4.6 / 2.3.3 / 1.8.0 |
| matplotlib / seaborn / joblib | 3.11.2 / 0.13.2 / 1.6.0 |
| pytest (dev) / streamlit (ui extra) | 9.2.0 / 1.67.0 |
| Lock consistency | `uv lock --check --offline` → exit 0. `uv.lock` was byte-identical before and after (`cmp`). |

**No dependency downloads occurred.**
- Every Python invocation used `UV_OFFLINE=1 uv run --no-sync`.
- None of the following were run: `uv sync`, `uv add`, `uv lock` (other than the offline check), `pip`, conda, or cache clearing.
- The `.venv` was not recreated.
- Streamlit was already present in the retained `.venv` from an earlier authorized UI-extra installation.

---

## E. Dataset verification

| Item | Value |
|---|---|
| Canonical path | `data/raw/hour.csv` |
| Rows × columns | 17,379 × 17. Null cells: 0. Duplicate rows: 0. `cnt == casual + registered` on all rows. Dates 2011-01-01 to 2012-12-31. |
| SHA-256 of the committed (LF) file, the canonical value | `b03a2d02e8c10f435c43c7f0b358b7e34a003afea53dbc37f0183f2763295133` |
| SHA-256 of this Windows working copy (CRLF via autocrlf) | `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f` |
| Integrity outcome | PASS. No content difference from HEAD; the two hashes differ only in line endings (17,380 CR bytes). |

**Correction to earlier reports:** previous runs recorded `e03de4…504f` as the dataset hash. That value is only the CRLF form produced on this Windows machine. The file as stored on GitHub hashes to `b03a2d…3133`. See finding M-1 in section G.

---

## F. Reproduction results

### EDA (data-scientist)
- `uv run --no-sync python src/data_analysis/eda.py` exited 0.
- All 9 outputs are **byte-identical** to HEAD (the 3 CSVs in `artifacts/eda/` and figures `reports/figures/01–06`).
- The numbers in `eda-findings.md` reproduce:
  - Hourly peaks: 08:00 (359.0) and 17:00 (461.5).
  - Season means by code: 111.1, 208.3, 236.0, 198.9.
  - Weather means: 204.9, 175.2, 111.6, 74.3.
  - Correlation with `temp`: r = 0.405.

### Modelling (ml-engineer)
- `uv run --no-sync python src/modelling/train.py` exited 0 in 5.7 s.
- Split: chronological (sorted by `instant`, no shuffle), split index 13,903.
  - Train: 13,903 rows, 2011-01-01 to 2012-08-07.
  - Test: 3,476 rows, 2012-08-07 to 2012-12-31.
- Features: 12 predictors. Excluded: `cnt`, `casual`, `registered`, `instant`, `dteday`.
- `StandardScaler` is fitted on the training split only (scaler `mean_` equals the training means; `n_samples_seen_` = 13,903).

| Model | MAE | RMSE | R² | Reference (Run 2) | Difference |
|---|---:|---:|---:|---|---|
| Mean baseline (`DummyRegressor`) | 174.9846 | 232.6084 | −0.11300 | 174.98 / 232.61 / −0.11 | none |
| Random Forest (100 trees, seed 42) | 45.0211 | 69.6241 | 0.90028 | 45.02 / 69.62 / 0.90 | none |

- QA recomputed these metrics from the saved model, with both sklearn and manual formulas, and got identical values.
- The baseline's negative R² comes from demand growth: the training mean is 174.6 and the test mean is 248.8.
- Residual diagnostics (notebook only):
  - RF mean residual +16.46, std 67.65. This is a systematic under-prediction in late 2012.
  - Largest errors are at peak hours (17:00 MAE 104.3).

### Model artifact
- Path: `modelling/artifacts/pipeline.joblib`. It is gitignored and was regenerated in this run.
- SHA-256 `73ad7db16e4e5a4c473d145a5a2bdd35068fdf6389e7caad120fecdf9872a834`, 119,890,330 bytes.
- QA regenerated it in an isolated copy of the project and got a byte-identical file.
- This shows byte-level reproducibility on this machine and environment only. It is not a cross-platform guarantee.
- `modelling/metrics.json`, `artifacts/inference-contract.json` and both `modelling/figures/*.png` are byte-identical to HEAD.

### Inference contract
- The 12 `feature_names` match the pipeline's `feature_names_in_`, in the same order.
- Data types and value ranges match the data.
- The contract's example input predicts **820.52**, equal to the value stored in the contract.

### Notebook (colab-notebook-engineer)
- Format: nbformat 4.5, 37 cells (19 code), execution counts 1–19 in order.
- Dataset access:
  - Locally it uses a relative path; in Colab it uses `files.upload()`.
  - It never downloads data and has no fallback dataset.
  - A SHA-256 check stops the notebook on a mismatch.
- All code cells were executed **locally** in the project environment, with `%`/`!` lines skipped. The metrics match the values above exactly, and printed output matches the stored outputs.
- **Not executed in Google Colab** (no authenticated Colab runtime). See section G.

### Streamlit application (inference-ui-builder, ui-launcher)
- The app loads `modelling/artifacts/pipeline.joblib` via `@st.cache_resource` and accepts exactly the 12 contract features, with range checks.
- If the model file is missing, it shows a clear error and disables the Predict button.
- AppTest results:

| Input | Displayed |
|---|---|
| Contract example | "821 rentals / hour" |
| Minimum edge | "20 rentals / hour" |
| Maximum edge | "84 rentals / hour" |

- There were no exceptions. The live launch is in section H.

---

## G. QA results

**Final verdict: PASS WITH LIMITATIONS.** The first audit returned **FAIL**; after fix M-1, the re-audit of commit `7add08b` passed with limitations.

**Tests:** `UV_OFFLINE=1 uv run --no-sync pytest -v`: **39 collected, 39 passed, 0 failed, 0 skipped, 0 errors.**

| File | Tests |
|---|---:|
| `test_load.py` | 11 |
| `test_eda.py` | 5 |
| `test_ml.py` | 11 |
| `test_inference.py` | 12 |

### Resolved findings

**M-1 (Major): the notebook's SHA-256 check failed on the dataset as GitHub stores it.**
- The notebook hard-coded the CRLF hash `e03de4…`.
- Any LF copy failed with "SHA-256 mismatch". That includes Colab, Linux, macOS, GitHub raw downloads and Windows with `autocrlf=false`.
- Phases 0–6 missed this because every check used this machine's CRLF working copy.
- Fix (commit `7add08b`): hash the file after converting CRLF to LF, and expect the canonical LF hash `b03a2d…`.
- QA verified the fixed check against five inputs:

| Input | Result |
|---|---|
| LF file | passes |
| CRLF file | passes |
| Tampered LF file | rejected |
| Tampered CRLF file | rejected |
| Extra newline | rejected |

**m-2 (Minor): the README did not say how to rebuild the gitignored model.** Fixed by adding a "Reproducing the analysis and model" section.

### Open findings
These were not fixed. They are recommendations for the owners and the user.

| ID | Severity | Finding |
|---|---|---|
| m-1 | Minor | **Season labels.** Season code 1 covers about 21 Dec–20 Mar in the data, which is winter. The app, the EDA figure 03, the notebook, the contract and the reports label it "Spring", following the bundled `Readme.txt`. The live UCI page says 1 = winter. Numbers and predictions are unaffected; only the labels mislead. Fixing it needs one consistent decision across the project. |
| m-3 | Minor | Notebook cells 17 and 34 use causal-sounding wording ("suppresses demand"), although disclaimers follow. |
| m-4 | Minor | `.claude/agents/ui-launcher.md:32` and `ml-engineer.md:96` name `bike_demand_pipeline.joblib`. The correct file is `pipeline.joblib`, and the ui-launcher was briefed with it. `.claude/` was preserved unedited. |
| m-5 | Minor | Test gaps: the split test re-sorts the data itself; the leakage test is partial; `compute_metrics` has no unit test; app validation is duplicated in the tests rather than imported. |
| m-6 | Minor | The contract's `output_format.note` still says predictions may be negative, contradicting corrected C4/C5. It is generated by `train.py`, so fixing it needs a code change and contract regeneration. |
| m-7 | Minor | An old absolute local path containing a username is still in pushed git history. HEAD is clean; removing it from history would need a history rewrite, which was not authorized. |
| m-8 | Minor | The temp/atemp normalization constants differ between `Readme.txt` (÷41, ÷50) and the live UCI page (min-max scaling over −8..39 and −16..50). Only the °C hints in the app are affected. |
| i-1 | Info | RF under-predicts on average (+16.5), and this is not discussed. Residual diagnostics exist only in the notebook, not in `train.py` or `ml-results.md`. |
| i-2 | Info | The Context7 hook's `REQUIRED_LIBRARIES` list omits joblib, streamlit and pytest, and it ignores each entry's `status`. The hook is a workflow safeguard, not a security boundary. |
| i-3 | Info | `.gitignore` has no `*.env`, `*.pem` or `*.key` patterns. No secrets are tracked. |
| i-4 | Info | No `.gitattributes` file. Adding `* text=auto` would remove the CRLF-only ` M` noise on Windows. |
| i-5 | Info | Overlapping reports (`qa-report.md` and `qa-audit-report.md`; `final-verification.md` and `post-run2-evidence-review.md`). `post-run2-evidence-review.md` still cites the CRLF hash. |
| i-6 | Info | Research wording issues: the unsourced claim that growth was caused by network expansion; the wind-speed sentence that contradicts itself; 165 hours missing from the two-year span, not documented. |

### Limitations
1. **The notebook was not executed in Google Colab.** Colab behaviour, including the upload widget and Colab's preinstalled library versions, is inferred from the code and from the local and LF-file tests.
2. Figures were compared byte-for-byte; they were not reviewed visually in detail.
3. The original UCI zip was not downloaded, per the no-download rule. Whether it uses CRLF or LF is unknown. The fixed check accepts either line-ending form of the same content.

---

## H. UI launch evidence

**Authorization:** QA returned PASS WITH LIMITATIONS. The Lead Agent explicitly authorized a **local-only** launch, because none of the limitations affects the app's correctness.

**Pre-launch checks**

| Check | Result |
|---|---|
| `app/app.py` | present |
| Contract | valid, 12 features |
| `pipeline.joblib` | present, SHA-256 `73ad7db1…a834` matches |
| Streamlit | 1.67.0 importable |
| Port 8501 | free |

**Launch command**
- Effective command: `uv run --no-sync streamlit run app/app.py --server.port 8501 --server.headless true`, with `UV_OFFLINE=1`.
- `--no-sync` was added to the established command so uv could not sync dependencies.
- It was started as a detached process.

**Running processes**

| Process | PID |
|---|---|
| uv launcher | 17020 |
| `streamlit.exe` | 10916 |
| `.venv` python | 10268 |
| Owner of the socket listening on `[::]:8501` | 8332 |

**Verification**

| Check | Result |
|---|---|
| Local URL | **http://localhost:8501** |
| HTTP `GET /` | **200** (7,863 bytes), confirmed by the ui-launcher and again by the Lead with curl |
| Health check `GET /_stcore/health` | **200**, body `ok` |
| Server logs | "You can now view your Streamlit app in your browser"; no errors |

**Browser interaction (verified by the Lead in Chrome)**
- The page rendered the sidebar inputs and the Predict Demand button.
- Clicking **Predict Demand** with the default inputs (the contract example) displayed **"Predicted Demand: 821 rentals / hour"**. This is consistent with the contract's 820.52.

**Exposure note**
- By default, Streamlit listens on all network interfaces (`[::]:8501`). It printed a LAN URL and an external IP URL.
- Neither was tested, and no tunnel or public deployment was set up.
- To restrict the server to this machine, relaunch with `--server.address 127.0.0.1`.

**To stop the server:** `Stop-Process -Name streamlit`, then also stop PID 17020 if it is still running.

---

## I. Change register

All changes were authorized by the Lead Agent after a reported, independently verified defect. Each owning agent changed only its own files, and no two agents worked on the same file concurrently.

| File | Why it changed | Agent | Authorized | Commit |
|---|---|---|---|---|
| `README.md` | C1: stale `src/models`/`src/evaluation` layout; broken import `src.data_pipeline.load_data` (module is `load`); loader-error sentence claimed null/negative-`cnt` checks that do not exist | project-setup | Yes | `5b5c514` |
| `reports/repository-architecture.md` | C2: the approved-structure doc did not match the built repo (paths, 11 agents, figure locations, notebook pip note) | repository-architect | Yes | `5b5c514` |
| `reports/eda-findings.md` | C3: column types were "13 int / 3 float" (actually 12 int / 4 float); weather drop was "63%" (actually 63.7%, now "~64%") | data-scientist | Yes | `5b5c514` |
| `reports/ml-results.md` | C4: 1–977 was labelled the training range (it is the full-dataset range; training is 1–957); negative-prediction note was wrong for a Random Forest | ml-engineer | Yes | `5b5c514` |
| `notebooks/bike_demand_investigation.ipynb` | C5: a stored output exposed the local absolute path and username; the top-3 features were wrong (actually hr / atemp / temp); the negative-prediction note was wrong | colab-notebook-engineer | Yes | `5b5c514` |
| `notebooks/bike_demand_investigation.ipynb` | M-1: SHA-256 check made independent of line endings; canonical LF hash | colab-notebook-engineer | Yes | `7add08b` |
| `README.md` | m-2: commands to regenerate the EDA and the gitignored model after cloning | project-setup | Yes | `7add08b` |
| `reports/final-run-report.md` | This report (sections A–J) | Lead Agent | Yes (mission section 7) | follow-up commit on the same branch |

**Not changed, by decision:**
- `data/raw/*`
- `src/`, `app/`, `tests/`
- `.claude/`, `CLAUDE.md`, `.gitignore`, `pyproject.toml`, `uv.lock`
- the `.venv`

Regenerated EDA and model outputs were byte-identical to HEAD, so they were not committed. `pipeline.joblib` is gitignored.

**Push status:** nothing was pushed. The branch `fix/run3-reproducibility-corrections` exists locally only. Pushing it or merging it to `master` needs the user's approval: `git push -u origin fix/run3-reproducibility-corrections`.

---

## J. Final conclusion

| Component | Status |
|---|---|
| Repository recovery from GitHub | **Fully reproduced.** All 46 files restored; HEAD = `origin/master` `f614793`. |
| Environment (retained `.venv`, no downloads) | **Fully reproduced.** Versions match the lock; offline lock check clean. |
| Dataset integrity | **Fully reproduced.** Content identical; canonical LF hash `b03a2d…`. |
| EDA | **Fully reproduced.** 9/9 outputs byte-identical. |
| Modelling, metrics, artifact, contract | **Fully reproduced.** Metrics equal the Run 2 reference exactly; artifact byte-identical when regenerated on this machine. |
| Automated tests | **Fully reproduced.** 39/39 passing. |
| Notebook | **Partially reproduced.** Local execution of its code reproduces every metric, and after fix M-1 its dataset check works for LF and CRLF copies. It has **not** been executed in Google Colab. |
| Streamlit application | **Fully reproduced locally.** HTTP 200, health check `ok`, and a browser prediction of 821 rentals/hour. |

**Overall:** the project **was reproduced from GitHub using the retained local resources**, with no dependency downloads, and the UI launch was verified locally after QA authorization.

The reproduction was not achieved purely by restoring the files: one Major defect (M-1) had to be fixed first. The notebook's dataset check would have rejected the GitHub-hosted dataset on any non-Windows or LF checkout, including Colab. M-1 and six documentation inaccuracies were corrected in two authorized local commits.

Colab execution remains an explicit, unverified limitation. The minor findings listed in section G are left for the owners' decision. The most visible of them is the season labels.
