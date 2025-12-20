# 皇冠新材 IT 资产管理系统 - 系统架构文档

## 系统概述

这是一个基于 Flask 的企业级 IT 资产管理系统,用于管理设备、配件、维修工单、审批流程等核心业务。

**项目名称**: 皇冠新材IT资产管理系统  
**技术栈**: Python 3.11 + Flask + SQLAlchemy + Bootstrap 4  
**数据库**: SQLite  
**部署方式**: Docker + Gunicorn  

---

## 核心功能模块

### 1. 用户认证与权限管理 (`app/auth/`)

**功能**:
- 用户登录/登出
- 密码重置
- 角色权限控制
- 账号申请审批

**角色体系**:
- `super_admin`: 超级管理员
- `admin`: 管理员
- `department_head`: 部门负责人
- `technician`: 技术员
- `user`: 普通用户

**闭环检查**:
- ✅ 登录 → 会话管理 → 登出
- ✅ 密码重置 → 邮件验证 → 密码更新
- ✅ 账号申请 → 管理员审批 → 账号激活

---

### 2. 设备管理 (`app/main/routes.py`)

**核心实体**: `Equipment`

**功能闭环**:
```
设备录入 → 设备查询 → 设备编辑 → 设备状态变更 → 设备报废
    ↓
设备分配 → 设备归还 → 设备借用 → 设备调拨
    ↓
二维码生成 → 标签打印 → 扫码查询
```

**状态流转**:
```
available(可用) → in_use(使用中) → repair(维修中) → retired(已报废)
```

**闭环检查**:
- ✅ 设备创建 → 分配给部门 → 状态更新 → 归档
- ✅ 设备借用 → 审批流程 → 借用归还 → 记录更新
- ✅ 设备调拨 → 跨部门审批 → 库存转移 → 部门更新
- ✅ 设备报废 → 审批流程 → 状态变更 → 成本核算

---

### 3. 配件管理 (`app/main/routes.py`)

**核心实体**: `SparePart`

**功能闭环**:
```
配件入库 → 库存管理 → 配件申请 → 审批流程 → 配件出库 → 库存扣减
    ↓
库存预警 → 采购建议 → 补货入库
```

**闭环检查**:
- ✅ 配件创建 → 设置库存 → 设置预警阈值
- ✅ 配件申请 → 审批 → 出库 → 库存自动扣减
- ✅ 库存不足 → 预警通知 → 采购建议
- ✅ 批量导入/导出功能完整

---

### 4. 维修工单管理 (`app/main/routes.py`)

**核心实体**: `RepairOrder`

**完整生命周期**:
```
故障报修 → 部门审核 → 管理员审批 → 技术员接单 → 金额评估 
    → 金额审批 → 维修执行 → 配件申领 → 完工验收 → 工单关闭
```

**状态流转**:
```
submitted → department_head_approved → admin_approved 
    → in_progress → completed → cancelled
```

**金额阈值审批**:
- 低于阈值: 自动跳过财务/管理员审批
- 达到阈值: 触发额外审批节点

**闭环检查**:
- ✅ 用户提交 → 审批流程 → 技术员处理 → 完成
- ✅ 金额评估 → 阈值判断 → 动态审批节点
- ✅ 配件关联 → 库存扣减 → 成本累计
- ✅ 审批拒绝 → 工单取消 → 通知发送

---

### 5. 审批流程引擎 (`app/admin/`, `app/main/approval_history_routes.py`)

**核心实体**: 
- `WorkflowTemplate`: 流程模板
- `WorkflowNode`: 流程节点
- `ApprovalWorkflow`: 审批实例

**可配置审批流程**:
```
工单类型 → 流程模板 → 多个节点(顺序执行)
    ↓
每个节点:
  - 所需角色
  - 金额阈值
  - 跳过规则(< 阈值跳过 / ≥ 阈值需要)
```

**动态审批逻辑**:
```python
if 工单金额 < 节点阈值 and 跳过规则="金额<阈值时跳过":
    自动跳过该节点
elif 工单金额 >= 节点阈值 and 跳过规则="金额≥阈值时需要":
    需要审批
```

