from django.urls import path
from .views import getAssets

urlpatterns = [
    path('api/get-assets/',getAssets)
]
