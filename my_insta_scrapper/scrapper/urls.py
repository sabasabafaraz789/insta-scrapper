from django.urls import path
from . import views

urlpatterns = [
    path('scrapper/', views.scrapper, name='scrapper'),
]