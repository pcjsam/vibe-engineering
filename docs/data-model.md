# Data Model: Memory-Driven Development (with Local Claude Code Execution)

This model is **memory-first** (MongoDB Atlas + Voyage embeddings). Markdown is rendered as **views**; the source of truth is the **memory store**.

---

## 1) Entities Overview

| Entity      | Role         | Description                                                                                                                           |
| ----------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Note**    | Knowledge    | Atomic project knowledge (principles, requirements, ADRs, designs, tasks, test-specs, agent specs, etc.). Embeddable and retrievable. |
| **Edge**    | Relationship | Directed link between notes (e.g., *Task implements Requirement*, *Test verifies Task*). Enables traceability and multi-hop recall.   |
| **Fact**    | Observation  | Immutable event/metric (builds, tests, coverage, **agent runs** on the dev machine). Feeds analytics/learning loops.                  |
| **Project** | Scope        | Logical container for all notes/edges/facts for an app.                                                                               |

> You can skip **edges** early and store related IDs in each note’s `links[]`. Add edges when you need many-to-many traceability.

---

## 2) Collections

* `projects(_id, slug, owners[], created_at, repo_url?)`
* `notes(_id, project_id, type, title, text, fields{}, tags[], embedding?, links[], created_by, updated_at)`
* `edges(_id, src_id, dst_id, rel)`
* `facts(_id, project_id, kind, payload{}, ts)`

**Vector index (Atlas Vector Search) on `notes.embedding`** with `project_id`, `type`, `tags`, and relevant `fields.*` as filterable keys.

---

## 3) Notes

A **Note** is the smallest unit of knowledge.

### Common Structure

```json
{
  "_id": "note_abc",
  "project_id": "proj_app",
  "type": "adr",
  "title": "Example",
  "text": "Human-readable content...",
  "fields": { "component": "billing" },
  "tags": ["adr","billing"],
  "embedding": [/* vector */],
  "links": ["note_xyz"],             // optional, if skipping edges
  "created_by": "y",
  "updated_at": "2025-10-11T00:00:00Z"
}
```

### Note Types (recommended)

| Type            | Purpose                                  | Key `fields`                                                                   |
| --------------- | ---------------------------------------- | ------------------------------------------------------------------------------ |
| **principle**   | Engineering constitution/guardrails.     | `domain`, `priority`, `owner`                                                  |
| **requirement** | Functional or non-functional user story. | `priority`, `component`, `user_story`, `acceptance`                            |
| **adr**         | Architecture decision + rationale.       | `status`, `date`, `decision`, `context`, `consequences`                        |
| **design-high** | System/diagram level description.        | `components[]`, `dependencies[]`                                               |
| **design-low**  | Module/API schemas & flows.              | `module`, `interface`, `data_flows`                                            |
| **threat**      | Security/reliability risk + mitigation.  | `risk_level`, `mitigation`, `component`                                        |
| **test-spec**   | What to test and how.                    | `scope`, `method`, `coverage_target`                                           |
| **task**        | Executable work unit.                    | `assignee`, `status`, `component`, `est_time`, **`executor`**, **`exec_spec`** |
| **agent-spec**  | Agent capabilities/policy/profile.       | `agent`, `capabilities[]`, `tools[]`, `limits`, `prompting`, `working_dir`     |
| **code-note**   | Summary of code elements (not raw code). | `file`, `symbol`, `hash`, `loc`, `imports[]`, `summary`                        |
| **ci-policy**   | Local quality gates/policies.            | `min_coverage`, `required_checks[]`                                            |

#### Task note (extended for local Claude Code)

* `fields.executor`: `"claude-code"` or `"human"`
* `fields.exec_spec`: runtime contract the agent will follow locally:

  * `working_dir`, `commands[]` (allowed), `entry_task`, `artifacts[]` (files to produce), `env` (names, not values), `approval_required` (bool)

**Example — `task`**

