from django.urls import path

from .views import say_hi

urlpatterns = [
    path('exists/', say_hi)
]
