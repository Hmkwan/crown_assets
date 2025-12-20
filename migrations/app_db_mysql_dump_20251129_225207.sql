-- MySQL dump generated from SQLite by sqlite_to_mysql.py
-- Review the dump before importing. BACKUP your target DB.

SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `account_request`;
CREATE TABLE `account_request` (
  `id` INT NOT NULL,
  `username` TEXT,
  `full_name` TEXT,
  `employee_no` TEXT,
  `email` TEXT,
  `department` TEXT,
  `role_requested` TEXT,
  `reason` TEXT,
  `password_hash` TEXT,
  `status` TEXT,
  `created_date` DATETIME,
  `processed_date` DATETIME,
  `approver_id` INT,
  `approver_comments` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `action_log`;
CREATE TABLE `action_log` (
  `id` INT NOT NULL,
  `action_name` TEXT,
  `workflow_node_id` INT,
  `approval_workflow_id` INT,
  `payload` TEXT,
  `status` TEXT,
  `result` TEXT,
  `executed_at` DATETIME,
  `retry_count` INT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `approval_decision`;
CREATE TABLE `approval_decision` (
  `id` INT NOT NULL,
  `approval_workflow_id` INT,
  `approver_id` INT,
  `decision` TEXT,
  `comments` TEXT,
  `created_at` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `approval_workflow`;
CREATE TABLE `approval_workflow` (
  `id` INT NOT NULL,
  `order_type` TEXT,
  `order_id` INT,
  `approver_id` INT,
  `approval_level` TEXT,
  `node_id` INT,
  `status` TEXT,
  `comments` TEXT,
  `created_date` DATETIME,
  `approved_date` DATETIME,
  `auto_assigned` TINYINT(1),
  `required_approvals` INT DEFAULT 1,
  `actions_on_reject` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `asset_cost`;
CREATE TABLE `asset_cost` (
  `id` INT NOT NULL,
  `equipment_id` INT,
  `purchase_price` DOUBLE,
  `purchase_date` DATETIME,
  `maintenance_cost` DOUBLE,
  `depreciation_rate` DOUBLE,
  `residual_value` DOUBLE,
  `depreciation_method` TEXT,
  `expected_lifespan` INT,
  `supplier` TEXT,
  `warranty_period` INT,
  `created_date` DATETIME,
  `updated_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `asset_handover`;
CREATE TABLE `asset_handover` (
  `id` INT NOT NULL,
  `from_user_id` INT,
  `to_user_id` INT,
  `equipment_ids` TEXT,
  `status` TEXT,
  `reason` TEXT,
  `reason_detail` TEXT,
  `created_date` DATETIME,
  `completed_date` DATETIME,
  `completed_by_id` INT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `asset_lifecycle`;
CREATE TABLE `asset_lifecycle` (
  `id` INT NOT NULL,
  `equipment_id` INT,
  `event_type` TEXT,
  `event_date` DATETIME,
  `old_status` TEXT,
  `new_status` TEXT,
  `description` TEXT,
  `responsible_user_id` INT,
  `cost_involved` DOUBLE,
  `documents` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `audit_log`;
CREATE TABLE `audit_log` (
  `id` INT NOT NULL,
  `user_id` INT,
  `action_type` TEXT,
  `resource_type` TEXT,
  `resource_id` INT,
  `old_value` TEXT,
  `new_value` TEXT,
  `ip_address` TEXT,
  `reason` TEXT,
  `created_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `department`;
CREATE TABLE `department` (
  `id` INT NOT NULL,
  `name` TEXT,
  `code` TEXT,
  `cost_center` TEXT,
  `location` TEXT,
  `description` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `department` (`id`, `name`, `code`, `cost_center`, `location`, `description`) VALUES (1, '信息部', 'IT', 'CC001', 'A座5楼', '信息技术部门');
INSERT INTO `department` (`id`, `name`, `code`, `cost_center`, `location`, `description`) VALUES (2, '财务部', 'FIN', 'CC002', 'A座3楼', '财务管理部门');
INSERT INTO `department` (`id`, `name`, `code`, `cost_center`, `location`, `description`) VALUES (3, '人力行政部', 'HR', 'CC003', 'A座2楼', '人力资源部门');
INSERT INTO `department` (`id`, `name`, `code`, `cost_center`, `location`, `description`) VALUES (4, '国内销售中心', 'SALES', 'CC004', 'B座1楼', '销售部门');
INSERT INTO `department` (`id`, `name`, `code`, `cost_center`, `location`, `description`) VALUES (5, '生产办', 'PROD', 'CC005', 'C厂房', '生产制造部门');
INSERT INTO `department` (`id`, `name`, `code`, `cost_center`, `location`, `description`) VALUES (6, '企管部', 'ADMIN', 'CC006', 'A座4楼', '企业管理部门');

DROP TABLE IF EXISTS `equipment`;
CREATE TABLE `equipment` (
  `id` INT NOT NULL,
  `name` TEXT,
  `type_id` INT,
  `type` TEXT,
  `brand` TEXT,
  `model` TEXT,
  `serial_number` TEXT,
  `purchase_date` DATETIME,
  `price` DOUBLE,
  `department_id` INT,
  `department` TEXT,
  `status` TEXT,
  `is_public_pool` TINYINT(1),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `equipment_application`;
CREATE TABLE `equipment_application` (
  `id` INT NOT NULL,
  `equipment_id` INT,
  `applicant_id` INT,
  `applicant_dept` TEXT,
  `reason` TEXT,
  `status` TEXT,
  `created_date` DATETIME,
  `approved_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `equipment_loan`;
CREATE TABLE `equipment_loan` (
  `id` INT NOT NULL,
  `equipment_id` INT,
  `requester_id` INT,
  `requester_dept` TEXT,
  `start_date` DATETIME,
  `end_date` DATETIME,
  `status` TEXT,
  `approved_by` INT,
  `approved_date` DATETIME,
  `borrowed_date` DATETIME,
  `returned_date` DATETIME,
  `notes` TEXT,
  `pickup_notified` TINYINT(1),
  `created_date` DATETIME,
  `updated_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `equipment_scrap`;
CREATE TABLE `equipment_scrap` (
  `id` INT NOT NULL,
  `equipment_id` INT,
  `requester_id` INT,
  `description` TEXT,
  `status` TEXT,
  `created_date` DATETIME,
  `updated_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `equipment_transfer`;
CREATE TABLE `equipment_transfer` (
  `id` INT NOT NULL,
  `equipment_id` INT,
  `from_department` TEXT,
  `to_department` TEXT,
  `requester_id` INT,
  `description` TEXT,
  `status` TEXT,
  `created_date` DATETIME,
  `updated_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `equipment_type`;
CREATE TABLE `equipment_type` (
  `id` INT NOT NULL,
  `name` TEXT NOT NULL,
  `description` TEXT,
  `created_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (1, '台式电脑', '台式办公电脑', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (2, '笔记本电脑', '笔记本办公电脑', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (3, '服务器', '服务器设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (4, '打印机', '激光/喷墨打印机', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (5, '扫描仪', '文档扫描设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (6, '投影仪', '会议投影设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (7, '显示器', '显示器设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (8, '路由器', '网络路由器', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (9, '交换机', '网络交换机', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (10, '防火墙', '网络安全设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (11, 'UPS电源', '不间断电源', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (12, '网络存储', 'NAS/SAN存储设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (13, '摄像头', '监控摄像设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (14, '会议设备', '会议系统设备', '2025-11-30 04:36:06');
INSERT INTO `equipment_type` (`id`, `name`, `description`, `created_date`) VALUES (15, '电话设备', 'IP电话等通讯设备', '2025-11-30 04:36:06');

DROP TABLE IF EXISTS `inventory_warning`;
CREATE TABLE `inventory_warning` (
  `id` INT NOT NULL,
  `spare_part_id` INT,
  `min_threshold` INT,
  `critical_threshold` INT,
  `reorder_quantity` INT,
  `lead_time_days` INT,
  `enabled` TINYINT(1),
  `last_warned_date` DATETIME,
  `created_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `notification`;
CREATE TABLE `notification` (
  `id` INT NOT NULL,
  `user_id` INT,
  `title` TEXT,
  `message` TEXT,
  `is_read` TINYINT(1),
  `created_date` DATETIME,
  `order_type` TEXT,
  `order_id` INT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `notification` (`id`, `user_id`, `title`, `message`, `is_read`, `created_date`, `order_type`, `order_id`) VALUES (1, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:26:36', NULL, NULL);
INSERT INTO `notification` (`id`, `user_id`, `title`, `message`, `is_read`, `created_date`, `order_type`, `order_id`) VALUES (2, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:26:50', NULL, NULL);
INSERT INTO `notification` (`id`, `user_id`, `title`, `message`, `is_read`, `created_date`, `order_type`, `order_id`) VALUES (3, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:31:54', NULL, NULL);
INSERT INTO `notification` (`id`, `user_id`, `title`, `message`, `is_read`, `created_date`, `order_type`, `order_id`) VALUES (4, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:38:24', NULL, NULL);
INSERT INTO `notification` (`id`, `user_id`, `title`, `message`, `is_read`, `created_date`, `order_type`, `order_id`) VALUES (5, 6, '测试通知', '这是一条测试通知', 0, '2025-11-30 05:38:39', NULL, NULL);

DROP TABLE IF EXISTS `part_replacement`;
CREATE TABLE `part_replacement` (
  `id` INT NOT NULL,
  `repair_order_id` INT,
  `spare_part_id` INT,
  `quantity` INT,
  `replacement_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `part_request_order`;
CREATE TABLE `part_request_order` (
  `id` INT NOT NULL,
  `requester_id` INT,
  `department_head_id` INT,
  `admin_id` INT,
  `part_name` TEXT,
  `part_number` TEXT,
  `quantity` INT,
  `reason` TEXT,
  `status` TEXT,
  `department_head_approved` TINYINT(1),
  `admin_approved` TINYINT(1),
  `created_date` DATETIME,
  `updated_date` DATETIME,
  `completed_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `permission`;
CREATE TABLE `permission` (
  `id` INT NOT NULL,
  `role_id` INT,
  `module` TEXT,
  `action` TEXT,
  `resource_type` TEXT,
  `conditions` TEXT,
  `is_granted` TINYINT(1),
  `priority` INT,
  `created_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `repair_order`;
CREATE TABLE `repair_order` (
  `id` INT NOT NULL,
  `equipment_id` INT,
  `requester_id` INT,
  `technician_id` INT,
  `department_head_id` INT,
  `admin_id` INT,
  `description` TEXT,
  `status` TEXT,
  `created_date` DATETIME,
  `updated_date` DATETIME,
  `completed_date` DATETIME,
  `department_head_approved` TINYINT(1),
  `admin_approved` TINYINT(1),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `role_definition`;
CREATE TABLE `role_definition` (
  `id` INT NOT NULL,
  `name` TEXT,
  `description` TEXT,
  `is_custom` TINYINT(1),
  `is_active` TINYINT(1),
  `created_date` DATETIME,
  `created_by_id` INT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `spare_part`;
CREATE TABLE `spare_part` (
  `id` INT NOT NULL,
  `name` TEXT,
  `part_number` TEXT,
  `type_id` INT,
  `price` DOUBLE,
  `stock_quantity` INT,
  `min_stock_level` INT,
  `department_id` INT,
  `department` TEXT,
  `location` TEXT,
  `purchase_date` DATETIME,
  `is_public` TINYINT(1),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `spare_part_type`;
CREATE TABLE `spare_part_type` (
  `id` INT NOT NULL,
  `name` TEXT NOT NULL,
  `description` TEXT,
  `created_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (1, '内存条', '电脑内存条', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (2, '硬盘', '机械硬盘/固态硬盘', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (3, '电源', '电源适配器/电源模块', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (4, '主板', '电脑主板', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (5, 'CPU', '中央处理器', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (6, '显卡', '图形处理器', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (7, '散热器', 'CPU散热器', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (8, '机箱风扇', '机箱散热风扇', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (9, '网卡', '有线/无线网卡', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (10, '声卡', '声卡设备', '2025-11-30 04:36:06');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (11, '键盘', '键盘设备', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (12, '鼠标', '鼠标设备', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (13, '数据线', '各类数据传输线', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (14, '网线', '网络连接线', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (15, '电源线', '电源连接线', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (16, '墨盒/硒鼓', '打印机耗材', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (17, '打印纸', '打印用纸', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (18, '投影灯泡', '投影仪灯泡', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (19, '电池', 'UPS/设备电池', '2025-11-30 04:36:07');
INSERT INTO `spare_part_type` (`id`, `name`, `description`, `created_date`) VALUES (20, '转接头', '各类转接器', '2025-11-30 04:36:07');

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` INT NOT NULL,
  `username` TEXT,
  `email` TEXT,
  `password_hash` TEXT,
  `role` TEXT,
  `department_id` INT,
  `department` TEXT,
  `is_active` TINYINT(1),
  `workflow_roles` TEXT,
  `can_manage_equipment` TINYINT(1),
  `can_manage_spare_parts` TINYINT(1),
  `can_manage_repairs` TINYINT(1),
  `can_manage_part_requests` TINYINT(1),
  `can_view_workflow` TINYINT(1),
  `can_edit_workflow` TINYINT(1),
  `can_manage_workflow_templates` TINYINT(1),
  `can_view_reports` TINYINT(1),
  `can_view_logs` TINYINT(1),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `role`, `department_id`, `department`, `is_active`, `workflow_roles`, `can_manage_equipment`, `can_manage_spare_parts`, `can_manage_repairs`, `can_manage_part_requests`, `can_view_workflow`, `can_edit_workflow`, `can_manage_workflow_templates`, `can_view_reports`, `can_view_logs`) VALUES (1, 'admin', 'admin@example.com', 'scrypt:32768:8:1$ZKqSXjZUHDHAs39q$1ff3e69086342f985b93697fb1c7ec19a5dc0c6e11cab3f8b96baf860044f802ad95bae8a998a7dabb0616b211cb582f54c86128b83b4a0f9b3811f99f805daf', 'admin', NULL, '超级管理员', 1, '["admin"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `role`, `department_id`, `department`, `is_active`, `workflow_roles`, `can_manage_equipment`, `can_manage_spare_parts`, `can_manage_repairs`, `can_manage_part_requests`, `can_view_workflow`, `can_edit_workflow`, `can_manage_workflow_templates`, `can_view_reports`, `can_view_logs`) VALUES (2, '陈松', 'chengs@crown.com.cn', 'scrypt:32768:8:1$gIPhb6J3XL5SySfW$6b511c03c16a9a6837fd5d7a103665b7b089ac8ee8c46e8503afdb8f236e1e0b79800fbd488df2c21ed544e53ccd8f1603f5f4c46a0a6447fcc88c67492bfe4f', 'department_head', 6, '企管部', 1, '["department_head"]', 1, 1, 1, 1, 1, 0, 0, 1, 0);
INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `role`, `department_id`, `department`, `is_active`, `workflow_roles`, `can_manage_equipment`, `can_manage_spare_parts`, `can_manage_repairs`, `can_manage_part_requests`, `can_view_workflow`, `can_edit_workflow`, `can_manage_workflow_templates`, `can_view_reports`, `can_view_logs`) VALUES (3, '吴文杨', 'wuwy@crown.com.cn', 'scrypt:32768:8:1$sSZm3A6ziQKRbQ7K$43fc8af8fee04e349853f45f7563e603a5e815a895ddd4ff69b122a058c973225855537244781ba0114af07143a90ecf43cdc1b034037d2215678b40f7cf361a', 'admin', 1, '信息部', 1, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `role`, `department_id`, `department`, `is_active`, `workflow_roles`, `can_manage_equipment`, `can_manage_spare_parts`, `can_manage_repairs`, `can_manage_part_requests`, `can_view_workflow`, `can_edit_workflow`, `can_manage_workflow_templates`, `can_view_reports`, `can_view_logs`) VALUES (4, '关鹤鸣', 'guanhm@crown.com.cn', 'scrypt:32768:8:1$oRAInE569dBPprb2$deba730add0c20a3fc6cc65d4b13d00e74f3267a175982d553777eaf44624a3320a0963a60c9f239df9538b9ff75a6c85d95991c90de8fdba491dbb60eee6b6e', 'technician', 1, '信息部', 1, '["security"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `role`, `department_id`, `department`, `is_active`, `workflow_roles`, `can_manage_equipment`, `can_manage_spare_parts`, `can_manage_repairs`, `can_manage_part_requests`, `can_view_workflow`, `can_edit_workflow`, `can_manage_workflow_templates`, `can_view_reports`, `can_view_logs`) VALUES (5, '朱绪', 'zhux@crown.com.cn', 'scrypt:32768:8:1$aQxV3PLh3ZBMqWIP$cc5aa81827b50e19febb39384c6419b376923fa7cb52e2e57bfcf7bc8dfd6872c0940127b3413a8a0e90fea2ff4991a0a082bb3bdb00d6f46e9c4c88c7363721', 'user', 6, '企管部', 1, '["auditor"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `role`, `department_id`, `department`, `is_active`, `workflow_roles`, `can_manage_equipment`, `can_manage_spare_parts`, `can_manage_repairs`, `can_manage_part_requests`, `can_view_workflow`, `can_edit_workflow`, `can_manage_workflow_templates`, `can_view_reports`, `can_view_logs`) VALUES (6, 'testuser', 'test@example.com', 'pbkdf2:sha256:260000$u1sNyWFHZYCtduoe$8149ed2e7c5c07b66099bc367e4b99dfbe092858ada65cc0e0214fdd4725b227', 'user', 5, '生产办', 1, '["employee", "warehouse"]', 0, 0, 0, 0, 0, 0, 0, 0, 0);

DROP TABLE IF EXISTS `user_activity_log`;
CREATE TABLE `user_activity_log` (
  `id` INT NOT NULL,
  `user_id` INT,
  `action` TEXT,
  `description` TEXT,
  `timestamp` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (1, 1, '数据库重置', '用户 admin 重置了数据库 (IP: 10.168.93.93)', '2025-11-30 04:36:07');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (2, 1, '用户登出', '用户 admin 登出系统', '2025-11-30 04:36:08');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (3, 1, '用户登录', '用户 admin 登录系统', '2025-11-30 04:36:13');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (4, 1, '访问页面', '部门管理 (IP: 10.168.93.93)', '2025-11-30 05:16:12');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (5, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:16:47');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (6, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:16:58');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (7, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:16:59');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (8, 1, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 05:17:00');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (9, 1, '创建用户', '管理员 admin 创建了用户 陈松 (IP: 10.168.93.93)', '2025-11-30 05:18:02');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (10, 1, '创建用户', '管理员 admin 创建了用户 吴文杨 (IP: 10.168.93.93)', '2025-11-30 05:18:38');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (11, 1, '创建用户', '管理员 admin 创建了用户 关鹤鸣 (IP: 10.168.93.93)', '2025-11-30 05:19:21');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (12, 1, '编辑用户', '管理员 admin 编辑了用户 陈松 (IP: 10.168.93.93)', '2025-11-30 05:20:49');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (13, 1, '创建用户', '管理员 admin 创建了用户 朱绪 (IP: 10.168.93.93)', '2025-11-30 05:21:33');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (14, 1, '编辑用户', '管理员 admin 编辑了用户 关鹤鸣 (IP: 10.168.93.93)', '2025-11-30 05:24:34');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (15, 1, '编辑用户', '管理员 admin 编辑了用户 testuser (IP: 10.168.93.93)', '2025-11-30 05:27:29');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (16, 1, '访问页面', '公开仓库 (IP: 10.168.93.93)', '2025-11-30 05:43:48');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (17, 1, '导出数据库(MySQL)', '用户 admin 导出了数据库到 MySQL 转储: app_db_mysql_dump_20251129_224405.sql (IP: 10.168.93.93)', '2025-11-30 06:44:05');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (18, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_150734.db (IP: 10.168.93.93)', '2025-11-30 06:45:27');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (19, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_150609.db (IP: 10.168.93.93)', '2025-11-30 06:45:32');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (20, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251127_151846.db (IP: 10.168.93.93)', '2025-11-30 06:45:38');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (21, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_155439.db (IP: 10.168.93.93)', '2025-11-30 06:45:44');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (22, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251128_163122.db (IP: 10.168.93.93)', '2025-11-30 06:45:49');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (23, 1, '删除备份', '用户 admin 删除了备份文件: app_backup_20251129_171125.db (IP: 10.168.93.93)', '2025-11-30 06:46:09');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (24, 1, '用户登出', '用户 admin 登出系统', '2025-11-30 06:46:34');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (25, 4, '用户登录', '用户 关鹤鸣 登录系统', '2025-11-30 06:46:37');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (26, 4, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-30 06:47:04');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (27, 4, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 06:47:08');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (28, 4, '用户登出', '用户 关鹤鸣 登出系统', '2025-11-30 06:47:26');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (29, 2, '用户登录', '用户 陈松 登录系统', '2025-11-30 06:47:38');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (30, 2, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 06:47:44');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (31, 2, '访问页面', '配件列表 (IP: 10.168.93.93)', '2025-11-30 06:47:54');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (32, 2, '访问页面', '设备列表 (IP: 10.168.93.93)', '2025-11-30 06:47:58');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (33, 2, '用户登出', '用户 陈松 登出系统', '2025-11-30 06:48:45');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (34, 3, '用户登录', '用户 吴文杨 登录系统', '2025-11-30 06:48:57');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (35, 3, '导出数据库(MSSQL)', '用户 吴文杨 导出了数据库到 MSSQL 转储: app_db_mssql_dump_20251129_224914.sql (IP: 10.168.93.93)', '2025-11-30 06:49:14');
INSERT INTO `user_activity_log` (`id`, `user_id`, `action`, `description`, `timestamp`) VALUES (36, 3, '导出数据库(PostgreSQL)', '用户 吴文杨 导出了数据库到 PostgreSQL 转储: app_db_postgresql_dump_20251129_225058.sql (IP: 10.168.93.93)', '2025-11-30 06:50:58');

DROP TABLE IF EXISTS `user_custom_role`;
CREATE TABLE `user_custom_role` (
  `user_id` INT NOT NULL,
  `role_id` INT NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `workflow_instance`;
CREATE TABLE `workflow_instance` (
  `id` INT NOT NULL,
  `template_id` INT,
  `order_type` TEXT NOT NULL,
  `order_id` INT NOT NULL,
  `current_node_id` INT,
  `status` TEXT,
  `started_at` DATETIME,
  `finished_at` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `workflow_node`;
CREATE TABLE `workflow_node` (
  `id` INT NOT NULL,
  `template_id` INT,
  `name` TEXT,
  `order_type` TEXT,
  `node_type` TEXT,
  `role_required` TEXT,
  `approver_user_id` INT,
  `approver_user_ids` TEXT,
  `sequence` INT,
  `is_active` TINYINT(1),
  `created_date` DATETIME,
  `is_parallel` TINYINT(1),
  `required_approvals` INT,
  `actions_on_reject` TEXT,
  `actions_on_approve` TEXT,
  `condition_expr` TEXT,
  `timeout_seconds` INT,
  `escalation_target` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `workflow_step`;
CREATE TABLE `workflow_step` (
  `id` INT NOT NULL,
  `template_id` INT,
  `sequence` INT,
  `step_name` TEXT,
  `approver_role` TEXT,
  `approver_dept` TEXT,
  `is_parallel` TINYINT(1),
  `timeout_days` INT,
  `required_approvals` INT,
  `conditions` TEXT,
  `actions_on_approve` TEXT,
  `actions_on_reject` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (1, 1, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (2, 1, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (3, 2, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (4, 2, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (5, 3, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (6, 3, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (7, 4, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (8, 4, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (9, 5, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (10, 5, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (11, 6, 1, '部门主管审批', 'department_head', NULL, 0, 2, 1, '{}', '{}', '{"return_to": "requester"}');
INSERT INTO `workflow_step` (`id`, `template_id`, `sequence`, `step_name`, `approver_role`, `approver_dept`, `is_parallel`, `timeout_days`, `required_approvals`, `conditions`, `actions_on_approve`, `actions_on_reject`) VALUES (12, 6, 2, '管理员审批', 'admin', NULL, 0, 3, 1, '{}', '{}', '{"return_to": "requester"}');

DROP TABLE IF EXISTS `workflow_template`;
CREATE TABLE `workflow_template` (
  `id` INT NOT NULL,
  `name` TEXT,
  `order_type` TEXT,
  `description` TEXT,
  `is_active` TINYINT(1),
  `is_default` TINYINT(1),
  `created_by_id` INT,
  `created_date` DATETIME,
  `updated_date` DATETIME,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `workflow_template` (`id`, `name`, `order_type`, `description`, `is_active`, `is_default`, `created_by_id`, `created_date`, `updated_date`) VALUES (1, '标准维修流程', 'repair_order', '员工申请 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO `workflow_template` (`id`, `name`, `order_type`, `description`, `is_active`, `is_default`, `created_by_id`, `created_date`, `updated_date`) VALUES (2, '标准配件申请流程', 'part_request_order', '员工申请 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO `workflow_template` (`id`, `name`, `order_type`, `description`, `is_active`, `is_default`, `created_by_id`, `created_date`, `updated_date`) VALUES (3, '标准设备调拨流程', 'equipment_transfer', '申请调拨 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO `workflow_template` (`id`, `name`, `order_type`, `description`, `is_active`, `is_default`, `created_by_id`, `created_date`, `updated_date`) VALUES (4, '标准设备报废流程', 'equipment_scrap', '申请报废 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO `workflow_template` (`id`, `name`, `order_type`, `description`, `is_active`, `is_default`, `created_by_id`, `created_date`, `updated_date`) VALUES (5, '标准设备借用流程', 'equipment_loan', '申请借用 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');
INSERT INTO `workflow_template` (`id`, `name`, `order_type`, `description`, `is_active`, `is_default`, `created_by_id`, `created_date`, `updated_date`) VALUES (6, '标准设备申领流程', 'equipment_application', '申请设备 → 部门主管审批 → 管理员审批', 1, 0, 1, '2025-11-30 04:36:07', '2025-11-30 04:36:07');

SET FOREIGN_KEY_CHECKS=1;
