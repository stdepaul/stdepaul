"""stdepaul URL Configuration

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
from django.urls import path

from root_app import views as root_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # home
    path('', root_views.home, name='home'),
    # allauth
    # user profile page
    # about
    # rules
    # privacy policy
    # terms of service
    # wizard results page (list and/or map)
     
    # registration (custom, wizard (donator org, donator indv, regular user, etc))

    # assistance request create
    # assistance request detail
    # assistance request update
    # assistance request delete
    # stdepaul.org/assistance/global/food-banks
    # stdepaul.org/assistance/us-tx-dallas/food-banks/posts/request/detail/80/i-need-food
    # stdepaul.org/assistance/us-tx-dallas/<help_type>+<help_type>

    # assistance offers - (number of applicants to acccept (first come first serve), serving city, state, country, or global (affects visibility of offer post))
    # assistance offer create
    # assistance offer detail
    # assistance offer update
    # assistance offer delete
    # stdepaul.org/assistance/us-tx-dallas/food-banks/posts/offer/detail/53/i-own-a-food-bank
    # stdepaul.org/assistance/us-tx-dallas/food-banks/organization/detail/55/arts-district-food-bank

    # wiki "these spaces need content", each wiki has a faq with common questions, like "how long does approval take?" for disability, tc
    # stdepaul.org/assistance/us-tx-dallas/food-banks/wiki/detail/135/dallas-food-bank
    # stdepaul.org/assistance/us-tx-dallas/food-banks/wiki/create


]
