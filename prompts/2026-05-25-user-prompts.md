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
