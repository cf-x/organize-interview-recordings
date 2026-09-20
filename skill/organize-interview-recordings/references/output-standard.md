# Interview Note Output Standard

## Source and estimate policy

Use four distinct truth levels:

| Level | Label and treatment |
| --- | --- |
| Recorded fact | Put in `我的回答（整理）` or `面试官回答（整理）`; preserve meaning and known numbers. |
| Local project fact | Use directly in the AI answer and keep it consistent across sessions. |
| Completed but locally undocumented experiment | Default to `结果待核对`; an explicitly requested estimate must disclose assumptions and missing evidence. |
| Unknown history | Write `未保留完整回答`; never backfill it as a historical quote. |

Historical answers may be wrong. Keep the wrong claim in the historical field, then correct it in the AI field.

## AI color contract

Use purple only as provenance, not decoration. Recorded answers and verified source facts remain normal text.

- Local Markdown AI answer label: `<span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span>`
- Local Markdown estimate label: `<span style="color:#7C3AED"><strong>🟣 AI 推测实验结果：</strong></span>`
- Feishu rich-text label: `<b><span text-color="purple">🟣 AI 生成优化回答：</span></b>` or `<b><span text-color="purple">🟣 AI 推测实验结果：</span></b>`
- Reconstruction of an inaudible question: use `<span style="color:#7C3AED"><strong>🟣 AI 重建问题：</strong></span>` and state the evidence used.

Color the label, not necessarily the full paragraph. Never use purple for a recorded answer or a source-backed number. If a table mixes verified and estimated values, put `（AI 推测）` in each estimated row or cell and add a purple disclosure immediately before the table.

## Canonical template

```markdown
# YYYY-MM-DD Company Round

## 基本信息

- <span style="color:#7C3AED"><strong>🟣 AI 补充说明：</strong></span> 标注为“AI 生成/推测/重建”的内容基于本地资料和通用知识；估算需注明依据，不替代原始日志。
- **轮次：**
- **方向：**
- **录屏：**
- **转写：**
- **信息来源：**

## 问答记录

<a id="q1"></a>

### 1. Concise topic

- **时间：** 可核对的时间范围；无录音时注明原笔记来源。
- **面试官问：**
- **我的回答（整理）：**

<span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span>

- **结论：** 一句话回答核心问题。
- **做法：** 关键动作或机制。
- **验证：** 指标、对照与证据；有依据再报数。
- **边界：** 必要的条件、限制或待核对项。

### 2. Candidate question

- **我的问题（整理）：**
- **面试官回答（整理）：**

<span style="color:#7C3AED"><strong>🟣 AI 生成的更好追问：</strong></span>

- **职责：** 新人前三个月主要负责什么？
- **验收：** 用哪些指标判断工作效果？

## 面试总结

- **考察重点：**
- **主要问题：**
- **改进方向：**
```

For a coding test, replace `面试官问` with `题目`, `我的回答` with `我的作答`, and use `AI 补充的更好解法`.

## What to retain

Retain questions that reveal at least one of these:

- project ownership, experiment design, evidence, or failure analysis
- core technical concepts, code, system design, data, evaluation, or deployment
- product reasoning, business constraints, or tradeoffs
- motivation, career choice, availability, collaboration, or candidate questions

Merge redundant follow-ups. Remove greetings, repeated restatements, tool setup chatter, and empty acknowledgements.

## Optimized answer shape and style

AI 优化回答统一使用「关键词 + 短句」分点作答，适用于单场笔记、跨场题库、代码解法、反问建议和用户要求的飞书同步。

- **格式：** 紫色 AI 标签单独一行，空一行后写列表。每点用 `- **关键词：** 短句。`；在线使用等价的列表块，保留紫色标签。
- **长度：** 通常 3–5 点，每点 1–2 个短句。简单题可更少，复杂题按子问题分组；不为凑点数添加内容。
- **顺序：** 先结论，再按需补机制、做法、验证和边界。关键词随题意选择，不必每题机械套用相同标题。
- **表达：** 用自然、直接的中文和具体动词。讲个人工作时用“我负责”“我做过”；省略铺垫、口头连接词和重复结论。
- **完整性：** 保留关键条件、因果关系、数字口径、证据等级和个人职责。关键词用于提示重点，不能只堆名词、缩写或箭头。
- **技术细节：** 少见术语首次出现时简释。必要公式、张量形状和代码单独列出，不能为了短而删掉解题步骤。
- **事实边界：** 已做、建议、估算、待核对分别写清。历史回答保持忠实，不随优化答案改写事实。
- **避免：** 大段口述稿、整段引号、长句套短标签，以及“形成闭环”“从多个维度”“实现赋能”等报告用语。避免比喻、拟人、口号和装饰性排比。
- **例外：** 用户明确要求逐字稿、完整自我介绍或特定格式时，按用户要求交付。

### 示例：如何处理长尾识别错误？

以下为改进方案示例，不能当作已完成的项目经历：

```markdown
<span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span>

- **问题：** 长尾场景识别差，先按错误类型拆分。
- **数据：** 补对应样本，调整训练采样比例。
- **验证：** 单看长尾测试集，同时检查整体 WER。
- **边界：** 这是改进方案；实际收益需实验确认。
```

### 完稿检查

1. AI 回答是否使用列表，每点都有清晰关键词？
2. 是否一眼能找到结论，每点只讲一个重点？
3. 长句、重复内容和口头铺垫是否已删减？
4. 公式、条件、指标口径和事实边界是否仍完整？
5. 是否仍有换成列表后照样冗长的段落？如有，继续拆分或精简。

## Missing results and conflicting sources

Do not supply default numeric improvement ranges. Even a confirmed completed experiment does not establish its result. Preserve the recorded claim and mark missing results as `结果待核对`.

When the user requests an estimate, label it purple and state its baseline, metric, slice, absolute/relative units, assumptions and derivation. If these cannot support a range, explain what measurement is needed. Never normalize contradictory historical results into one invented number.

Check provenance inside local materials: verified logs, user recollection, plans and previous AI estimates retain their original evidence level. Distinguish personal demos from production, mock tools from real APIs, preference judgments from factual accuracy, and plans from completed work.

## Common transcript hallucinations

Reject repeated or context-free phrases such as:

- `感谢观看`
- `请不吝点赞`
- repeated `订阅`, `打赏`, `好`, or punctuation
- a sentence repeated dozens of times with no turn-taking
- confident words produced over silent audio

Use timestamps, audio energy, adjacent turns, and visible frames to decide. Preserve raw transcripts even when unusable.
