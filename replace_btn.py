import os

file_path = 'c:/Users/USER/NORSUWESITE/dashboard/templates/dashboard/admin-dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

open_post_modal_target = """    document.getElementById('postType').value = 'announcement';
    document.getElementById('postModal').classList.add('show');"""
open_post_modal_replace = """    document.getElementById('postType').value = 'announcement';
    const submitBtn = document.getElementById('postSubmitBtn');
    if (submitBtn) submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Publish Post';
    document.getElementById('postModal').classList.add('show');"""
content = content.replace(open_post_modal_target, open_post_modal_replace)

edit_post_target = """        } else {
            preview.style.display = 'none';
        }

        document.getElementById('postModal').classList.add('show');"""
edit_post_replace = """        } else {
            preview.style.display = 'none';
        }

        const submitBtn = document.getElementById('postSubmitBtn');
        if (submitBtn) submitBtn.innerHTML = '<i class="fas fa-save"></i> Save Post';

        document.getElementById('postModal').classList.add('show');"""
content = content.replace(edit_post_target, edit_post_replace)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated button text toggling")
