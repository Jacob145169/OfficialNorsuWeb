
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'norsu_dashboard.settings')
django.setup()

from dashboard.models import Post

print(f"Total posts: {Post.objects.count()}")
print(f"Posts for CAS: {Post.objects.filter(college__iexact='cas').count()}")
for p in Post.objects.filter(college__iexact='cas'):
    print(f"- {p.title} (Type: {p.post_type}, Status: {p.status})")