**管理员干预功能**:
- 强制批准/拒绝
- 转交他人
- 打回到指定节点
- 终止流程

**闭环检查**:
- ✅ 流程配置 → 节点创建 → 金额阈值设置
- ✅ 工单提交 → 自动创建审批实例 → 节点执行
- ✅ 金额判断 → 动态跳过/执行节点
- ✅ 审批完成 → 工单状态更新 → 通知发送
- ✅ 管理员干预 → 流程终止 → 后续节点标记跳过

---

### 6. 成本分析 (`app/main/cost_routes.py`)

**功能闭环**:
```
设备采购成本 → AssetCost表记录
    ↓
维修成本累计 → repair_cost_total字段
    ↓
年度成本汇总 → 部门成本对比 → 预算管理
```

**闭环检查**:
- ✅ 设备成本录入 → 成本表创建
- ✅ 维修成本累计 → 自动更新total字段
- ✅ 部门成本汇总 → 年度对比报表
- ✅ 预算设置 → 预算超支预警

---

### 7. 库存预警 (`app/main/inventory_routes.py`)

**预警机制**:
```
配件库存 < 最小库存阈值 → 触发预警
    ↓
生成采购建议 → 管理员查看 → 采购执行 → 入库更新
```

**闭环检查**:
- ✅ 库存实时监控 → 低于阈值预警
- ✅ 预警列表展示 → 采购建议生成
- ✅ 采购后入库 → 预警自动解除

---

### 8. 生命周期管理 (`app/main/lifecycle_routes.py`)

**功能闭环**:
```
设备采购日期 → 使用年限计算 → 折旧分析
    ↓
即将到期设备 → 报废提醒 → 报废流程 → 设备归档
```

**闭环检查**:
- ✅ 设备年限计算 → 到期提醒
- ✅ 报废申请 → 审批流程 → 状态更新
- ✅ 历史归档 → 数据查询

---

### 9. 通知系统 (`app/models.py` - Notification)

**通知触发点**:
- 审批待处理
- 审批结果(批准/拒绝)
- 工单状态变更
- 库存预警
- 设备到期提醒

**闭环检查**:
- ✅ 事件触发 → 通知创建 → 用户查看 → 标记已读
- ✅ 通知中心显示 → 导航栏徽章提示

---

### 10. 导入/导出 (`app/utils/import_export.py`)

**支持格式**: CSV, Excel

**功能**:
- 设备批量导入/导出
- 配件批量导入/导出
- 用户批量导入
- 报表导出

**闭环检查**:
- ✅ 模板下载 → 数据填写 → 批量导入 → 验证 → 入库
- ✅ 数据导出 → CSV生成 → 下载

---

## 数据库模型关系图

```
User (用户)
  ├─ 1:N → Equipment (拥有的设备)
  ├─ 1:N → RepairOrder (提交的维修单)
  ├─ 1:N → ApprovalWorkflow (审批记录)
  └─ 1:N → UserActivityLog (操作日志)

Equipment (设备)
  ├─ N:1 → Department (所属部门)
  ├─ 1:N → RepairOrder (维修记录)
  ├─ 1:1 → AssetCost (成本记录)
  └─ 1:N → EquipmentTransfer (调拨记录)

RepairOrder (维修工单)
  ├─ N:1 → Equipment (关联设备)
  ├─ N:1 → User (申请人/技术员)
  ├─ 1:N → ApprovalWorkflow (审批流程)
  └─ N:N → SparePart (使用的配件)

ApprovalWorkflow (审批流程)
  ├─ N:1 → WorkflowNode (流程节点)
  ├─ N:1 → User (审批人)
  └─ 1:1 → 工单实体 (repair_order/part_request/etc)

WorkflowTemplate (流程模板)
  └─ 1:N → WorkflowNode (包含的节点)
```

---

## 技术架构

