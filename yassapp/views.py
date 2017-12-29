import base64
import json
import requests
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.response import Response
from django.contrib import messages, auth
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import translation
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views import View
from .email import sendEmail


from yassapp.models import Auction
from yassapp.forms import *
import datetime


def getauction(request, offset):
    auction = get_object_or_404(Auction, id=offset)

    return render(request, 'auction.html', {
        'auction': auction,
    })

def archive(request):

    try:
        translation.activate(request.session[translation.LANGUAGE_SESSION_KEY])
    except KeyError:
        request.session[translation.LANGUAGE_SESSION_KEY] = "en"

    auctions = Auction.objects.all().order_by('id')

    query = request.GET.get("q")
    if query:
        auctions = auctions.filter(title__icontains=query)

    symbol = request.GET.get('currency', 'EUR')
    if symbol != 'EUR':
        rate = get_rate(symbol)
        for auction in auctions:
            auction.price = round(float(auction.price) * rate, 2)

    currency_form = currForm(initial={'currency': symbol})

    try:
        language = request.session[translation.LANGUAGE_SESSION_KEY]
    except KeyError:
        language = 'en'
    language_form = langForm(initial={'language': language})

    return render(request,'archive.html', {
        'auctions': auctions,
        'language': language_form,
        'currency': currency_form,
        'symbol': symbol,
    })

def redirectView(request):
    return HttpResponseRedirect('/home/')


@method_decorator(login_required, name="dispatch")
class Addauction(View):
    def get(self, request):
        form = createAuction()
        return render(request, 'createauction.html', {'form': form})

    def post(self, request):
        form = createAuction(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            auction_t = cd['title']
            auction_d = cd['description']
            auction_p = cd['price']
            auction_st = cd['deadline']
            form = confAuction()
            return render(request, 'confirmation.html', {'form': form, "a_title": auction_t, "a_description": auction_d,
                                                      "a_price": auction_p, "a_time": auction_st})
        else:
            messages.add_message(request, messages.ERROR, "Not valid data")
            return render(request, 'createauction.html', {'form': form,})


def saveauction(request):
    option = request.POST.get('option', '')
    if option == 'Yes' and request.user.is_authenticated():
        a_title = request.POST.get('a_title', '')
        a_description = request.POST.get('a_description', '')
        a_price = request.POST.get('a_price', '')
        a_time = request.POST.get('a_time', '')
        auction = Auction(title=a_title, description=a_description, timestamp=datetime.datetime.now(), price=a_price,
                          owner=request.user, deadline=a_time)
        auction.save()

        ###########
        ###########
        ########### Comment this for doing tests
        messages.add_message(request, messages.INFO, "New auction has been saved")
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))

