import os

file_path = 'c:/Users/USER/NORSUWESITE/dashboard/templates/dashboard/super-admin-dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "const collegeColleges = document.getElementById('collegeColleges').value;" in line:
        lines.insert(i + 1, "            const collegeThemeColor = document.getElementById('collegeThemeColor').value;\n")
        break

for i in range(6000, len(lines)):
    if "collegeFormData.append('description', collegeColleges);" in lines[i]:
        lines.insert(i + 1, "            collegeFormData.append('theme_color', collegeThemeColor);\n")
        break

for i in range(7000, len(lines)):
    if "removeCollegeImage(); // Clear image preview" in lines[i]:
        lines.insert(i + 1, "            document.getElementById('collegeThemeColor').value = '#0078d4';\n            document.getElementById('collegeThemeColorText').value = '#0078D4';\n")
        break

for i in range(7600, len(lines)):
    if "document.getElementById('collegeStatus').value = college.status;" in lines[i]:
        edit_logic = """            if (college.theme_color) {
                document.getElementById('collegeThemeColor').value = college.theme_color;
                document.getElementById('collegeThemeColorText').value = college.theme_color.toUpperCase();
            } else {
                document.getElementById('collegeThemeColor').value = '#0078d4';
                document.getElementById('collegeThemeColorText').value = '#0078D4';
            }
"""
        lines.insert(i + 1, edit_logic)
        break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Updated JS logic in super-admin-dashboard.html")
