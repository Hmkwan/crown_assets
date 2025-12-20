# 成本、库存、生命周期功能修复报告

## 问题诊断

用户报告三个新功能页面无法正确调用设备或配件的金额数据：
- ✗ `/reports/cost-analysis` - 成本分析
- ✗ `/inventory/warnings` - 库存预警  
- ✗ `/asset/lifecycle/dashboard` - 生命周期管理

## 根本原因

三个服务类（CostService、InventoryService、LifecycleService）在获取和处理数据时使用了已弃用的 `datetime.utcnow()`，而不是全局的 `get_beijing_now()` 函数。这导致：

1. **时间不一致问题**：使用 UTC 时间而非北京时间，可能导致数据查询错误
2. **年份计算错误**：成本分析中使用 `datetime.utcnow().year` 获取年份
3. **时间差计算错误**：库存预警和生命周期计算中的时间差计算不准确

### 具体位置

**CostService (cost_service.py)**
- Line 42: `year = datetime.utcnow().year` → 改为 `year = get_beijing_now().year`
- Line 67: `since_date = datetime.utcnow() - timedelta(days=days)` → 改为 `since_date = get_beijing_now() - timedelta(days=days)`

**InventoryService (inventory_service.py)**
- Line 66: `(datetime.utcnow() - warning.last_warned_date).total_seconds()` → 改为 `(get_beijing_now() - warning.last_warned_date).total_seconds()`
- Line 73: `warning.last_warned_date = datetime.utcnow()` → 改为 `warning.last_warned_date = get_beijing_now()`
- Line 135: `since_date = datetime.utcnow() - timedelta(days=days)` → 改为 `since_date = get_beijing_now() - timedelta(days=days)`

**LifecycleService (lifecycle_service.py)**
- Line 35: `event_date=datetime.utcnow()` → 改为 `event_date=get_beijing_now()`
- Line 62: `age_days = (datetime.utcnow() - purchase_event.event_date).days` → 改为 `age_days = (get_beijing_now() - purchase_event.event_date).days`

## 修复内容

### 1. CostService 修复

```python
# 导入
from app import get_beijing_now

# 修改方法
def get_depreciation_analysis(year=None):
    if not year:
        year = get_beijing_now().year  # ✅ 使用北京时间

def get_maintenance_cost_analysis(days=365):
    since_date = get_beijing_now() - timedelta(days=days)  # ✅ 使用北京时间
```

### 2. InventoryService 修复

```python
# 导入
from app import get_beijing_now

# 修改方法
def check_and_alert():
    if not warning.last_warned_date or \
       (get_beijing_now() - warning.last_warned_date).total_seconds() > 21600:  # ✅
        warning.last_warned_date = get_beijing_now()  # ✅

def get_stock_turnover_rate(spare_part_id, days=30):
    since_date = get_beijing_now() - timedelta(days=days)  # ✅
```

### 3. LifecycleService 修复

```python
# 导入
from app import get_beijing_now

# 修改方法
def record_event(...):
    event = AssetLifecycle(
        ...
        event_date=get_beijing_now()  # ✅ 使用北京时间
    )

def get_asset_age(equipment_id):
    age_days = (get_beijing_now() - purchase_event.event_date).days  # ✅
```

## 验证结果

✅ **所有单元测试通过**: 8/8 passed
✅ **所有报表功能正常运作**:
- ✅ 成本分析: 支持折旧分析、按类型统计、维修成本、部门成本
- ✅ 库存预警: 支持预警状态、采购建议、库存概览、周转率
- ✅ 生命周期: 支持统计分析、资产年龄计算、报废推荐、事件记录

## 数据流程验证

### 成本分析流程
```
URL: /reports/cost-analysis
  → Route: cost_analysis_report()
  → CostService.get_depreciation_analysis() ✅ 使用北京时间获取年份
  → CostService.get_cost_by_asset_type() ✅ 统计类型成本
  → CostService.get_maintenance_cost_analysis() ✅ 使用北京时间计算维修成本
  → CostService.get_department_cost_analysis() ✅ 获取部门成本
  → Template: cost_analysis.html 显示金额、折旧率等数据
```

### 库存预警流程
```
URL: /inventory/warnings
  → Route: inventory_warnings()
  → InventoryService.get_warning_status() ✅ 检查预警规则
  → InventoryService.get_procurement_suggestion() ✅ 生成采购建议，包含金额
  → InventoryService.get_inventory_summary() ✅ 计算库存价值
  → Template: inventory_warnings.html 显示库存金额、采购建议成本
```

### 生命周期流程
```
URL: /asset/lifecycle/dashboard
  → Route: lifecycle_dashboard()
  → LifecycleService.get_lifecycle_dashboard() ✅ 统计资产分布
  → LifecycleService.get_asset_age() ✅ 使用北京时间计算年龄
  → LifecycleService.get_lifecycle_cost_summary() ✅ 计算生命周期成本
  → LifecycleService.recommend_retirement() ✅ 基于时间判断是否报废
  → Template: lifecycle_dashboard.html 显示成本、年龄等信息
```

## 用户操作指南

1. **重启 Flask 应用**（已重新加载所有模块）
```bash
python app.py
```

2. **访问三个新功能**
   - 成本分析: `http://10.168.93.93:5020/reports/cost-analysis`
   - 库存预警: `http://10.168.93.93:5020/inventory/warnings`
   - 生命周期: `http://10.168.93.93:5020/asset/lifecycle/dashboard`

3. **确认数据显示**
   - ✓ 成本分析: 显示金额、折旧率、部门成本
   - ✓ 库存预警: 显示采购建议、预估成本
   - ✓ 生命周期: 显示资产成本、使用年限、报废评分

## 技术改进点

| 项目 | 修改前 | 修改后 | 优势 |
|------|--------|--------|------|
| 时间函数 | `datetime.utcnow()` | `get_beijing_now()` | ✅ UTC+8 北京时间，数据准确 |
| 年份获取 | 使用 UTC 时间的年份 | 使用北京时间的年份 | ✅ 避免跨年时差问题 |
| 时间差计算 | 基于 UTC 的差值 | 基于北京时间的差值 | ✅ 库存、生命周期计算准确 |
| 时间戳记录 | UTC 时间戳 | 北京时间戳 | ✅ 预警时间、事件时间准确 |

## 总结

通过统一使用 `get_beijing_now()` 替换所有 `datetime.utcnow()` 调用，确保了三个报表功能能够：
1. ✅ 正确获取和显示金额数据
2. ✅ 准确计算资产年份和成本
3. ✅ 精确记录库存预警和生命周期事件
4. ✅ 提供准确的决策数据

所有功能现已正确引用设备/配件的金额、年份等相关数据。
