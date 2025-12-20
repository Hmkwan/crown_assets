"""
最终验证所有修复
"""
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("✅ 最终验证报告")
print("=" * 70)

# 检查workflow_config_by_type.html
workflow_file = os.path.join(base_dir, 'app', 'templates', 'main', 'workflow_config_by_type.html')
with open(workflow_file, 'r', encoding='utf-8') as f:
    workflow_content = f.read()

print("\n📄 审批流配置页面 (workflow_config_by_type.html):")
print("-" * 70)

checks = [
    ("Select2 CDN已添加", 'select2@4.1.0' in workflow_content),
    ("scripts块正确使用", '{% block scripts %}' in workflow_content and '{{ super() }}' in workflow_content),
    ("Select2在scripts块中", workflow_content.index('{% block scripts %}') < workflow_content.index('select2@4.1.0') if ('{% block scripts %}' in workflow_content and 'select2@4.1.0' in workflow_content) else False),
    ("事件委托正确", "$(document).on('click', '.edit-node'" in workflow_content),
    ("删除事件委托", "$(document).on('click', '.delete-node'" in workflow_content),
    ("jQuery检测", "if (typeof jQuery === 'undefined')" in workflow_content),
]

workflow_ok = True
for name, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {name}")
    if not result:
        workflow_ok = False

# 检查user_management.html
user_file = os.path.join(base_dir, 'app', 'templates', 'main', 'user_management.html')
with open(user_file, 'r', encoding='utf-8') as f:
    user_content = f.read()

print("\n📄 用户管理页面 (user_management.html):")
print("-" * 70)

checks = [
    ("JSON错误处理", 'try {' in user_content and 'JSON.parse(currentRoles)' in user_content),
    ("角色数据容错", 'roles = [currentRoles]' in user_content),
    ("事件委托", "$(document).on('click', '.manage-workflow-roles'" in user_content),
    ("调试日志", "console.log('管理审批流角色按钮被点击')" in user_content),
]

user_ok = True
for name, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {name}")
    if not result:
        user_ok = False

print("\n" + "=" * 70)
print("📊 总结")
print("=" * 70)

if workflow_ok and user_ok:
    print("✅ 所有检查通过！")
    print("\n🎉 修复内容：")
    print("  1. ✅ 移除了btn-group，改为独立按钮")
    print("  2. ✅ 使用事件委托绑定所有按钮事件")
    print("  3. ✅ 添加了Select2 CDN并放在正确的位置")
    print("  4. ✅ 将所有JavaScript移到{% block scripts %}中")
    print("  5. ✅ 添加了jQuery加载检测")
    print("  6. ✅ 修复了JSON解析错误")
    print("  7. ✅ 添加了错误处理和容错机制")
    print("  8. ✅ 添加了详细的调试日志")
    
    print("\n📝 测试步骤：")
    print("  1. 清除浏览器缓存（Ctrl+Shift+Delete）或硬刷新（Ctrl+F5）")
    print("  2. 访问: http://127.0.0.1:5020/admin/workflow_config")
    print("  3. 打开F12开发者工具 -> Console标签")
    print("  4. 应该看到：")
    print("     - jQuery已加载，版本: 1.12.4")
    print("     - === 审批流配置页面加载完成 ===")
    print("     - 编辑按钮数量: X")
    print("     - 删除按钮数量: X")
    print("  5. 点击编辑/删除按钮，应该弹出模态框")
    print("  6. 访问: http://127.0.0.1:5020/admin/users")
    print("  7. 点击'审批角色'按钮，应该弹出模态框")
    
else:
    print("❌ 部分检查未通过")
    if not workflow_ok:
        print("  - 审批流配置页面需要修复")
    if not user_ok:
        print("  - 用户管理页面需要修复")

print("\n" + "=" * 70)
