
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'norsu_dashboard.settings')
django.setup()

from dashboard.models import Post

print("College values in DB for CAS posts:")
for p in Post.objects.filter(title__icontains='Hara & Hari'):
    print(f"Post: {p.title}, College field: '{p.college}'")

print("\nDistinct college values in Post table:")
from django.db.models import Count
for c in Post.objects.values('college').annotate(count=Count('id')):
    print(f"'{c['college']}': {c['count']}")
