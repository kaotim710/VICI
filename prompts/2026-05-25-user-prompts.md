# 2026-05-25 User Prompts

## Regression Milestone Implementation Request

```text
好，除了第五項之外都先實作。目前我發現jpm這份有問題，待會做完我們再來修改
```

## Recovery Action Placement Request

```text
將recovery actions移至後方
```

## Supplemental Subsection Raw Preview Request

```text
supplement portion也應該要根據每一個title，讓其能夠單獨還原成Show original filing structure
```

## Filing Review Follow-Up Request

```text
aapl, msft, wmt, 都表現不錯

bac 2023 Item 8. Financial Statements and Supplementary DataTable of Contents: 也是極大頁數在表示這個item，是否需要檢測頁數一但過多，就偵測是否含有table of content，然後自動切分成跟supplement portion一樣的模式。做完以bac的另一份filing來做交叉查核

JPM 2023 有多項item(1C, 8)僅有一句但是引用到其他頁數的部分，這些都放在後面頁數(item 15之後)，該如何制定處理策略
JPM 2023 item 6 抽取到了首頁的toc，做更改並同時利用jpm另一份做交叉查核
JPM 2023 item 15 後含有table of content， 應自動切分成跟supplement portion一樣的模式。做完以JNJ的另一份filing來做交叉查核

UNH 2014 item 2 抽取到了首頁的toc，做更改並同時利用unh另一份做交叉查核
UNH 2014 item 7 抽取到了首頁的toc，做更改並同時利用unh另一份做交叉查核
UNH 2014 item 8 內含有table of content， 應自動切分成跟supplement portion一樣的模式。做完以unh的另一份filing來做交叉查核
UNH 2014 item 13 抽取到了首頁的toc，做更改並同時利用unh另一份做交叉查核
UNH 2014 item 14 抽取到了首頁的toc，做更改並同時利用unh另一份做交叉查核

JNJ 2023 item 8 內含有table of content， 應自動切分成跟supplement portion一樣的模式。做完以JNJ的另一份filing來做交叉查核

XOM 2014 item 15 內含有table of content， 應自動切分成跟supplement portion一樣的模式。做完以XOM的另一份filing來做交叉查核
XOM 2014 Supplemental after Item 15 這部分只有標題而已沒有內文，看是否要跟我前一句說item 15的部分做統合。做完以XOM的另一份filing來做交叉查核

CVX 2023 item 5 這部分還切到了item 6 跟 item 7
CVX 2023 item 5 這部分還切到了item 7
CVX 2023 item 14 內含有table of content， 應自動切分成跟supplement portion一樣的模式。做完以CVX的另一份filing來做交叉查核

AMZN 2023 item 1C 這部分還切到了item 2 跟 item 3
AMZN 2023 item 2 抽取到了首頁的toc，做更改並同時利用amzn另一份做交叉查核
AMZN 2023 item 3 抽取到了首頁的toc，做更改並同時利用amzn另一份做交叉查核
AMZN 2023 item 5 這部分還切到了item 6
AMZN 2023 item 16 抽取到了首頁的toc，做更改並同時利用amzn另一份做交叉查核
```

## Reviewed Issue Regression Test Request

```text
將我提出的這些問題加入測試當中，以便未來用新filing 做validation
```

## Validation Strategy Confirmation Request

```text
目前是根據剛更新的策略去跑的嗎
```

## Fallback Strategy Planning Request

```text
目前的fallback 策略，以及下一步
```

## Validation Milestone Run Request

```text
先跑milestone
```

## Three Milestone Implementation Request

```text
好，接下來實作這3個milestone
```

## Live SEC API Test Request

```text
好，測試目前api call 抓不抓得到資料
```

## Live SEC Extraction Next Step Request

```text
好，進行下一步
```

## Live SEC Multi-Filing Smoke Test Request

```text
利用其他的filing跑真實測試，包括xom, jnj, jpm 等，並且年份在2015-2020 隨機擇一，看是不是有昨天類似的問題。跑完給我看report和warning
```

## Live Result Frontend Parsing Page Request

```text
將這次的結果也放在前端當作raw data，並且在user搜尋完filing和年份後，跑解析頁面出來
```

## Live Raw Structure Restore Request

```text
我剛check了，原本的Show original filing structure 不見了
```

## Upload Intake And Zeabur Prep Request

```text
好，現在實作intake檔案上傳的部分，做完測試完要準備部署至zeabur
```

## Fiscal Year Dropdown Request

```text
api call的fiscal year 以下拉選單的方式表示年份，
```

## Upload Metadata Inference Request

