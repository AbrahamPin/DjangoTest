from datetime import datetime
from django.contrib import messages, auth
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse
from yassapp.models import *
from yassapp.views import *

from yassapp.forms import *


##############################################################################
# Comment or disable any use of "messages" in other files in order to make   #
# the tests work without problems.                                           #
# because django.contrib.messages.middleware.MessageMiddleware does not work #
# in testing.                                                                #
##############################################################################

def re_date(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M')

# Create Auction Test Cases TR2.1
class CreateAuctionTestCase(TestCase):
    # Get data from this json
    fixtures = ['initial_data.json']

    # Create auction
    def setUp(self):
        self.factory = RequestFactory()

        self.owner = User.objects.create_user(
            username='testUser',
            email='owner@yaas.com',
            password='owner123'
        )
        self.title = 'Table'
        self.description = 'Round and large table.'
        self.price = 20

        # added more seconds due to the fact that it delays when it runs the test for valid date and it fails after
        self.deadline = (datetime.datetime.now() + datetime.timedelta(days=3)).replace(second=59, microsecond=0,
                                                                      tzinfo=None)
        self.bidder = ''
        self.activestatus = True
        self.banstatus = False
        self.session = ''


    # asserts that the mail is sent upon publication
    def email_sent(self):
        self.auction_save()
        self.assertEquals(len(mail.outbox), 1)

    # asserts that a deadline less than three days layer from now is invalid
    def invalid_deadline_form(self):
        form_data = {
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'deadline': (self.deadline - datetime.timedelta(minutes=1)).replace(tzinfo=None),

        }
        form = createAuction(data=form_data)
        self.assertFalse(form.is_valid())

    # asserts that a deadline greater or equal than three days layer from now
    # is valid
    def valid_deadline_form(self):
        form_data = {
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'deadline': self.deadline
        }
        form = createAuction(data=form_data)
        self.assertTrue(form.is_valid())

    # asserts that a discarded auction is not registered
    def cancel_auction(self):
        before = Auction.objects.all().count()
        response = self.new_auction_request({
            'a_title': self.title,
            'a_description': self.description,
            'a_price': self.price,
            'a_time': re_date(self.deadline),
            'option': 'No',
            'submit': False,
        })
        after = Auction.objects.all().count()
        self.assertEquals(after, before)
        self.assertEquals(response.status_code, 302)

    # asserts that a non-logged user can't create an auction
    def invaliduser_auction(self):
        before = Auction.objects.all().count()
        response = self.new_auction_request({
            'a_title': self.title,
            'a_description': self.description,
            'a_price': self.price,
            'a_time': re_date(self.deadline),
            'option': "Yes",
            'submit': True
        }, False)
        after = Auction.objects.all().count()

        self.assertEquals(before, after)
        self.assertEquals(response.status_code, 302)

    # asserts that a published auction is registered
    def add_auction(self):
        before = Auction.objects.all().count()
        response = self.new_auction_request({
            'a_title': self.title,
            'a_description': self.description,
            'a_price': self.price,
            'a_time': re_date(self.deadline),
            'option': 'Yes'
        })
        after = Auction.objects.all().count()

        self.assertEquals(after, before + 1)
        self.assertEquals(response.status_code, 302)

    # asserts that a published auction is registered correctly
    def registered_auction(self):
        self.new_auction_request({
            'a_title': self.title,
            'a_description': self.description,
            'a_price': self.price,
            'a_time': re_date(self.deadline),
            'option': 'Yes'
        })

        last_auction = Auction.objects.all().last()
        self.assertEquals(self.title, last_auction.title)
        self.assertEquals(self.description, last_auction.description)
        self.assertEquals(self.price, last_auction.price)
        self.assertEquals(re_date(self.deadline), re_date(last_auction.deadline))
        self.assertEquals(True, last_auction.activestatus)

    # Save Auction
    def auction_save(self):
        self.auction = Auction(
            owner=self.owner,
            title=self.title,
            description=self.description,
            price=self.price,
            deadline=self.deadline,
            bidder=self.bidder,
            activestatus=self.activestatus,
            banstatus=self.banstatus,
            session=self.session
        )
        self.auction.save()

    def new_auction_request(self, form_data, logged_user=True):
        request = self.factory.post('add_auction', form_data)
        if logged_user:
            request.user = self.owner
        else:
            request.user = AnonymousUser()

        return saveauction(request)


# Bid Test Cases TR2.2 and TR2.3
class BidAuctionTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.factory = RequestFactory()

        self.owner = User.objects.create_user(
            username='adminUser',
            email='owner@yaas.com',
            password='owner123'
        )
        self.title = 'Table'
        self.description = 'Round and large table.'
        self.price = 20

        # added more seconds due to the fact that it delays when it runs the test for valid date and it fails after
        self.deadline = (datetime.datetime.now() + datetime.timedelta(days=3)).replace(second=59, microsecond=0,
                                                                                       tzinfo=None)
        self.bidder = ''
        self.activestatus = True
        self.banstatus = False
        self.session = ''

        self.auction = Auction(
            owner=self.owner,
            title=self.title,
            description=self.description,
            price=self.price,
            deadline=self.deadline,
            bidder=self.bidder,
            activestatus=self.activestatus,
            banstatus=self.banstatus,
            session=self.session
        )
        self.auction.save()

        self.bidder = User.objects.create_user(
            username='bidUser',
            email='bidder@yaas.com',
            password='bidder123'
        )

        self.admin = User.objects.get(pk=1)

    # asserts that a valid bid can be placed
    def add_bid(self):
        self.new_bid_request({
            'price': 30.20
        })

        # had to call this because the auction was not being updated in the db after placing a bid
        self.auction.refresh_from_db()
        self.assertEquals(30.20, float(self.auction.price))

    # asserts that a bid on a inactive or banned auction is denied
    def inactive_banned_bid(self):
        self.auction.activestatus = False
        self.auction.save()

        response = self.new_bid_request({
         'price': 31.20
        })

        self.auction.refresh_from_db()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(20, self.auction.price)


    # asserts that the seller can't bid on his own auction
    def seller_bid(self):
        self.bidder = self.auction.owner
        response = self.new_bid_request({
            'price': 31.20
        })

        self.auction.refresh_from_db()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(20, self.auction.price)

    # asserts that a bid on an auction being updated is denied
    def updating_auction(self):
        self.session = '2c7bc9d3015ad2f1f9fb9cf319b055c0'
        self.auction.session = self.session
        self.auction.save()

        response = self.new_bid_request({
            'price': 31.20
        })

        self.auction.refresh_from_db()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(20, self.auction.price)

    # asserts that a bid lower than the base price of the auction is denied
    def lower_price_bid(self):
        response = self.new_bid_request({
            'price': 19.10
        })

        self.auction.refresh_from_db()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(20, float(self.auction.price))

    def new_bid_request(self, form_data, logged_user=True):
        request = self.factory.post('bid', form_data)
        if logged_user:
            request.user = self.bidder
        else:
            request.user = AnonymousUser()
        return updatebid(request, self.auction.id)
