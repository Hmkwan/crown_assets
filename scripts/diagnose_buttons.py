"""
诊断按钮点击问题
"""

# 检查关键文件
print("=" * 70)
print("🔍 诊断按钮点击问题")
print("=" * 70)

print("\n1️⃣ 检查关键JavaScript代码...")

import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 检查审批流配置页面
workflow_file = os.path.join(base_dir, 'app', 'templates', 'main', 'workflow_config_by_type.html')
with open(workflow_file, 'r', encoding='utf-8') as f:
    workflow_html = f.read()

checks = [
    ("Select2 CDN", 'select2@4.1.0' in workflow_html),
    ("编辑按钮事件委托", "$(document).on('click', '.edit-node'" in workflow_html),
    ("删除按钮事件委托", "$(document).on('click', '.delete-node'" in workflow_html),
    ("Select2错误处理", 'try {' in workflow_html and 'catch (e)' in workflow_html),
    ("调试日志", "console.log('编辑节点按钮被点击')" in workflow_html),
]

all_pass = True
for name, result in checks:
    if result:
        print(f"   ✅ {name}")
    else:
        print(f"   ❌ {name}")
        all_pass = False

# 检查用户管理页面
print("\n2️⃣ 检查用户管理页面...")
user_file = os.path.join(base_dir, 'app', 'templates', 'main', 'user_management.html')
with open(user_file, 'r', encoding='utf-8') as f:
    user_html = f.read()

checks = [
    ("审批角色按钮", 'manage-workflow-roles' in user_html),
    ("审批角色事件委托", "$(document).on('click', '.manage-workflow-roles'" in user_html),
    ("模态框创建", '$workflowRolesModal' in user_html or 'workflowRolesModal' in user_html),
    ("调试日志", "console.log('管理审批流角色按钮被点击')" in user_html),
]

for name, result in checks:
    if result:
        print(f"   ✅ {name}")
    else:
        print(f"   ❌ {name}")
        all_pass = False

print("\n" + "=" * 70)
print("📋 诊断结果")
print("=" * 70)

if all_pass:
    print("✅ 所有检查通过！")
    print("\n🔍 如果按钮仍然无法点击，请：")
    print("1. 访问 http://127.0.0.1:5020/test_buttons 测试基本功能")
    print("2. 打开浏览器开发者工具（F12）-> Console标签")
    print("3. 刷新审批流配置页面，查看是否有JavaScript错误")
    print("4. 点击按钮，查看是否输出调试日志")
    print("\n可能的原因：")
    print("- 浏览器缓存未清除（按Ctrl+F5强制刷新）")
    print("- CDN资源加载失败（检查网络连接）")
    print("- 其他JavaScript错误阻塞了事件绑定")
else:
    print("❌ 部分检查未通过，请查看上方详情")

print("\n" + "=" * 70)
print("📖 调试步骤：")
print("=" * 70)
print("""
1. 打开浏览器访问: http://127.0.0.1:5020/test_buttons
   - 测试基本的jQuery和Bootstrap功能
   - 查看控制台日志

2. 访问审批流配置页面: http://127.0.0.1:5020/admin/workflow_config
   - 按F12打开开发者工具
   - 切换到Console标签
   - 应该看到: "=== 审批流配置页面加载完成 ==="
   
3. 点击"编辑"按钮
   - 应该看到: "编辑节点按钮被点击"
   - 模态框应该弹出

4. 如果没有日志输出或有错误：
   - 截图发送给开发人员
   - 记录错误信息
""")
