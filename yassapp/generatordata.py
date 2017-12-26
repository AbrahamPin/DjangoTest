import random
from datetime import timedelta

from yassapp.models import Auction
from autofixture import AutoFixture, generators
from autofixture.autofixtures import UserFixture
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone

call_command('flush', interactive=False)

user = User(is_superuser=True, email='adminyaas@yaas.com', is_staff=True, is_active=True, date_joined='2017-07-01',
            username='admin')
user.set_password('admin123')
user.save()
UserFixture(User, password='yaasapp123').create(49)

AutoFixture(Auction, field_values={
    'owner_id': generators.IntegerGenerator(min_value=1, max_value=50),
    'title': generators.LoremWordGenerator(1),
    'description': generators.LoremSentenceGenerator(max_length=256),
    'bidder': generators.StaticGenerator(''),
    'price': generators.FloatGenerator(decimal_digits=2, min_value=1, max_value=100),
    'timestamp': generators.DateTimeGenerator(timezone.now()),
    'deadline': generators.DateTimeGenerator(max_date=(timezone.now() + timedelta((5 * 365) / 12))),
    'activestatus': generators.StaticGenerator(True),
    'banstatus': generators.StaticGenerator(False),
    'session': generators.StaticGenerator('')
}).create(50)
