from yassapp.views import *
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^home/$', archive, name="home"),
    url(r'^createuser/$', register),
    url(r'^login/$', login_view),
    url(r'^logout/$', logout_view),
    url(r'^editprofile/$', editprofile, name="editprofile"),
    url(r'^password/$', changepassword, name="changepassword"),

    url(r'^add/$', Addauction.as_view(), name="add_auction"),
    url(r'^edit/(\d+)/$', editauction),
    url(r'^saveauction/$', saveauction),
    url(r'^update/(\d+)/$', updateauction),

    url(r'^bid/(\d+)/$', bid),
    url(r'^updatebid/(\d+)/$', updatebid),

    url(r'^ban/(\d+)/$', ban),
    url(r'^confirmban/(\d+)/$', confirmban),



    #url(r'^search/$', search_form, name="searchform"),
    #url(r'^delete/$', deleteAuction.as_view(), name="delete_auction"),
    # url(r'^authview/$', auth_view),
    # url(r'^i18n/', include('django.conf.urls.i18n')),
    # url(r'^currencies/', include('currencies.urls')),
    #
    url(r'^admin/', include(admin.site.urls)),
]






