from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = 'Create or reset the primary superadmin account.'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='superadmin')
            user.set_password('admin123')
            user.is_superuser = True
            user.is_staff = True
            user.email = 'superadmin@norsu.edu.ph'
            user.save()
            self.stdout.write(self.style.SUCCESS('Superadmin password reset successfully.'))
        except User.DoesNotExist:
            User.objects.create_superuser(
                username='superadmin',
                email='superadmin@norsu.edu.ph',
                password='admin123',
            )
            self.stdout.write(self.style.SUCCESS('Superadmin created successfully.'))

        self.stdout.write(self.style.SUCCESS('Username: superadmin'))
        self.stdout.write(self.style.SUCCESS('Password: admin123'))
        self.stdout.write(self.style.WARNING('Change these credentials immediately from the Super Admin dashboard before deploying.'))
