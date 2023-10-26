from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spoonacular_username = models.CharField(max_length=100)
    spoonacular_password = models.CharField(max_length=100)
    spoonacular_hash = models.CharField(max_length=100)
