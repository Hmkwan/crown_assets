-- PostgreSQL dump generated from SQLite
-- Source: C:\Users\it03.GD\Desktop\TEST\app.db
-- Generated at: 2025-11-29 14:50:58
-- Timezone conversion: UTC -> Asia/Shanghai

-- Start transaction
BEGIN;

-- Table: department
DROP TABLE IF EXISTS "department" CASCADE;
CREATE TABLE "department" (
  "id" SERIAL,
  "name" TEXT,
  "code" TEXT,
  "cost_center" TEXT,
  "location" TEXT,
  "description" TEXT,
  PRIMARY KEY ("id")
);

-- Data for table: department
INSERT INTO "department" ("id", "name", "code", "cost_center", "location", "description") VALUES (1, '信息部', 'IT', 'CC001', 'A座5楼', '信息技术部门');
INSERT INTO "department" ("id", "name", "code", "cost_center", "location", "description") VALUES (2, '财务部', 'FIN', 'CC002', 'A座3楼', '财务管理部门');
INSERT INTO "department" ("id", "name", "code", "cost_center", "location", "description") VALUES (3, '人力行政部', 'HR', 'CC003', 'A座2楼', '人力资源部门');
INSERT INTO "department" ("id", "name", "code", "cost_center", "location", "description") VALUES (4, '国内销售中心', 'SALES', 'CC004', 'B座1楼', '销售部门');
INSERT INTO "department" ("id", "name", "code", "cost_center", "location", "description") VALUES (5, '生产办', 'PROD', 'CC005', 'C厂房', '生产制造部门');
INSERT INTO "department" ("id", "name", "code", "cost_center", "location", "description") VALUES (6, '企管部', 'ADMIN', 'CC006', 'A座4楼', '企业管理部门');

-- Reset sequence for department.id
SELECT setval(pg_get_serial_sequence('"department"', 'id'), COALESCE((SELECT MAX("id") FROM "department"), 1), true);

