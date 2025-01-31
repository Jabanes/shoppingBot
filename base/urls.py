from django.urls import path
from . import views

urlpatterns = [
    path('whatsapp/', views.handle_whatsapp_message, name='handle_whatsapp_message'),
]
