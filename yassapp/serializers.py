from rest_framework import serializers
from yassapp.models import Auction

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id', 'title', 'description', 'timestamp', 'price', 'owner_id', 'start_time')

