from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create the events_customuser_user_permissions table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE events_customuser_user_permissions (
                    id SERIAL PRIMARY KEY,
                    customuser_id INTEGER REFERENCES events_customuser(id) ON DELETE CASCADE,
                    permission_id INTEGER REFERENCES auth_permission(id) ON DELETE CASCADE
                );
            ''')
        self.stdout.write(self.style.SUCCESS('Table events_customuser_user_permissions created successfully'))