```json
{
  "_id": "note_task_teams_create_001",
  "project_id": "proj_hack_leaderboard",
  "type": "task",
  "title": "Implement Create Team endpoint and form",
  "text": "POST /teams with validation; React form using shadcn/ui; persist to MongoDB.",
  "fields": {
    "assignee": "y",
    "status": "open",
    "component": "teams",
    "est_time": "2h",
    "executor": "claude-code",
    "exec_spec": {
      "working_dir": ".",
      "commands": ["uv run pytest -q", "uv run fastapi dev", "pnpm test", "pnpm lint", "pnpm build"],
      "artifacts": ["api/routes/teams.py", "src/components/CreateTeamForm.tsx", "tests/test_teams.py"],
      "env": ["MONGODB_URI", "VOYAGE_API_KEY"],
      "approval_required": true
    }
  },
  "tags": ["teams","backend","frontend"],
  "embedding": null,
  "created_by": "y",
  "updated_at": "2025-10-11T10:30:00Z"
}
```

**Example — `agent-spec` (Claude Code local)**

```json
{
  "_id": "note_agent_spec_claude_code",
  "project_id": "proj_hack_leaderboard",
  "type": "agent-spec",
  "title": "Claude Code Local Profile",
  "text": "Local execution profile for Claude Code running on developer machine.",
  "fields": {
    "agent": "claude-code",
    "capabilities": ["read-edit-files","run-commands","write-tests","refactor"],
    "tools": ["bash","node","pnpm","python","uv","pytest","ruff","black","mypy","vite","vitest","playwright"],
    "limits": {"max_runtime_sec": 900, "max_changes": 50},
    "prompting": {"style": "plan-before-act", "require-tests": true},
    "working_dir": "."
  },
  "tags": ["agent","claude","local"],
  "embedding": null,
  "created_by": "y",
  "updated_at": "2025-10-11T10:30:00Z"
}
```

---

## 4) Edges

**Purpose:** traceability and dependency context.

**Structure**

```json
{ "_id": "edge_1", "src_id": "note_req_001", "dst_id": "note_task_teams_create_001", "rel": "implements" }
```

**Common `rel` values:** `implements`, `tests`, `satisfies`, `decided-by`, `supersedes`, `blocks`, `duplicates`.

> Optional in v1: if omitted, store related IDs in `links[]` on notes.

---

## 5) Facts

**Facts** record outcomes and telemetry, including **local Claude Code runs**.

**Structure**

```json
{
  "_id": "fact_1",
  "project_id": "proj_hack_leaderboard",
  "kind": "test-run",
  "payload": { "task_id": "note_task_teams_create_001", "command": "pytest -q", "passed": true, "summary": "23 passed", "coverage_delta": "+2.4%" },
  "ts": "2025-10-11T10:40:00Z"
}
```

**Recommended `kind` values**

* `build`, `test-run`, `coverage`, `benchmark`, `lint`, `commit`
* **`agent-run`** (for Claude Code local execution)
* `code-summary` (automated code note refresh)

**Example — `agent-run` (Claude Code)**

```json
{
  "_id": "fact_agent_run_20251011_1",
  "project_id": "proj_hack_leaderboard",
  "kind": "agent-run",
  "payload": {
    "agent": "claude-code",
    "task_id": "note_task_teams_create_001",
    "executor": "local",
    "working_dir": ".",
    "commands": [
      {"cmd": "pnpm lint", "exit_code": 0},
      {"cmd": "uv run pytest -q", "exit_code": 0, "summary": "23 passed"}
    ],
    "files_changed": [
      "api/routes/teams.py",
      "src/components/CreateTeamForm.tsx",
      "tests/test_teams.py"
    ],
    "artifacts": ["api/routes/teams.py","src/components/CreateTeamForm.tsx","tests/test_teams.py"],
    "result": "success",
    "notes": "Implemented endpoint and form; tests passing."
  },
  "ts": "2025-10-11T10:45:00Z"
}
```

---

## 6) Engineering Constitution (store as a `principle` note)

### Architecture

