from django.db import models
#from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta, date
from django.core.exceptions import ValidationError

# The following function will automatically create a Token whenever we create a new user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=19, decimal_places=2)
    deadline = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)

    def clean(self, *args, **kwargs):
        # run the base validation
        super(Auction, self).clean(*args, **kwargs)

        # Don't allow dates older than now.
        print("Modelooo: ", self.start_time)
        if self.start_time < datetime.datetime.now():
            raise ValidationError('Start time must be later than now.')

    #class Meta:
    #   ordering = ['timestamp']