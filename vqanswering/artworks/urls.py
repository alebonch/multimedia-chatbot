from django.urls import path
from .views import Artworkchat

urlpatterns = [
    path('gallery/<str:link>/', Artworkchat.as_view(), name='artworkchat'),
    ]