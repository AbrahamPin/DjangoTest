from django.contrib import messages, auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views import View


from yassapp.models import Auction
from yassapp.forms import createAuction, confAuction, UserCreationForm
import datetime

def archive(request):
    try:
        translation.activate(request.session[translation.LANGUAGE_SESSION_KEY])
    except KeyError:
        request.session[translation.LANGUAGE_SESSION_KEY] = "en"
        #translation.activate(request.session[translation.LANGUAGE_SESSION_KEY])


    auctions = Auction.objects.all().order_by('-timestamp')

    return render(request,'archive.html', {'auctions': auctions, })

    #auctions = Auction.objects.order_by('-timestamp')
    #return render(request, "archive.html",{'auctions':auctions})

def emailView(request):
    body = "email body"
    from_email = 'noreply@yaas.com'
    to_email = 'abraham_1396@hotmail.com'
    send_mail('Test Email Subject', body, from_email, [to_email,], fail_silently=False)
    messages.add_message(request, messages.INFO, "Email confirmation has been sent")
    return HttpResponseRedirect(reverse("home"))

def redirectView(request):
    return HttpResponseRedirect('/home/')

def view(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    return render(request,'archive.html', {'auctions': [auction,], })

def editauction(request, offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    else:
        auction = get_object_or_404(Auction, id=offset)
        return render(request,"editauction.html",
            {'user': request.user,
             "title": auction.title,
             "id": auction.id,
             "description": auction.description})


def updateauction(request, offset):
    auctions = Auction.objects.filter(id= offset)
    if len(auctions) > 0:
        auction = auctions[0]
    else:
        messages.add_message(request, messages.INFO, "Invalid auction id")
        return HttpResponseRedirect(reverse("home"))

    if request.method=="POST":
        description = request.POST["description"].strip()
        title = request.POST["title"].strip()
        auction.title = title
        auction.body = description

        auction.save()
        messages.add_message(request, messages.INFO, "Auction updated")

    return HttpResponseRedirect(reverse("home"))

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
            print("Add auction:", auction_t, auction_d, auction_p, auction_st)
            form = confAuction()
            return render(request,'wizardtest.html', {'form': form, "a_title": auction_t, "a_description": auction_d,
                                                      "a_price": auction_p, "a_time": auction_st})
        else:
            messages.add_message(request, messages.ERROR, "Not valid data")
            return render(request, 'createauction.html', {'form': form,})

def saveauction(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        a_title = request.POST.get('a_title', '')
        a_description = request.POST.get('a_description', '')
        a_price = request.POST.get('a_price', '')
        a_time = request.POST.get('a_time', '')
        print("fecha:", a_time)
        print("Save auction:", a_title, a_description, a_price, a_time)
        auction = Auction(title=a_title, description=a_description, timestamp=datetime.datetime.now(), price=a_price,
                          owner=request.user, deadline=a_time)
        auction.save()
        messages.add_message(request, messages.INFO, "New auction has been saved")
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


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        nextTo = request.GET.get('next', reverse("home"))
        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request,user)
            print(user.password)
            return HttpResponseRedirect(nextTo)

    return render(request,"login.html")

def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Logged out")
    return HttpResponseRedirect(reverse("home"))
