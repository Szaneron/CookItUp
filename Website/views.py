import decimal
import json
import os

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from django.contrib import messages
from sweetify import sweetify

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
    response_popular = requests.get(popular_url)
    response_latest = requests.get(latest_url)

    if response_popular.status_code == 200 and response_latest.status_code == 200:
        popular_recipes = response_popular.json()
        latest_recipes = response_latest.json()

        return render(request, 'home_page.html',
                      {'popular_recipes': popular_recipes, 'latest_recipes': latest_recipes, })

    elif response_popular.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_popular.json()['message'],
                       button='Close', timer=4000, timerProgressBar='true')
        return render(request, 'home_page.html')

    elif response_latest.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_latest.json()['message'],
                       button='Close', timer=4000, timerProgressBar='true')
        return render(request, 'home_page.html')

    else:
        return render(request, 'home_page.html')


def recipe(request):
    # Get API key environment variable
    api_key = os.getenv('SPOONACULAR_API_KEY')
    api_question = 'initial'
    section_title = 'Popular recipes'
    search_button = None

    # Number of recipes to get from api request
    recipes_number = 12

    # ID's from random to put them into another request with nutrition
    random_ids = ['638248', '647634', '639411', '1055614', '645145', '633754', '664501', '638199', '641794', '665616']
    ids_string = ','.join(map(str, random_ids))

    recipes_url = f'https://api.spoonacular.com/recipes/informationBulk?ids={ids_string}&includeNutrition=true&apiKey=' + api_key

    if request.method == 'POST':
        if 'soup' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=soup&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Soup Recipes'
            search_button = 'soup'

        elif 'main_course' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=main course&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Main Course Recipes'
            search_button = 'main_course'

        elif 'side_dish' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=side dish&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Side Dish Recipes'
            search_button = 'side_dish'

        elif 'dessert' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=dessert&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Dessert Recipes'
            search_button = 'dessert'

        elif 'salad' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=salad&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Salad Recipes'
            search_button = 'salad'

        elif 'appetizer' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=appetizer&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Appetizer Recipes'
            search_button = 'appetizer'

        elif 'breakfast' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=breakfast&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Breakfast Recipes'
            search_button = 'breakfast'

        elif 'sauce' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=sauce&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Sauce Recipes'
            search_button = 'sauce'

        elif 'drink' in request.POST:
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&type=drink&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Drink Recipes'
            search_button = 'drink'

        elif 'search_recipe_query' in request.POST:
            search_query = request.POST['search_query']
            recipes_url = f'https://api.spoonacular.com/recipes/complexSearch?number={recipes_number}&query={search_query}&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&apiKey=' + api_key
            section_title = 'Filtered Recipes'

        return render(request, 'recipe.html',
                      {'recipes_url': recipes_url, 'section_title': section_title, 'search_button': search_button, })

    context = {
        'api_key': api_key,
        'api_question': api_question,
        'recipes_url': recipes_url,
        'section_title': section_title,
        'search_button': search_button,
    }
    return render(request, 'recipe.html', context)


