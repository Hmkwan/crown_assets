# 公开仓库功能实现总结

## 功能概述
在首页和管理面板添加了公开仓库入口,可以查看所有部门设置为公开的设备和配件信息。系统超级管理员admin或授权管理员角色的人员可以进行编辑、新增、修改、删除、查看等操作。

## 实现内容

### 1. 数据库修改
- **表**: `spare_part`
- **新增字段**: `is_public` (BOOLEAN, 默认值: 0/False)
- **用途**: 标记配件是否公开到公共仓库
- **迁移脚本**: `scripts/add_spare_part_is_public.py`

### 2. 路由(app/main/routes.py)

#### 公开仓库主路由
```python
@bp.route('/public_pool')
@login_required
def public_pool()
```
- **功能**: 显示公开仓库页面
- **支持**: 设备(equipment)和配件(spare_part)两种资源类型切换
- **筛选**: 部门筛选、关键词搜索
- **权限**: 所有登录用户可查看

#### 配件管理路由
```python
@bp.route('/spare_parts/bulk_public', methods=['POST'])
def bulk_public_spare_parts()  # 批量公开配件

@bp.route('/spare_parts/bulk_unpublic', methods=['POST'])
def bulk_unpublic_spare_parts()  # 批量取消公开配件
```
- **权限**: 仅admin用户可操作
- **功能**: 批量设置配件的公开状态

### 3. 模板文件

#### public_pool.html (新建)
- **位置**: `app/templates/main/public_pool.html`
- **功能**:
  - 统计卡片显示公开设备和配件数量
  - Tab导航切换设备/配件视图
  - 部门筛选和关键词搜索
  - 设备列表显示(借用按钮)
  - 配件列表显示(申请按钮)
  - 分页导航
  - 使用说明

#### spare_parts.html (更新)
- **位置**: `app/templates/main/spare_parts.html`
- **新增功能**:
  - 公开状态列(显示徽章: 公开/私有)
  - 批量公开/取消公开按钮
  - 单个配件公开/取消公开按钮
  - JavaScript处理批量操作

### 4. 首页入口更新

所有用户角色的首页tiles配置已更新:
- **Admin**: 已有"公开仓库"入口
- **Technician**: "公开设备仓库" → "公开仓库"
- **Department Head**: "公开设备仓库" → "公开仓库"
- **User**: 已有"公开仓库"入口

### 5. 管理面板入口
Admin管理面板已添加"公开仓库"入口

## 使用方法

### 查看公开仓库
1. 登录系统
2. 点击首页或管理面板的"公开仓库"卡片
3. 默认显示公开设备列表
4. 点击"公开配件"Tab切换到配件视图
5. 使用部门筛选和搜索功能查找资源

### 设置配件为公开(Admin)
1. 访问配件管理页面(`/spare_parts`)
2. 使用admin账号登录
3. 勾选要公开的配件
4. 点击"批量公开"按钮
   或
5. 点击单个配件的"设为公开"按钮

### 取消配件公开(Admin)
1. 访问配件管理页面
2. 勾选要取消公开的配件
3. 点击"批量取消公开"按钮
   或
4. 点击单个配件的"取消公开"按钮

## 权限说明
- **查看公开仓库**: 所有登录用户
- **设置公开状态**: 仅admin用户
- **借用设备**: 按现有借用流程权限
- **申请配件**: 按现有申请流程权限

## 测试状态
- ✅ 数据库迁移成功
- ✅ is_public字段添加成功
- ✅ 公开设备: 1个
- ✅ 公开配件: 3个
- ✅ 路由创建成功
- ✅ 模板文件创建成功
- ✅ UI元素添加成功

## 文件清单

### 新建文件
1. `app/templates/main/public_pool.html` - 公开仓库页面模板
2. `scripts/add_spare_part_is_public.py` - 数据库迁移脚本
3. `test_public_pool.py` - 功能测试脚本
4. `scripts/set_public_parts.py` - 设置测试数据脚本

### 修改文件
1. `app/main/routes.py`
   - 新增public_pool()路由
   - 新增bulk_public_spare_parts()路由
   - 新增bulk_unpublic_spare_parts()路由
   - 更新所有角色的tiles配置

2. `app/models.py`
   - SparePart类添加is_public字段

3. `app/templates/main/spare_parts.html`
   - 添加公开状态列
   - 添加批量公开/取消公开按钮
   - 添加单个公开/取消公开按钮
   - 更新JavaScript处理函数

## 后续建议
1. 在设备管理页面也添加类似的批量公开/取消公开功能(设备已有is_public_pool字段)
2. 在公开仓库页面添加更多筛选条件(如设备类型、价格范围等)
3. 添加公开资源的使用统计功能
4. 考虑添加部门间资源借用的审批流程

## 日期
2025年11月29日
