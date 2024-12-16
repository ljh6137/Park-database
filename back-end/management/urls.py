from django.urls import path
from django.urls import re_path
# from django.conf.urls import url
from . import views

# urlpatterns = [
#     path("register/", views.register),
#     # ex: /polls/
#     # re_path(r"^register/$", views.register),
#     # path("management/register/", views.register),
#     # # ex: /polls/5/
#     # path("<int:question_id>/", views.detail, name="detail"),
#     # # ex: /polls/5/results/
#     # path("<int:question_id>/results/", views.results, name="results"),
#     # # ex: /polls/5/vote/
#     # path("<int:question_id>/vote/", views.vote, name="vote"),
# ]


urlpatterns = [
    path('rented_vehicles/', views.rented_vehicles_view, name='rented_vehicles'),
    path('', views.home_view, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('rent_car/', views.rent_car_view, name='rent_car'),
]
