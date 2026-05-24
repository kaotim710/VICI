# User Prompts

## Architecture Request

```text
我們正在設計一個 production-style 的 SEC 10-K Item Extraction Pipeline。
這個系統的目標是：

從 SEC 10-K filing 中，
穩定抽取：
- Item 1
- Item 1A
- Item 7
等 section，並且能被獨立取用，

系統必須：
- robust
- inspectable
- uncertainty-aware
- production-oriented

成果最後必須部署在 Zeabur
開發過程必須公開 repo，且 commit history 要能反映真實開發過程
在 repo 根目錄建 prompts/ 資料夾保存主要 prompt

目前規劃的 architecture 如下：

==================================================
High-Level Pipeline
==================================================

1. Filing Intake Layer
- ticker/year query
- SEC API ingestion
- user upload support
- raw filing storage

↓

2. Narrative Extraction Layer
- HTML cleaning
- iXBRL metadata suppression
- malformed DOM normalization
- structured narrative blocks

↓

3. Candidate Retrieval Layer
- regex retrieval
- alias retrieval
- DOM heading retrieval
- TOC-assisted retrieval

↓

4. Candidate Rerank & Validation Layer
- structural validation
- TOC filtering
- semantic validation
- optional cross-filing validation

↓

5. Boundary Reconstruction Layer
- reconstruct item boundaries
- legal section transition graph

↓

6. Retry / Recovery Graph
- bounded retries
- strategy-changing retries
- fallback parsing
- optional LLM verifier

↓

7. Confidence Engine
- explainable confidence scoring
- multi-signal aggregation

↓

8. Evaluation Layer
- boundary accuracy
- TOC false positive rate
- retry frequency
- held-out filing robustness

==================================================
Core Design Philosophy
==================================================

- deterministic parsing first
- LLM only for ambiguity recovery
- retrieval + validation architecture
- bounded retry graph
- explainable confidence
- inspectable failure handling
- no autonomous agent orchestration

==================================================

==================================================

請先：

1. 分析整體 architecture 的優缺點
2. 找出可能的 edge cases
3. 分析：
   - silent failure risk
   - retrieval failure
   - validation failure
   - retry explosion risk
4. 分析：
   - 哪些部分過度設計
   - 哪些部分可能不足
5. 分析：
   - 哪些部分應該 deterministic
   - 哪些部分適合使用 embedding
   - 哪些部分適合使用 LLM
6. 分析：
   - memory risk
   - latency risk
   - scaling risk
7. 提出：
   - 更 production-grade 的修改建議
   - 更簡潔的實作方式
   - 更適合 incremental implementation 的方式

請：
- 用 architecture review 的角度分析
- 不要直接開始 coding
- 不要過早抽象化
- focus 在 reliability 與 robustness
```

## Implementation Request

```text
照你的五個milestones來實作，你會怎麼開始？gold data set 我會選美股前五大的產業別，個別的前五大公司，在過去二十年內挑五個時間節點來做
```

```text
好，你可以開始實作。testing的部分可以照你說的先抽20個filing即可，另外prompts中也需要放我跟你下的prompt
```

## SEC Data Source Request

```text
你可以使用以下來源
資料來源
* API overview：https://www.sec.gov/search-filings/edgar-application-programming-interfaces
* Submissions API：https://data.sec.gov/submissions/CIK{10位補零}.json
* Full-text Search：https://efts.sec.gov/LATEST/search-index?q={query}&forms=10-K
* 檔案下載：https://www.sec.gov/Archives/edgar/data/{CIK}/{accession-去破折號}/{filename}
* XBRL Company Facts（可用於交叉驗證）：https://data.sec.gov/api/xbrl/companyfacts/CIK{10位補零}.json
* 規範：需帶 User-Agent header、10 req/sec、無需 API key
```

## Prompt Token Usage Request

```text
另外我想在prompts/中記錄我的prompt token消耗
```

## Seed Filing Download Request

```text
好，接下來先下載20份的10-k來當test filing
```

## Next Milestone Request

```text
ok，進行下一個milestone
```

## Continue Milestones Request

```text
好，繼續實作後續的milestone
```