-- Table: equipment_type
DROP TABLE IF EXISTS "equipment_type" CASCADE;
CREATE TABLE "equipment_type" (
  "id" SERIAL,
  "name" TEXT NOT NULL,
  "description" TEXT,
  "created_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Data for table: equipment_type
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (1, '台式电脑', '台式办公电脑', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (2, '笔记本电脑', '笔记本办公电脑', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (3, '服务器', '服务器设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (4, '打印机', '激光/喷墨打印机', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (5, '扫描仪', '文档扫描设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (6, '投影仪', '会议投影设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (7, '显示器', '显示器设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (8, '路由器', '网络路由器', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (9, '交换机', '网络交换机', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (10, '防火墙', '网络安全设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (11, 'UPS电源', '不间断电源', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (12, '网络存储', 'NAS/SAN存储设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (13, '摄像头', '监控摄像设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (14, '会议设备', '会议系统设备', '2025-11-30 04:36:06');
INSERT INTO "equipment_type" ("id", "name", "description", "created_date") VALUES (15, '电话设备', 'IP电话等通讯设备', '2025-11-30 04:36:06');

-- Reset sequence for equipment_type.id
SELECT setval(pg_get_serial_sequence('"equipment_type"', 'id'), COALESCE((SELECT MAX("id") FROM "equipment_type"), 1), true);

-- Table: spare_part_type
DROP TABLE IF EXISTS "spare_part_type" CASCADE;
CREATE TABLE "spare_part_type" (
  "id" SERIAL,
  "name" TEXT NOT NULL,
  "description" TEXT,
  "created_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Data for table: spare_part_type
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (1, '内存条', '电脑内存条', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (2, '硬盘', '机械硬盘/固态硬盘', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (3, '电源', '电源适配器/电源模块', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (4, '主板', '电脑主板', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (5, 'CPU', '中央处理器', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (6, '显卡', '图形处理器', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (7, '散热器', 'CPU散热器', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (8, '机箱风扇', '机箱散热风扇', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (9, '网卡', '有线/无线网卡', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (10, '声卡', '声卡设备', '2025-11-30 04:36:06');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (11, '键盘', '键盘设备', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (12, '鼠标', '鼠标设备', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (13, '数据线', '各类数据传输线', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (14, '网线', '网络连接线', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (15, '电源线', '电源连接线', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (16, '墨盒/硒鼓', '打印机耗材', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (17, '打印纸', '打印用纸', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (18, '投影灯泡', '投影仪灯泡', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (19, '电池', 'UPS/设备电池', '2025-11-30 04:36:07');
INSERT INTO "spare_part_type" ("id", "name", "description", "created_date") VALUES (20, '转接头', '各类转接器', '2025-11-30 04:36:07');

-- Reset sequence for spare_part_type.id
SELECT setval(pg_get_serial_sequence('"spare_part_type"', 'id'), COALESCE((SELECT MAX("id") FROM "spare_part_type"), 1), true);

-- Table: action_log
DROP TABLE IF EXISTS "action_log" CASCADE;
CREATE TABLE "action_log" (
  "id" SERIAL,
  "action_name" TEXT,
  "workflow_node_id" INTEGER,
  "approval_workflow_id" INTEGER,
  "payload" TEXT,
  "status" TEXT,
  "result" TEXT,
  "executed_at" TIMESTAMP,
  "retry_count" INTEGER,
  PRIMARY KEY ("id")
);

-- Table: user
DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE "user" (
  "id" SERIAL,
  "username" TEXT,
  "email" TEXT,
  "password_hash" TEXT,
  "role" TEXT,
  "department_id" INTEGER,
  "department" TEXT,
  "is_active" BOOLEAN,
  "workflow_roles" TEXT,
  "can_manage_equipment" BOOLEAN,
  "can_manage_spare_parts" BOOLEAN,
  "can_manage_repairs" BOOLEAN,
  "can_manage_part_requests" BOOLEAN,
  "can_view_workflow" BOOLEAN,
  "can_edit_workflow" BOOLEAN,
  "can_manage_workflow_templates" BOOLEAN,
  "can_view_reports" BOOLEAN,
  "can_view_logs" BOOLEAN,
  PRIMARY KEY ("id")
);

-- Data for table: user
INSERT INTO "user" ("id", "username", "email", "password_hash", "role", "department_id", "department", "is_active", "workflow_roles", "can_manage_equipment", "can_manage_spare_parts", "can_manage_repairs", "can_manage_part_requests", "can_view_workflow", "can_edit_workflow", "can_manage_workflow_templates", "can_view_reports", "can_view_logs") VALUES (1, 'admin', 'admin@example.com', 'scrypt:32768:8:1$ZKqSXjZUHDHAs39q$1ff3e69086342f985b93697fb1c7ec19a5dc0c6e11cab3f8b96baf860044f802ad95bae8a998a7dabb0616b211cb582f54c86128b83b4a0f9b3811f99f805daf', 'admin', NULL, '超级管理员', 1, '["admin"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO "user" ("id", "username", "email", "password_hash", "role", "department_id", "department", "is_active", "workflow_roles", "can_manage_equipment", "can_manage_spare_parts", "can_manage_repairs", "can_manage_part_requests", "can_view_workflow", "can_edit_workflow", "can_manage_workflow_templates", "can_view_reports", "can_view_logs") VALUES (2, '陈松', 'chengs@crown.com.cn', 'scrypt:32768:8:1$gIPhb6J3XL5SySfW$6b511c03c16a9a6837fd5d7a103665b7b089ac8ee8c46e8503afdb8f236e1e0b79800fbd488df2c21ed544e53ccd8f1603f5f4c46a0a6447fcc88c67492bfe4f', 'department_head', 6, '企管部', 1, '["department_head"]', 1, 1, 1, 1, 1, 0, 0, 1, 0);
INSERT INTO "user" ("id", "username", "email", "password_hash", "role", "department_id", "department", "is_active", "workflow_roles", "can_manage_equipment", "can_manage_spare_parts", "can_manage_repairs", "can_manage_part_requests", "can_view_workflow", "can_edit_workflow", "can_manage_workflow_templates", "can_view_reports", "can_view_logs") VALUES (3, '吴文杨', 'wuwy@crown.com.cn', 'scrypt:32768:8:1$sSZm3A6ziQKRbQ7K$43fc8af8fee04e349853f45f7563e603a5e815a895ddd4ff69b122a058c973225855537244781ba0114af07143a90ecf43cdc1b034037d2215678b40f7cf361a', 'admin', 1, '信息部', 1, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO "user" ("id", "username", "email", "password_hash", "role", "department_id", "department", "is_active", "workflow_roles", "can_manage_equipment", "can_manage_spare_parts", "can_manage_repairs", "can_manage_part_requests", "can_view_workflow", "can_edit_workflow", "can_manage_workflow_templates", "can_view_reports", "can_view_logs") VALUES (4, '关鹤鸣', 'guanhm@crown.com.cn', 'scrypt:32768:8:1$oRAInE569dBPprb2$deba730add0c20a3fc6cc65d4b13d00e74f3267a175982d553777eaf44624a3320a0963a60c9f239df9538b9ff75a6c85d95991c90de8fdba491dbb60eee6b6e', 'technician', 1, '信息部', 1, '["security"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO "user" ("id", "username", "email", "password_hash", "role", "department_id", "department", "is_active", "workflow_roles", "can_manage_equipment", "can_manage_spare_parts", "can_manage_repairs", "can_manage_part_requests", "can_view_workflow", "can_edit_workflow", "can_manage_workflow_templates", "can_view_reports", "can_view_logs") VALUES (5, '朱绪', 'zhux@crown.com.cn', 'scrypt:32768:8:1$aQxV3PLh3ZBMqWIP$cc5aa81827b50e19febb39384c6419b376923fa7cb52e2e57bfcf7bc8dfd6872c0940127b3413a8a0e90fea2ff4991a0a082bb3bdb00d6f46e9c4c88c7363721', 'user', 6, '企管部', 1, '["auditor"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO "user" ("id", "username", "email", "password_hash", "role", "department_id", "department", "is_active", "workflow_roles", "can_manage_equipment", "can_manage_spare_parts", "can_manage_repairs", "can_manage_part_requests", "can_view_workflow", "can_edit_workflow", "can_manage_workflow_templates", "can_view_reports", "can_view_logs") VALUES (6, 'testuser', 'test@example.com', 'pbkdf2:sha256:260000$u1sNyWFHZYCtduoe$8149ed2e7c5c07b66099bc367e4b99dfbe092858ada65cc0e0214fdd4725b227', 'user', 5, '生产办', 1, '["employee", "warehouse"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);

-- Reset sequence for user.id
SELECT setval(pg_get_serial_sequence('"user"', 'id'), COALESCE((SELECT MAX("id") FROM "user"), 1), true);

-- Table: equipment
DROP TABLE IF EXISTS "equipment" CASCADE;
CREATE TABLE "equipment" (
  "id" SERIAL,
  "name" TEXT,
  "type_id" INTEGER,
  "type" TEXT,
  "brand" TEXT,
  "model" TEXT,
  "serial_number" TEXT,
  "purchase_date" TIMESTAMP,
  "price" DOUBLE PRECISION,
  "department_id" INTEGER,
  "department" TEXT,
  "status" TEXT,
  "is_public_pool" BOOLEAN,
  PRIMARY KEY ("id")
);

-- Table: spare_part
DROP TABLE IF EXISTS "spare_part" CASCADE;
CREATE TABLE "spare_part" (
  "id" SERIAL,
  "name" TEXT,
  "part_number" TEXT,
  "type_id" INTEGER,
  "price" DOUBLE PRECISION,
  "stock_quantity" INTEGER,
  "min_stock_level" INTEGER,
  "department_id" INTEGER,
  "department" TEXT,
  "location" TEXT,
  "purchase_date" TIMESTAMP,
  "is_public" BOOLEAN,
  PRIMARY KEY ("id")
);

-- Table: repair_order
DROP TABLE IF EXISTS "repair_order" CASCADE;
CREATE TABLE "repair_order" (
  "id" SERIAL,
  "equipment_id" INTEGER,
  "requester_id" INTEGER,
  "technician_id" INTEGER,
  "department_head_id" INTEGER,
  "admin_id" INTEGER,
  "description" TEXT,
  "status" TEXT,
  "created_date" TIMESTAMP,
  "updated_date" TIMESTAMP,
  "completed_date" TIMESTAMP,
  "department_head_approved" BOOLEAN,
  "admin_approved" BOOLEAN,
  PRIMARY KEY ("id")
);

-- Table: part_request_order
DROP TABLE IF EXISTS "part_request_order" CASCADE;
CREATE TABLE "part_request_order" (
  "id" SERIAL,
  "requester_id" INTEGER,
  "department_head_id" INTEGER,
  "admin_id" INTEGER,
  "part_name" TEXT,
  "part_number" TEXT,
  "quantity" INTEGER,
  "reason" TEXT,
  "status" TEXT,
  "department_head_approved" BOOLEAN,
  "admin_approved" BOOLEAN,
  "created_date" TIMESTAMP,
  "updated_date" TIMESTAMP,
  "completed_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: account_request
DROP TABLE IF EXISTS "account_request" CASCADE;
CREATE TABLE "account_request" (
  "id" SERIAL,
  "username" TEXT,
  "full_name" TEXT,
  "employee_no" TEXT,
  "email" TEXT,
  "department" TEXT,
  "role_requested" TEXT,
  "reason" TEXT,
  "password_hash" TEXT,
  "status" TEXT,
  "created_date" TIMESTAMP,
  "processed_date" TIMESTAMP,
  "approver_id" INTEGER,
  "approver_comments" TEXT,
  PRIMARY KEY ("id")
);

-- Table: equipment_transfer
DROP TABLE IF EXISTS "equipment_transfer" CASCADE;
CREATE TABLE "equipment_transfer" (
  "id" SERIAL,
  "equipment_id" INTEGER,
  "from_department" TEXT,
  "to_department" TEXT,
  "requester_id" INTEGER,
  "description" TEXT,
  "status" TEXT,
  "created_date" TIMESTAMP,
  "updated_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: equipment_scrap
DROP TABLE IF EXISTS "equipment_scrap" CASCADE;
CREATE TABLE "equipment_scrap" (
  "id" SERIAL,
  "equipment_id" INTEGER,
  "requester_id" INTEGER,
  "description" TEXT,
  "status" TEXT,
  "created_date" TIMESTAMP,
  "updated_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: equipment_loan
DROP TABLE IF EXISTS "equipment_loan" CASCADE;
CREATE TABLE "equipment_loan" (
  "id" SERIAL,
  "equipment_id" INTEGER,
  "requester_id" INTEGER,
  "requester_dept" TEXT,
  "start_date" TIMESTAMP,
  "end_date" TIMESTAMP,
  "status" TEXT,
  "approved_by" INTEGER,
  "approved_date" TIMESTAMP,
  "borrowed_date" TIMESTAMP,
  "returned_date" TIMESTAMP,
  "notes" TEXT,
  "pickup_notified" BOOLEAN,
  "created_date" TIMESTAMP,
  "updated_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: equipment_application
DROP TABLE IF EXISTS "equipment_application" CASCADE;
CREATE TABLE "equipment_application" (
  "id" SERIAL,
  "equipment_id" INTEGER,
  "applicant_id" INTEGER,
  "applicant_dept" TEXT,
  "reason" TEXT,
  "status" TEXT,
  "created_date" TIMESTAMP,
  "approved_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: notification
DROP TABLE IF EXISTS "notification" CASCADE;
CREATE TABLE "notification" (
  "id" SERIAL,
  "user_id" INTEGER,
  "title" TEXT,
  "message" TEXT,
  "is_read" BOOLEAN,
  "created_date" TIMESTAMP,
  "order_type" TEXT,
  "order_id" INTEGER,
  PRIMARY KEY ("id")
);

-- Data for table: notification
INSERT INTO "notification" ("id", "user_id", "title", "message", "is_read", "created_date", "order_type", "order_id") VALUES (1, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:26:36', NULL, NULL);
INSERT INTO "notification" ("id", "user_id", "title", "message", "is_read", "created_date", "order_type", "order_id") VALUES (2, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:26:50', NULL, NULL);
INSERT INTO "notification" ("id", "user_id", "title", "message", "is_read", "created_date", "order_type", "order_id") VALUES (3, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:31:54', NULL, NULL);
INSERT INTO "notification" ("id", "user_id", "title", "message", "is_read", "created_date", "order_type", "order_id") VALUES (4, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:38:24', NULL, NULL);
INSERT INTO "notification" ("id", "user_id", "title", "message", "is_read", "created_date", "order_type", "order_id") VALUES (5, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:38:39', NULL, NULL);

-- Reset sequence for notification.id
SELECT setval(pg_get_serial_sequence('"notification"', 'id'), COALESCE((SELECT MAX("id") FROM "notification"), 1), true);

-- Table: user_activity_log
DROP TABLE IF EXISTS "user_activity_log" CASCADE;
CREATE TABLE "user_activity_log" (
  "id" SERIAL,
  "user_id" INTEGER,
  "action" TEXT,
  "description" TEXT,
  "timestamp" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Data for table: user_activity_log
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (1, 1, '数据库重置', '用户 admin 重置了数据库 (IP: 10.168.93.93)', '2025-11-30 04:36:07');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (2, 1, '用户登出', '用户 admin 登出系统', '2025-11-30 04:36:08');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (3, 1, '用户登录', '用户 admin 登录系统', '2025-11-30 04:36:13');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (4, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-30 05:16:12');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (5, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:16:47');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (6, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:16:58');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (7, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:16:59');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (8, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 05:17:00');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (9, 1, '创建用户', '管理员 admin 创建了用户 陈松 (IP: 10.168.93.93)', '2025-11-30 05:18:02');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (10, 1, '创建用户', '管理员 admin 创建了用户 吴文杨 (IP: 10.168.93.93)', '2025-11-30 05:18:38');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (11, 1, '创建用户', '管理员 admin 创建了用户 关鹤鸣 (IP: 10.168.93.93)', '2025-11-30 05:19:21');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (12, 1, '编辑用户', '管理员 admin 编辑了用户 陈松 (IP: 10.168.93.93)', '2025-11-30 05:20:49');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (13, 1, '创建用户', '管理员 admin 创建了用户 朱绪 (IP: 10.168.93.93)', '2025-11-30 05:21:33');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (14, 1, '编辑用户', '管理员 admin 编辑了用户 关鹤鸣 (IP: 10.168.93.93)', '2025-11-30 05:24:34');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (15, 1, '编辑用户', '管理员 admin 编辑了用户 testuser (IP: 10.168.93.93)', '2025-11-30 05:27:29');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (16, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:43:48');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (17, 1, '导出数据库(MySQL)', '用户 admin 导出了数据库到 MySQL 转储: app_db_mysql_dump_20251129_224405.sql (IP: 10.168.93.93)', '2025-11-30 06:44:05');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (18, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_150734.db (IP: 10.168.93.93)', '2025-11-30 06:45:27');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (19, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_150609.db (IP: 10.168.93.93)', '2025-11-30 06:45:32');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (20, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251127_151846.db (IP: 10.168.93.93)', '2025-11-30 06:45:38');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (21, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_155439.db (IP: 10.168.93.93)', '2025-11-30 06:45:44');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (22, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_163122.db (IP: 10.168.93.93)', '2025-11-30 06:45:49');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (23, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251129_171125.db (IP: 10.168.93.93)', '2025-11-30 06:46:09');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (24, 1, '用户登出', '用户 admin 登出系统', '2025-11-30 06:46:34');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (25, 4, '用户登录', '用户 关鹤鸣 登录系统', '2025-11-30 06:46:37');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (26, 4, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-30 06:47:04');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (27, 4, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 06:47:08');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (28, 4, '用户登出', '用户 关鹤鸣 登出系统', '2025-11-30 06:47:26');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (29, 2, '用户登录', '用户 陈松 登录系统', '2025-11-30 06:47:38');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (30, 2, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 06:47:44');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (31, 2, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 06:47:54');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (32, 2, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-30 06:47:58');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (33, 2, '用户登出', '用户 陈松 登出系统', '2025-11-30 06:48:45');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (34, 3, '用户登录', '用户 吴文杨 登录系统', '2025-11-30 06:48:57');
INSERT INTO "user_activity_log" ("id", "user_id", "action", "description", "timestamp") VALUES (35, 3, '导出数据库(MSSQL)', '用户 吴文杨 导出了数据库到 MSSQL 转储: app_db_mssql_dump_20251129_224914.sql (IP: 10.168.93.93)', '2025-11-30 06:49:14');

-- Reset sequence for user_activity_log.id
SELECT setval(pg_get_serial_sequence('"user_activity_log"', 'id'), COALESCE((SELECT MAX("id") FROM "user_activity_log"), 1), true);

-- Table: asset_cost
DROP TABLE IF EXISTS "asset_cost" CASCADE;
CREATE TABLE "asset_cost" (
  "id" SERIAL,
  "equipment_id" INTEGER,
  "purchase_price" DOUBLE PRECISION,
  "purchase_date" TIMESTAMP,
  "maintenance_cost" DOUBLE PRECISION,
  "depreciation_rate" DOUBLE PRECISION,
  "residual_value" DOUBLE PRECISION,
  "depreciation_method" TEXT,
  "expected_lifespan" INTEGER,
  "supplier" TEXT,
  "warranty_period" INTEGER,
  "created_date" TIMESTAMP,
  "updated_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: asset_lifecycle
DROP TABLE IF EXISTS "asset_lifecycle" CASCADE;
CREATE TABLE "asset_lifecycle" (
  "id" SERIAL,
  "equipment_id" INTEGER,
  "event_type" TEXT,
  "event_date" TIMESTAMP,
  "old_status" TEXT,
  "new_status" TEXT,
  "description" TEXT,
  "responsible_user_id" INTEGER,
  "cost_involved" DOUBLE PRECISION,
  "documents" TEXT,
  PRIMARY KEY ("id")
);

-- Table: inventory_warning
DROP TABLE IF EXISTS "inventory_warning" CASCADE;
CREATE TABLE "inventory_warning" (
  "id" SERIAL,
  "spare_part_id" INTEGER,
  "min_threshold" INTEGER,
  "critical_threshold" INTEGER,
  "reorder_quantity" INTEGER,
  "lead_time_days" INTEGER,
  "enabled" BOOLEAN,
  "last_warned_date" TIMESTAMP,
  "created_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: asset_handover
DROP TABLE IF EXISTS "asset_handover" CASCADE;
CREATE TABLE "asset_handover" (
  "id" SERIAL,
  "from_user_id" INTEGER,
  "to_user_id" INTEGER,
  "equipment_ids" TEXT,
  "status" TEXT,
  "reason" TEXT,
  "reason_detail" TEXT,
  "created_date" TIMESTAMP,
  "completed_date" TIMESTAMP,
  "completed_by_id" INTEGER,
  PRIMARY KEY ("id")
);

-- Table: role_definition
DROP TABLE IF EXISTS "role_definition" CASCADE;
CREATE TABLE "role_definition" (
  "id" SERIAL,
  "name" TEXT,
  "description" TEXT,
  "is_custom" BOOLEAN,
  "is_active" BOOLEAN,
  "created_date" TIMESTAMP,
  "created_by_id" INTEGER,
  PRIMARY KEY ("id")
);

-- Table: audit_log
DROP TABLE IF EXISTS "audit_log" CASCADE;
CREATE TABLE "audit_log" (
  "id" SERIAL,
  "user_id" INTEGER,
  "action_type" TEXT,
  "resource_type" TEXT,
  "resource_id" INTEGER,
  "old_value" TEXT,
  "new_value" TEXT,
  "ip_address" TEXT,
  "reason" TEXT,
  "created_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: workflow_template
DROP TABLE IF EXISTS "workflow_template" CASCADE;
CREATE TABLE "workflow_template" (
  "id" SERIAL,
  "name" TEXT,
  "order_type" TEXT,
  "description" TEXT,
  "is_active" BOOLEAN,
  "is_default" BOOLEAN,
  "created_by_id" INTEGER,
  "created_date" TIMESTAMP,
  "updated_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Data for table: workflow_template
INSERT INTO "workflow_template" ("id", "name", "order_type", "description", "is_active", "is_default", "created_by_id", "created_date", "updated_date") VALUES (1, '标准维修流程', 'repair_order', '员工申请 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO "workflow_template" ("id", "name", "order_type", "description", "is_active", "is_default", "created_by_id", "created_date", "updated_date") VALUES (2, '标准配件申请流程', 'part_request_order', '员工申请 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO "workflow_template" ("id", "name", "order_type", "description", "is_active", "is_default", "created_by_id", "created_date", "updated_date") VALUES (3, '标准设备调拨流程', 'equipment_transfer', '申请调拨 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO "workflow_template" ("id", "name", "order_type", "description", "is_active", "is_default", "created_by_id", "created_date", "updated_date") VALUES (4, '标准设备报废流程', 'equipment_scrap', '申请报废 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO "workflow_template" ("id", "name", "order_type", "description", "is_active", "is_default", "created_by_id", "created_date", "updated_date") VALUES (5, '标准设备借用流程', 'equipment_loan', '申请借用 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO "workflow_template" ("id", "name", "order_type", "description", "is_active", "is_default", "created_by_id", "created_date", "updated_date") VALUES (6, '标准设备申领流程', 'equipment_application', '申请设备 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');

-- Reset sequence for workflow_template.id
SELECT setval(pg_get_serial_sequence('"workflow_template"', 'id'), COALESCE((SELECT MAX("id") FROM "workflow_template"), 1), true);

-- Table: part_replacement
DROP TABLE IF EXISTS "part_replacement" CASCADE;
CREATE TABLE "part_replacement" (
  "id" SERIAL,
  "repair_order_id" INTEGER,
  "spare_part_id" INTEGER,
  "quantity" INTEGER,
  "replacement_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: workflow_node
DROP TABLE IF EXISTS "workflow_node" CASCADE;
CREATE TABLE "workflow_node" (
  "id" SERIAL,
  "template_id" INTEGER,
  "name" TEXT,
  "order_type" TEXT,
  "node_type" TEXT,
  "role_required" TEXT,
  "approver_user_id" INTEGER,
  "approver_user_ids" TEXT,
  "sequence" INTEGER,
  "is_active" BOOLEAN,
  "created_date" TIMESTAMP,
  "is_parallel" BOOLEAN,
  "required_approvals" INTEGER,
  "actions_on_reject" TEXT,
  "actions_on_approve" TEXT,
  "condition_expr" TEXT,
  "timeout_seconds" INTEGER,
  "escalation_target" TEXT,
  PRIMARY KEY ("id")
);

-- Table: permission
DROP TABLE IF EXISTS "permission" CASCADE;
CREATE TABLE "permission" (
  "id" SERIAL,
  "role_id" INTEGER,
  "module" TEXT,
  "action" TEXT,
  "resource_type" TEXT,
  "conditions" TEXT,
  "is_granted" BOOLEAN,
  "priority" INTEGER,
  "created_date" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: user_custom_role
DROP TABLE IF EXISTS "user_custom_role" CASCADE;
CREATE TABLE "user_custom_role" (
  "user_id" SERIAL,
  "role_id" INTEGER NOT NULL,
  PRIMARY KEY ("user_id", "role_id")
);

-- Table: workflow_step
DROP TABLE IF EXISTS "workflow_step" CASCADE;
CREATE TABLE "workflow_step" (
  "id" SERIAL,
  "template_id" INTEGER,
  "sequence" INTEGER,
  "step_name" TEXT,
  "approver_role" TEXT,
  "approver_dept" TEXT,
  "is_parallel" BOOLEAN,
  "timeout_days" INTEGER,
  "required_approvals" INTEGER,
  "conditions" TEXT,
  "actions_on_approve" TEXT,
  "actions_on_reject" TEXT,
  PRIMARY KEY ("id")
);

-- Data for table: workflow_step
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (1, 1, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (2, 1, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (3, 2, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (4, 2, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (5, 3, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (6, 3, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (7, 4, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (8, 4, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (9, 5, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (10, 5, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (11, 6, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO "workflow_step" ("id", "template_id", "sequence", "step_name", "approver_role", "approver_dept", "is_parallel", "timeout_days", "required_approvals", "conditions", "actions_on_approve", "actions_on_reject") VALUES (12, 6, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');

-- Reset sequence for workflow_step.id
SELECT setval(pg_get_serial_sequence('"workflow_step"', 'id'), COALESCE((SELECT MAX("id") FROM "workflow_step"), 1), true);

-- Table: workflow_instance
DROP TABLE IF EXISTS "workflow_instance" CASCADE;
CREATE TABLE "workflow_instance" (
  "id" SERIAL,
  "template_id" INTEGER,
  "order_type" TEXT NOT NULL,
  "order_id" INTEGER NOT NULL,
  "current_node_id" INTEGER,
  "status" TEXT,
  "started_at" TIMESTAMP,
  "finished_at" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Table: approval_workflow
DROP TABLE IF EXISTS "approval_workflow" CASCADE;
CREATE TABLE "approval_workflow" (
  "id" SERIAL,
  "order_type" TEXT,
  "order_id" INTEGER,
  "approver_id" INTEGER,
  "approval_level" TEXT,
  "node_id" INTEGER,
  "status" TEXT,
  "comments" TEXT,
  "created_date" TIMESTAMP,
  "approved_date" TIMESTAMP,
  "auto_assigned" BOOLEAN,
  "required_approvals" INTEGER,
  "actions_on_reject" TEXT,
  PRIMARY KEY ("id")
);

-- Table: approval_decision
DROP TABLE IF EXISTS "approval_decision" CASCADE;
CREATE TABLE "approval_decision" (
  "id" SERIAL,
  "approval_workflow_id" INTEGER,
  "approver_id" INTEGER,
  "decision" TEXT,
  "comments" TEXT,
  "created_at" TIMESTAMP,
  PRIMARY KEY ("id")
);

-- Commit transaction
COMMIT;

-- End of dump
