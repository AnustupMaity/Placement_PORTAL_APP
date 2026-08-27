import os

files = [
    'frontend/src/components/AdminDashboard.vue',
    'frontend/src/components/StudentDashboard.vue',
    'frontend/src/components/CompanyDashboard.vue'
]

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace(
            'n in notifications.slice(0, 5)',
            'n in (Array.isArray(notifications) ? notifications : []).slice(0, 5)'
        )
        content = content.replace(
            'notifications.length === 0',
            '(!notifications || !Array.isArray(notifications) || notifications.length === 0)'
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Not found: {filepath}")

print("Vue dashboard templates patched successfully.")
