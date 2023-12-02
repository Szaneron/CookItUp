from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_user, name="register_user"),
    path("login/", views.login_user, name="login_user"),
    path("logout/", views.logout_user, name="logout_user"),
    path("home/", views.home, name="home"),
    path("recipe/", views.recipe, name="recipe"),
    path("recipe/<int:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path("shopping_list/", views.shopping_list, name="shopping_list"),
    path("contact/", views.contact, name="contact"),
    path("statute/", views.statute, name="statute"),
    path("features/", views.features, name="features"),
]
