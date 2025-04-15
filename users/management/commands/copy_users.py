from django.core.management.base import BaseCommand
from django.contrib.auth.models import User as OldUser
from users.models import UserAccount

class Command(BaseCommand):
    help = 'Copy users from auth.User to users.UserAccount'

    def handle(self, *args, **kwargs):
        count = 0
        skipped = 0
        for old_user in OldUser.objects.all():
            try:
                # Fallback email if email is missing
                email = old_user.email or f"{old_user.username}@placeholder.com"

                if not UserAccount.objects.filter(email=email).exists():
                    UserAccount.objects.create(
                        email=email,
                        first_name=old_user.first_name or 'First',
                        last_name=old_user.last_name or 'Last',
                        is_active=old_user.is_active,
                        is_staff=old_user.is_staff,
                        is_superuser=old_user.is_superuser,
                        password=old_user.password  # hashed!
                    )
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Copied: {email}"))
                else:
                    self.stdout.write(f"⚠️  Skipped (already exists): {email}")
            except Exception as e:
                skipped += 1
                self.stderr.write(f"❌ Failed to copy user '{old_user.username}': {e}")
        
        self.stdout.write(self.style.SUCCESS(f"✅ Done. Total users copied: {count}"))
        self.stdout.write(self.style.WARNING(f"⚠️ Skipped due to error: {skipped}"))
