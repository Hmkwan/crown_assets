# 功能：维护与报废（Maintenance & Disposal）

## 概述
维护模块覆盖计划性维护、维修工单的生命周期与报废流程，包含财务审批规则。

## 关键文件
- `app/main/maintenance_routes.py`
- `app/models.py`（`MaintenancePlan`, `MaintenanceRecord`, `EquipmentScrap`）

## 建议
- 维护操作记录应包含执行人、时间、耗材与成本明细
- 报废需加入审计与财务记账的挂钩点