### 后端架构
```
Flask Application
  ├─ Blueprints
  │   ├─ auth_bp (认证)
  │   ├─ main_bp (主业务)
  │   └─ admin_bp (管理员)
  │
  ├─ Extensions
  │   ├─ SQLAlchemy (ORM)
  │   ├─ Flask-Login (会话)
  │   ├─ Flask-Migrate (数据库迁移)
  │   └─ Flask-WTF (表单验证)
  │
  └─ Services
      ├─ 审批流程服务
      ├─ 通知服务
      └─ 导入/导出服务
```

### 前端架构
```
Bootstrap 4 + jQuery
  ├─ 响应式布局
  ├─ 模态框交互
  ├─ AJAX数据提交
  └─ DataTables表格
```

---

## 部署架构

```
Docker Container
  ├─ Gunicorn (WSGI Server)
  │   └─ 4 workers
  │
  ├─ Flask App
  │   └─ SQLite Database
  │
  └─ Volume Mounts
      ├─ ./app (代码实时同步)
      ├─ ./app.db (数据持久化)
      └─ ./static (静态资源)
```

**端口**: 5020  
**环境**: Production / Development (可切换)

---

## 安全机制

1. **身份认证**: Flask-Login会话管理
2. **权限控制**: 基于角色的访问控制(RBAC)
3. **CSRF保护**: Flask-WTF内置CSRF token
4. **密码加密**: Werkzeug password hash
5. **SQL注入防护**: SQLAlchemy ORM参数化查询
6. **XSS防护**: Jinja2自动转义

---

## 核心业务流程完整性检查清单

### ✅ 维修工单完整流程
- [x] 用户提交 → 创建工单
- [x] 自动创建审批流程实例
- [x] 部门审核节点
- [x] 管理员审批节点
- [x] 技术员接单
- [x] 金额评估 → 动态触发金额审批
- [x] 技术员执行维修
- [x] 配件申领 → 库存扣减
- [x] 完工确认
- [x] 成本累计

### ✅ 配件申请完整流程
- [x] 用户提交申请
- [x] 审批流程(可配置)
- [x] 审批通过 → 库存扣减
- [x] 审批拒绝 → 通知申请人

### ✅ 设备调拨完整流程
- [x] 发起调拨申请
- [x] 源部门审批
- [x] 目标部门审批
- [x] 管理员审批
- [x] 执行调拨 → 更新归属
- [x] 记录历史

### ✅ 设备报废完整流程
- [x] 发起报废申请
- [x] 部门审批
- [x] 管理员审批
- [x] 财务审批(高价值设备)
- [x] 执行报废 → 状态更新
- [x] 成本核销

### ✅ 审批流程配置
- [x] 创建流程模板
- [x] 添加/编辑/删除节点
- [x] 设置金额阈值
- [x] 配置跳过规则
- [x] 实时生效

### ✅ 管理员干预
- [x] 查看所有审批流程
- [x] 打回到指定节点
- [x] 跳过当前节点
- [x] 重新分配审批人
- [x] 强制终止流程

---

## 已知问题和改进建议

### 潜在问题
1. **性能**: 大量数据时表格加载可能较慢
   - 建议: 实现分页或虚拟滚动
   
2. **并发**: SQLite不适合高并发写入
   - 建议: 生产环境迁移到PostgreSQL/MySQL

3. **文件存储**: 附件存储在本地文件系统
   - 建议: 迁移到对象存储(OSS/S3)

### 功能增强
1. **移动端优化**: 当前主要针对PC端
2. **消息推送**: 集成微信/钉钉通知
3. **高级报表**: BI仪表板
4. **AI预测**: 故障预测、采购预测

---

## 维护指南

### 数据库备份
```bash
# 自动备份(每日)
docker exec equipment-management-system python -c "from app.utils.db_management import backup_database; backup_database()"
```

### 日志查看
```bash
# 查看应用日志
docker logs -f equipment-management-system

# 查看错误日志
docker logs equipment-management-system 2>&1 | grep ERROR
```

### 代码更新
```bash
# 开发模式(实时同步)
docker-compose up

# 生产模式(需要重启)
docker-compose down
docker-compose up -d
```

---

**文档版本**: v2.0  
**最后更新**: 2025-11-30  
**维护者**: IT部门
