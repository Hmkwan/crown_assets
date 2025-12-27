Remaining warnings triage (post-fixes)

Summary (from last full pytest run):
- Total remaining warnings: 12
- Breakdown (representative):
  - openpyxl.packaging.core: DeprecationWarning: uses datetime.datetime.utcnow() (created/modified) — 2 warnings
  - sqlalchemy.sql.sqltypes: DeprecationWarning: uses datetime.datetime.utcfromtimestamp() — 1 warning
  - sqlalchemy.sql.schema: DeprecationWarning: uses datetime.datetime.utcnow() — 2 warnings
  - small number of SQLAlchemy informational / RemovedIn20Warning about SQLAlchemy 2.0 compatibility (informational, requires dependency pinning or plan for upgrade)

Classification:
- External (third-party): openpyxl, SQLAlchemy internals — these are not in our codebase and should be addressed upstream.
- Internal: none remaining related to datetime.utcnow(); we replaced occurrences in tests/scripts and helper functions.

Proposed actions (short-term):
1. Suppress the known third-party DeprecationWarnings in `pytest.ini` (added entries) so CI output is actionable.
2. Open issues/PRs upstream for openpyxl / relevant SQLAlchemy modules where appropriate (I can prepare draft text for each issue).
3. For SQLAlchemy 2.0 warnings: pin SQLAlchemy to `<2.0` in requirements for now, and add an item to roadmap to update code for 2.0 compatibility.

Next steps I will take:
- Mark this triage as completed in the TODOs, then start implementing the `app/utils/db_management.py` refactor (parameterize SQL, whitelist filenames/tables, add unit tests).