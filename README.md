# VICI SEC 10-K Item Extraction Pipeline

VICI 是一個 production-style 的 SEC 10-K item extraction pipeline。它以 deterministic
parsing 為主，搭配可檢查的 evidence、明確的 uncertainty、以及 reviewer-friendly 的原始
filing 結構預覽，目標是在真實 SEC filing 格式變異下，仍能穩定抽取 10-K 的各個 Item。

目前支援的核心目標包含 Item 1、Item 1A、Item 7、Item 8、Item 15，以及標準 10-K item
set 中其他 section。系統設計重點不是只追求「看起來有抽到文字」，而是讓每個 boundary
decision 都能被檢查、驗證與回溯。

## 核心策略

VICI 採用 deterministic-first 策略：

- 從多種 deterministic signal 找 candidate：regex heading、alias、DOM/raw heading
  evidence、TOC row、Form 10-K cross-reference index。
- 透過 legal item order、validated next-item evidence、TOC ordering、cross-reference
  page span，以及 bounded terminal fallback 重建 item boundary。
- warning 是 review signal，不是自動 failure。很短的 `Not applicable` section，或很長的
  exhibit/table/financial-statement section，都可能是合法內容。
- 對 table、image、exhibit、supplemental section 保留 scoped original filing HTML，方便
  reviewer 檢查原始結構與還原度。
- 每個 item payload 會輸出 evidence offset、candidate attempts、confidence components、
  SEC item format metadata、warnings、recovery actions，以及 per-item `strategy_trace`。
- 預設 extraction path 不使用 LLM 或 embedding。它們只保留給未來 bounded ambiguity
  recovery 使用，而且必須在 deterministic signal 用盡後才可啟動。

主要策略文件：

- [Extraction strategy](docs/extraction-strategy.md)
- [Production readiness review](docs/production-readiness.md)
- [Retry policy](docs/retry-policy.md)
- [Recovery readiness](docs/recovery-readiness.md)
- [SEC data sources](docs/sec-data-sources.md)

## 快速開始

執行完整測試：

```bash
python3 -m unittest discover -s tests
```

對本地 filing 檔案跑 CLI extraction：

```bash
PYTHONPATH=src python3 -m sec_item_extractor path/to/10k.html --items 1 1A 7
```

啟動本地 review UI：

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/run_web_ui.py --host 127.0.0.1 --port 8000
```

接著開啟 `http://127.0.0.1:8000`。

## Intake 方式

Web UI 支援四種主要入口：

- 從 `/testing` 選擇本地 seed fixture。
- 透過 SEC ticker/year 或 CIK/year 即時抓取並解析，不預設保存 raw filing。
- 上傳 HTML/TXT filing，直接在 memory 中解析。
- 對 hosted environment 中過大的 upload，先用 bounded leading sample 判斷 ticker/CIK/year，
  再轉到 SEC live direct fetch。

Live SEC request 需要設定描述性的 `SEC_USER_AGENT`。SEC request 會使用官方 submissions、
archives、company ticker directory endpoint，並且受 rate limit 控制。

## 執行方式

### 測試

完整測試：

```bash
python3 -m unittest discover -s tests
```

常用 focused tests：

```bash
python3 -m unittest tests.test_extractor tests.test_web_ui
python3 -m unittest tests.test_eval_manifest
```

### CLI

```bash
PYTHONPATH=src python3 -m sec_item_extractor path/to/10k.html --items 1 1A 7
```

CLI 會輸出 JSON，內容包含 filing status、item results、confidence components、warnings
與 evidence。

### Web UI

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/run_web_ui.py --host 127.0.0.1 --port 8000
```

Frontend 是由 `frontend/` 提供的 React single-page app；Python server 保留 extraction API，
並服務 `/`、`/upload`、`/sec-live`、`/filings/...` 等路由。

Live SEC request 需要 `SEC_USER_AGENT`。Upload parsing 不需要 SEC credential。
`MAX_UPLOAD_BYTES` 控制上傳大小限制，預設為 25 MB。

### Seed / Validation / Regression Report

本地檢查 extractor quality 時常用：

```bash
python3 scripts/evaluate_seed.py
python3 scripts/evaluate_validation.py
python3 scripts/evaluate_regression.py
```

只有需要更新 raw fixture 時才執行 SEC download scripts：

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/fetch_seed_filings.py
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/fetch_validation_filings.py
```

### Deployed Eval

對已部署網站執行 manifest-driven eval：

```bash
python3 scripts/run_deployed_eval_set.py --base-url https://vici-ten.vercel.app --sleep 1
```

Eval runner 會在 `reports/` 下輸出 aggregate JSON 與 Markdown report。

## 主要設計決策