* **Frontend:** React + TypeScript, shadcn/ui, Tailwind, Vite, React Router
* **Backend:** Python FastAPI (async), Uvicorn (dev)
* **Database:** MongoDB Atlas (app: `teams`, `ratings`), plus memory (`projects`, `notes`, `edges`, `facts`)
* **Embeddings:** Voyage AI; Atlas Vector Search for recall
* **SoC:** FE = UX/state; BE = domain logic/validation/persistence

### Frontend Standards

* **Testing:** Vitest + React Testing Library; E2E via Playwright
* **Quality:** ESLint (typescript-eslint), Prettier, TS strict mode
* **Security & A11y:** sanitize inputs; WCAG AA; semantic HTML/ARIA
* **Build:** code splitting, lazy routes

### Backend Standards

* **Validation:** Pydantic v2 models at boundaries
* **DB Access:** `motor` (async)
* **Testing:** pytest (+ httpx for API), coverage.py
* **Quality:** Ruff (lint), Black (format), mypy (optional)
* **Security:** least-priv Mongo user; secrets via env/secret manager; CORS limited to FE origin

### Data & Memory

* **App Data:**

  * `teams`: `{ name, project, members[{name,email,title}], created_at }`
  * `ratings`: `{ team_id, judge, score, notes, created_at }`
