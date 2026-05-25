# SEC 10-K Item Extraction Pipeline

這個專案是一個 production-style 的 SEC 10-K item extraction pipeline。它以 deterministic
parsing 為主，搭配可檢查的 evidence、明確的 uncertainty、以及 reviewer-friendly 的原始
filing 結構預覽，目標是在真實 SEC filing 格式變異下，仍能穩定抽取 10-K 的各個 Item。

核心目標是抽取完整 10-K item set，而不是只抽取少數重點 section。系統設計重點不是只追求
「看起來有抽到文字」，而是讓每個 boundary decision 都能被檢查、驗證與回溯；如果檔案全空、
格式錯誤，或完整 filing 缺少大多數 item，系統應誠實回傳 `failed`。

## 核心策略

本專案的策略可以統合成四層：

- `Deterministic retrieval`：從 regex heading、alias、DOM/raw heading、TOC row、Form 10-K
  cross-reference index 等訊號找 candidate。
- `Boundary validation`：用 legal item order、next-item evidence、TOC ordering、page span、
  terminal fallback 重建並驗證 section boundary。
- `Inspectable uncertainty`：輸出 evidence、candidate attempts、confidence components、
  warnings、recommended actions、SEC format metadata、`strategy_trace`，讓 reviewer 能理解為何
  這樣切。
- `Raw fidelity and honest failure`：table/image/exhibit/supplemental section 以 scoped original
  filing HTML 檢查；空檔、薄檔、缺少大多數 item 的完整 filing 直接標為 `failed`。

預設 extraction path 不使用 LLM 或 embedding。它們只保留給未來 bounded ambiguity recovery，
且只能處理低信心、語意模糊的局部 evidence packet，不會成為主解析器。

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

Eval runner 會在 `reports/` 下輸出 aggregate JSON 與 Markdown report。這些檔案多數是可重產的
local generated artifacts，預設不再 tracked；只有小型 testing sample 會保留在 repo 中。

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

## 成本、效能與擴充性

### 成本紀律

- 預設 extraction 不使用 LLM 或 embedding，因此 runtime model cost 為零。
- SEC API 不需要 API key，但必須提供 `User-Agent`，並遵守 rate limit。
- `prompts/token-usage.md` 只記錄開發過程中的 user prompt token 估算，不是 billing record。
  目前 ledger 共有 86 筆 prompt，估算 prompt tokens 合計約 3,902，其中 actual prompt tokens
  欄位尚未填入。
- 本專案開發過程使用 Codex Pro 5x 方案，約使用 40% weekly usage 完成目前的設計、實作、
  review 與文件整理。
- 若未來加入 LLM verifier，只能針對 low-confidence ambiguity 傳送 bounded evidence packet，
  不可把整份 10-K 丟給模型。

### 效能

- Live SEC extraction 是 on-demand：使用者指定 ticker/CIK + fiscal year 後才抓取與解析 filing。
- Raw filing 預設不持久化；table/image/exhibit preview 只保留 scoped fragment，避免渲染整份 filing。
- Batch eval 應透過 `scripts/run_deployed_eval_set.py` 執行，並用 `--sleep` 控制節奏，不應透過前端連續點擊。
- Vercel serverless path 適合 demo 與 validation；大型 filing 或長時間 batch workload 可能遇到 timeout 或 request body 限制。

### 擴充性

- 新 filing 問題應先加入 reviewed issue case 或 eval manifest，再改 parser rule。
- 公司/年度特定格式可以作為 strategy memory，但要建立在主策略之上，不能取代 deterministic evidence。
- 若導入 embedding/LLM，應只作為 recovery/verifier，並在 report 中統計觸發次數、接受率與成本。

## AI 協助的部分

AI 在此專案中協助 development 與 review，但不是 runtime autonomous agent。

AI 協助的環節包含：

- architecture review，以及 robustness、validation、retry、cost、deployment 風險分析
- 將 Andrej Karpathy 的 Skills 概念整理成 Codex workspace 的 `AGENTS.md` 協作規範，用來約束
  coding agent 在此 repo 中的執行方式
