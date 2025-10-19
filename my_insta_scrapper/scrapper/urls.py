from django.urls import path
from . import views

urlpatterns = [
    path('', views.instagram_dashboard, name='instagram_dashboard'),
    path('scrape/', views.instagram_dashboard, name='scrape_instagram'),
]