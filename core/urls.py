# C:\wamp64\www\ImobCloud\core\urls.py

from django.urls import path
from .views import UserProfileView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]