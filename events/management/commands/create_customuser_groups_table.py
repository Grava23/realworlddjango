from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create the events_customuser_groups table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE events_customuser_groups (
                    id SERIAL PRIMARY KEY,
                    customuser_id INTEGER REFERENCES events_customuser(id) ON DELETE CASCADE,
                    group_id INTEGER REFERENCES auth_group(id) ON DELETE CASCADE
                );
            ''')
        self.stdout.write(self.style.SUCCESS('Table events_customuser_groups created successfully'))
