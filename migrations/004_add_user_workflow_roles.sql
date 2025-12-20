-- 为 User 表添加 workflow_roles 字段
-- Migration 004: Add workflow_roles to User table

-- 添加审批流角色字段（JSON格式存储多个角色）
ALTER TABLE user ADD COLUMN workflow_roles TEXT;

-- 为现有用户自动设置默认角色
-- admin 用户自动获得 admin 角色
UPDATE user SET workflow_roles = '["admin"]' WHERE role = 'admin';

-- department_head 用户自动获得 department_head 角色
UPDATE user SET workflow_roles = '["department_head"]' WHERE role = 'department_head';

-- technician 用户自动获得 admin 角色
UPDATE user SET workflow_roles = '["admin"]' WHERE role = 'technician';

-- 其他普通用户默认为 employee
UPDATE user SET workflow_roles = '["employee"]' WHERE role = 'user' OR workflow_roles IS NULL;