* **Memory Data:**

  * `notes` (principle, requirement, adr, design-high, design-low, threat, test-spec, task, agent-spec, code-note, ci-policy)
  * `edges` (optional graph)
  * `facts` (build/test/coverage/benchmark/lint/commit/**agent-run**)
* **Code in Memory:** store **summaries**, not raw code (`code-note`)

### Testing & Gates (local)

* Each **task** requires a **test-spec** prior to implementation
* Minimum local checks: FE+BE unit tests, linters/formatters, type checks
* Coverage target: **+2% delta** per feature until baseline


### Observability & Performance

* **Logging:** structured (JSON on BE)
* **Perf (initial budgets):** FE TTI < 2s (dev), API p50 < 50ms, memory recall < 100ms

### Security & Privacy

* Validate & sanitize inputs; least-privilege DB; no secrets in repo; minimal retention for personal data

### Change Management

* Small tasks with tests; ADR changes **supersede** older ones with links
* Weekly memory consolidation: dedupe, summarize, re-embed stale notes

---

## 7) Execution Flow (Specify → Plan → Tasks → Implement with Claude Code)

1. **Specify**

   * Prompt → atomic `requirement` notes (embedded).

2. **Plan**

   * Create `adr`, `design-high`, `design-low`, `threat` notes linked to requirements.

3. **Tasks**

   * Expand to `task` notes (each with `test-spec`).
   * For Claude Code execution, set `fields.executor = "claude-code"` and define `fields.exec_spec`.

4. **Implement** (local developer machine)

   * Recall memory (vector + filters).
   * Launch **Claude Code** against the working directory with the task’s `exec_spec`.
   * Record results as `facts(kind="agent-run")`, plus `test-run`/`coverage` facts.
   * Optionally emit/update `code-note` summaries for changed files.

---

## 8) Minimal Examples (copy as seeds)

**Principles (note)**

```json
{
  "_id": "note_principles_001",
  "project_id": "proj_hack_leaderboard",
  "type": "principle",
  "title": "Engineering Constitution",
  "text": "Architecture: React+TS (shadcn/ui, Tailwind, Vite) + FastAPI + MongoDB Atlas; Embeddings: Voyage; Docs as views; memory is source of truth. Frontend: Vitest/RTL/Playwright, ESLint/Prettier, TS strict, WCAG AA. Backend: pytest/httpx, coverage, Ruff/Black, Pydantic v2, motor. Security: input validation, least-privileged DB, secrets via env. Data: app collections (teams, ratings), memory collections (projects, notes, edges, facts). Code in memory = summaries only. Tasks must include test-spec; local gates run tests/linters/types. Coverage +2% delta until baseline. Claude Code executes tasks locally per agent-spec; results captured as agent-run facts.",
  "fields": { "domain": "web-app", "priority": "high", "owner": "engineering" },
  "tags": ["principles","frontend","backend","quality","security","memory","claude"],
  "embedding": null,
  "created_by": "y",
  "updated_at": "2025-10-11T10:35:00Z"
}
```

**Agent Spec (note)**

```json
{
  "_id": "note_agent_spec_claude_code",
  "project_id": "proj_hack_leaderboard",
  "type": "agent-spec",
  "title": "Claude Code Local Profile",
  "text": "Local capabilities, tools, limits, and prompting policy for Claude Code.",
  "fields": {
    "agent": "claude-code",
    "capabilities": ["read-edit-files","run-commands","write-tests","refactor"],
    "tools": ["bash","node","pnpm","python","uv","pytest","ruff","black","mypy","vite","vitest","playwright"],
    "limits": {"max_runtime_sec": 900, "max_changes": 50},
    "prompting": {"style": "plan-before-act", "require-tests": true},
    "working_dir": "."
  },
  "tags": ["agent","claude","local"],
  "embedding": null,
  "created_by": "y",
  "updated_at": "2025-10-11T10:35:00Z"
}
```

**Task (note)**

```json
{
  "_id": "note_task_leaderboard_sort_001",
  "project_id": "proj_hack_leaderboard",
  "type": "task",
  "title": "Implement Leaderboard sort by average rating",
  "text": "Aggregate ratings by team; compute average; expose GET /leaderboard?sort=avg_rating; show table in React.",
  "fields": {
    "assignee": "y",
    "status": "open",
    "component": "leaderboard",
    "est_time": "2h",
    "executor": "claude-code",
    "exec_spec": {
      "working_dir": ".",
      "commands": ["uv run pytest -q", "pnpm test", "pnpm lint", "pnpm build"],
      "artifacts": ["api/routes/leaderboard.py","src/pages/Leaderboard.tsx","tests/test_leaderboard.py"],
      "env": ["MONGODB_URI"],
      "approval_required": true
    }
  },
  "tags": ["leaderboard","backend","frontend"],
  "embedding": null,
  "created_by": "y",
  "updated_at": "2025-10-11T10:35:00Z"
}
```

**Agent Run (fact)**

```json
{
  "_id": "fact_agent_run_20251011_leaderboard_1",
  "project_id": "proj_hack_leaderboard",
  "kind": "agent-run",
  "payload": {
    "agent": "claude-code",
    "task_id": "note_task_leaderboard_sort_001",
    "executor": "local",
    "working_dir": ".",
    "commands": [
      {"cmd": "pnpm lint", "exit_code": 0},
      {"cmd": "uv run pytest -q", "exit_code": 0, "summary": "12 passed"},
      {"cmd": "pnpm build", "exit_code": 0}
    ],
    "files_changed": [
      "api/routes/leaderboard.py",
      "src/pages/Leaderboard.tsx",
      "tests/test_leaderboard.py"
    ],
    "artifacts": ["api/routes/leaderboard.py","src/pages/Leaderboard.tsx","tests/test_leaderboard.py"],
    "result": "success",
    "notes": "Feature implemented; tests passing."
  },
  "ts": "2025-10-11T10:50:00Z"
}
```

**Test Run (fact)**

```json
{
  "_id": "fact_test_run_20251011_leaderboard_1",
  "project_id": "proj_hack_leaderboard",
  "kind": "test-run",
  "payload": { "task_id": "note_task_leaderboard_sort_001", "command": "pytest -q", "passed": true, "summary": "12 passed", "coverage_delta": "+1.8%" },
  "ts": "2025-10-11T10:51:00Z"
}
```

---

## 9) Minimal Traceability Chain

```
requirement -> adr/design-high/design-low -> task(executor=claude-code, exec_spec=…) -> test-spec
   ^                                                                    |
   |                                                                    v
  principle --------------------------------------------------------> facts(agent-run/test-run/coverage)
```
