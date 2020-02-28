"""praca_inzynierska URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls import url
from app import views
from accounts import views as accounts_views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signup/$', accounts_views.signup,name='signup'),
    url(r'^login/$', accounts_views.login, name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(),name='logout'),
    url(r'^users/$', views.show_user_repo, name='show_user_repo'),
    url(r'^bokeh/',views.bokeh,name='bokeh'),
    url(r'^days/',views.days,name='days'),
    url(r'^favorites/',views.favorites,name='favorites'),

    url('admin/', admin.site.urls),
]
