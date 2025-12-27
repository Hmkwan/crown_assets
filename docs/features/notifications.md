# 功能：通知（Notifications）

## 概述
系统内通知用于审批、库存、工单、到期等多种事件触达；支持站内通知和可配置的外部通知集成（WeWork/企业微信等）。

## 关键文件
- 模型：`app/models.py`（`Notification`）
- 服务：`app/services/notification_service.py`
- 路由与 UI：`app/main/*` 中有关通知的接口与展示

## 建议
- 增强通知失败的重试机制与告警
- 增加通知策略（优先级、合并策略、沉默时段）
