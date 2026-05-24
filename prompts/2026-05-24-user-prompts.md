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

## Seed Extraction Markdown Request

```text
目前先測試對test filing 做extracting，並且以md的形式展示
```

## Seed Extraction Snippet Request

```text
我看過測試了，目前沒問題，snippet部分除了開頭，也需要把結尾也列出來
```

## Next Step Request

```text
好，進行下一步
```

## Warning Audit Report Request

```text
好，先把這部分搞定，並產生我可以看的test report
```

## Candidate Pair Resolver Request

```text
先實作看看，並跑測試
```

## Warning Count Follow-Up Request

```text
warning數有下降嗎？有的話再做後續的部分
```

## Gold Boundary Implementation Request

```text
好，你先實作吧
```

## Recovery Runner Implementation Request

```text
好
```

## Full Item Testing Request

```text
testing 方面開始去對全item抽取，而不是只會單一幾個item
```

## TOC-Assisted Boundary Request

```text
首先，每一份filing都可能會長得不同，不一定都有明確的item1-16，這部分需要透過toc還判斷開頭以及結尾
```

## Continue TOC Implementation Request

```text
好，繼續實作
```

## MVP Run Request

```text
好，根據milestone進行下一步，13 failed的部分後續處理，先跑mvp
```

## Failed Item Recovery Request

```text
好，根據milestone進行下一步，13 failed的部分後續處理
```

## Reliability Milestone Request

```text
可以，先把1-5做好
```

## Retry Policy Contract Request

```text
可以補RetryPolicy，另外先確認working tree是否有未處理的部分
```

## Frontend Test Filing UI Request

```text
先簡單創建前端UI，入口頁面先讓user從當前的test filing裡選擇要看哪一份的，之後進入下層頁面，左邊navi bar是放toc，主要extract出來的item放在中間至右邊。不要使用cache會任何預設的資料，我要整個pipeline是在確認跑哪一份filing時才開始執行的
```

## Frontend Recovery UI Request

```text
1-3直接做，4的話把未使用的部分清掉，5先不做。
```

## Held-Out Validation Filing Request

```text
好，接下來testing部分找另外5間公司前一年度和十年前的filing來做validatation
```

## Validation Warning Review Request

```text
好，我review以下問題，並commet。大部分屬於length長度太小難以判斷，這部分若是可以以我剛說的上下段落是否是正常的item來確定位子是否正確，正確的話，仍要返回內容，即使只有標題或是一兩句話。另外有exhibit的話，也要展示，若有指向其他段落的引用，也要提供可讓user去查看的button。
nvda_2015_10k Item 8: 本身僅一句sentence
nvda_2025_10k Item 6: 本身段落too short（只有一個單詞）
nvda_2025_10k Item 8: 本身僅一句sentence
googl_2015_10k Item 1B: 本身僅一句sentence
googl_2015_10k Item 15: 包含其他段落引用，以及表格
meta_2025_10k Item 6: 本身段落too short（只有一個單詞）
lly_2015_10k Item 7A: 本身僅兩句sentence
lly_2015_10k Item 15: exhibit的部分
lly_2025_10k Item 6: 本身段落too short（只有一個單詞）
lly_2025_10k Item 7A: 本身僅兩句sentence
lly_2025_10k Item 16: 本身僅一句sentence
pg_2015_10k Item 7A: 本身僅一句sentence
pg_2025_10k Item 6: 僅留有標題
pg_2025_10k Item 7A: 本身僅一句sentence
```

## Exhibit Table Frontend Request

```text
過長的部分目前都是偏exhibit或是table的話，在前端也簡單實作讓其可以顯示。另外若有圖片目前的處理策略是什麼
```
