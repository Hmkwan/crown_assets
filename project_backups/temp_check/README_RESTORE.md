# 项目备份

备份时间: 2025-11-30 00:11:16
原项目路径: C:\Users\it03.GD\Desktop\TEST

## 备份内容

### 目录 (6个)
- app/ (0.00 B)
- alembic/ (0.00 B)
- migrations/ (0.00 B)
- scripts/ (0.00 B)
- static/ (0.00 B)
- tests/ (0.00 B)

### 文件 (23个)
- app.py (1.01 KB)
- config.py (964.00 B)
- requirements.txt (176.00 B)
- alembic.ini (4.69 KB)
- boot.bat (81.00 B)
- boot.sh (89.00 B)
- init_db.py (6.71 KB)
- init_default_workflow.py (14.46 KB)
- create_admin.py (1.60 KB)
- check_index.py (1.75 KB)
- download_cdn_resources.py (3.42 KB)
- update_base_template.py (4.52 KB)
- QUICK_START_GUIDE.md (9.87 KB)
- DEPLOYMENT_OPTIMIZATION_GUIDE.md (6.29 KB)
- PERFORMANCE_DIAGNOSIS.md (2.02 KB)
- DEVELOPMENT_REPORT.md (17.09 KB)
- DELIVERY_CHECKLIST.md (9.87 KB)
- FINAL_DELIVERY.md (15.06 KB)
- PERMISSION_SYSTEM_ENHANCEMENT.md (4.28 KB)
- REPORTS_FIXES_SUMMARY.md (6.16 KB)
- SYSTEM_IMPROVEMENT_PLAN.md (7.37 KB)
- WORKFLOW_ENHANCEMENTS.md (4.51 KB)
- app.db (336.00 KB)

总计: 23 个文件, 457.96 KB

## 恢复步骤

1. 解压备份文件到目标目录
2. 安装Python 3.7+
3. 创建虚拟环境:
   ```
   python -m venv .venv
   .venv\Scripts\activate  (Windows)
   source .venv/bin/activate  (Linux/Mac)
   ```
4. 安装依赖:
   ```
   pip install -r requirements.txt
   ```
5. 初始化数据库（如果没有备份数据库）:
   ```
   python init_db.py
   python create_admin.py
   ```
6. 启动服务:
   ```
   python app.py
   ```

## 注意事项

- 确保Python版本一致
- 检查数据库文件是否完整
- 根据新环境修改config.py中的配置
- 首次运行前清除浏览器缓存

更多信息请查看 QUICK_START_GUIDE.md
