# Sample Prompts

## Requirement Prompt

Generate a web application for a Hackathon Leaderboard site. Allow users to enter their team information, including team members (name, email, title), project, and allow judges to rate projects.

## Plan Prompt

User Prompt:
Inputs:
Requirements:
{requirements_json}

Principles:
{principles_note_text}

Optional tech stack (use defaults if omitted):
{user_provided_stack or
"Frontend: React + TypeScript + shadcn/ui + Tailwind + Vite;
Backend: Python FastAPI + Pymongo (MongoDB Atlas);
Embeddings: Voyage AI;
Testing: Vitest / Pytest;
Linting: ESLint + Ruff + Black."}