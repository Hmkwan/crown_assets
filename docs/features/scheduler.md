# 功能：调度器（Scheduler / APScheduler）

## 概述
使用 APScheduler 管理周期性任务（定期运行维护、同步或回填任务）。调度器可通过环境变量控制是否启用（`SCHEDULER_ENABLED`、`SCHEDULER_JOBS`）。

## 关键文件
- `app/scheduler.py`（任务定义）
- `app/__init__.py`（在 create_app 中按环境变量初始化 scheduler）

## 主要任务示例
- 数据同步任务（与外部系统同步部门/用户）
- DB 回填或过期清理任务
- 日志上报与统计汇总

## 建议
- 每个周期性任务应有幂等性保证，增加任务运行的异常监控与重试策略
- 把关键调度任务的运行历史写入 DB，便于审计与重试