def recipe_detail(request, recipe_id):
    user_profile = request.user.userprofile

    # Get API key environment variable
    api_key = os.getenv('SPOONACULAR_API_KEY')
    recipe_url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey=' + api_key
    response_recipe = requests.get(recipe_url)

    similar_url = f'https://api.spoonacular.com/recipes/{recipe_id}/similar?number=4&apiKey=' + api_key
    response_similar = requests.get(similar_url)

    if response_recipe.status_code == 200 and response_similar.status_code == 200:
        recipe_similar = response_similar.json()

        # Get similar recipes id
        similar_ids = []
        for recipe in recipe_similar:
            similar_ids.append(recipe['id'])
        ids_string = ','.join(map(str, similar_ids))
        similar_recipes_url = f'https://api.spoonacular.com/recipes/informationBulk?ids={ids_string}&includeNutrition=true&apiKey=' + api_key
        response_similar_recipes = requests.get(similar_recipes_url)

        if response_similar_recipes.status_code == 200:
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

            try:
                product_matches = recipe_detail['winePairing']['productMatches'][0]
                # Set product matches price
                product_matches_price = product_matches['price']
                product_matches_price = product_matches_price.replace('$', '')
                product_matches_price = decimal.Decimal(product_matches_price)
                product_matches_price = round(product_matches_price, 2)
                product_matches_price = str(product_matches_price) + ' $'

            except IndexError:
                product_matches = None
                product_matches_price = None

            except KeyError:
                product_matches = recipe_detail['winePairing']['productMatches'][0]
                product_matches_price = None

            if request.method == 'POST':
                if 'add_to_cart' in request.POST:
                    items_name_list = []
                    print('Adding to cart')
                    ingredients = recipe_detail['extendedIngredients']
                    for ingredient in ingredients:
                        ingredient_amount = ingredient['measures']['metric']['amount']
                        ingredient_unit = ingredient['measures']['metric']['unitLong']
                        ingredient_name = ingredient['name']

                        combined_string_item = f'{ingredient_amount} {ingredient_unit} {ingredient_name}'
                        items_name_list.append(combined_string_item)

                    add_item_success_request_count = 0
                    add_item_failed_request_messages = []

                    for item in items_name_list:
                        item_to_add = {'item': item, 'parse': True}

                        add_to_shopping_list_url = f'https://api.spoonacular.com/mealplanner/{user_profile.spoonacular_username}/shopping-list/items?hash={user_profile.spoonacular_hash}&apiKey={api_key}'
                        response_add_to_shopping_list = requests.post(add_to_shopping_list_url, json=item_to_add)

                        if response_add_to_shopping_list.status_code == 200:
                            add_item_success_request_count += 1
                        else:
                            add_item_failed_request_messages.append(
                                f"{response_add_to_shopping_list.status_code}: {response_add_to_shopping_list.text}")

                    if add_item_success_request_count == len(items_name_list):
                        sweetify.success(request, 'Success',
                                         text='The ingredients have been added to the shopping list',
                                         button='Close', timer=4000, timerProgressBar='true')
                    else:
                        sweetify.error(request, 'Request Failed',
                                       text=add_item_failed_request_messages[0],
                                       button='Close', timer=4000, timerProgressBar='true')

                context = {
                    'recipe_detail': recipe_detail,
                    'selected_nutrients': selected_nutrients,
                    'recipe_steps': recipe_steps,
                    'similar_recipes': similar_recipes,
                    'product_matches': product_matches,
                    'product_matches_price': product_matches_price,
                }
                return render(request, 'recipe_detail.html', context)

            context = {
                'recipe_detail': recipe_detail,
                'selected_nutrients': selected_nutrients,
                'recipe_steps': recipe_steps,
                'similar_recipes': similar_recipes,
                'product_matches': product_matches,
                'product_matches_price': product_matches_price,
            }

            return render(request, 'recipe_detail.html', context)

        elif response_similar_recipes.status_code == 402:
            sweetify.error(request, 'Request Failed',
                           text=response_similar_recipes.json()['message'],
                           button='Close', timer=4000, timerProgressBar='true')
            return render(request, 'recipe_detail.html')

        else:
            return render(request, 'recipe_detail.html')

    elif response_recipe.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_recipe.json()['message'],
                       button='Close', timer=4000, timerProgressBar='true')
        return render(request, 'recipe_detail.html')

    elif response_similar.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_similar.json()['message'],
                       button='Close', timer=4000, timerProgressBar='true')
        return render(request, 'recipe_detail.html')

    else:
        return render(request, 'recipe_detail.html')


def shopping_list(request):
    user_profile = request.user.userprofile

    def get_all_shopping_list_items_id():
        ids_list = []
        for _ in shopping_list['aisles']:
            for _ in _['items']:
                ids_list.append(_['id'])

        return ids_list

    def clear_shopping_list(shopping_list_ids):
        positive_status_codes_count = 0
        error_message = ''
        for _ in shopping_list_ids:
            delete_from_shopping_list_url = f'https://api.spoonacular.com/mealplanner/{user_profile.spoonacular_username}/shopping-list/items/{_}?hash={user_profile.spoonacular_hash}&apiKey={api_key}'
            response_delete_from_shopping_list = requests.delete(delete_from_shopping_list_url)

            if response_delete_from_shopping_list.status_code == 200:
                positive_status_codes_count += 1
            else:
                error_message = response_delete_from_shopping_list.json()['message']

        if positive_status_codes_count == len(shopping_list_ids):
            sweetify.success(request, 'Success',
                             text='The list has been cleared',
                             button='Close', timer=4000, timerProgressBar='true')
        else:
            sweetify.error(request, 'Request Failed',
                           text=error_message,
                           button='Close', timer=4000, timerProgressBar='true')

    # Get API key environment variable
    api_key = os.getenv('SPOONACULAR_API_KEY')
    shopping_list_url = f'https://api.spoonacular.com/mealplanner/{user_profile.spoonacular_username}/shopping-list?hash={user_profile.spoonacular_hash}&apiKey={api_key}'
    response_shopping_list = requests.get(shopping_list_url)

    if response_shopping_list.status_code == 200:
        shopping_list = response_shopping_list.json()

        shopping_list_ids = get_all_shopping_list_items_id()
        clear_shopping_list(shopping_list_ids)

    return render(request, 'shopping_list.html')