- 將 reviewer observation 轉成 deterministic strategy rule 與 regression test
- 實作 focused parser、UI、report、documentation change
- 產生並維護策略文件，例如 `docs/extraction-strategy.md` 與 `docs/production-readiness.md`
- 設計 seed、validation、reviewed-issue、production eval workflows
- 解讀 warning pattern，並在引入任何 LLM recovery 前，優先提出 deterministic fix

預設 extraction pipeline 不使用 AI model。LLM 或 embedding 只保留為未來 bounded recovery
option，用於 low-confidence semantic ambiguity；primary source of truth 仍是 deterministic
parsing 與可檢查 evidence。

## 部署

目前部署主線是 Vercel。Repo 內含 Vercel adapter：

- `api/index.py` 將既有 Python `WebUiHandler` 暴露為 Vercel Python Function。
- `vercel.json` 將所有 route rewrite 到該 function，因此 `/`、`/upload`、`/sec-live`、
  `/assets/...`、`/api/...` 都會維持相同行為。

Vercel 環境變數：

```bash
SEC_USER_AGENT="Your Name your.email@example.com"
MAX_UPLOAD_BYTES=26214400
```

Vercel 不會直接跑 Dockerfile，而是以 Python Function 形式執行，所以比較適合 demo 與
validation。

Vercel 有 request body / upload size 限制。大型公開 SEC filing 不應依賴完整檔案 upload；目前策略是：

- 小型 HTML/TXT filing 可直接 upload 並在 memory 中解析。
- 大型 filing 先以 bounded leading sample 判斷 ticker/CIK/year。
- 如果可識別為公開 SEC filing，轉到 live SEC direct fetch，再從 SEC archive 下載完整 filing。
- 如果 sample 無法判斷 ticker/CIK/year，系統應要求 user 改用 ticker/year 或 CIK/year search。

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

目前人工 review 後表現較穩定、可作為 sanity reference 的 seed filings 包含：

- Apple：AAPL 2014、AAPL 2023
- Microsoft：MSFT 2014、MSFT 2023
- JPMorgan Chase：JPM 2014、JPM 2023
- Bank of America：BAC 2014、BAC 2023
- UnitedHealth Group：UNH 2014、UNH 2023
- Johnson & Johnson：JNJ 2014、JNJ 2023
- Exxon Mobil：XOM 2014、XOM 2023
- Chevron：CVX 2014、CVX 2023
- Walmart：WMT 2014、WMT 2023
- Amazon：AMZN 2014、AMZN 2023

其中 gold test 目前明確覆蓋 AAPL 2023、MSFT 2023、WMT 2014、WMT 2023 等 boundary 或
raw structure fidelity expectation。這些案例不代表系統已經解決所有 filing 格式，而是目前
review 過、抽取表現較穩定、適合用來防止 regression 的基準樣本。

目前已知拆分仍不理想或需要繼續改善的案例：

- JPM 2023：Item 1C、Item 8 等 section 有一句話引用到後方頁面；Item 15 後方還有獨立 TOC、
  table、圖表與 supplemental content。這類 same-filing reference 與 supplemental section
  已有初步 recovery/partition，但仍需要更穩定的 page-range composite handling。
- JNJ 2023：Item 8 內部 financial statement TOC 需要像 supplemental section 一樣做子項切分；
  目前可呈現 internal TOC，但仍需要更多 fidelity check。
- INTC 2025：Form 10-K Cross-Reference Index 對多個 item 給出頁碼或共用 reference。Item 2、
  Item 3、Item 5、Item 7、Item 7A、Item 9A、Item 9B，以及 Part III 的 Item 10-14，都可能因
  cross-reference range、bold heading、或 TOC row 混淆而切得不夠精準。這是後續需要 bounded
  LLM verifier 或 company-specific strategy memory 輔助的代表案例。
- Citigroup Inc. 2023：部分 upload/live filing 在 TOC、cross-reference、以及 item heading
  normal form 上仍容易造成切分失敗或漏抽，代表金融業大型 filing 還需要更多
  company-specific review cases。
- McDonald's 2020：部分 item boundary 在 dense heading、TOC-like row、或相鄰 section transition
  下仍切分不佳，需要補進 reviewed issue cases 後再設計 deterministic fix。

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

Gold test 會讀取 [fixtures/gold/boundaries.seed.json](fixtures/gold/boundaries.seed.json)，並在本地
輸出 generated report 到 `reports/gold_boundary_report.md`。它主要檢查：

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
