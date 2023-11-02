import decimal
import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from dotenv import load_dotenv
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import UserProfile

import requests

load_dotenv()


def register_user(request):
    api_key = os.getenv('SPOONACULAR_API_KEY')

    if request.method == 'POST':
        # User registration form support in Django
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Get user data from the form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # Send a request to the Spoonacular API
            spoonacular_data = {
                "username": username
            }

            response = requests.post("https://api.spoonacular.com/users/connect?apiKey=" + api_key,
                                     json=spoonacular_data)

            if response.status_code == 200:
                # Get data from Spoonacular
                spoonacular_response = response.json()
                spoonacular_username = spoonacular_response['username']
                spoonacular_password = spoonacular_response['spoonacularPassword']
                spoonacular_hash = spoonacular_response['hash']

                # Save data from Spoonacular in the userprofile model
                UserProfile.objects.create(user=user, spoonacular_username=spoonacular_username,
                                           spoonacular_password=spoonacular_password, spoonacular_hash=spoonacular_hash)

                # Log in the user to the Django system
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Error connecting the user to the spoonacular api')

    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login_user')

    else:
        return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('home')


def home(request):
    # Get API key environment variable
    api_key = os.getenv('SPOONACULAR_API_KEY')
    popular_url = 'https://api.spoonacular.com/recipes/informationBulk?ids=638248,647634,639411,1055614&includeNutrition=true&apiKey=' + api_key
    latest_url = 'https://api.spoonacular.com/recipes/informationBulk?ids=654125,656752,800754,1098357&includeNutrition=true&apiKey=' + api_key
    response1 = requests.get(popular_url)
    response2 = requests.get(latest_url)

    if response1.status_code == 200 and response2.status_code == 200:
        popular_recipes = response1.json()
        latest_recipes = response2.json()
        return render(request, 'home_page.html',
                      {'popular_recipes': popular_recipes, 'latest_recipes': latest_recipes, })
    else:
        return render(request, 'home_page.html')


def recipe_detail(request, recipe_id):
    # Get API key environment variable
    api_key = os.getenv('SPOONACULAR_API_KEY')
    recipe_url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey=' + api_key
    response_recipe = requests.get(recipe_url)

    similar_url = f'https://api.spoonacular.com/recipes/{recipe_id}/similar?number=4&apiKey=' + api_key
    response_similar = requests.get(similar_url)

    recipe_similar = response_similar.json()

    similar_ids = []
    for recipe in recipe_similar:
        similar_ids.append(recipe['id'])
    ids_string = ','.join(map(str, similar_ids))
    similar_recipes_url = f'https://api.spoonacular.com/recipes/informationBulk?ids={ids_string}&includeNutrition=true&apiKey=' + api_key
    response_similar_recipes = requests.get(similar_recipes_url)

    if response_recipe.status_code == 200 and response_similar.status_code == 200 and response_similar_recipes.status_code == 200:
        recipe_detail = response_recipe.json()
        similar_recipes = response_similar_recipes.json()

        desired_nutrients = ['Calories', 'Protein', 'Fat', 'Carbohydrates', 'Fiber', 'Sugar']
        selected_nutrients = [nutrient for nutrient in recipe_detail['nutrition']['nutrients'] if
                              nutrient['name'] in desired_nutrients]

        # Get recipe steps
        recipe_steps = []
        for instruction in recipe_detail['analyzedInstructions']:
            for step in instruction['steps']:
                recipe_steps.append(step)

        product_matches = recipe_detail['winePairing']['productMatches'][0]

        # Set product matches price
        product_matches_price = product_matches['price']
        product_matches_price = product_matches_price.replace('$', '')
        product_matches_price = decimal.Decimal(product_matches_price)
        product_matches_price = round(product_matches_price, 2)
        product_matches_price = str(product_matches_price) + ' $'

        context = {
            'recipe_detail': recipe_detail,
            'selected_nutrients': selected_nutrients,
            'recipe_steps': recipe_steps,
            'similar_recipes': similar_recipes,
            'product_matches': product_matches,
            'product_matches_price': product_matches_price,

        }
        return render(request, 'recipe_detail.html', context)

    else:
        return render(request, 'recipe_detail.html')
