# 功能：CI 与测试（CI & Testing）

## 概述
建议在 CI 中加入完整测试矩阵：Unit/Integration tests（带 Postgres）、Bandit、安全扫描、以及可选的 mypy 类型检查。

## 建议的 CI Job
1. Lint + Bandit
2. Unit tests (sqlite or in-memory fast suite)
3. Integration tests against Postgres (docker service), run `pytest -q` with `TEST_DATABASE_URI` 指向容器中的 Postgres
4. mypy (可分阶段逐步打开 strict 模式)
5. E2E（可选）: Playwright 或 Selenium 针对关键 UI 流程

## 现状
- 本地手动已验证 Docker Compose 下的 Postgres 测试能运行并通过（部分快照：40 passed,1 skipped）。
- 建议在 PR 模板中提醒运维在生产前执行 `alembic upgrade head`，并把 migration 运行写为部署 checklist。
