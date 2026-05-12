import re

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We will look for patterns like:
    # const arrayName = JSON.parse(localStorage.getItem('storageKey') || '[]');
    # const updatedArrayName = arrayName.filter(...);
    
    # We will inject:
    # const itemToArchive = arrayName.find(...);
    # if (itemToArchive) archiveItem('storageKey', itemToArchive);
    
    # Let's do it manually for the known ones:
    deletes = [
        ('superAdminNews', 'News'),
        ('superAdminAlumni', 'Alumni'),
        ('superAdminAnnouncements', 'Announcement'),
        ('superAdminColleges', 'College'),
        ('superAdminHistoryInfo', 'History'),
        ('superAdminNORSUInfo', 'NORSU Info'),
        ('superAdminAlumniNews', 'Alumni News'),
        ('superAdminAlumniEvents', 'Alumni Event'),
        ('superAdminSuccessStories', 'Success Story'),
        ('superAdminAchievements', 'Achievement'),
        ('superAdminMediaUploads', 'Media Upload')
    ]
    
    for key, type_name in deletes:
        # Find the block where item is deleted
        # usually looks like: const something = JSON.parse(localStorage.getItem('key') || '[]');
        # then filter.
        
        pattern = r"(const\s+(\w+)\s*=\s*JSON\.parse\(localStorage\.getItem\('{}'\)\s*\|\|\s*'\[\]'\);)\s*(const\s+(\w+)\s*=\s*\2\.filter\(([^=]+)\s*=>\s*\5\.id\s*!==\s*([^\)]+)\);)".format(key)
        
        def repl(match):
            parse_line = match.group(1)
            array_name = match.group(2)
            filter_line = match.group(3)
            item_var = match.group(5)
            id_var = match.group(6)
            
            inject = f"\n                const itemToArchive = {array_name}.find({item_var} => {item_var}.id === {id_var});\n                if (itemToArchive) archiveItem('{type_name}', '{key}', itemToArchive);\n                "
            return parse_line + inject + filter_line
            
        content = re.sub(pattern, repl, content)
        
    # Now for deletePost which uses backend:
    # We need to fetch the post before deleting
    post_pattern = r"(async function deletePost\(id\) \{[\s\S]*?if \(_confirmed\) \{)"
    def post_repl(match):
        return match.group(1) + """
                try {
                    const postRow = document.querySelector(`tr td button[onclick="deletePost(${id})"]`);
                    if (postRow) {
                        const title = postRow.closest('tr').children[0].innerText;
                        archiveItem('Post', 'api_post', {id: id, title: title});
                    }
                } catch(e) {}
"""
    content = re.sub(post_pattern, post_repl, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Patching complete.")

patch_file(r'c:\Users\USER\OneDrive\Desktop\NORSUWESITE\dashboard\templates\dashboard\super-admin-dashboard.html')
