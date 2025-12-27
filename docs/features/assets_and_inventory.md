# 功能：资产（Assets）与库存（Inventory）

## 概述
资产管理包含设备录入、借用、调拨、报废、二维码与标签打印。库存管理涉及配件入库、出库、预警与采购建议。

## 关键文件
- 资产：`app/main/asset_routes.py`、`app/models.py`（`Equipment`, `AssetCost`）
- 库存/配件：`app/main/inventory_routes.py`、`app/models.py`（`SparePart`, `InventoryWarning`）

## 建议
- 为关键库存操作（出库、分配）添加事务保护（确保扣减与记录一致）
- 对导入功能加强数据验证与回滚策略
