# 部署与迁移指南（聊天附件修复相关）

## 目标
确保历史数据中的附件路径能被服务正确识别，并在升级后所有缩略图/下载接口不再返回 5xx 错误。

## 必备步骤（严格顺序）

1. 备份数据库（强制）
   - 备份 Postgres 数据库快照或导出 SQL

2. 升级代码并执行 Alembic migration
   - `git checkout <release-branch>`
   - `pip install -r requirements.txt`
   - `alembic upgrade head`

3. 运行规范化脚本（dry-run → apply）
   - 先 dry-run：`python scripts/normalize_attachment_paths.py --dry-run` 或 `python scripts/deploy_normalize_check.py`（会在检测到潜在更改时以非 0 退出）
   - 检查输出，确认将更新的记录（数量与示例）
   - 如确认：`python scripts/normalize_attachment_paths.py --apply`

   注意：脚本会直接更新 DB，务必在生产运行前备份并在 staging 先试跑一次。

4. 验证步骤
   - 在服务器上运行小型健康检查脚本：`python scripts/check_attach.py --sample-ids 6,8,10`
   - 检查返回 HTTP 状态和响应类型（缩略图应为 image/png）

5. 运行 Playwright 烟雾测试（可选，但推荐）
   - `python scripts/validate_chat_playwright.py --headless --save-screenshots`
   - 检查 `scripts/playwright_artifacts/` 内的截图以及 `scripts/playwright_server_logs.txt`

## 回滚策略
- 如果 upload/thumbnail 仍有严重异常：
  - 立即恢复 DB 备份
  - 回退应用代码
  - 联系负责人并审查 `scripts/playwright_server_logs.txt`

## 其他注意事项
- 本脚本对文件路径的匹配做了常见前缀替换（如 `/app/app/uploads` -> `/app/uploads`），若你的部署有不同路径模式，请先在 staging 环境测试并更新 `scripts/normalize_attachment_paths.py` 的路径替换规则。