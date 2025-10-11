Awesome—here’s a tight blueprint you can build this weekend.

# CLI: `mem-spec` (spec-kit style, memory-backed)

## 1) High-level architecture

| Layer         | Choice                                   | Notes                                                                              |
| ------------- | ---------------------------------------- | ---------------------------------------------------------------------------------- |
| CLI framework | **Python + Typer** (or Node + Commander) | Fast to scaffold, great DX.                                                        |
| Memory store  | **MongoDB Atlas**                        | Docs for atomic notes; **Atlas Vector Search** for retrieval; hybrid filters.      |
| Embeddings    | **Voyage AI**                            | Store vectors on `notes.embedding`.                                                |
| LLMs          | **FireworksAI / Meta (Llama)**           | Provider-agnostic via small adapter.                                               |
| Repo I/O      | Git                                      | Render Markdown views (ADRs/specs) into `/docs/…`; memory remains source of truth. |

---

## 2) Data model (MongoDB)

**Collections**

* `projects(_id, slug, repo_url, created_at, owners[...])`
* `notes(_id, project_id, type, title, text, fields{…}, links[ids], tags[], embedding, created_by, updated_at)`

  * `type ∈ {principle, requirement, adr, design-high, design-low, threat, test-spec, task, code-fact, ci-fact}`
* `edges(_id, src_id, dst_id, rel)` where `rel ∈ {satisfies, implements, tests, supersedes, blocks, duplicates}`
* `facts(_id, project_id, kind, payload, ts)` for PRs, CI, coverage.

**Vector index (Atlas)**

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {"type": "vector", "dimensions": 1024, "similarity": "cosine"},
      "type": {"type": "token"},
      "tags": {"type": "token"},
      "project_id": {"type": "token"}
    }
  }
}
```

---

## 3) CLI surface (commands)

| Command                | What it does                                                    | Inputs → Outputs                                  |
| ---------------------- | --------------------------------------------------------------- | ------------------------------------------------- |
| `mem-spec init`        | Create a project + load principles/guidelines                   | repo URL → `projects` doc                         |
| `mem-spec specify`     | Create **requirements + user stories** as **notes**             | prompt / yaml → `notes:type=requirement`          |
| `mem-spec plan`        | Build **high/low-level design + ADRs**                          | constraints → `notes:type=adr/design-*` + `edges` |
| `mem-spec tasks`       | Explode plan into **actionable tasks** with **test-spec** stubs | plan ids → `notes:type=task,test-spec`            |
| `mem-spec implement`   | Agent recall + code patch proposal; write back **code-facts**   | task id → PR link + `facts`                       |
| `mem-spec recall`      | Retrieve relevant memory for a scope (service/file)             | scope → ranked notes                              |
| `mem-spec render`      | Generate Markdown ADRs/specs directory from memory              | memory → `/docs/…` markdown                       |
| `mem-spec gate`        | Pre-PR check: ensure required links exist                       | PR num → pass/fail + missing items                |
| `mem-spec consolidate` | Cluster, dedupe, supersede old ADRs; write summaries            | project → updated notes/edges                     |
| `mem-spec import`      | Ingest existing Markdown ADRs/specs                             | repo path → notes/edges                           |

---

## 4) Memory write/recall patterns

**Write (ingest)**

1. Create `note` with text + `fields` (e.g., `owner`, `risk`, `component`, `files[]`).
2. Compute embeddings (Voyage) → save to `embedding`.
3. Add `edges` to link requirement→ADR→task→test-spec.

**Recall (hybrid)**

* Vector query on `embedding` **+** filters: `project_id`, `type in (...)`, `component`, `files contains "src/billing/*"`.
* Optional graph walk: start from a task, expand to upstream ADRs and downstream test-specs.

---

**Note schema (Pydantic)**

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Note(BaseModel):
    project_id: str
    type: str
    title: str
    text: str
    fields: Dict[str, str] = {}
    tags: List[str] = []
    links: List[str] = []
    embedding: Optional[List[float]] = None
```

**Vector query (Motor)**

```python
pipeline = [
  {"$search": {"index": "notes_vec",
    "compound": {
      "must": [
        {"knnBeta": {"vector": query_vec, "path": "embedding", "k": 16}},
        {"equals": {"path": "project_id", "value": project_id}}
      ],
      "should": [{"equals": {"path": "type", "value": want_type}}]
    }}},
  {"$limit": 16}
]
results = await db.notes.aggregate(pipeline).to_list(16)
```

---

## 6) Workflows per stage (what the command should do)

### `init`

* Create `project`, seed `principles` & `guidelines` as `notes:type=principle`.
* Optionally import existing `/docs` markdown via `import`.

### `specify`

* Turn user stories/requirements (prompt/YAML) → atomic `requirements`.
* Auto-tag components, risks, **link** to principles.
* Emit `render` preview for PR (human review).

### `plan`

* For each requirement, create:

  * `design-high`, `design-low`, and at least one `adr`.
  * Link to components/files; attach acceptance criteria.
* Create `threat` notes (STRIDE checklist) and link to plan.

### `tasks`

* Expand implementation tasks with **test-spec** per task (unit/e2e).
* Each task links upstream to its ADR/design + downstream to test-spec.

### `implement`

* **Recall** memory for the task scope (files/component/ADR).
* Generate patch/proposal with the coding LLM; open PR.
* Write `facts` back: PR URL, CI outcome, coverage delta.

### `render`

* Generate Markdown ADRs/specs from memory (MADR template) for humans; do not treat as source of truth.

---

## 7) Rendering ADRs/specs (views)

* `mem-spec render` → `/docs/adr/NNN-title.md`, `/docs/specs/feature-x.md`
* Each file includes backlinks (from `edges`) so humans see traceability.
* Commit generated docs; reviewers comment on views; CLI reconciles edits back into notes (optional).

---

## 8) Consolidation & hygiene

* Nightly job: cluster similar ADRs; mark **`supersedes`** edges; synthesize a **living summary** per component.
* Prune orphaned tasks; surface **spec vs code drift** (e.g., files changed with no linked ADR).

---

## 9) DX niceties you’ll appreciate at a hackathon

* **Profiles**: `mem-spec auth set --provider voyage --op item "Voyage Key"` to fetch keys via 1Password.
* **Scoping**: `--scope "services/billing/**"` limits recall to relevant memory.
* **Templates**: ship MADR & test-spec templates; allow user overrides in `/.mem-spec/templates`.

---

## 10) Success criteria (measurable)

* PRs missing ADR/test-spec drop to near zero (CI gate).
* First-try build pass rate ↑ (memory-informed coding).
* Coverage delta per merged task ≥ target.
* Time-to-fix failed agent PRs ↓ (previous attempts/causes recalled automatically).
