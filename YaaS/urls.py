"""YaaS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from EkList import views

urlpatterns = [
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^home/', views.home_page, name="home"),
    url(r'^ban/(?P<auction_id>[0-9]+)/$', views.ban_auction, name="ban"),

    url(r'^auction/(?P<auction_id>[0-9]+)/$', views.view_auction, name="auction"),
    url(r'^bid/(?P<auction_id>[0-9]+)/$', views.post_bid, name="bid"),
    url(r'^create/$', views.create_auction, name="create"),
    url(r'^verify/$', views.verify_auction, name="verify"),
    url(r'^edit/(?P<auction_id>[0-9]+)/$', views.edit_auction, name="edit"),
    url(r'^search/.*', views.search_auction, name="search"),

    url(r'^login/.*', views.login_user, name="login"),
    url(r'^logout/$', views.logout_session, name="logout"),
    url(r'^register/$', views.register_user, name="register"),
    url(r'^profile/(?P<username>.*)/$', views.user_profile, name="profile_page"),

    url(r'^change_language/$', views.toggle_language, name="language"),

    url(r'^password_change/$', auth_views.password_change, name="password_change"),
    url(r'^password_change/done/$', views.password_change_done, name="password_change_done"),

    url(r'^password_reset/$', auth_views.password_reset, name="password_reset"),
    url(r'^password_reset/done/$', views.password_reset_done, name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name="password_reset_confirm"),
    url(r'^reset/done/$', views.password_reset_complete, name="password_reset_complete"),

    url(r'.*', views.redirect_home, name="home_redirect")
]
