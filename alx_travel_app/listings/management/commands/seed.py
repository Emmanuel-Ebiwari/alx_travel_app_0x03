import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing
import environ

env = environ.Env()
# Optionally read .env file if you want
environ.Env.read_env()

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample users and properties'

    def handle(self, *args, **kwargs):
        create_user_flag = env.bool('CREATE_USER', default=False)
        default_password = env.str('DEFAULT_USER_PASSWORD', default='')

        if not User.objects.exists():
            if create_user_flag:
                self.stdout.write('No users found. Creating a default user...')
                User.objects.create_user(
                    username='defaultuser',
                    email='default@example.com',
                    password=default_password
                )
                self.stdout.write(self.style.SUCCESS('Default user created.'))
            else:
                self.stdout.write(self.style.WARNING(
                    'No users found. Set CREATE_USER=True and DEFAULT_USER_PASSWORD in your env to auto-create a default user.'
                ))
                return

        host = User.objects.first()

        sample_data = [
            {
                "name": "Cozy Cabin in the Woods",
                "description": "A lovely secluded cabin surrounded by nature.",
                "location": "Asheville, NC",
                "price_per_night": 150.00,
            },
            {
                "name": "Beachfront Paradise",
                "description": "Wake up to the sound of waves and golden sand.",
                "location": "Malibu, CA",
                "price_per_night": 450.00,
            },
            {
                "name": "City Center Apartment",
                "description": "Modern and stylish apartment in the heart of the city.",
                "location": "New York, NY",
                "price_per_night": 220.00,
            },
        ]

        for data in sample_data:
            Listing.objects.create(
                property_id=uuid.uuid4(),
                host=host,
                name=data['name'],
                description=data['description'],
                location=data['location'],
                price_per_night=data['price_per_night'],
            )

        self.stdout.write(self.style.SUCCESS('Sample properties have been added.'))
