# PR 标题（简短）

> 修复：聊天附件上传与缩略图（包含迁移、测试、烟雾测试与部署步骤）

## 变更说明
- 修复：将 `ChatAttachment.message_id` 设为可空并修改上传逻辑，避免 FK 上传失败
- 新增：按需生成缩略图并增加路径分支解析（`_resolve_existing_path`）以解决容器路径差异
- 新增：`scripts/normalize_attachment_paths.py`（dry-run / --apply）用于历史数据规范化
- 新增：单元测试 `tests/test_chat_thumbnail_and_download.py`、`tests/test_chat_attachment_migrations.py`
- 新增：GitHub Actions workflow `playwright-smoke.yml` 用于运行 Playwright 烟雾测试并上传 artifacts

## 部署步骤（简要）
1. 备份数据库（强制）
2. 运行 Alembic migration (`alembic upgrade head`) 或等同的迁移流程
3. 运行规范化脚本（先 dry-run）：
   - `python scripts/normalize_attachment_paths.py --dry-run`
   - 验证输出后 `python scripts/normalize_attachment_paths.py --apply`
4. 在部署后执行 Playwright 烟雾测试以验证缩略图/下载（可选）：
   - `python scripts/validate_chat_playwright.py --headless --save-screenshots`

## 合并前检查（Checklist）
- [ ] 单元测试通过（`pytest -q`）
- [ ] 在 staging 环境运行规范化脚本并验证实际改动
- [ ] 备份已经创建并成功可恢复
- [ ] Playwright 烟雾测试在 staging 或 CI 成功（截图保存并上传）

## 回滚计划
- 如果出现问题，回滚步骤：
  1. 回滚到上一个数据库备份／快照
  2. 回退代码到上一个稳定 commit
  3. 通知团队并排查日志

---
*由自动化 PR 模板生成，合并后请补充部署与数据库备份的实际负责人信息*