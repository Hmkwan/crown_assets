# 审批角色系统使用指南

## 系统概述

全新的审批角色管理系统已成功部署!该系统提供了灵活的角色权限管理和用户授权功能。

## 初始化状态

✅ 数据库表已创建
✅ 系统角色已初始化
✅ 现有用户已自动分配对应角色

### 系统角色列表

已初始化5个系统角色:

1. **👨‍💼 系统管理员** (admin)
   - 级别: 100
   - 权限: 所有工单类型
   - 金额限制: 无限制
   - 已分配: 2个用户 (admin, 吴文杨)

2. **👔 部门负责人** (department_head)
   - 级别: 50
   - 权限: 维修、备件、调拨、报废、借用、申购
   - 金额限制: ¥10,000
   - 已分配: 1个用户 (陈松)

3. **🔧 技术员** (technician)
   - 级别: 30
   - 权限: 维修、备件
   - 金额限制: ¥5,000
   - 已分配: 1个用户 (关鹤鸣)

4. **📦 仓库管理员** (warehouse)
   - 级别: 30
   - 权限: 备件、调拨
   - 金额限制: ¥3,000
   - 已分配: 0个用户

5. **💰 财务审批** (finance)
   - 级别: 70
   - 权限: 所有工单类型
   - 金额限制: 无限制
   - 已分配: 0个用户

## 访问地址

### 1. 审批角色管理
**URL**: http://localhost:5020/admin/approval_roles

**功能**:
- 查看所有审批角色
- 创建自定义角色
- 编辑角色信息(仅限自定义角色)
- 删除角色(仅限自定义角色)
- 查看角色详情和用户列表
- 配置角色权限和金额限制

### 2. 角色分配管理
**URL**: http://localhost:5020/admin/approval_roles/assign

**功能**:
- 为用户分配审批角色
- 设置角色生效/失效日期
- 撤销用户角色
- 查看用户的所有角色
- 搜索和筛选用户

### 3. 原审批流程配置
**URL**: http://localhost:5020/admin/workflow_config

**说明**: 该页面已更新,未来将集成新的审批角色系统

## API 端点

### 角色管理 API

```
GET    /admin/approval_roles             - 角色管理页面
GET    /admin/approval_roles/list        - 获取角色列表
GET    /admin/approval_roles/<id>        - 获取角色详情
POST   /admin/approval_roles/create      - 创建角色
PUT    /admin/approval_roles/<id>/update - 更新角色
DELETE /admin/approval_roles/<id>/delete - 删除角色
```

### 角色分配 API

```
GET    /admin/approval_roles/assign                - 角色分配页面
POST   /admin/approval_roles/assign/create         - 分配角色
DELETE /admin/approval_roles/assign/<id>/revoke    - 撤销角色
GET    /admin/approval_roles/user/<user_id>        - 获取用户角色
```

## 使用流程

### 创建自定义角色

1. 访问审批角色管理页面
2. 点击"创建新角色"按钮
3. 填写角色信息:
   - 角色代码(唯一标识)
   - 角色名称
   - 角色描述
   - 图标(emoji)
   - 颜色
   - 级别(1-100)
   - 最大审批金额
   - 勾选审批权限
4. 保存角色

### 为用户分配角色

1. 访问角色分配管理页面
2. 找到目标用户
3. 点击"分配角色"按钮
4. 选择要分配的角色
5. 可选: 设置生效日期和失效日期
6. 添加备注(可选)
7. 确认分配

### 撤销用户角色

1. 在角色分配页面找到用户
2. 点击角色旁边的 ❌ 按钮
3. 确认撤销

## 权限类型说明

系统支持6种工单类型的审批权限:

1. **维修工单** (`can_approve_repair`)
   - 设备维修申请的审批

2. **备件申请** (`can_approve_part_request`)
   - 备件领用申请的审批

3. **设备调拨** (`can_approve_equipment_transfer`)
   - 设备跨部门调拨的审批

4. **设备报废** (`can_approve_equipment_scrap`)
   - 设备报废申请的审批

5. **设备借用** (`can_approve_equipment_loan`)
   - 设备临时借用的审批

6. **设备申购** (`can_approve_equipment_application`)
   - 新设备采购申请的审批

## 角色级别说明

- 级别范围: 1-100
- 数值越大,权限级别越高
- 建议分级:
  - 1-20: 普通操作员
  - 21-40: 技术员/专员
  - 41-60: 部门负责人
  - 61-80: 高级管理
  - 81-100: 系统管理员

## 金额限制说明

- 留空表示无金额限制
- 当审批金额超过角色限制时,需要更高级别的角色审批
- 可用于实现分级审批流程

## 数据库表结构

### approval_role 表
存储审批角色定义

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| code | String(64) | 角色代码(唯一) |
| name | String(120) | 角色名称 |
| description | Text | 角色描述 |
| category | String(32) | 分类(system/custom) |
| level | Integer | 角色级别 |
| icon | String(10) | 图标 |
| color | String(20) | 颜色 |
| can_approve_* | Boolean | 各类审批权限 |
| max_approval_amount | Float | 最大审批金额 |
| is_system_role | Boolean | 是否系统角色 |
| is_active | Boolean | 是否启用 |

### user_approval_role 表
存储用户角色分配关系

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID |
| role_id | Integer | 角色ID |
| assigned_by_id | Integer | 分配人ID |
| assigned_date | DateTime | 分配日期 |
| start_date | Date | 生效日期 |
| end_date | Date | 失效日期 |
| is_active | Boolean | 是否启用 |
| notes | Text | 备注 |

## 下一步开发计划

### 即将实现的功能

1. **工作流集成**
   - 在工作流节点配置中使用审批角色
   - 替代现有的简单角色字段
   - 支持多角色审批

2. **权限检查**
   - 在审批逻辑中检查用户角色权限
   - 验证金额限制
   - 自动路由到合适的审批人

3. **标准审批步骤**
   - 为每种工单类型配置标准流程
   - 快速创建审批模板
   - 支持模板复用

4. **报表统计**
   - 角色使用情况统计
   - 审批效率分析
   - 权限审计日志

5. **通知提醒**
   - 角色即将过期提醒
   - 审批任务推送
   - 权限变更通知

## 测试建议

1. **创建测试角色**
   - 创建1-2个自定义角色
   - 设置不同的权限和金额限制
   - 测试编辑和删除功能

2. **角色分配测试**
   - 为测试用户分配角色
   - 测试多角色分配
   - 测试日期范围限制
   - 测试角色撤销

3. **权限验证**
   - 验证不同角色的用户看到的界面
   - 测试金额限制功能
   - 验证系统角色不可删除

4. **UI 测试**
   - 测试响应式布局
   - 验证所有按钮和表单
   - 检查数据加载和刷新

## 技术栈

- **后端**: Flask 2.0.3, SQLAlchemy
- **前端**: Bootstrap 4.6.2, jQuery
- **数据库**: SQLite (app.db)
- **部署**: Docker Container
- **服务器**: Gunicorn

## 故障排除

### 页面无法访问
1. 检查容器状态: `docker ps`
2. 查看容器日志: `docker logs equipment-management-system`
3. 重启容器: `docker restart equipment-management-system`

### 角色创建失败
1. 检查角色代码是否重复
2. 验证必填字段是否填写
3. 查看浏览器控制台错误

### 角色分配失败
1. 检查用户是否已有此角色
2. 验证日期范围是否合理
3. 确认用户和角色都存在

## 联系支持

如遇问题,请联系系统管理员。
