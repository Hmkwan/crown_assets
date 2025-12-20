-- SQL Server dump generated from SQLite by sqlite_to_mssql.py
-- Review the dump before importing. BACKUP your target DB.

IF OBJECT_ID(N'dbo.account_request', N'U') IS NOT NULL DROP TABLE dbo.account_request;
CREATE TABLE dbo.account_request (
  [id] INT NOT NULL,
  [username] NVARCHAR(MAX),
  [full_name] NVARCHAR(MAX),
  [employee_no] NVARCHAR(MAX),
  [email] NVARCHAR(MAX),
  [department] NVARCHAR(MAX),
  [role_requested] NVARCHAR(MAX),
  [reason] NVARCHAR(MAX),
  [password_hash] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [created_date] DATETIME2,
  [processed_date] DATETIME2,
  [approver_id] INT,
  [approver_comments] NVARCHAR(MAX),
  CONSTRAINT PK_account_request PRIMARY KEY ([id])
);

INSERT INTO dbo.account_request ([id], [username], [full_name], [employee_no], [email], [department], [role_requested], [reason], [password_hash], [status], [created_date], [processed_date], [approver_id], [approver_comments]) VALUES (1, '关鹤鸣', '关鹤鸣', 'HGKP01380', '2122@SS.COM', '人力行政部', 'user', '测试', 'pbkdf2:sha256:260000$7ovO4Gh1sQWWfIMw$f11e78d357a9038561de695f68f1a3b626305186a40d1dd0ee77f8a109a9ae7a', 'approved', '2025-11-19 17:20:36', '2025-11-20 08:04:10', 1, '');

IF OBJECT_ID(N'dbo.approval_workflow', N'U') IS NOT NULL DROP TABLE dbo.approval_workflow;
CREATE TABLE dbo.approval_workflow (
  [id] INT NOT NULL,
  [order_type] NVARCHAR(MAX),
  [order_id] INT,
  [approver_id] INT,
  [approval_level] NVARCHAR(MAX),
  [node_id] INT,
  [status] NVARCHAR(MAX),
  [comments] NVARCHAR(MAX),
  [created_date] DATETIME2,
  [approved_date] DATETIME2,
  [auto_assigned] BIT,
  [required_approvals] INT DEFAULT 1,
  [actions_on_reject] NVARCHAR(MAX),
  CONSTRAINT PK_approval_workflow PRIMARY KEY ([id])
);

INSERT INTO dbo.approval_workflow ([id], [order_type], [order_id], [approver_id], [approval_level], [node_id], [status], [comments], [created_date], [approved_date], [auto_assigned], [required_approvals], [actions_on_reject]) VALUES (1, 'equipment_scrap', 1, 1, 'department_head', NULL, 'approved', '', '2025-11-19 16:12:14', '2025-11-19 16:12:45', 1, 1, NULL);
INSERT INTO dbo.approval_workflow ([id], [order_type], [order_id], [approver_id], [approval_level], [node_id], [status], [comments], [created_date], [approved_date], [auto_assigned], [required_approvals], [actions_on_reject]) VALUES (2, 'equipment_scrap', 1, 1, 'admin', NULL, 'approved', '', '2025-11-19 16:12:15', '2025-11-19 16:12:48', 0, 1, NULL);
INSERT INTO dbo.approval_workflow ([id], [order_type], [order_id], [approver_id], [approval_level], [node_id], [status], [comments], [created_date], [approved_date], [auto_assigned], [required_approvals], [actions_on_reject]) VALUES (3, 'part_request_order', 1, 1, 'department_head', 3, 'approved', '', '2025-11-21 09:26:33', '2025-11-28 13:47:29', 1, 1, NULL);
INSERT INTO dbo.approval_workflow ([id], [order_type], [order_id], [approver_id], [approval_level], [node_id], [status], [comments], [created_date], [approved_date], [auto_assigned], [required_approvals], [actions_on_reject]) VALUES (4, 'part_request_order', 1, 1, 'admin', 4, 'approved', '', '2025-11-21 09:26:34', '2025-11-28 13:47:32', 0, 1, NULL);
INSERT INTO dbo.approval_workflow ([id], [order_type], [order_id], [approver_id], [approval_level], [node_id], [status], [comments], [created_date], [approved_date], [auto_assigned], [required_approvals], [actions_on_reject]) VALUES (5, 'part_request_order', 1, 1, 'admin', 4, 'approved', '', '2025-11-28 21:47:29', '2025-11-28 13:47:33', 0, 1, NULL);

