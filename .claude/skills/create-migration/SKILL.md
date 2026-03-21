---
name: create-migration
description: Generate and apply an Alembic migration for schema changes. Use when adding/modifying SQLAlchemy models.
disable-model-invocation: true
---

1. Ask what model/column/table changed and get a short description (e.g. "add phone to clients")
2. Run: `cd /c/Arun/investment/backend && alembic revision --autogenerate -m "<description>"`
3. Show the generated file path and its full contents for review
4. Ask user to confirm before proceeding
5. On confirmation, run: `alembic upgrade head`
6. Verify with: `alembic current` and show output
7. Remind user: never hand-edit migration files after applying them
