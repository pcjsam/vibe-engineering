# Sample Prompts

## Requirement Prompt

Generate a web application for a Hackathon Leaderboard site. Allow users to enter their team information, including team members (name, email, title), project, and allow judges to rate projects.

## Plan Prompt

System Prompt:
You are a senior architect planning a web application.
Create three planning notes: ADR, design-high, and design-low.
Each must include a session_id to link back to this run.

User Prompt:
Inputs:
Requirements:
{requirements_json}

Principles:
{principles_note_text}

Optional tech stack (use defaults if omitted):
{user_provided_stack or
"Frontend: React + TypeScript + shadcn/ui + Tailwind + Vite;
Backend: Python FastAPI + Motor (MongoDB Atlas);
Embeddings: Voyage AI;
Testing: Vitest / Pytest;
Linting: ESLint + Ruff + Black."}

Rules:
- Output a JSON object with keys: adr, design_high, design_low.
- Each note must include the following schema and a session_id. The session ID is equal in all notes related to the same development cycle (init > specify > plan > ...)