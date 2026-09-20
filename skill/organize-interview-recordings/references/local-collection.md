# Local Knowledge Search and Cross-Session Collection

Use this workflow when the user wants reusable interview preparation documents across multiple sessions.

## Authorized sources

Search the active workspace and only additional local roots explicitly authorized by the user. Treat those additional roots as read-only unless the user separately requests edits. Read files relevant to the questions being reconstructed, and link the source when it materially changes an optimized answer.

Do not publish local paths, source documents, resumes, recordings, transcripts, personal identifiers, private company details, or credentials. Replace machine-specific paths with configurable placeholders in any reusable or public artifact.

## Suggested layout

Keep generated Markdown under the active interview-recording workspace. Adapt names to the user's language and existing structure.

```text
interview-notes/
  YYYYMMDD_organization_round.md
interview-question-bank/
  projects/
    project-name.md
  technical.md
  coding.md
  hr.md
  other.md
interview-index.md
```

Create only the collection documents needed by retained questions. Preserve stable filenames and reuse an existing layout when one is already established.

## Ownership and routing

The canonical session note retains complete interview context and the historical answer. The collection is a reusable preparation view. Assign every retained semantic question to one primary owner:

1. Project-grounded questions go to the relevant project document.
2. Reusable theory, architecture, model, data, evaluation, or system-design questions go to the technical document.
3. Coding exercises, algorithms, debugging, SQL, and implementation prompts go to the coding document.
4. Motivation, career choice, availability, compensation, location, collaboration, strengths, weaknesses, and candidate questions go to the HR document.
5. Valuable questions that fit none of these go to the other document.

When a question spans categories, choose the category that best matches what the interviewer tested. Add a link from a secondary document only when it materially improves discovery; do not duplicate the full block.

## Semantic deduplication

Before inserting a question, search a compact catalog of primary collection headings, then read candidate blocks. Inspect all headings on first indexing, ambiguous matches or requested global cleanup. Compare the tested capability, constraints, and expected answer while ignoring organization-specific preambles and wording.

- If meaning is equivalent, update the existing canonical block. Add the new session link and merge only new evidence, tradeoffs, failure cases, or a stronger answer.
- If a follow-up tests a distinct capability, keep it separate.
- If two collection blocks are duplicates, back up the files, preserve the stronger block, merge source links, and replace the weaker block with a link.
- Never rewrite the historical answer in the canonical session note during collection deduplication.

Each canonical collection question should include the normalized question, source-session links, concise historical answer points, a purple-labeled optimized answer, source links for imported facts, and boundaries or uncertainty where evidence is incomplete.

## Index and audit

Update the master index with the session note, recording, transcript status, retained-question count, and collection documents touched. Verify that each retained question has one primary owner, links resolve, likely duplicates were reviewed, and AI labels use the purple provenance convention. Report inserted, merged, linked, and deferred counts.

## Catalog and stable ownership

Use `scripts/question_catalog.py build --root /workspace --file topics/project.md --file topics/technical.md --catalog /workspace/.interview-state/questions.json` to create a compact catalog from explicitly selected primary files. Include all primary owners; exclude learning views, backups and session notes. Query with `query --catalog <path> --text "question keywords" --limit 8`.

The query is lexical candidate retrieval, not semantic deduplication. No hit does not establish novelty: try synonyms, related project and broader headings before adding a question. Before using a hit, verify the owner file's SHA-256 or rebuild the catalog after edits; the helper records freshness but does not refresh automatically.

New primary questions get an explicit stable `<a id="question-unique-id"></a>` directly below their H2 heading. Preserve IDs on renaming; keep older anchors as aliases. Never derive persistent IDs from changing question wording. Legacy entries can be located by owner/title until an ID is assigned during their next authorized edit.

Maintain a private per-session ownership ledger with `session_question_anchor`, `owner`, `primary_anchor`, `action` (inserted/merged/linked/deferred), and any deferred reason. Check every retained question is accounted for and every resolved question has exactly one primary owner; explicit unresolved entries stay deferred. Multiple source questions may map to one primary question, so report those counts separately. Validate all resolved anchors after writing.

## Keep updates small

Full historical answers remain in session notes. In the collection, merge repeated historical points and preserve only meaningful differences with source links. Do not append another dated paragraph for unchanged evidence. Update an AI answer only for a substantive improvement; otherwise add the source link alone.

Learning editions are derived views, not additional primary owners. Refresh affected view sections only when that view is in the requested scope; otherwise record that it is stale. Do not rewrite all older session notes to enforce a new style version. Audit touched content strictly and report legacy limitations separately.
