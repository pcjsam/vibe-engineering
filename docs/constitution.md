# Engineering Constitution


## Architecture

* **Frontend:** React + TypeScript + shadcn/ui (Tailwind CSS)
* **Backend:** Python FastAPI (async-first)
* **Database:** MongoDB Atlas (document-first; schema via Pydantic models)
* **Embeddings:** Voyage AI (used for semantic memory and context retrieval)
* **Separation of Concerns:**

  * FE handles UX/state and presentation.
  * BE owns domain logic, validation, and persistence.

---

## Frontend (JS/TS + React)

* **Framework:** React + TypeScript
* **UI Components:** shadcn/ui (built on Radix)
* **Styling:** Tailwind CSS; use class-based composition, not inline styles
* **Build Tool:** Vite (fast dev server, hot reload, TypeScript-native)
* **Routing:** React Router v6
* **Testing:**

  * Unit: **Vitest**
  * Component/UI: **React Testing Library**
  * E2E: **Playwright**
* **Linting & Formatting:**

  * **ESLint** (`typescript-eslint` rules)
  * **Prettier** (format-on-save)
  * TypeScript strict mode: enabled (`noImplicitAny`, `strictNullChecks`)
* **Accessibility:**

  * Follow WCAG AA compliance.
  * Use semantic HTML and ARIA attributes.
* **Security:** Sanitize user input; validate API responses.
* **Build Targets:** Optimize bundles with code splitting and lazy loading.

---

## Backend (Python + FastAPI)

* **Framework:** FastAPI (async endpoints, `APIRouter` per domain)
* **Validation:** Pydantic v2 models for request/response schemas
* **Database Access:** Motor (async MongoDB driver)
* **Collections:**

  * `teams` – team and project info
  * `ratings` – judges’ evaluations
  * `leaderboard` – aggregated results
* **Testing:**

  * Unit: **pytest**
  * Integration/API: **httpx**
  * Coverage: **coverage.py**
* **Code Quality:**

  * **Ruff** – linting
  * **Black** – formatting
  * **mypy** – optional type checking
* **Security:**

  * Input validation, safe defaults
  * Least-privileged MongoDB user
  * Secrets in environment variables or 1Password
* **Server:** Uvicorn in dev; Gunicorn (Uvicorn workers) in prod

---

## Data & Memory

* **App Data:**

  * Stored in MongoDB collections (`teams`, `ratings`, `leaderboard`)
* **Memory Data:**

  * `notes` – requirements, ADRs, designs, tasks, test-specs, etc.
  * `edges` – relationships between notes (implements/tests/supersedes).
  * `facts` – immutable events (test runs, builds, benchmarks).
* **Embeddings:**

  * Use Voyage for text embeddings; stored in `notes.embedding`.
  * Store code summaries (not raw code) with file path, hash, and vector.

---

## Testing & Quality Gates

* Every **task** must have a **test-spec** before implementation.
* Pre-commit checks:
  * Run linting and formatting (FE & BE).
  * Run unit and integration tests.
  * No failing or skipped tests allowed in main branch.

---

## Developer Experience

* **Frontend Commands:**

  * `pnpm dev`, `pnpm test`, `pnpm lint`, `pnpm build`
* **Backend Commands:**

  * `uv run fastapi dev`, `pytest -q`, `ruff check`, `black --check`
* **Formatting:** enforced; matches CI formatting.
* **Docs generation:** `mem-spec render` → `/docs/*`
* **Small atomic changes:** prefer small commits and quick merges.

---

## Documentation

* **Memory as source of truth:** all specs, ADRs, and test-plans live as `notes`.
* **Markdown as view:** rendered for human review only.
* **Traceability:** Requirement → ADR → Design → Task → Test-spec → Fact.
* **Versioning:** Superseded ADRs remain linked; old context never deleted.

---

## Security & Privacy

* Validate and sanitize all user inputs.
* Enforce least-privilege database credentials.
* No secrets in code or Git history.
* Handle judge/team data per GDPR-style minimal retention.