def editauction(request, offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    else:
        auction = get_object_or_404(Auction, id=offset)
        if request.user == auction.owner:
            if auction.session == '' or auction.session == request.session._get_or_create_session_key():
                auction.session = request.session._get_or_create_session_key()
                auction.save()

                return render(request,"editauction.html",
                    {'user': request.user,
                     "title": auction.title,
                     "id": auction.id,
                     "description": auction.description})
            elif auction.session != request.session._get_or_create_session_key():

                messages.add_message(request, messages.INFO, "Auction is being edited in this moment!")
                return HttpResponseRedirect(reverse("home"))
        else:
            messages.add_message(request, messages.INFO, "Invalid User for editing.")
            return HttpResponseRedirect(reverse("home"))


def updateauction(request, offset):
    auctions = Auction.objects.filter(id=offset)

    if len(auctions) > 0:
        auction = auctions[0]
    else:
        messages.add_message(request, messages.INFO, "Invalid auction id")
        return HttpResponseRedirect(reverse("home"))

    if request.method=="POST":
        description = request.POST["description"].strip()
        title = request.POST["title"].strip()
        auction.title = title
        auction.description = description

        auction.session = ''
        auction.save()

        messages.add_message(request, messages.INFO, "Auction description updated")

    return HttpResponseRedirect(reverse("home"))


def bid(request, offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    else:
        auction = get_object_or_404(Auction, id=offset)

        if (auction.activestatus == False) or (auction.banstatus == True):

            ###########
            ###########
            ########### Comment this for doing tests
            messages.add_message(request, messages.INFO, "Auction is Due or Banned.")
            return HttpResponseRedirect(reverse("home"))
        else:
            if str(request.user) != auction.bidder:
                if auction.session == '':
                    form = bidAuction(initial={'price': auction.price})
                    return render(request,"bid.html",
                        {'user': request.user,
                         'form': form,
                         "title": auction.title,
                         "id": auction.id,
                         "description": auction.description,
                         "price": auction.price,
                         "bidder": request.user})
                else:

                    ###########
                    ###########
                    ########### Comment this for doing tests
                    messages.add_message(request, messages.INFO, "Auction is being updated right now, wait and try again.")
                    return HttpResponseRedirect(reverse("home"))
            else:

                ###########
                ###########
                ########### Comment this for doing tests
                messages.add_message(request, messages.INFO, "No new bids since your last bid.")
                return HttpResponseRedirect(reverse("home"))

def updatebid(request, offset):
    auctions = Auction.objects.filter(id=offset)

    if len(auctions) > 0:
        auction = auctions[0]
    else:
        messages.add_message(request, messages.INFO, "Time Ran Out")
        return HttpResponseRedirect(reverse("home"))

    if (auction.activestatus == False) or (auction.banstatus == True):

        ###########
        ###########
        ########### Comment this for doing tests
        messages.add_message(request, messages.INFO, "Auction is Due or Banned.")
        return HttpResponseRedirect(reverse("home"))

    if request.user == auction.owner:

        ###########
        ###########
        ########### Comment this for doing tests
        messages.add_message(request, messages.INFO, "Bidder can't be the owner.")
        return HttpResponseRedirect(reverse("home"))


    if request.method=="POST":
        if auction.session == '':
            price = request.POST["price"].strip()
            if float(auction.price) + .01 <= float(price):
                previousbidder = auction.bidder
                auction.bidder = str(request.user)
                auction.price = price

                if auction.deadline <= (datetime.datetime.now() + datetime.timedelta(minutes=5)):
                    auction.deadline = auction.deadline + datetime.timedelta(minutes=5)

                    ###########
                    ###########
                    ########### Comment this for doing tests
                    messages.add_message(request, messages.INFO, "Auction deadline has 5 more minutes.")
                    auction.save()
                else:
                    auction.save()

                #Send email to Seller
                subject = "New Bid on your Auction"
                recipient_list = [auction.owner.email]
                message = "Your auction has a new bid."
                sendEmail(subject, recipient_list, message)

                #Send email to New Bidder
                user = User.objects.get(username=auction.bidder)
                subject = "New Bid on an Auction"
                recipient_list = [user.email]
                message = "Your bid has been successfully submitted."
                sendEmail(subject, recipient_list, message)

                #Send email to Old Bidder
                if previousbidder != '':
                    user = User.objects.get(username=previousbidder)
                    subject = "Bid Surpassed"
                    recipient_list = [user.email]
                    message = "Your bid on an Auction has been surpassed."
                    sendEmail(subject, recipient_list, message)

                ###########
                ###########
                ########### Comment this for doing tests
                messages.add_message(request, messages.INFO, "You made a new bid!")
            else:

                ###########
                ###########
                ########### Comment this for doing tests
                messages.add_message(request, messages.INFO, "The bid has to be higher than 0.01 from the current price")
                return HttpResponseRedirect(reverse("home"))
                # form = bidAuction(initial={'price': auction.price})
                # return render(request, "bid.html",
                #               {'user': request.user,
                #                'form': form,
                #                "title": auction.title,
                #                "id": auction.id,
                #                "description": auction.description,
                #                "price": auction.price,
                #                "bidder": request.user})
        else:

            ###########
            ###########
            ########### Comment this for doing tests
            messages.add_message(request, messages.INFO, "Auction is being updated right now, wait and try again.")
            return HttpResponseRedirect(reverse("home"))

    return HttpResponseRedirect(reverse("home"))


def ban(request, offset):
    auction = get_object_or_404(Auction, id=offset)
    form = confAuction()
    return render(request, "ban.html",
                  {'form': form,
                   'id': auction.id})

def confirmban(request, offset):
    option = request.POST.get('option', '')
    if option == 'Yes':
        auction = get_object_or_404(Auction, id=offset)

        auction.banstatus = True
        auction.activestatus = False
        auction.save()

        # Send Email to Seller
        subject = "Auction Banned"
        message = "One of your auctions has been banned"
        recipient_list = [auction.owner.email]
        sendEmail(subject, recipient_list, message)

        messages.add_message(request, messages.INFO, "Auction has been banned.")
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))

