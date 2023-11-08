from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path("", views.base, name='base'),
    path("predictions", views.predictions, name='predictions'),
    path("column_select", views.column_select, name='column_select'),

]