- `Deterministic-first extraction`：一般 parsing 使用本地規則與 structured evidence，而不是
  LLM。這讓輸出可重現，也比較容易驗證與控管成本。
- `Retrieval plus validation`：先從多個 signal 找 item heading candidate，再根據 legal item
  order、TOC evidence、cross-reference pages、boundary context 做 filtering 與 validation。
- `Inspectable uncertainty`：warnings、confidence components、strategy trace、candidate attempts、
  recommended recovery actions 都是 API payload 的一部分。
- `Raw fidelity for complex sections`：table、image、exhibit、signature、supplemental section 可
  透過 scoped original filing HTML 檢查，而不是只依賴 plaintext。
- `Honest failure`：全空檔案，或完整 filing extraction 缺少大多數 item 時，會回傳 `failed`，
  不會把少數抽到的 snippet 包裝成成功。
- `No autonomous recovery`：recovery action 必須由 user 明確觸發。系統可以呈現 same-filing
  reference、internal TOC、exhibit link，但不會靜默替換 primary item content。
- `Layered validation`：seed、held-out validation、reviewed issue cases、48-filing eval set 分別
  覆蓋不同 reliability risk，因為 SEC item boundary 並沒有公開 ground truth dataset。
- `Deployment-aware intake`：hosted upload path 會避免大型 raw upload；如果可判斷 ticker/CIK
  與 fiscal year，就改走 SEC direct fetch。

## AI 協助的部分

AI 在此專案中協助 development 與 review，但不是 runtime autonomous agent。

AI 協助的環節包含：

- architecture review，以及 robustness、validation、retry、cost、deployment 風險分析
- 將 reviewer observation 轉成 deterministic strategy rule 與 regression test
- 實作 focused parser、UI、report、documentation change
- 產生並維護策略文件，例如 `docs/extraction-strategy.md` 與 `docs/production-readiness.md`
- 設計 seed、validation、reviewed-issue、production eval workflows
- 解讀 warning pattern，並在引入任何 LLM recovery 前，優先提出 deterministic fix

預設 extraction pipeline 不使用 AI model。LLM 或 embedding 只保留為未來 bounded recovery
option，用於 low-confidence semantic ambiguity；primary source of truth 仍是 deterministic
parsing 與可檢查 evidence。

## 部署

### Zeabur

Repo 內含 `Dockerfile`，可用於 Zeabur 或其他 Docker-style hosting。

建議環境變數：

```bash
HOST=0.0.0.0
PORT=8000
SEC_USER_AGENT="Your Name your.email@example.com"
MAX_UPLOAD_BYTES=26214400
```

健康檢查 path 使用 `/api/health`。如果沒有設定 `SEC_USER_AGENT`，live SEC intake 會被阻擋，
但 upload parsing 仍可使用。

### Vercel

Repo 也包含 Vercel adapter：

- `api/index.py` 將既有 Python `WebUiHandler` 暴露為 Vercel Python Function。
- `vercel.json` 將所有 route rewrite 到該 function，因此 `/`、`/upload`、`/sec-live`、
  `/assets/...`、`/api/...` 都會維持相同行為。

Vercel 環境變數：

```bash
SEC_USER_AGENT="Your Name your.email@example.com"
MAX_UPLOAD_BYTES=26214400
```

Vercel 不會直接跑 Dockerfile，而是以 Python Function 形式執行，所以比較適合 demo 與
validation。若要處理長時間 extraction workload 或大型 filing，Docker deployment 仍較適合。

## Evaluation 與資料集

此專案使用 layered validation，原因是 SEC 10-K item boundary 沒有公開 ground-truth dataset。

資料集：

- [Seed filings](fixtures/gold/seed_filings.json)：20 份 filings，用於 regression development。
- [Gold boundary expectations](fixtures/gold/boundaries.seed.json)：人工確認過的 lightweight gold
  test，不追求完整逐字 ground truth，而是檢查重要 item 的 start/end evidence、recovery action
  routing，以及 table/image raw structure fidelity。
- [Held-out validation filings](fixtures/gold/validation_filings.json)：10 份從 seed corpus 保留
  出來的 validation filings。
- [Production eval filings](fixtures/gold/eval_filings.json)：48 個 filing slots，涵蓋 Technology、
  Financials、Industrials / Energy；每個 bucket 有六間大型公司與兩間中小型公司。
- [Reviewed issue cases](fixtures/gold/reviewed_issue_cases.json)：將 user-reviewed failure 轉成
  regression checks。

Boundary label 格式參考 [fixtures/gold/boundaries.example.json](fixtures/gold/boundaries.example.json)。

目前人工 review 後表現較穩定、可作為 sanity reference 的 filing 包含：