@login_required
def auth_view(request):
    output = "User is authenticated."
    return HttpResponse(output)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()

            messages.add_message(request, messages.INFO, "New User is created. Please Login")

            return HttpResponseRedirect(reverse("home"))
        else:
            form = UserCreationForm(request.POST)
    else:
        form =UserCreationForm()

    return render(request,"registration.html", {'form': form})

def editprofile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "New Email Saved")
            return HttpResponseRedirect(reverse("editprofile"))
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
    return render(request, "editprofile.html", args)


def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Password Changed.")
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse("editprofile"))
        else:
            messages.error(request, 'Passwords did not match.')
            return HttpResponseRedirect(reverse("changepassword"))
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
    return render(request, "changepassword.html", args)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        nextTo = request.GET.get('next', reverse("home"))
        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request,user)
            return HttpResponseRedirect(nextTo)

    return render(request,"login.html")

def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Logged out")
    return HttpResponseRedirect(reverse("home"))

class AuctionApi(View):
    def get(self, request, offset):
        try:
            auction = Auction.objects.get(~Q(banstatus=True), ~Q(activestatus=False), pk=offset)
        except Auction.DoesNotExist:
            return json_error('No auction found.', 404)

        return JsonResponse({
            'auction': auction.to_json()
        })

    def put(self, request, offset):
        user = authenticate_user(request)
        if user is None:
            return json_error('Invalid credentials.', 401)

        try:
            price = json.loads(request.body)['price']
        except KeyError:
            return json_error('Missing parameter.', 400)

        try:
            auction = Auction.objects.get(~Q(banstatus=True), pk=offset)
        except Auction.DoesNotExist:
            return json_error('No auction found.', 404)

        auction.price = price

        response = JsonResponse({
            'Success msg'
            'success': str(price) + '€ bid placed (' + auction.title + ').'
        })
        response.status_code = 201
        return response


class AuctionsApi(View):
    def get(self, request, search_query=''):
        auctions = Auction.objects.filter(~Q(banstatus=True), ~Q(activestatus=False),  title__contains=search_query).order_by('-deadline')
        if not auctions:
            return json_error('No auction found.', 404)

        auctions_json = []
        for auction in auctions:
            auctions_json.append({'auction': auction.to_json()})

        return JsonResponse({
            'auctions:': auctions_json
        })


def authenticate_user(request):
    if 'HTTP_AUTHORIZATION' not in request.META:
        return None

    auth_header = request.META['HTTP_AUTHORIZATION']
    encoded_credentials = auth_header.split(' ')[1]
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
    username, password = decoded_credentials.split(':')
    return authenticate(username=username, password=password)


def json_error(message, error_code):
    response = JsonResponse({
        'error': message
    })
    response.status_code = error_code

    return response

def get_rate(symbol, base='EUR'):
    return requests.get('https://api.fixer.io/latest', params={'base': base, 'symbols': symbol}).json()['rates'][symbol]

