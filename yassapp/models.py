from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

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
    owner = models.ForeignKey(User, related_name="seller", on_delete=models.CASCADE)
    bidder = models.CharField(max_length=150, blank=True)
    banstatus = models.BooleanField(default=False)
    activestatus = models.BooleanField(default=True)
    session = models.CharField(max_length=64, default='')

    def __str__(self):
        return self.title

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'seller': self.owner.username,
            'description': self.description,
            'price': self.price,
            'deadline': self.deadline,
            'bidder': self.bidder
        }