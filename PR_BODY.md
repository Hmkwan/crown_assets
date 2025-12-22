# PR: 修复聊天附件上传与缩略图并添加 Playwright 烟雾测试

## 概要
修复聊天附件上传过程中的 FK 错误（将 `ChatAttachment.message_id` 设为可空并调整上传逻辑），添加按需缩略图生成与路径解析以修复容器内路径差异导致的 500 错误。附带：规范化脚本、即测脚本与 Playwright 烟雾测试 workflow。

## 主要变更
- `app/chat_routes.py` — 上传/缩略图/下载路径解析与日志
- `app/chat_models.py` — `message_id` 可空（迁移文件已添加）
- `scripts/normalize_attachment_paths.py` — dry-run / --apply，修复 dry-run 计数 bug
- `scripts/deploy_normalize_check.py` — 部署检查（dry-run 后非 0 退出以阻止盲目 apply）
- `scripts/validate_chat_playwright.py` — 改进以便在 CI 上执行（保存 artifacts / 非 0 退出）
- `tests/*` — 新增/更新测试（缩略图、迁移、规范化检测）
- `.github/workflows/playwright-smoke.yml` — Playwright 烟雾测试 CI
- `docs/DEPLOYMENT.md`、`.github/PULL_REQUEST_TEMPLATE.md` — 部署和 PR 模板

## 部署步骤（简要，见 `docs/DEPLOYMENT.md`）
- 备份 DB
- `alembic upgrade head`
- `python scripts/deploy_normalize_check.py`（或 `python scripts/normalize_attachment_paths.py --dry-run`）
- 如果 dry-run 显示潜在更改：在备份后执行 `python scripts/normalize_attachment_paths.py --apply`
- 运行 Playwright 烟雾测试校验（可选）：`python scripts/validate_chat_playwright.py --headless --save-screenshots`

## 合并前检查
- [ ] `pytest -q` 相关测试通过
- [ ] 在 staging 上执行规范化脚本并确认 `--apply` 结果
- [ ] 备份完成并可回滚
- [ ] Playwright 烟雾测试在 CI 或 staging 运行成功（Artifacts 可用）

## 回滚步骤
1. 恢复 DB 备份
2. 回退代码
3. 通知团队并排查日志

---

分支建议：`fix/chat-attachments-thumbnail-ci`