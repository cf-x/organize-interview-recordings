# Interview Note Output Standard

## Source and estimate policy

Use four distinct truth levels:

| Level | Label and treatment |
| --- | --- |
| Recorded fact | Put in `我的回答（整理）` or `面试官回答（整理）`; preserve meaning and known numbers. |
| Local project fact | Use directly in the AI answer and keep it consistent across sessions. |
| Completed but locally undocumented experiment | Give an `AI 推定的合理范围`; state that logs are unavailable locally. |
| Unknown history | Write `未保留完整回答`; never backfill it as a historical quote. |

Historical answers may be wrong. Keep the original claim in the historical field, then correct it in the AI field.

## AI color contract

Use purple only as provenance, not decoration. Recorded answers and verified source facts remain normal text.

- Local Markdown AI answer label: `<span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span>`
- Local Markdown estimate label: `<span style="color:#7C3AED"><strong>🟣 AI 推测实验结果：</strong></span>`
- Online rich-text label: `<b><span text-color="purple">🟣 AI 生成优化回答：</span></b>` or `<b><span text-color="purple">🟣 AI 推测实验结果：</span></b>`
- Reconstruction of an inaudible question: use `<span style="color:#7C3AED"><strong>🟣 AI 重建问题：</strong></span>` and state the evidence used.

Color the label, not necessarily the whole paragraph. Never use purple for a recorded answer or a source-backed number. If a table mixes verified and estimated values, put `（AI 推测）` in every estimated row or cell and add a purple disclosure before the table.

## Canonical template

```markdown
# YYYY-MM-DD Organization Round

## 基本信息

- <span style="color:#7C3AED"><strong>🟣 AI 补充说明：</strong></span> 标注为“AI 生成/推测/重建”的内容基于本地资料和通用知识；数字区间为合理估算，不替代原始日志。
- **轮次：**
- **方向：**
- **录屏：**
- **转写：**
- **信息来源：**

## 问答记录

### 1. Concise topic

- **面试官问：**
- **我的回答（整理）：**
- <span style="color:#7C3AED"><strong>🟣 AI 生成优化回答：</strong></span>

### 2. Candidate question

- **我的问题（整理）：**
- **面试官回答（整理）：**
- <span style="color:#7C3AED"><strong>🟣 AI 生成的更好追问：</strong></span>

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

## Optimized answer shape

Prefer this order when applicable:

1. Problem or observed failure
2. Constraint and rejected alternatives
3. Chosen design and implementation detail
4. Evaluation and result
5. Cost, limitation, or boundary
6. Next experiment or production safeguard

Do not force all six parts into simple theory or coding questions.

## Plausible range guidance

Ranges are reasoning defaults, not facts. Adjust them to model size, dataset, baseline, and domain.

| Topic | Usually defensible AI-estimated range |
| --- | --- |
| Mature-model overall WER/CER gain | about 0.3-1.5 absolute points or 3%-8% relative |
| Low-resource/hard-slice WER gain | about 0.8-2 absolute points or 5%-12% relative |
| Prompt repetition reduction | about 20%-40% relative; larger only with a defined failure subset |
| Router Top-1 language consistency | about 85%-95% for ordinary languages; 60%-80% for confusable pairs |
| No-prior vs known-language gap | about 0.3-1 absolute point after specialization |
| Full-expert fusion RTF increase | about 10%-30% at whole-model level when limited to late layers |
| 4x vs 8x acoustic downsampling | about 0.3-0.8 absolute accuracy-point tradeoff and 1.5-2x sequence compute |
| LLM Judge vs human agreement | about 75%-90% with a rubric and blind ordering |
| Human audit sample | about 5%-10% of generated preference/evaluation data |
| SFT/DPO preference difference | about 3-8 percentage points; factual accuracy may differ much less |

Always include the baseline, metric, test slice, and whether the range is absolute or relative.

## Common transcript hallucinations

Reject repeated or context-free phrases such as:

- `感谢观看`
- `请不吝点赞`
- repeated `订阅`, `打赏`, `好`, or punctuation
- a sentence repeated dozens of times with no turn-taking
- confident words produced over silent audio

Use timestamps, audio energy, adjacent turns, and visible frames to decide. Preserve raw transcripts even when unusable.