```text
upload 的部分，不需要ticker, fiscal year, form 的輸入選項，反而是輸入檔案後，將這些從檔案中顯示出來給user
```

## React Apple Frontend Refactor Request

```text
好，以react頁面重構整個前端，並且以apple風格做設計，之後準備部署至zeabur
```

## Loading Animation And Centered Search Request

```text
任何loading的部分可以加上動畫，以及頁面排版應該是將search bar放在正中間，接著往下問說 or upload your filing
```

## Testing Subpage Request

```text
live smoke raw data的部分可以和local seed filing放在另外一個sub page叫testing
```

## React Frontend Completion Request

```text
重新把上面react前端未完成的部分補完
```

## Upload Regression Review Request

```text
自我檢測這兩份，我剛review了，目前extract都產生問題，intc誤把toc認為是item，citi則是完成沒抽取到
```

## SEC Item Format Validation Request

```text
確認upload或是api call的 filing每個item 都有遵照sec的固定標題與格式內容
```

## Zeabur Deployment Request

```text
好，我們部署至zeabur
```

## Vercel Deployment Alternative Request

```text
改用vercel部署呢？
```

## Vercel Connected Request

```text
我已連上線
```

## Vercel Project Identity Request

```text
VICI SEC Item Extractor Tim Kao [email redacted]
```

## Vercel GitHub Auto Deploy Question

```text
好，目前確認已部署，如果我在本地做更改push到github，vercel的頁面也會隨之改變嗎
```

## Prompt Logging Pause Request

```text
好，目前先暫停把prompt push 到文件中
```

## INTC Cross Reference Index Request

```text
intc 2025在 在toc尾部有Form 10-K Cross-Reference Index，這邊有對應的頁數，應該先查閱這部分後，才去切？
intc 2025 item 1 應該從 "our business"開始切
intc 2025 item 1A 應該從 "risk factor"開始切
```

## Citi Upload Error Request

```text
目前無法上傳這個citi檔案：
error: Upload extraction failed: Unexpected token 'R', "Request En"... is not valid JSON
Unexpected token 'R', "Request En"... is not valid JSON
```

## Search State Persistence Request

```text
當搜完ticker進到頁面後，user再按回上一頁，ticker跟fiscal year選項應該是要保留原本user的輸入值
```

## Continue Current Work Request

```text
繼續你目前的動作
```

## INTC Item Cross Reference Review Request

```text
intc 2025 item 2 應該只切到 sales and marketing 之前，並且根據前面的toc，Form 10-K Cross-Reference Index這個項目的頁碼數是11跟32，因此32的property也應該放進來
intc 2025 item 3 應該只切到key terms之前
intc 2025 item 5 應該只切到53頁的內容
intc 2025 item 7 也引用了多數頁面，應該將其整合
intc 2025 item 7A 應該切到risk factor 之前
intc 2025 item 9A 應該切到exhibit 之前
intc 2025 item 9B 沒有正確切到，Form 10-K Cross-Reference Index 寫了page 54
intc 2025 item  item 10, 11, 12, 13, 14 在Form 10-K Cross-Reference Index都是寫同一個reference，但目前11,12,13,14只抓了toc

我認為是不是可以當信心指數過低或是複雜情況時，call llm api來判斷之後的粗體標題不是和當前有關。並且根據不同公司，記下不同的策略，以便之後調取同個公司，不同年度的10-k時，可以快速地的切分，當然這個前提是有一個主策略在
```

## Vercel Upload Limit Strategy Question

```text
目前vercel上傳檔案超過限制的部分你怎麼處理
```

## Oversized Upload Implementation Request

```text
好，你先做吧
```

## Oversized Upload Recheck Request

```text
目前vercel上傳檔案超過限制的部分你怎麼處理
```

## SEC Ticker Directory Source Request

```text
https://www.sec.gov/files/company_tickers.json 這裡有ticker 對應cik和公司名稱的對照表
```

## Citi Upload Still Blocked Request

```text
我實測了, citi這個檔案還是會被擋下來並且出現一樣的error
```

## Upload Guidance Copy Request

```text
"Recommended on Vercel For large public filings, upload uses a small header sample to identify ticker/year, then switches to live SEC extraction. " 這部分可以不用顯示，upload limit也改完suggest 4.5 mb，不要讓user認為有效能不足的問題
```

## Project Assessment Request

```text
對於目前的專案你有什麼看法
```

## Risk Optimization Request

```text
好，先根據風險去優化目前的內容
```

## Ticker Or CIK Intake Request

```text
intake這邊應該要可以輸入ticker或是cik，都要做regex測試
```

## Prompt Logging Resume Request

```text
接下來的prompt 寫入
```
