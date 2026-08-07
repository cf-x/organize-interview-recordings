# Optional Feishu/Lark Sync

Use this workflow only when the user explicitly requests online synchronization or online document optimization. The local organization workflow works without any Feishu dependency.

## 1. Discover compatible tools

- Use a purpose-built Feishu/Lark connector or CLI already available in the environment.
- Read that tool's installed skills and references completely before authentication or document mutation.
- If no compatible tool is installed, report that online sync is unavailable and complete all local work. Do not install a connector or request credentials unless the user asks.
- Act as the user for user-owned documents only when the tool distinguishes user and bot identities.

## 2. Check authorization before discovery

Verify the authenticated identity, token validity, and required document/drive scopes before document lookup.

If authorization is absent, expired, or missing scopes:

1. Start a fresh authorization flow using the selected tool.
2. Show the exact official verification URL or QR code without rewriting it.
3. Store temporary QR images only inside the current workspace and keep them out of Git.
4. Stop online work until the user completes authorization.
5. Never ask the user to paste an access token into chat, a note, or a repository.

For application/bot scope errors, show the official administration URL returned by the tool and explain which scope is missing. Do not attempt user login to repair an application permission.

## 3. Build a local-to-online routing map

Search local indexes, manifests, YAML/JSON metadata, and note links before searching the online drive. Route in this order:

1. Exact same-session document linked by date, organization, and interview round.
2. Existing organization/project document for project facts and experiments.
3. Existing paper document for method, experiments, ablations, and contribution questions.
4. Existing technical-topic document for reusable theory or engineering questions.
5. Existing master interview document when no narrower owner exists.
6. Create a document only when no suitable owner exists and creation is authorized.

Do not route by filename alone. Compare organization, project, round, date, headings, and question meaning. Maintain a routing ledger with local path, online URL/token, reason, pre-write revision, and intended section.

## 4. Fetch narrowly and deduplicate

1. Fetch the target outline to a useful depth.
2. Fetch only the relevant section or keyword neighborhood.
3. Normalize questions by removing numbering, punctuation, organization prefixes, and wrappers such as `请介绍一下`.
4. Treat questions as duplicates when they test the same capability and their answers share the same evidence.
5. Merge stronger wording and preserve genuinely new evidence, failure cases, or metrics.
6. Do not append a complete local note when only a small number of questions are new.

Keep these content owners distinct:

- Recorded history stays in the session note.
- Reusable technical knowledge goes to the topic document.
- Project experiments go to the project document.
- Paper results go to the paper document.
- HR and career decisions stay in the interview or career document.

## 5. Write incrementally and serially

- Prefer precise replace/insert operations over whole-document replacement.
- Record the pre-write revision before each mutation.
- Perform one document write at a time and inspect the returned result, warnings, and revision.
- Re-fetch after replacement, deletion, partial success, or failure before reusing block identifiers.
- Never delete a source document, silently replace attachments, or create a competing copy when a suitable document already exists.

## 6. Apply purple AI provenance

For rich-text XML tools, use visible labels equivalent to:

```xml
<b><span text-color="purple">🟣 AI 生成优化回答：</span></b>
<b><span text-color="purple">🟣 AI 推测实验结果：</span></b>
<b><span text-color="purple">🟣 AI 重建问题：</span></b>
```

Do not recolor verified facts. Estimated table rows must contain visible `AI 推测` text even when a purple disclosure precedes the table.

## 7. Read back and audit

After every write:

1. Fetch the target section again.
2. Confirm new questions appear once and in the intended section.
3. Confirm AI labels are visibly purple.
4. Confirm verified facts were not rewritten as estimates.
5. Record the post-write revision and URL.

Treat failures, partial success, warnings, unchanged revisions, or empty read-back results as incomplete. The final report must list updated and deferred documents, inserted/merged/skipped counts, pre/post revisions, backup path, and authorization or permission blockers.
