from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Hash existing plain text passwords in the User model.'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            if not user.password.startswith('pbkdf2_sha256$'):  # Check if already hashed
                print(f"Hashing password for user: {user.username}")
                # Store the current plain password for hashing
                plain_password = user.password
                user.set_password(plain_password)  # Hash the password
                user.save()  # Save the hashed password
        print("Password hashing complete.")
