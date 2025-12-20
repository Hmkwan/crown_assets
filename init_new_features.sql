-- IT资产管理系统 - 新功能表结构初始化脚本
-- 执行此脚本添加企业级功能所需的表

-- ============================================
-- 1. 资产成本管理表 (Asset Cost Management)
-- ============================================

CREATE TABLE IF NOT EXISTS asset_cost (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL UNIQUE,
    purchase_price FLOAT DEFAULT 0,
    annual_depreciation_rate FLOAT DEFAULT 15,
    expected_lifespan_years INTEGER DEFAULT 5,
    residual_value_percent FLOAT DEFAULT 10,
    annual_maintenance_cost FLOAT DEFAULT 0,
    annual_repair_frequency FLOAT DEFAULT 0,
    max_repair_cost FLOAT DEFAULT 0,
    total_upgrade_cost FLOAT DEFAULT 0,
    other_cost FLOAT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES equipment(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_asset_cost_asset_id ON asset_cost(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_cost_created_at ON asset_cost(created_at);

-- ============================================
-- 2. 资产生命周期事件表 (Asset Lifecycle Events)
-- ============================================

CREATE TABLE IF NOT EXISTS asset_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- purchase, deployment, maintenance, upgrade, retirement
    event_date DATE NOT NULL,
    description TEXT,
    cost FLOAT DEFAULT 0,
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES equipment(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lifecycle_asset_id ON asset_lifecycle(asset_id);
CREATE INDEX IF NOT EXISTS idx_lifecycle_event_type ON asset_lifecycle(event_type);
CREATE INDEX IF NOT EXISTS idx_lifecycle_event_date ON asset_lifecycle(event_date);

-- ============================================
-- 3. 库存预警规则表 (Inventory Warning Rules)
-- ============================================

CREATE TABLE IF NOT EXISTS inventory_warning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spare_part_id INTEGER NOT NULL UNIQUE,
    min_threshold INTEGER DEFAULT 5,
    critical_threshold INTEGER DEFAULT 2,
    max_threshold INTEGER DEFAULT 100,
    reorder_quantity INTEGER DEFAULT 10,
    last_alert_date DATE,
    alert_status VARCHAR(20),  -- normal, warning, critical
    last_check_time TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (spare_part_id) REFERENCES spare_part(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_inventory_warning_spare_part_id ON inventory_warning(spare_part_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warning_alert_status ON inventory_warning(alert_status);

-- ============================================
-- 4. 资产交接记录表 (Asset Handover Records)
-- ============================================

CREATE TABLE IF NOT EXISTS asset_handover (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    from_department VARCHAR(100),
    to_department VARCHAR(100),
    from_person VARCHAR(100),
    to_person VARCHAR(100),
    handover_date DATE NOT NULL,
    reason VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES equipment(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_handover_asset_id ON asset_handover(asset_id);
CREATE INDEX IF NOT EXISTS idx_handover_handover_date ON asset_handover(handover_date);

-- ============================================
-- 初始化库存预警规则（示例数据）
-- ============================================

-- 为现有配件添加默认预警规则 (如果spare_part表存在)
INSERT OR IGNORE INTO inventory_warning 
(spare_part_id, min_threshold, critical_threshold, max_threshold, reorder_quantity, alert_status)
SELECT id, 5, 2, 100, 10, 'normal' FROM spare_part WHERE id NOT IN 
    (SELECT spare_part_id FROM inventory_warning);

-- ============================================
-- 验证脚本
-- ============================================

-- 验证表创建成功
SELECT name FROM sqlite_master WHERE type='table' AND name IN 
    ('asset_cost', 'asset_lifecycle', 'inventory_warning', 'asset_handover');

-- 验证索引创建成功
SELECT name FROM sqlite_master WHERE type='index' AND 
    name LIKE 'idx_%' ORDER BY name;
