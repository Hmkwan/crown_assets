# 功能：审批引擎（Approvals / Workflow）

## 概述
可配置的审批流程引擎，支持自定义流程模板、节点、条件表达式与动态跳过规则。

## 关键文件
- 引擎核心：`app/approval_engine.py`
- 模型：`app/approval_models.py`（`WorkflowTemplate`, `WorkflowNode`, `ApprovalInstance`, `ApprovalStep`）
- 路由/管理：`app/main/workflow_routes.py`, `app/admin/approval_management_routes.py`
- 测试：`tests/test_workflow_*` 系列

## 主要功能
- 模板创建/编辑/删除
- 节点配置（角色、阈值、条件）
- 工单触发审批实例并逐节点执行
- 管理员干预（强制通过/拒绝/终止/回退）

## 已知问题与修复
- 风险点：审批条件表达式当前使用 `eval(node.condition_expr, ...)` 执行（安全风险：任意表达式执行）
  - 建议替换方案：
    - 使用受限表达式解析器（例如 `asteval`、`asteval` 限制上下文），或实现定制的 DSL，仅支持算术/比较/逻辑运算与白名单变量。
    - 添加严格单元测试覆盖各类表达式与越权尝试。

## 测试覆盖
- 流程创建、节点跳过、金额阈值触发、管理员干预。建议添加更多针对恶意表达式与边界情况的测试。

## 建议
- 移除或替代 `eval`，并在变更后添加安全回归测试。
- 增强审批可观测性（每次条件判断的输入/输出日志，便于排查）。