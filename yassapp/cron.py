from django.db.models import Q
from django_cron import CronJobBase, Schedule
from .views import sendEmail
from .models import *
from datetime import *

class CronResolver(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'yassapp.resolver'

    def do(self):
        today = datetime.today()
        auctions = Auction.objects.filter(~Q(banstatus=True), ~Q(activestatus=False), Q(deadline__lte=today))
        for auction in auctions:
            if auction.bidder == '':
                auction.activestatus = False
                # Send email to seller
                subject = "Auction is Due"
                message = "One of your auctions has reached its deadline and did not have any bidders."
                recipient_list = [auction.owner.email]
                sendEmail(subject, recipient_list, message)
            else:
                auction.activestatus = False
                user = User.objects.get(username=auction.bidder)
                # Send email to seller
                subject = "Auction is Due"
                message = "One of your auctions has reached its deadline and had a winner."
                recipient_list = [auction.owner.email]
                sendEmail(subject, recipient_list, message)

                # Send email to highest bidder
                subject = "Congratulations on your bid!"
                message = "You have won on your last bid in an auction."
                recipient_list = [user.email]
                sendEmail(subject, recipient_list, message)

            auction.save()