IF OBJECT_ID(N'dbo.asset_cost', N'U') IS NOT NULL DROP TABLE dbo.asset_cost;
CREATE TABLE dbo.asset_cost (
  [id] INT NOT NULL,
  [equipment_id] INT,
  [purchase_price] FLOAT,
  [purchase_date] DATETIME2,
  [maintenance_cost] FLOAT,
  [depreciation_rate] FLOAT,
  [residual_value] FLOAT,
  [depreciation_method] NVARCHAR(MAX),
  [expected_lifespan] INT,
  [supplier] NVARCHAR(MAX),
  [warranty_period] INT,
  [created_date] DATETIME2,
  [updated_date] DATETIME2,
  CONSTRAINT PK_asset_cost PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.asset_handover', N'U') IS NOT NULL DROP TABLE dbo.asset_handover;
CREATE TABLE dbo.asset_handover (
  [id] INT NOT NULL,
  [from_user_id] INT,
  [to_user_id] INT,
  [equipment_ids] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [reason] NVARCHAR(MAX),
  [reason_detail] NVARCHAR(MAX),
  [created_date] DATETIME2,
  [completed_date] DATETIME2,
  [completed_by_id] INT,
  CONSTRAINT PK_asset_handover PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.asset_lifecycle', N'U') IS NOT NULL DROP TABLE dbo.asset_lifecycle;
CREATE TABLE dbo.asset_lifecycle (
  [id] INT NOT NULL,
  [equipment_id] INT,
  [event_type] NVARCHAR(MAX),
  [event_date] DATETIME2,
  [old_status] NVARCHAR(MAX),
  [new_status] NVARCHAR(MAX),
  [description] NVARCHAR(MAX),
  [responsible_user_id] INT,
  [cost_involved] FLOAT,
  [documents] NVARCHAR(MAX),
  CONSTRAINT PK_asset_lifecycle PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.audit_log', N'U') IS NOT NULL DROP TABLE dbo.audit_log;
CREATE TABLE dbo.audit_log (
  [id] INT NOT NULL,
  [user_id] INT,
  [action_type] NVARCHAR(MAX),
  [resource_type] NVARCHAR(MAX),
  [resource_id] INT,
  [old_value] NVARCHAR(MAX),
  [new_value] NVARCHAR(MAX),
  [ip_address] NVARCHAR(MAX),
  [reason] NVARCHAR(MAX),
  [created_date] DATETIME2,
  CONSTRAINT PK_audit_log PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.department', N'U') IS NOT NULL DROP TABLE dbo.department;
CREATE TABLE dbo.department (
  [id] INT NOT NULL,
  [name] NVARCHAR(MAX),
  [code] NVARCHAR(MAX),
  [cost_center] NVARCHAR(MAX),
  [location] NVARCHAR(MAX),
  [description] NVARCHAR(MAX),
  CONSTRAINT PK_department PRIMARY KEY ([id])
);

INSERT INTO dbo.department ([id], [name], [code], [cost_center], [location], [description]) VALUES (1, '信息部', 'IT', 'CC001', '办公楼三楼', '信息技术部门');
INSERT INTO dbo.department ([id], [name], [code], [cost_center], [location], [description]) VALUES (2, '财务部', 'FIN', 'CC002', '办公楼一楼', '财务管理部门');
INSERT INTO dbo.department ([id], [name], [code], [cost_center], [location], [description]) VALUES (3, '人力行政部', 'HR', 'CC003', '一号厂房', '人力资源部门');
INSERT INTO dbo.department ([id], [name], [code], [cost_center], [location], [description]) VALUES (4, '国内销售中心', 'SALES', 'CC004', '办公楼一楼', '销售部门');
INSERT INTO dbo.department ([id], [name], [code], [cost_center], [location], [description]) VALUES (5, '生产办', 'PROD', 'CC005', '六号厂房', '生产制造部门');
INSERT INTO dbo.department ([id], [name], [code], [cost_center], [location], [description]) VALUES (6, '企管部', 'QG', 'CC006', '办公楼三楼', '企业管理部');

IF OBJECT_ID(N'dbo.equipment', N'U') IS NOT NULL DROP TABLE dbo.equipment;
CREATE TABLE dbo.equipment (
  [id] INT NOT NULL,
  [name] NVARCHAR(MAX),
  [type_id] INT,
  [type] NVARCHAR(MAX),
  [brand] NVARCHAR(MAX),
  [model] NVARCHAR(MAX),
  [serial_number] NVARCHAR(MAX),
  [purchase_date] DATETIME2,
  [department_id] INT,
  [department] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [is_public_pool] BIT,
  [price] FLOAT DEFAULT 0.0,
  CONSTRAINT PK_equipment PRIMARY KEY ([id])
);

INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (19, '宏碁笔记本高配', 1, '电脑', '宏碁', '2044', '3240', '2025-12-07 08:00:00', 1, '信息部', 'active', 0, 0.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (20, '宏碁笔记本高配', 1, '电脑', '宏碁', '2045', '3241', '2025-12-08 08:00:00', 1, '信息部', 'active', 0, 0.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (21, '宏碁笔记本高配', 1, '电脑', '宏碁', '2046', '3242', '2025-12-09 08:00:00', 1, '信息部', 'active', 0, 0.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (22, '宏碁笔记本高配', 1, '电脑', '宏碁', '2047', '3243', '2025-12-10 08:00:00', 1, '信息部', 'active', 0, 0.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (23, '宏碁笔记本高配', 1, '电脑', '宏碁', '2048', '3244', '2025-12-11 08:00:00', 1, '信息部', 'active', 0, 0.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (24, '宏碁笔记本高配', 1, '电脑', '宏碁', '2049', '3245', '2025-12-12 08:00:00', 1, '信息部', 'active', 0, 0.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (25, '宏碁笔记本高配', 1, '电脑', '宏碁', '2050', '3246', '2020-12-13 08:00:00', 1, '信息部', 'active', 0, 6651.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (26, '宏碁笔记本高配', 1, '电脑', '宏碁', '2051', '3247', '2025-12-14 08:00:00', 1, '信息部', 'active', 0, 666.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (27, '宏碁笔记本高配', 1, '电脑', '宏碁', '2032', '3228', '2025-12-15 08:00:00', 1, '信息部', 'active', 0, 9952.0);
INSERT INTO dbo.equipment ([id], [name], [type_id], [type], [brand], [model], [serial_number], [purchase_date], [department_id], [department], [status], [is_public_pool], [price]) VALUES (28, '惠普154', 2, '打印机', '惠普', '惠普', '4', '2011-11-07 08:00:00', 6, '企管部', 'active', 0, 6552.0);

IF OBJECT_ID(N'dbo.equipment_application', N'U') IS NOT NULL DROP TABLE dbo.equipment_application;
CREATE TABLE dbo.equipment_application (
  [id] INT NOT NULL,
  [equipment_id] INT,
  [applicant_id] INT,
  [applicant_dept] NVARCHAR(MAX),
  [reason] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [created_date] DATETIME2,
  [approved_date] DATETIME2,
  CONSTRAINT PK_equipment_application PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.equipment_loan', N'U') IS NOT NULL DROP TABLE dbo.equipment_loan;
CREATE TABLE dbo.equipment_loan (
  [id] INT NOT NULL,
  [equipment_id] INT,
  [requester_id] INT,
  [requester_dept] NVARCHAR(MAX),
  [start_date] DATETIME2,
  [end_date] DATETIME2,
  [status] NVARCHAR(MAX),
  [approved_by] INT,
  [approved_date] DATETIME2,
  [borrowed_date] DATETIME2,
  [returned_date] DATETIME2,
  [notes] NVARCHAR(MAX),
  [pickup_notified] BIT,
  [created_date] DATETIME2,
  [updated_date] DATETIME2,
  CONSTRAINT PK_equipment_loan PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.equipment_scrap', N'U') IS NOT NULL DROP TABLE dbo.equipment_scrap;
CREATE TABLE dbo.equipment_scrap (
  [id] INT NOT NULL,
  [equipment_id] INT,
  [requester_id] INT,
  [description] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [created_date] DATETIME2,
  [updated_date] DATETIME2,
  CONSTRAINT PK_equipment_scrap PRIMARY KEY ([id])
);

INSERT INTO dbo.equipment_scrap ([id], [equipment_id], [requester_id], [description], [status], [created_date], [updated_date]) VALUES (1, NULL, 2, '哦', 'approved', '2025-11-19 16:12:14', '2025-11-20 16:40:44');

IF OBJECT_ID(N'dbo.equipment_transfer', N'U') IS NOT NULL DROP TABLE dbo.equipment_transfer;
CREATE TABLE dbo.equipment_transfer (
  [id] INT NOT NULL,
  [equipment_id] INT,
  [from_department] NVARCHAR(MAX),
  [to_department] NVARCHAR(MAX),
  [requester_id] INT,
  [description] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [created_date] DATETIME2,
  [updated_date] DATETIME2,
  CONSTRAINT PK_equipment_transfer PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.equipment_type', N'U') IS NOT NULL DROP TABLE dbo.equipment_type;
CREATE TABLE dbo.equipment_type (
  [id] INT NOT NULL,
  [name] NVARCHAR(MAX) NOT NULL,
  [description] NVARCHAR(MAX),
  [created_date] DATETIME2,
  CONSTRAINT PK_equipment_type PRIMARY KEY ([id])
);

INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (1, '电脑', '包括台式机、笔记本等计算设备', '2025-11-19 11:48:12');
INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (2, '打印机', '各类打印设备', '2025-11-19 11:48:12');
INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (3, '投影仪', '投影显示设备', '2025-11-19 11:48:12');
INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (4, '服务器', '服务器设备', '2025-11-19 11:48:12');
INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (5, '网络设备', '路由器、交换机等网络设备', '2025-11-19 11:48:12');
INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (6, '办公设备', '其他办公设备', '2025-11-19 11:48:12');
INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (7, '移动设备', '手机、平板等移动设备', '2025-11-19 11:48:12');
INSERT INTO dbo.equipment_type ([id], [name], [description], [created_date]) VALUES (8, '显示器', '显示设备', '2025-11-20 16:40:22');

IF OBJECT_ID(N'dbo.inventory_warning', N'U') IS NOT NULL DROP TABLE dbo.inventory_warning;
CREATE TABLE dbo.inventory_warning (
  [id] INT NOT NULL,
  [spare_part_id] INT,
  [min_threshold] INT,
  [critical_threshold] INT,
  [reorder_quantity] INT,
  [lead_time_days] INT,
  [enabled] BIT,
  [last_warned_date] DATETIME2,
  [created_date] DATETIME2,
  CONSTRAINT PK_inventory_warning PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.notification', N'U') IS NOT NULL DROP TABLE dbo.notification;
CREATE TABLE dbo.notification (
  [id] INT NOT NULL,
  [user_id] INT,
  [title] NVARCHAR(MAX),
  [message] NVARCHAR(MAX),
  [is_read] BIT,
  [created_date] DATETIME2,
  [order_type] NVARCHAR(MAX),
  [order_id] INT,
  CONSTRAINT PK_notification PRIMARY KEY ([id])
);

INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (1, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 13:52:08', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (2, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 13:52:33', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (3, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:03:32', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (4, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:03:46', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (5, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:03:49', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (6, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:04:05', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (7, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:04:20', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (8, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:04:40', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (9, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:05:02', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (10, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:05:18', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (11, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:06:12', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (12, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:06:34', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (13, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:07:03', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (14, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:10:32', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (15, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:10:51', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (16, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:11:30', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (17, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:12:37', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (18, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:14:18', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (19, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:21:13', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (20, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:32:08', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (21, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:33:03', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (22, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 15:35:21', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (23, 2, '测试通知', '这是一条测试通知', 1, '2025-11-19 16:06:36', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (24, 1, '自动分配审批', '系统将 设备报废#1 的审批节点 部门领导 自动分配给您，请尽快处理。', 1, '2025-11-19 16:12:14', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (25, 2, '设备报废已提交', '您已提交设备报废申请 #1，等待审批流程。', 1, '2025-11-19 16:12:14', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (26, 2, '设备报废完成', '您的设备报废申请 #1 已完成', 1, '2025-11-19 16:12:48', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (27, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 16:22:58', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (28, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 16:48:43', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (29, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 16:49:09', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (30, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 16:52:36', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (31, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:11:38', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (32, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:12:26', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (33, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:15:20', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (34, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:19:26', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (35, 1, '新的账号申请', '员工 关鹤鸣 提交账号申请，请尽快审批。', 1, '2025-11-19 17:20:36', 'account_request', 1);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (36, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:28:25', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (37, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:30:20', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (38, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:30:26', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (39, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:33:28', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (40, 2, '测试通知', '这是一条测试通知', 0, '2025-11-19 17:34:59', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (41, 2, '测试通知', '这是一条测试通知', 0, '2025-11-20 08:03:48', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (42, 4, '账号已开通', '管理员已经批准了您的账号申请，现在可以使用申请时设置的密码登录系统。', 0, '2025-11-20 08:04:10', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (43, 1, '自动分配审批', '系统将 配件申请#1 的审批节点 部门领导 自动分配给您，请尽快处理。', 1, '2025-11-21 09:26:33', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (44, 1, '新配件申请', '用户 admin 提交了新的配件申请 #1', 1, '2025-11-21 09:26:33', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (45, 5, '新配件申请', '用户 admin 提交了新的配件申请 #1', 0, '2025-11-21 09:26:33', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (46, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:38:18', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (47, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:39:40', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (48, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:41:35', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (49, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:41:42', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (50, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:41:55', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (51, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:45:11', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (52, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:45:18', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (53, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:45:35', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (54, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:45:59', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (55, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:46:10', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (56, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:46:20', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (57, 1, '配件申请审批状态更新', '您的配件申请 #1 已被 admin 批准', 1, '2025-11-28 21:47:29', 'part_request_order', 1);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (58, 1, '配件申请审批完成', '您的配件申请 #1 已被 admin 批准，库存已减少', 1, '2025-11-28 21:47:32', 'part_request_order', 1);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (59, 1, '配件申请审批完成', '您的配件申请 #1 已被 admin 批准，库存已减少', 1, '2025-11-28 21:47:33', 'part_request_order', 1);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (60, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:54:40', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (61, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:54:56', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (62, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:55:52', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (63, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:57:16', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (64, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 21:57:26', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (65, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:12:02', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (66, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:12:28', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (67, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:12:53', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (68, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:13:22', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (69, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:14:13', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (70, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:14:28', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (71, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:15:24', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (72, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:16:14', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (73, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:16:59', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (74, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:17:55', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (75, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:18:28', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (76, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:45:28', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (77, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:46:11', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (78, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:48:17', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (79, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:57:06', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (80, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:57:28', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (81, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:57:56', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (82, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:58:17', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (83, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:58:34', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (84, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:58:46', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (85, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 22:58:53', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (86, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 23:04:31', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (87, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 23:05:09', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (88, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 23:05:22', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (89, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 23:05:46', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (90, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 23:09:06', NULL, NULL);
INSERT INTO dbo.notification ([id], [user_id], [title], [message], [is_read], [created_date], [order_type], [order_id]) VALUES (91, 2, '测试通知', '这是一条测试通知', 0, '2025-11-28 23:13:18', NULL, NULL);

IF OBJECT_ID(N'dbo.part_replacement', N'U') IS NOT NULL DROP TABLE dbo.part_replacement;
CREATE TABLE dbo.part_replacement (
  [id] INT NOT NULL,
  [repair_order_id] INT,
  [spare_part_id] INT,
  [quantity] INT,
  [replacement_date] DATETIME2,
  CONSTRAINT PK_part_replacement PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.part_request_order', N'U') IS NOT NULL DROP TABLE dbo.part_request_order;
CREATE TABLE dbo.part_request_order (
  [id] INT NOT NULL,
  [requester_id] INT,
  [department_head_id] INT,
  [admin_id] INT,
  [part_name] NVARCHAR(MAX),
  [part_number] NVARCHAR(MAX),
  [quantity] INT,
  [reason] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [department_head_approved] BIT,
  [admin_approved] BIT,
  [created_date] DATETIME2,
  [updated_date] DATETIME2,
  [completed_date] DATETIME2,
  CONSTRAINT PK_part_request_order PRIMARY KEY ([id])
);

INSERT INTO dbo.part_request_order ([id], [requester_id], [department_head_id], [admin_id], [part_name], [part_number], [quantity], [reason], [status], [department_head_approved], [admin_approved], [created_date], [updated_date], [completed_date]) VALUES (1, 1, 1, 1, '内存10G', 'me1003', 1, '李卓富内存损坏', 'approved', 1, 1, '2025-11-21 09:26:33', '2025-11-28 21:47:33', '2025-11-28 13:47:33');

IF OBJECT_ID(N'dbo.permission', N'U') IS NOT NULL DROP TABLE dbo.permission;
CREATE TABLE dbo.permission (
  [id] INT NOT NULL,
  [role_id] INT,
  [module] NVARCHAR(MAX),
  [action] NVARCHAR(MAX),
  [resource_type] NVARCHAR(MAX),
  [conditions] NVARCHAR(MAX),
  [is_granted] BIT,
  [priority] INT,
  [created_date] DATETIME2,
  CONSTRAINT PK_permission PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.repair_order', N'U') IS NOT NULL DROP TABLE dbo.repair_order;
CREATE TABLE dbo.repair_order (
  [id] INT NOT NULL,
  [equipment_id] INT,
  [requester_id] INT,
  [technician_id] INT,
  [department_head_id] INT,
  [admin_id] INT,
  [description] NVARCHAR(MAX),
  [status] NVARCHAR(MAX),
  [created_date] DATETIME2,
  [updated_date] DATETIME2,
  [completed_date] DATETIME2,
  [department_head_approved] BIT,
  [admin_approved] BIT,
  CONSTRAINT PK_repair_order PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.role_definition', N'U') IS NOT NULL DROP TABLE dbo.role_definition;
CREATE TABLE dbo.role_definition (
  [id] INT NOT NULL,
  [name] NVARCHAR(MAX),
  [description] NVARCHAR(MAX),
  [is_custom] BIT,
  [is_active] BIT,
  [created_date] DATETIME2,
  [created_by_id] INT,
  CONSTRAINT PK_role_definition PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.spare_part', N'U') IS NOT NULL DROP TABLE dbo.spare_part;
CREATE TABLE dbo.spare_part (
  [id] INT NOT NULL,
  [name] NVARCHAR(MAX),
  [part_number] NVARCHAR(MAX),
  [price] FLOAT,
  [stock_quantity] INT,
  [min_stock_level] INT,
  [department_id] INT,
  [department] NVARCHAR(MAX),
  [location] NVARCHAR(MAX),
  [purchase_date] DATETIME2,
  CONSTRAINT PK_spare_part PRIMARY KEY ([id])
);

INSERT INTO dbo.spare_part ([id], [name], [part_number], [price], [stock_quantity], [min_stock_level], [department_id], [department], [location], [purchase_date]) VALUES (2, '内存9G', 'me1002', 2.0, 16, 10, NULL, '信息部', '信息部', '2025-11-05 08:00:00');
INSERT INTO dbo.spare_part ([id], [name], [part_number], [price], [stock_quantity], [min_stock_level], [department_id], [department], [location], [purchase_date]) VALUES (3, '内存10G', 'me1003', 663.0, 15, 10, NULL, '信息部', '信息部', '2025-11-01 08:00:00');
INSERT INTO dbo.spare_part ([id], [name], [part_number], [price], [stock_quantity], [min_stock_level], [department_id], [department], [location], [purchase_date]) VALUES (4, '内存11G', 'me1004', 4.0, 18, 10, NULL, '信息部', '信息部', '2025-11-02 08:00:00');

IF OBJECT_ID(N'dbo.user', N'U') IS NOT NULL DROP TABLE dbo.user;
CREATE TABLE dbo.user (
  [id] INT NOT NULL,
  [username] NVARCHAR(MAX),
  [email] NVARCHAR(MAX),
  [password_hash] NVARCHAR(MAX),
  [role] NVARCHAR(MAX),
  [department_id] INT,
  [department] NVARCHAR(MAX),
  [can_manage_equipment] BIT,
  [can_manage_spare_parts] BIT,
  [can_manage_repairs] BIT,
  [can_manage_part_requests] BIT,
  [can_view_workflow] BIT,
  [can_view_reports] BIT,
  [can_view_logs] BIT,
  [can_edit_workflow] BIT DEFAULT 0,
  [can_manage_workflow_templates] BIT DEFAULT 0,
  [is_active] BIT DEFAULT 1,
  CONSTRAINT PK_user PRIMARY KEY ([id])
);

INSERT INTO dbo.user ([id], [username], [email], [password_hash], [role], [department_id], [department], [can_manage_equipment], [can_manage_spare_parts], [can_manage_repairs], [can_manage_part_requests], [can_view_workflow], [can_view_reports], [can_view_logs], [can_edit_workflow], [can_manage_workflow_templates], [is_active]) VALUES (1, 'admin', 'admin@example.com', 'pbkdf2:sha256:260000$4SuvzQQUOHCLe0h6$721d58bf645621c36fe85b2eef4bde94538288b8916226299210ffec0cb8609e', 'admin', 1, '信息部', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);
INSERT INTO dbo.user ([id], [username], [email], [password_hash], [role], [department_id], [department], [can_manage_equipment], [can_manage_spare_parts], [can_manage_repairs], [can_manage_part_requests], [can_view_workflow], [can_view_reports], [can_view_logs], [can_edit_workflow], [can_manage_workflow_templates], [is_active]) VALUES (2, 'testuser', 'test@example.com', 'pbkdf2:sha256:260000$1KZdQblEpA6UmBWz$5862d1a250e87640982c44d09e40be1300d65467f5e1e4fdde8a2b4d9dda8b85', 'user', 1, '信息部', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);
INSERT INTO dbo.user ([id], [username], [email], [password_hash], [role], [department_id], [department], [can_manage_equipment], [can_manage_spare_parts], [can_manage_repairs], [can_manage_part_requests], [can_view_workflow], [can_view_reports], [can_view_logs], [can_edit_workflow], [can_manage_workflow_templates], [is_active]) VALUES (3, '朱绪', '323@qq.com', 'pbkdf2:sha256:260000$ntnrw7tnwDoCmbto$23a3e58a69a33e9bb58fb27f574887105c2c4de99ca8ab7245a5f205410e81a6', 'technician', 6, '企管部', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);
INSERT INTO dbo.user ([id], [username], [email], [password_hash], [role], [department_id], [department], [can_manage_equipment], [can_manage_spare_parts], [can_manage_repairs], [can_manage_part_requests], [can_view_workflow], [can_view_reports], [can_view_logs], [can_edit_workflow], [can_manage_workflow_templates], [is_active]) VALUES (4, '关鹤鸣', '2122@SS.COM', 'pbkdf2:sha256:260000$7ovO4Gh1sQWWfIMw$f11e78d357a9038561de695f68f1a3b626305186a40d1dd0ee77f8a109a9ae7a', 'department_head', 3, '人力行政部', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);
INSERT INTO dbo.user ([id], [username], [email], [password_hash], [role], [department_id], [department], [can_manage_equipment], [can_manage_spare_parts], [can_manage_repairs], [can_manage_part_requests], [can_view_workflow], [can_view_reports], [can_view_logs], [can_edit_workflow], [can_manage_workflow_templates], [is_active]) VALUES (5, '吴文杨', 'wuwy@crown.com.cn', 'pbkdf2:sha256:260000$qwaJ7qVNMa5OrACk$9ffc8019bb3142203f2e4bdb9bd7b05b663b9b126eff22c94280a65ec1ffd081', 'admin', 1, '信息部', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);

IF OBJECT_ID(N'dbo.user_activity_log', N'U') IS NOT NULL DROP TABLE dbo.user_activity_log;
CREATE TABLE dbo.user_activity_log (
  [id] INT NOT NULL,
  [user_id] INT,
  [action] NVARCHAR(MAX),
  [description] NVARCHAR(MAX),
  [timestamp] DATETIME2,
  CONSTRAINT PK_user_activity_log PRIMARY KEY ([id])
);

INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (1, 1, '数据库重置', '用户 admin 重置了数据库 (IP: 10.168.93.93)', '2025-11-19 11:48:12');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (2, 1, '用户登出', '用户 admin 登出系统', '2025-11-19 11:48:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (3, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 11:48:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (4, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_114221.db (IP: 10.168.93.93)', '2025-11-19 11:48:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (5, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251119_114834.db (IP: 10.168.93.93)', '2025-11-19 11:48:34');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (6, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:49:25');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (7, 1, '更新部门', '更新部门 IT部 -> 信息部 (IP: 10.168.93.93)', '2025-11-19 11:50:05');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (8, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:50:05');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (9, 1, '更新部门', '更新部门 财务部 -> 财务部 (IP: 10.168.93.93)', '2025-11-19 11:50:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (10, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:50:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (11, 1, '更新部门', '更新部门 人事部 -> 人力行政部 (IP: 10.168.93.93)', '2025-11-19 11:50:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (12, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:50:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (13, 1, '更新部门', '更新部门 销售部 -> 销售部 (IP: 10.168.93.93)', '2025-11-19 11:50:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (14, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:50:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (15, 1, '更新部门', '更新部门 销售部 -> 国内销售中心 (IP: 10.168.93.93)', '2025-11-19 11:50:59');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (16, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:50:59');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (17, 1, '更新部门', '更新部门 生产部 -> 生产办 (IP: 10.168.93.93)', '2025-11-19 11:51:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (18, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:51:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (19, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 11:51:37');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (20, 1, '删除设备', '删除设备 办公电脑001 SN:PC2023001 (IP: 10.168.93.93)', '2025-11-19 11:51:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (21, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 11:51:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (22, 1, '删除设备', '删除设备 激光打印机001 SN:PR2023001 (IP: 10.168.93.93)', '2025-11-19 11:51:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (23, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 11:51:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (24, 1, '删除设备', '删除设备 办公电脑002 SN:PC2023002 (IP: 10.168.93.93)', '2025-11-19 11:51:55');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (25, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 11:51:55');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (26, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 11:52:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (27, 1, '删除配件', '删除配件 内存条 8GB DDR4#MEM001 (IP: 10.168.93.93)', '2025-11-19 11:52:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (28, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 11:52:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (29, 1, '删除配件', '删除配件 固态硬盘 256GB SATA#SSD001 (IP: 10.168.93.93)', '2025-11-19 11:52:11');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (30, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 11:52:11');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (31, 1, '删除配件', '删除配件 电源适配器 65W#PWR001 (IP: 10.168.93.93)', '2025-11-19 11:52:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (32, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 11:52:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (33, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:52:35');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (34, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 11:52:40');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (35, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_114834.db (IP: 10.168.93.93)', '2025-11-19 11:58:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (36, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 11:58:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (37, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251119_115824.db (IP: 10.168.93.93)', '2025-11-19 11:58:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (38, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_115824.db (IP: 10.168.93.93)', '2025-11-19 11:58:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (39, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_114928.db (IP: 10.168.93.93)', '2025-11-19 11:58:48');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (40, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_115602.db (IP: 10.168.93.93)', '2025-11-19 11:58:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (41, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_115458.db (IP: 10.168.93.93)', '2025-11-19 11:58:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (42, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 11:59:28');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (43, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 11:59:41');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (44, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 12:25:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (45, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 12:26:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (46, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 12:26:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (47, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 12:27:11');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (48, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 13:31:26');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (49, 1, '添加配件', '添加配件 内存8G#me1001 (IP: 10.168.93.93)', '2025-11-19 13:31:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (50, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 13:31:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (51, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_115829.db (IP: 10.168.93.93)', '2025-11-19 13:49:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (52, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_120007.db (IP: 10.168.93.93)', '2025-11-19 13:49:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (53, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_134201.db (IP: 10.168.93.93)', '2025-11-19 13:49:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (54, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_123109.db (IP: 10.168.93.93)', '2025-11-19 13:49:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (55, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_133944.db (IP: 10.168.93.93)', '2025-11-19 13:49:25');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (56, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_133817.db (IP: 10.168.93.93)', '2025-11-19 13:49:26');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (57, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_133530.db (IP: 10.168.93.93)', '2025-11-19 13:49:28');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (58, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:50:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (59, 1, '添加设备', '添加设备 宏碁笔记本高配#1 (IP: 10.168.93.93)', '2025-11-19 13:51:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (60, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:51:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (61, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:54:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (62, 1, '加入公开仓库', '设备 宏碁笔记本高配#1 加入信息部公开仓库 (IP: 10.168.93.93)', '2025-11-19 13:54:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (63, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:54:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (64, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:54:41');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (65, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:56:28');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (66, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:56:36');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (67, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:56:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (68, 1, '设为可申请', '设备 宏碁笔记本高配#1 设为可申请 (IP: 10.168.93.93)', '2025-11-19 13:56:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (69, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 13:56:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (70, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251119_135917.db (IP: 10.168.93.93)', '2025-11-19 13:59:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (71, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251119_135920.db (IP: 10.168.93.93)', '2025-11-19 13:59:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (72, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251119_135922.db (IP: 10.168.93.93)', '2025-11-19 13:59:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (73, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251119_135925.db (IP: 10.168.93.93)', '2025-11-19 13:59:25');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (74, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:01:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (75, 1, '移出公开仓库', '设备 宏碁笔记本高配#1 从信息部公开仓库移出 (IP: 10.168.93.93)', '2025-11-19 14:01:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (76, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:01:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (77, 1, '导入设备', '导入 26 台，跳过 1 台 (IP: 10.168.93.93)', '2025-11-19 14:02:11');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (78, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:02:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (79, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:02:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (80, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:02:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (81, 1, '加入公开仓库', '设备 宏碁笔记本高配#2 加入信息部公开仓库 (IP: 10.168.93.93)', '2025-11-19 14:02:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (82, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:02:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (83, 1, '加入公开仓库', '设备 宏碁笔记本高配#1 加入信息部公开仓库 (IP: 10.168.93.93)', '2025-11-19 14:03:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (84, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:03:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (85, 1, '设为可申请', '设备 宏碁笔记本高配#2 设为可申请 (IP: 10.168.93.93)', '2025-11-19 14:03:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (86, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:03:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (87, 1, '移出公开仓库', '设备 宏碁笔记本高配#1 从信息部公开仓库移出 (IP: 10.168.93.93)', '2025-11-19 14:03:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (88, 1, '移出公开仓库', '设备 宏碁笔记本高配#2 从信息部公开仓库移出 (IP: 10.168.93.93)', '2025-11-19 14:03:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (89, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:03:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (90, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:03:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (91, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:07:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (92, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:09:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (93, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:09:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (94, 1, '访问页面', '设备类型管理 (IP: 10.168.93.93)', '2025-11-19 14:09:40');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (95, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 14:54:18');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (96, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 14:54:28');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (97, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 14:54:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (98, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:54:45');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (99, 1, '加入公开仓库', '设备 宏碁笔记本高配#27 加入信息部公开仓库 (IP: 10.168.93.93)', '2025-11-19 14:54:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (100, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:54:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (101, 1, '设为可申请', '设备 宏碁笔记本高配#27 设为可申请 (IP: 10.168.93.93)', '2025-11-19 14:54:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (102, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:54:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (103, 1, '取消可申请', '设备 宏碁笔记本高配#27 取消可申请状态 (IP: 10.168.93.93)', '2025-11-19 14:55:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (104, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:55:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (105, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:57:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (106, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:57:19');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (107, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:57:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (108, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:57:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (109, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:57:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (110, 1, '取消可申请', '设备 宏碁笔记本高配#1 取消可申请状态 (IP: 10.168.93.93)', '2025-11-19 14:58:06');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (111, 1, '取消可申请', '设备 宏碁笔记本高配#2 取消可申请状态 (IP: 10.168.93.93)', '2025-11-19 14:58:06');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (112, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:58:06');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (113, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:58:07');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (114, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:58:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (115, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:58:11');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (116, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:58:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (117, 1, '导入设备', '导入 0 台，跳过 27 台 (IP: 10.168.93.93)', '2025-11-19 14:59:11');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (118, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:59:12');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (119, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 14:59:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (120, 1, '删除设备', '删除设备 宏碁笔记本高配 SN:3228 (IP: 10.168.93.93)', '2025-11-19 15:00:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (121, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:00:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (122, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:00:34');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (123, 1, '编辑用户', '管理员 admin 编辑了用户 testuser (IP: 10.168.93.93)', '2025-11-19 15:01:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (124, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:03:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (125, 1, '导入设备', '导入 1 台，跳过 26 台 (IP: 10.168.93.93)', '2025-11-19 15:04:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (126, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:04:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (127, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:04:12');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (128, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 15:04:41');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (129, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:04:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (130, 1, '导入设备', '导入 0 台，跳过 27 台 (IP: 10.168.93.93)', '2025-11-19 15:04:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (131, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:04:54');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (132, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:04:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (133, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:04:59');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (134, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:05:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (135, 1, '更新设备', '更新设备 宏碁笔记本高配#27 (IP: 10.168.93.93)', '2025-11-19 15:05:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (136, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:05:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (137, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:05:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (138, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:05:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (139, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:05:54');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (140, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:05:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (141, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:06:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (142, 1, '导出配件', '导出配件数据 共 1 条 (IP: 10.168.93.93)', '2025-11-19 15:06:07');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (143, 1, '导入配件', '导入 4 个，跳过 1 个 (IP: 10.168.93.93)', '2025-11-19 15:06:34');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (144, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:06:36');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (145, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:06:55');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (146, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:08:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (147, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 15:08:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (148, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:08:38');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (149, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:08:47');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (150, 1, '更新设备', '更新设备 宏碁笔记本高配#7 (IP: 10.168.93.93)', '2025-11-19 15:09:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (151, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:09:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (152, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:09:12');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (153, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:09:15');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (154, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:09:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (155, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:09:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (156, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:21:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (157, 1, '导入设备', '导入 0 台，跳过 27 台 (IP: 10.168.93.93)', '2025-11-19 15:21:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (158, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:21:34');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (159, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:21:38');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (160, 1, '导入配件', '导入 0 个，跳过 5 个 (IP: 10.168.93.93)', '2025-11-19 15:21:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (161, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:21:47');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (162, 1, '导出配件', '导出配件数据 共 5 条 (IP: 10.168.93.93)', '2025-11-19 15:21:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (163, 1, '导入配件', '导入 0 个，跳过 5 个 (IP: 10.168.93.93)', '2025-11-19 15:22:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (164, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:22:25');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (165, 1, '导出配件', '导出配件数据 共 5 条 (IP: 10.168.93.93)', '2025-11-19 15:23:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (166, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_150822.db (IP: 10.168.93.93)', '2025-11-19 15:24:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (167, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:25:37');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (168, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:26:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (169, 1, '导入设备', '导入 0 台，跳过 27 台 (IP: 10.168.93.93)', '2025-11-19 15:26:28');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (170, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:26:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (171, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:26:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (172, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:26:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (173, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:26:54');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (174, 1, '更新配件', '更新配件 内存10G#me1003 (IP: 10.168.93.93)', '2025-11-19 15:27:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (175, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:27:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (176, 1, '更新配件', '更新配件 内存11G#me1004 (IP: 10.168.93.93)', '2025-11-19 15:27:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (177, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:27:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (178, 1, '更新配件', '更新配件 内存12G#me1005 (IP: 10.168.93.93)', '2025-11-19 15:27:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (179, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:27:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (180, 1, '更新配件', '更新配件 内存9G#me1002 (IP: 10.168.93.93)', '2025-11-19 15:27:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (181, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:27:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (182, 1, '导出配件', '导出配件数据 共 5 条 (IP: 10.168.93.93)', '2025-11-19 15:27:47');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (183, 1, '导入配件', '导入 1 个，跳过 5 个 (IP: 10.168.93.93)', '2025-11-19 15:28:25');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (184, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 15:28:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (185, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 15:28:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (186, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 15:34:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (187, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:06:42');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (188, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:06:53');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (189, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:06:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (190, 1, '删除设备', '批量删除设备 宏碁笔记本高配#19 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (191, 1, '删除设备', '批量删除设备 宏碁笔记本高配#20 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (192, 1, '删除设备', '批量删除设备 宏碁笔记本高配#21 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (193, 1, '删除设备', '批量删除设备 宏碁笔记本高配#22 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (194, 1, '删除设备', '批量删除设备 宏碁笔记本高配#23 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (195, 1, '删除设备', '批量删除设备 宏碁笔记本高配#24 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (196, 1, '删除设备', '批量删除设备 宏碁笔记本高配#25 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (197, 1, '删除设备', '批量删除设备 宏碁笔记本高配#26 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (198, 1, '删除设备', '批量删除设备 宏碁笔记本高配#27 (IP: 10.168.93.93)', '2025-11-19 16:07:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (199, 1, '删除设备', '批量删除设备 宏碁笔记本高配#28 (IP: 10.168.93.93)', '2025-11-19 16:07:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (200, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:07:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (201, 1, '删除设备', '批量删除设备 宏碁笔记本高配#9 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (202, 1, '删除设备', '批量删除设备 宏碁笔记本高配#10 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (203, 1, '删除设备', '批量删除设备 宏碁笔记本高配#11 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (204, 1, '删除设备', '批量删除设备 宏碁笔记本高配#12 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (205, 1, '删除设备', '批量删除设备 宏碁笔记本高配#13 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (206, 1, '删除设备', '批量删除设备 宏碁笔记本高配#14 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (207, 1, '删除设备', '批量删除设备 宏碁笔记本高配#15 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (208, 1, '删除设备', '批量删除设备 宏碁笔记本高配#16 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (209, 1, '删除设备', '批量删除设备 宏碁笔记本高配#17 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (210, 1, '删除设备', '批量删除设备 宏碁笔记本高配#18 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (211, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:07:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (212, 1, '删除设备', '批量删除设备 宏碁笔记本高配#1 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (213, 1, '删除设备', '批量删除设备 宏碁笔记本高配#2 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (214, 1, '删除设备', '批量删除设备 宏碁笔记本高配#3 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (215, 1, '删除设备', '批量删除设备 宏碁笔记本高配#4 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (216, 1, '删除设备', '批量删除设备 宏碁笔记本高配#5 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (217, 1, '删除设备', '批量删除设备 宏碁笔记本高配#6 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (218, 1, '删除设备', '批量删除设备 宏碁笔记本高配#7 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (219, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:07:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (220, 1, '导入设备', '导入 27 台，跳过 0 台 (IP: 10.168.93.93)', '2025-11-19 16:07:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (221, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:07:18');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (222, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:07:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (223, 1, '更新设备', '更新设备 宏碁笔记本高配#7 (IP: 10.168.93.93)', '2025-11-19 16:07:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (224, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:07:31');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (225, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:07:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (226, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 16:07:36');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (227, 1, '删除配件', '批量删除配件 内存8G#me1001 (IP: 10.168.93.93)', '2025-11-19 16:07:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (228, 1, '删除配件', '批量删除配件 内存12G#me1005 (IP: 10.168.93.93)', '2025-11-19 16:07:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (229, 1, '删除配件', '批量删除配件 内存13G#me1006 (IP: 10.168.93.93)', '2025-11-19 16:07:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (230, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 16:07:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (231, 1, '重置密码', '管理员为用户 testuser 重置密码 (IP: 10.168.93.93)', '2025-11-19 16:10:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (232, 1, '用户登出', '用户 admin 登出系统', '2025-11-19 16:11:06');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (233, 2, '用户登录', '用户 testuser 登录系统', '2025-11-19 16:11:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (234, 2, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-19 16:11:31');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (235, 1, '自动分配审批', '对于 设备报废#1 的审批节点 部门领导，系统自动分配给管理员用户ID 1。', '2025-11-19 16:12:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (236, 2, '用户登出', '用户 testuser 登出系统', '2025-11-19 16:12:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (237, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 16:12:35');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (238, 1, '审批设备报废', '用户 admin 批准了设备报废申请 #1 (IP: 10.168.93.93)', '2025-11-19 16:12:45');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (239, 1, '审批设备报废', '用户 admin 批准了设备报废申请 #1 (IP: 10.168.93.93)', '2025-11-19 16:12:48');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (240, 1, '用户登出', '用户 admin 登出系统', '2025-11-19 16:18:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (241, 2, '用户登录', '用户 testuser 登录系统', '2025-11-19 16:18:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (242, 2, '用户登出', '用户 testuser 登出系统', '2025-11-19 16:19:15');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (243, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 16:19:18');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (244, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:19:47');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (245, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:19:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (246, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:20:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (247, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 16:23:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (248, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 16:27:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (249, 1, '添加部门', '添加部门 企管部 (IP: 10.168.93.93)', '2025-11-19 16:28:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (250, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-19 16:28:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (251, 1, '创建用户', '管理员 admin 创建了用户 朱绪 (IP: 10.168.93.93)', '2025-11-19 16:28:40');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (252, 1, '用户登出', '用户 admin 登出系统', '2025-11-19 16:28:47');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (253, 3, '用户登录', '用户 朱绪 登录系统', '2025-11-19 16:28:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (254, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:28:53');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (255, 3, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-19 16:29:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (256, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:29:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (257, 3, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-19 16:29:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (258, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:29:55');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (259, 3, '添加设备', '添加设备 惠普154#28 (IP: 10.168.93.93)', '2025-11-19 16:30:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (260, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:30:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (261, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:30:37');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (262, 3, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-19 16:30:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (263, 3, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-19 16:30:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (264, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:30:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (265, 3, '更新设备', '更新设备 惠普154#28 (IP: 10.168.93.93)', '2025-11-19 16:31:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (266, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:31:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (267, 3, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-19 16:31:21');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (268, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:31:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (269, 3, '更新设备', '更新设备 惠普154#28 (IP: 10.168.93.93)', '2025-11-19 16:31:34');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (270, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:31:34');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (271, 3, '用户登出', '用户 朱绪 登出系统', '2025-11-19 16:31:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (272, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 16:32:07');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (273, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:54:07');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (274, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-19 16:54:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (275, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 16:55:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (276, 1, '访问页面', '设备列表 (IP: 10.168.24.121)', '2025-11-19 16:56:19');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (277, 1, '更新设备', '更新设备 宏碁笔记本高配#19 (IP: 10.168.24.121)', '2025-11-19 16:56:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (278, 1, '访问页面', '设备列表 (IP: 10.168.24.121)', '2025-11-19 16:56:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (279, 1, '用户登出', '用户 admin 登出系统', '2025-11-19 16:57:38');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (280, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 17:20:41');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (281, 1, '用户登出', '用户 admin 登出系统', '2025-11-19 17:26:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (282, 1, '用户登录', '用户 admin 登录系统', '2025-11-19 17:27:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (283, 1, '用户登出', '用户 admin 登出系统', '2025-11-20 08:04:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (284, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 08:04:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (285, 3, '用户登录', '用户 朱绪 登录系统', '2025-11-20 08:31:59');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (286, 3, '用户登出', '用户 朱绪 登出系统', '2025-11-20 08:32:06');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (287, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 08:32:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (288, 1, '用户登出', '用户 admin 登出系统', '2025-11-20 08:32:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (289, 4, '用户登录', '用户 关鹤鸣 登录系统', '2025-11-20 08:32:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (290, 4, '用户登出', '用户 关鹤鸣 登出系统', '2025-11-20 08:33:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (291, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 08:33:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (292, 1, '用户登出', '用户 admin 登出系统', '2025-11-20 08:33:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (293, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 08:33:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (294, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:00:45');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (295, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:00:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (296, 1, '用户登出', '用户 admin 登出系统', '2025-11-20 09:02:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (297, 3, '用户登录', '用户 朱绪 登录系统', '2025-11-20 09:03:15');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (298, 3, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-20 09:03:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (299, 3, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-20 09:03:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (300, 3, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-20 09:03:41');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (301, 3, '访问页面', '公开设备仓库 (IP: 10.168.93.93)', '2025-11-20 09:03:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (302, 3, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-20 09:04:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (303, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:04:35');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (304, 3, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-20 09:04:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (305, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:04:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (306, 3, '更新设备', '更新设备 惠普154#28 (IP: 10.168.93.93)', '2025-11-20 09:04:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (307, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:04:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (308, 3, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:05:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (309, 3, '用户登出', '用户 朱绪 登出系统', '2025-11-20 09:14:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (310, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 09:15:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (311, 1, '创建用户', '管理员 admin 创建了用户 吴文杨 (IP: 10.168.93.93)', '2025-11-20 09:15:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (312, 1, '用户登出', '用户 admin 登出系统', '2025-11-20 09:15:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (313, 5, '用户登录', '用户 吴文杨 登录系统', '2025-11-20 09:15:59');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (314, 5, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:16:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (315, 5, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-20 09:16:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (316, 5, '用户登出', '用户 吴文杨 登出系统', '2025-11-20 09:22:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (317, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 09:22:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (318, 5, '用户登录', '用户 吴文杨 登录系统', '2025-11-20 09:22:48');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (319, 1, '用户登出', '用户 admin 登出系统', '2025-11-20 09:23:36');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (320, 5, '用户登录', '用户 吴文杨 登录系统', '2025-11-20 09:23:38');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (321, 5, '用户登录', '用户 吴文杨 登录系统', '2025-11-20 09:24:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (322, 5, '用户登出', '用户 吴文杨 登出系统', '2025-11-20 09:25:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (323, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 09:25:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (324, 3, '用户登录', '用户 朱绪 登录系统', '2025-11-20 09:25:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (325, 5, '访问页面', '部门管理 (IP: 10.168.93.191)', '2025-11-20 09:25:53');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (326, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 09:25:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (327, 3, '用户登出', '用户 朱绪 登出系统', '2025-11-20 09:26:08');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (328, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 09:26:15');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (329, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 09:26:18');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (330, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 09:26:27');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (331, 3, '用户登录', '用户 朱绪 登录系统', '2025-11-20 09:38:12');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (332, 3, '用户登出', '用户 朱绪 登出系统', '2025-11-20 09:38:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (333, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:41:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (334, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:41:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (335, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 09:41:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (336, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-20 10:21:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (337, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 11:07:06');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (338, 5, '访问页面', '设备类型管理 (IP: 10.168.93.191)', '2025-11-20 11:07:42');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (339, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 11:07:54');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (340, 5, '访问页面', '配件列表 (IP: 10.168.93.191)', '2025-11-20 11:08:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (341, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 11:08:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (342, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 11:12:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (343, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 11:28:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (344, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 11:28:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (345, 5, '访问页面', '设备列表 (IP: 10.168.93.191)', '2025-11-20 11:28:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (346, 5, '访问页面', '配件列表 (IP: 10.168.93.191)', '2025-11-20 11:28:21');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (347, 5, '访问页面', '设备类型管理 (IP: 10.168.93.191)', '2025-11-20 11:28:55');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (348, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 13:50:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (349, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 13:50:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (350, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 14:55:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (351, 3, '用户登录', '用户 朱绪 登录系统', '2025-11-20 14:56:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (352, 1, '用户登录', '用户 admin 登录系统', '2025-11-20 16:35:25');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (353, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_133403.db (IP: 10.168.93.93)', '2025-11-20 16:35:39');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (354, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_135917.db (IP: 10.168.93.93)', '2025-11-20 16:35:42');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (355, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_135920.db (IP: 10.168.93.93)', '2025-11-20 16:35:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (356, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_135922.db (IP: 10.168.93.93)', '2025-11-20 16:35:45');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (357, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_135333.db (IP: 10.168.93.93)', '2025-11-20 16:35:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (358, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_135925.db (IP: 10.168.93.93)', '2025-11-20 16:36:16');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (359, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_145633.db (IP: 10.168.93.93)', '2025-11-20 16:36:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (360, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_140640.db (IP: 10.168.93.93)', '2025-11-20 16:36:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (361, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_145511.db (IP: 10.168.93.93)', '2025-11-20 16:36:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (362, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_145512.db (IP: 10.168.93.93)', '2025-11-20 16:36:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (363, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_145835.db (IP: 10.168.93.93)', '2025-11-20 16:36:41');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (364, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_151230.db (IP: 10.168.93.93)', '2025-11-20 16:36:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (365, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_151337.db (IP: 10.168.93.93)', '2025-11-20 16:36:45');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (366, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_152214.db (IP: 10.168.93.93)', '2025-11-20 16:36:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (367, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_151519.db (IP: 10.168.93.93)', '2025-11-20 16:36:47');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (368, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_153501.db (IP: 10.168.93.93)', '2025-11-20 16:36:55');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (369, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_153621.db (IP: 10.168.93.93)', '2025-11-20 16:36:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (370, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_160738.db (IP: 10.168.93.93)', '2025-11-20 16:36:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (371, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_161205.db (IP: 10.168.93.93)', '2025-11-20 16:37:00');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (372, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_161042.db (IP: 10.168.93.93)', '2025-11-20 16:37:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (373, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_162540.db (IP: 10.168.93.93)', '2025-11-20 16:37:14');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (374, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_162358.db (IP: 10.168.93.93)', '2025-11-20 16:37:15');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (375, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_164412.db (IP: 10.168.93.93)', '2025-11-20 16:37:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (376, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_165009.db (IP: 10.168.93.93)', '2025-11-20 16:37:18');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (377, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_162335.db (IP: 10.168.93.93)', '2025-11-20 16:37:19');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (378, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_165337.db (IP: 10.168.93.93)', '2025-11-20 16:37:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (379, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_171116.db (IP: 10.168.93.93)', '2025-11-20 16:37:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (380, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_171621.db (IP: 10.168.93.93)', '2025-11-20 16:37:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (381, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_172027.db (IP: 10.168.93.93)', '2025-11-20 16:37:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (382, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_172435.db (IP: 10.168.93.93)', '2025-11-20 16:37:37');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (383, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251120_083222.db (IP: 10.168.93.93)', '2025-11-20 16:37:48');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (384, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251120_083223.db (IP: 10.168.93.93)', '2025-11-20 16:37:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (385, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251120_080450.db (IP: 10.168.93.93)', '2025-11-20 16:37:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (386, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251120_080741.db (IP: 10.168.93.93)', '2025-11-20 16:37:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (387, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_173559.db (IP: 10.168.93.93)', '2025-11-20 16:37:53');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (388, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_173428.db (IP: 10.168.93.93)', '2025-11-20 16:37:55');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (389, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_171326.db (IP: 10.168.93.93)', '2025-11-20 16:37:59');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (390, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_172748.db (IP: 10.168.93.93)', '2025-11-20 16:38:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (391, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_172925.db (IP: 10.168.93.93)', '2025-11-20 16:38:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (392, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251119_173126.db (IP: 10.168.93.93)', '2025-11-20 16:38:19');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (393, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251120_163826.db (IP: 10.168.93.93)', '2025-11-20 16:38:26');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (394, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:39:01');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (395, 1, '添加设备类型', '添加类型 显示器 (IP: 10.168.93.93)', '2025-11-20 16:39:21');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (396, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:39:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (397, 1, '访问页面', '设备类型管理 (IP: 10.168.93.93)', '2025-11-20 16:39:41');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (398, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:39:58');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (399, 1, '删除设备类型', '删除类型 显示器 (IP: 10.168.93.93)', '2025-11-20 16:40:07');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (400, 1, '添加设备类型', '添加类型 显示器 (IP: 10.168.93.93)', '2025-11-20 16:40:22');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (401, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:40:31');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (402, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:40:38');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (403, 1, '删除设备', '批量删除设备 宏碁笔记本高配#1 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (404, 1, '删除设备', '批量删除设备 宏碁笔记本高配#2 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (405, 1, '删除设备', '批量删除设备 宏碁笔记本高配#3 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (406, 1, '删除设备', '批量删除设备 宏碁笔记本高配#4 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (407, 1, '删除设备', '批量删除设备 宏碁笔记本高配#5 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (408, 1, '删除设备', '批量删除设备 宏碁笔记本高配#6 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (409, 1, '删除设备', '批量删除设备 宏碁笔记本高配#7 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (410, 1, '删除设备', '批量删除设备 宏碁笔记本高配#8 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (411, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:40:44');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (412, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:40:46');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (413, 1, '删除设备', '批量删除设备 宏碁笔记本高配#9 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (414, 1, '删除设备', '批量删除设备 宏碁笔记本高配#10 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (415, 1, '删除设备', '批量删除设备 宏碁笔记本高配#11 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (416, 1, '删除设备', '批量删除设备 宏碁笔记本高配#12 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (417, 1, '删除设备', '批量删除设备 宏碁笔记本高配#13 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (418, 1, '删除设备', '批量删除设备 宏碁笔记本高配#14 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (419, 1, '删除设备', '批量删除设备 宏碁笔记本高配#15 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (420, 1, '删除设备', '批量删除设备 宏碁笔记本高配#16 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (421, 1, '删除设备', '批量删除设备 宏碁笔记本高配#17 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (422, 1, '删除设备', '批量删除设备 宏碁笔记本高配#18 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (423, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:40:49');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (424, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:41:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (425, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:41:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (426, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:41:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (427, 1, '设为可申请', '设备 宏碁笔记本高配#19 设为可申请 (IP: 10.168.93.93)', '2025-11-20 16:41:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (428, 1, '设为可申请', '设备 惠普154#28 设为可申请 (IP: 10.168.93.93)', '2025-11-20 16:41:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (429, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:41:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (430, 1, '移出公开仓库', '设备 惠普154#28 从信息部公开仓库移出 (IP: 10.168.93.93)', '2025-11-20 16:41:48');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (431, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:41:48');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (432, 1, '取消可申请', '设备 惠普154#28 取消可申请状态 (IP: 10.168.93.93)', '2025-11-20 16:41:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (433, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:41:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (434, 1, '移出公开仓库', '设备 宏碁笔记本高配#19 从信息部公开仓库移出 (IP: 10.168.93.93)', '2025-11-20 16:41:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (435, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:41:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (436, 1, '取消可申请', '设备 宏碁笔记本高配#19 取消可申请状态 (IP: 10.168.93.93)', '2025-11-20 16:42:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (437, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-20 16:42:04');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (438, 1, '用户登录', '用户 admin 登录系统', '2025-11-21 08:36:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (439, 1, '用户登录', '用户 admin 登录系统', '2025-11-21 08:41:38');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (440, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-21 09:11:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (441, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-21 09:12:39');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (442, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-21 09:12:45');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (443, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-21 09:12:53');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (444, 1, '访问页面', '设备类型管理 (IP: 10.168.93.93)', '2025-11-21 09:13:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (445, 1, '用户登出', '用户 admin 登出系统', '2025-11-21 09:15:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (446, 1, '用户登录', '用户 admin 登录系统', '2025-11-21 09:25:43');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (447, 1, '自动分配审批', '对于 配件申请#1 的审批节点 部门领导，系统自动分配给管理员用户ID 1。', '2025-11-21 09:26:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (448, 1, '创建配件申请', '用户 admin 创建了配件申请 #1', '2025-11-21 09:26:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (449, 1, '用户登出', '用户 admin 登出系统', '2025-11-21 09:27:19');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (450, 4, '用户登录', '用户 关鹤鸣 登录系统', '2025-11-21 09:27:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (451, 1, '用户登录', '用户 admin 登录系统', '2025-11-22 09:10:54');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (452, 1, '用户登录', '用户 admin 登录系统', '2025-11-22 10:58:48');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (453, 1, '用户登录', '用户 admin 登录系统', '2025-11-24 09:07:05');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (454, 5, '数据库恢复', '用户 admin 恢复了数据库: app_backup_20251124_091115.db (IP: 10.168.93.93)', '2025-11-28 18:55:40');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (455, 1, '用户登录', '用户 admin 登录系统', '2025-11-28 21:42:15');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (456, 1, '审批配件申请', '用户 admin 批准了配件申请 #1 (配件: 内存10G, 数量: 1) (IP: 10.168.93.93)', '2025-11-28 21:47:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (457, 1, '减少配件库存', '配件申请 #1 审批完成，减少 内存10G 库存 1 个 (IP: 10.168.93.93)', '2025-11-28 21:47:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (458, 1, '审批配件申请', '用户 admin 批准了配件申请 #1 (配件: 内存10G, 数量: 1) (IP: 10.168.93.93)', '2025-11-28 21:47:32');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (459, 1, '减少配件库存', '配件申请 #1 审批完成，减少 内存10G 库存 1 个 (IP: 10.168.93.93)', '2025-11-28 21:47:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (460, 1, '审批配件申请', '用户 admin 批准了配件申请 #1 (配件: 内存10G, 数量: 1) (IP: 10.168.93.93)', '2025-11-28 21:47:33');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (461, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-28 21:47:56');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (462, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:47:59');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (463, 1, '更新设备', '更新设备 惠普154#28 (IP: 10.168.93.93)', '2025-11-28 21:48:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (464, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:48:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (465, 1, '更新设备', '更新设备 宏碁笔记本高配#27 (IP: 10.168.93.93)', '2025-11-28 21:48:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (466, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:48:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (467, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-28 21:48:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (468, 1, '更新配件', '更新配件 内存10G#me1003 (IP: 10.168.93.93)', '2025-11-28 21:49:07');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (469, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-28 21:49:07');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (470, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-28 21:53:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (471, 1, '访问页面', '资产/配件管理中心 (IP: 10.168.93.93)', '2025-11-28 21:53:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (472, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:58:50');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (473, 1, '更新设备', '更新设备 惠普154#28 (IP: 10.168.93.93)', '2025-11-28 21:58:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (474, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:58:57');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (475, 1, '更新设备', '更新设备 宏碁笔记本高配#27 (IP: 10.168.93.93)', '2025-11-28 21:59:05');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (476, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:59:05');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (477, 1, '更新设备', '更新设备 宏碁笔记本高配#26 (IP: 10.168.93.93)', '2025-11-28 21:59:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (478, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:59:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (479, 1, '更新设备', '更新设备 惠普154#28 (IP: 10.168.93.93)', '2025-11-28 21:59:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (480, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:59:24');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (481, 1, '更新设备', '更新设备 宏碁笔记本高配#25 (IP: 10.168.93.93)', '2025-11-28 21:59:42');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (482, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 21:59:42');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (483, 1, '访问页面', '设备类型管理 (IP: 10.168.93.93)', '2025-11-28 22:11:12');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (484, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-28 22:12:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (485, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-28 22:12:30');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (486, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-28 22:12:36');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (487, 1, '导出配件', '导出配件数据 共 3 条 (IP: 10.168.93.93)', '2025-11-28 22:12:39');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (488, 1, '访问页面', '设备类型管理 (IP: 10.168.93.93)', '2025-11-28 22:20:10');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (489, 1, '访问页面', '设备类型管理 (IP: 10.168.93.93)', '2025-11-28 22:20:17');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (490, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_062029.db (IP: 10.168.93.93)', '2025-11-28 22:20:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (491, 1, '访问页面', '资产/配件管理中心 (IP: 10.168.93.93)', '2025-11-28 22:25:26');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (492, 1, '访问页面', '设备类型管理 (IP: 10.168.93.93)', '2025-11-28 22:25:35');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (493, 1, '编辑用户', '管理员 admin 编辑了用户 关鹤鸣 (IP: 10.168.93.93)', '2025-11-28 22:26:31');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (494, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_065251.db (IP: 10.168.93.93)', '2025-11-28 22:52:51');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (495, 1, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-28 22:57:03');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (496, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_145813.db (IP: 10.168.93.93)', '2025-11-28 22:58:13');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (497, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_145923.db (IP: 10.168.93.93)', '2025-11-28 22:59:23');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (498, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_145942.db (IP: 10.168.93.93)', '2025-11-28 22:59:42');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (499, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_150011.db (IP: 10.168.93.93)', '2025-11-28 23:00:11');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (500, 1, '用户登出', '用户 admin 登出系统', '2025-11-28 23:01:52');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (501, 1, '用户登录', '用户 admin 登录系统', '2025-11-28 23:01:54');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (502, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_150609.db (IP: 10.168.93.93)', '2025-11-28 23:06:09');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (503, 1, '导出数据库(MySQL)', '用户 admin 导出了数据库到 MySQL 转储: app_db_mysql_dump_20251128_150719.sql (IP: 10.168.93.93)', '2025-11-28 23:07:20');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (504, 1, '导出数据库(MSSQL)', '用户 admin 导出了数据库到 MSSQL 转储: app_db_mssql_dump_20251128_150729.sql (IP: 10.168.93.93)', '2025-11-28 23:07:29');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (505, 1, '导出数据库(MySQL)', '用户 admin 导出了数据库到 MySQL 转储: app_db_mysql_dump_20251128_150731.sql (IP: 10.168.93.93)', '2025-11-28 23:07:31');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (506, 1, '数据库备份', '用户 admin 备份了数据库: app_backup_20251128_150734.db (IP: 10.168.93.93)', '2025-11-28 23:07:34');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (507, 1, '导出数据库(MySQL)', '用户 admin 导出了数据库到 MySQL 转储: app_db_mysql_dump_20251128_151502.sql (IP: 10.168.93.93)', '2025-11-28 23:15:02');
INSERT INTO dbo.user_activity_log ([id], [user_id], [action], [description], [timestamp]) VALUES (508, 1, '导出数据库(MSSQL)', '用户 admin 导出了数据库到 MSSQL 转储: app_db_mssql_dump_20251128_151536.sql (IP: 10.168.93.93)', '2025-11-28 23:15:36');

IF OBJECT_ID(N'dbo.user_custom_role', N'U') IS NOT NULL DROP TABLE dbo.user_custom_role;
CREATE TABLE dbo.user_custom_role (
  [user_id] INT NOT NULL,
  [role_id] INT NOT NULL,
  CONSTRAINT PK_user_custom_role PRIMARY KEY ([user_id], [role_id])
);

IF OBJECT_ID(N'dbo.workflow_node', N'U') IS NOT NULL DROP TABLE dbo.workflow_node;
CREATE TABLE dbo.workflow_node (
  [id] INT NOT NULL,
  [name] NVARCHAR(MAX),
  [order_type] NVARCHAR(MAX),
  [role_required] NVARCHAR(MAX),
  [sequence] INT,
  [is_active] BIT,
  [created_date] DATETIME2,
  [is_parallel] BIT DEFAULT 0,
  [required_approvals] INT DEFAULT 1,
  [actions_on_reject] NVARCHAR(MAX),
  [approver_user_id] INT,
  [approver_user_ids] NVARCHAR(MAX),
  CONSTRAINT PK_workflow_node PRIMARY KEY ([id])
);

INSERT INTO dbo.workflow_node ([id], [name], [order_type], [role_required], [sequence], [is_active], [created_date], [is_parallel], [required_approvals], [actions_on_reject], [approver_user_id], [approver_user_ids]) VALUES (1, '部门领导审批', 'repair_order', 'department_head', 1, 1, '2025-11-19 11:48:12', 0, 1, NULL, NULL, NULL);
INSERT INTO dbo.workflow_node ([id], [name], [order_type], [role_required], [sequence], [is_active], [created_date], [is_parallel], [required_approvals], [actions_on_reject], [approver_user_id], [approver_user_ids]) VALUES (2, '管理员审批', 'repair_order', 'admin', 2, 1, '2025-11-19 11:48:12', 0, 1, NULL, NULL, NULL);
INSERT INTO dbo.workflow_node ([id], [name], [order_type], [role_required], [sequence], [is_active], [created_date], [is_parallel], [required_approvals], [actions_on_reject], [approver_user_id], [approver_user_ids]) VALUES (3, '部门领导审批', 'part_request_order', 'department_head', 1, 1, '2025-11-19 11:48:12', 0, 1, NULL, NULL, NULL);
INSERT INTO dbo.workflow_node ([id], [name], [order_type], [role_required], [sequence], [is_active], [created_date], [is_parallel], [required_approvals], [actions_on_reject], [approver_user_id], [approver_user_ids]) VALUES (4, '管理员审批', 'part_request_order', 'admin', 2, 1, '2025-11-19 11:48:12', 0, 1, NULL, NULL, NULL);
INSERT INTO dbo.workflow_node ([id], [name], [order_type], [role_required], [sequence], [is_active], [created_date], [is_parallel], [required_approvals], [actions_on_reject], [approver_user_id], [approver_user_ids]) VALUES (5, '管理员审批', 'equipment_application', 'admin', 1, 1, '2025-11-20 09:16:48', 0, 1, NULL, 5, '[5]');

IF OBJECT_ID(N'dbo.workflow_step', N'U') IS NOT NULL DROP TABLE dbo.workflow_step;
CREATE TABLE dbo.workflow_step (
  [id] INT NOT NULL,
  [template_id] INT,
  [sequence] INT,
  [step_name] NVARCHAR(MAX),
  [approver_role] NVARCHAR(MAX),
  [approver_dept] NVARCHAR(MAX),
  [is_parallel] BIT,
  [timeout_days] INT,
  [required_approvals] INT,
  [conditions] NVARCHAR(MAX),
  [actions_on_approve] NVARCHAR(MAX),
  [actions_on_reject] NVARCHAR(MAX),
  CONSTRAINT PK_workflow_step PRIMARY KEY ([id])
);

IF OBJECT_ID(N'dbo.workflow_template', N'U') IS NOT NULL DROP TABLE dbo.workflow_template;
CREATE TABLE dbo.workflow_template (
  [id] INT NOT NULL,
  [name] NVARCHAR(MAX),
  [order_type] NVARCHAR(MAX),
  [description] NVARCHAR(MAX),
  [is_active] BIT,
  [is_default] BIT,
  [created_by_id] INT,
  [created_date] DATETIME2,
  [updated_date] DATETIME2,
  CONSTRAINT PK_workflow_template PRIMARY KEY ([id])
);

