import os
import django
from django.conf import settings
from django.apps import apps
from django.db.models import FileField, ImageField

# Setup django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'norsu_dashboard.settings')
django.setup()

def get_used_media_files():
    used_files = set()
    for model in apps.get_models():
        file_fields = []
        for field in model._meta.get_fields():
            if isinstance(field, FileField) or isinstance(field, ImageField):
                file_fields.append(field.name)
        
        if file_fields:
            # Get all instances
            try:
                instances = model.objects.all()
                for instance in instances:
                    for field_name in file_fields:
                        file_attr = getattr(instance, field_name)
                        if file_attr and hasattr(file_attr, 'name') and file_attr.name:
                            # file_attr.name is relative to MEDIA_ROOT
                            used_files.add(os.path.normpath(file_attr.name))
            except Exception as e:
                print(f"Error reading model {model}: {e}")
    return used_files

def get_all_media_files(media_root):
    all_files = set()
    for root, dirs, files in os.walk(media_root):
        for file in files:
            full_path = os.path.join(root, file)
            # get relative path to media_root
            rel_path = os.path.relpath(full_path, media_root)
            all_files.add(os.path.normpath(rel_path))
    return all_files

def main():
    media_root = settings.MEDIA_ROOT
    print(f"MEDIA_ROOT: {media_root}")
    
    used_files = get_used_media_files()
    all_files = get_all_media_files(media_root)
    
    unused_files = all_files - used_files
    
    print(f"Total media files in dir: {len(all_files)}")
    print(f"Total media files used in DB: {len(used_files)}")
    print(f"Total unused files based on DB: {len(unused_files)}")
    
    with open('unused_media.txt', 'w') as f:
        for uf in sorted(unused_files):
            f.write(uf + '\n')
            
if __name__ == '__main__':
    main()
