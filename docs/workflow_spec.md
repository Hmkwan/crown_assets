# 可配置企业级 IT 资产管理系统审批流设计规格书

> 本文档为开发团队/架构师/产品经理直接落地的审批流设计说明，涵盖流程要点、数据模型、节点分配、常见模板、API、数据库、UI、异常与安全等。

## 1. 核心设计理念
- 工作流引擎 + 模板化流程（BPMN-like），每类业务由流程模板驱动，模板由可配置节点组成（审批/条件/并行/分支/自动），节点可绑定“角色”或“具体用户”，节点可包含动态条件表达式和动作。
- 节点优先绑定“角色”，其次具体用户，支持并行审批、最少同意数配置。
- 状态机 + 审计日志，审批历史与操作日志完整不可篡改。
- 通知 & SLA & 超时升级，节点超时可自动提醒/升级。
- 权限分离（RBAC）+ 最少权限原则。
- 可扩展动作机制，支持设备分配、库存变更、工单创建、接口回调等。

## 2. 通用数据模型（ER/SQLAlchemy）
- `WorkflowTemplate`：流程模板，业务类型、节点集合。
- `WorkflowNode`：流程节点，类型、顺序、分配、条件、动作、超时等。
- `WorkflowInstance`：流程实例，追踪每个申请的当前状态。
- `ApprovalWorkflow`：审批实例，记录每个节点的审批状态。
- `ApprovalDecision`：并行/多人审批的单人决策。
- `ActionLog`：动作执行记录。
- 关联：User/Role/Notification/AuditLog 复用现有表。

> 详见 `app/workflow_models.py`，已实现 SQLAlchemy ORM。

## 3. 节点分配与流程规则
- 分配优先级：`approver_user_id` > `approver_user_ids` > `role_required`。
- 动态候选人：如 role=department_head，按申请单部门动态筛选。
- 并行审批：`is_parallel`+`required_approvals`，支持多审批人并行，最少同意数通过。
- 超时/升级：`timeout_seconds`+`escalation_target`，超时自动提醒/升级。
- 动作机制：节点通过/拒绝时可配置动作队列（如设备分配、API 回调等）。

## 4. 常见流程模板（示例）
- 设备申请：部门负责人→（金额>5万）财务→管理员。
- 权限申请：直属主管→IT 安全。
- 设备借用：主管→设备管理员。
- 调拨：调出主管→调入主管→管理员。
- 配件申请：部门负责人→采购/库存。
- 报废：资产管理员→部门负责人→财务。

## 5. API 设计（REST）
- 创建申请：POST `/api/v1/{order_type}`
- 查询待审批：GET `/api/v1/approvals?user_id=...`
- 审批操作：POST `/api/v1/approvals/{approval_id}/act`
- 查询流程状态：GET `/api/v1/workflows/{order_type}/{order_id}`
- 撤回/转交/委托/超时升级等接口。
- 错误码：400/403/404/409/500，详见正文。

## 6. 数据库示例（Postgres 风格）
详见正文与 `app/workflow_models.py`。

## 7. UI/交互建议
- 流程设计器（拖拽式）、请求人视图（时间线）、审批人面板（待办/模态）、管理员仪表盘（监控/SLA）、通知提醒。

## 8. 异常/边界/安全
- 并发冲突、缺少审批人、条件表达式错误、动作失败、回滚、审计不可篡改、RBAC 校验、2FA、数据保留策略。

## 9. 实施建议
- 分阶段上线，Feature Flag、灰度、回滚、监控、自动化测试。

---

> 详细内容、字段说明、API 示例、异常处理、审计与合规、开发分工等请参考本文件正文与 `app/workflow_models.py` 注释。