- `aapl_2023_10k`：Item 1、Item 1A、Item 7 boundary 在 gold test 中作為主要科技公司案例。
- `msft_2023_10k`：Item 1、Item 1A、Item 7 boundary 在 gold test 中作為另一個大型科技公司案例。
- `wmt_2014_10k`：Item 15 exhibit/table raw structure 還原作為 gold test 案例。
- `wmt_2023_10k`：Item 5 的 table/image raw structure fidelity 作為 gold test 案例。

這些案例不代表系統已經解決所有 filing 格式，而是目前 review 過、抽取表現不錯、適合用來防止
regression 的基準樣本。

下載 seed filings 到 ignored local fixtures：

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/fetch_seed_filings.py
```

評估目前本地存在的 seed filings：

```bash
python3 scripts/evaluate_seed.py
```

匯出 seed filings 的 Markdown extraction report：

```bash
python3 scripts/export_seed_extractions_md.py
```

匯出 warning-focused audit report：

```bash
python3 scripts/export_warning_audit_md.py
```

對 warnings 執行 deterministic recovery actions：

```bash
python3 scripts/run_recovery_actions.py
```

對 internal Item 7 TOC case，可傳入明確 subsection choice：

```bash
python3 scripts/run_recovery_actions.py --select "bac_2023_10k:7=Executive Summary"
```

評估 lightweight gold boundary expectations：

```bash
python3 scripts/evaluate_gold_boundaries.py
```

Gold test 會讀取 [fixtures/gold/boundaries.seed.json](fixtures/gold/boundaries.seed.json)，並輸出
[reports/gold_boundary_report.md](reports/gold_boundary_report.md)。它主要檢查：

- selected start evidence 是否包含預期 item heading。
- selected end evidence 是否落在預期 next item 或 terminal boundary。
- warning/recovery action 是否符合人工 review 的 expectation。
- raw table/image count 是否達到最低還原要求。

產生 seed + validation combined regression report：

```bash
python3 scripts/evaluate_regression.py
```

下載並評估 held-out validation filings：

```bash
SEC_USER_AGENT="Your Name your.email@example.com" python3 scripts/fetch_validation_filings.py
python3 scripts/evaluate_validation.py
```

Deployed eval report 會用來分類 warning categories、failed requests、failed items、SEC format
review counts 與 latency，讓 hosted behavior 可以和 local behavior 對照。

檢查 filing 的 normalized narrative blocks：

```bash
python3 scripts/inspect_document.py fixtures/filings/raw/aapl_2023_10k.html --limit 10
```

檢查 item heading candidates：

```bash
python3 scripts/inspect_candidates.py fixtures/filings/raw/aapl_2023_10k.html --limit 25
```

## SEC Intake Sources

Ingestion utilities 依照官方 SEC EDGAR API 格式實作，詳細來源記錄在
[docs/sec-data-sources.md](docs/sec-data-sources.md)。Request 需要 descriptive `User-Agent`，
預設 rate limit 為每秒 10 requests，不需要 API key。

## 目前 Reliability Surface

主要 result fields 都是為了 inspectability 而設計：

- `candidate_attempts`：被選中或被拒絕的 boundary attempts。
- `confidence_components`：可解釋的分數組成。
- `strategy_trace`：per-item deterministic decision path。
- `sec_format`：canonical SEC item title/label check。
- `warnings`：可 review 的 uncertainty categories。
- `recommended_actions`：明確的 recovery options。
- `raw_structure`：用於 table/image/exhibit review 的 scoped original filing HTML。

## Milestone Notes

### Block Model

HTML/text cleaning 會產生 `CleanDocument`，包含 normalized text 與 `NarrativeBlock` records。
每個 block 都包含 clean offsets、raw offsets、source type，以及可用時的 nearest block tag。
`html_to_text()` 仍保留給 deterministic extractor 使用。

### Candidate Evidence

Candidate retrieval 會把 block/raw metadata 附加到 heading candidates，並在每個 item result 中
記錄 selected 或 rejected candidate attempts。這讓 boundary decision 在不引入 embedding 或 LLM
的情況下仍可被檢查。

### Confidence Summary

Item results 包含 `confidence_components`，將 final score 拆成 deterministic、explainable 的
signals：legal boundary pair、TOC filtering、expected title match、section length。
`scripts/evaluate_seed.py` 也會輸出 seed filings 的 aggregate status、confidence-level、warning
counts。

### Reliability Regression

`scripts/evaluate_regression.py` 將 seed 與 validation filings 合併為單一 regression surface。
它會記錄 per-item status、confidence、warning categories、raw table/image counts、supplemental
section counts、raw preview availability，以及 recovery action counts。
