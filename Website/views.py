import decimal
import os
from io import BytesIO

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from sweetify import sweetify

from .forms import CustomUserCreationForm
from .models import UserProfile
from PIL import Image

load_dotenv()


class PageNumCanvas(canvas.Canvas):
    """
    A class that handles page numbering.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_y = 0
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page_num, page in enumerate(self.pages, start=1):
            self.__dict__.update(page)
            self.draw_page_number(page_num, num_pages)
            super().showPage()

        super().save()

    def draw_page_number(self, page_num, total_pages):
        page_text = f"Strona {page_num}/{total_pages}"
        text_width = self.stringWidth(page_text, 'monteserrat_regular', 10)
        self.setFont('monteserrat_regular', 10)
        self.drawRightString(587 - text_width, 50, page_text)  # Adjusted coordinates

    def set_y(self, y):
        self.current_y = y

    def get_y(self):
        return self.current_y


def generate_shopping_list_pdf(shopping_list):
    # Register fonts
    pdfmetrics.registerFont(TTFont('monteserrat_regular', 'Website/static/fonts/Montserrat_Regular_400.ttf'))
    pdfmetrics.registerFont(TTFont('monteserrat_bold', 'Website/static/fonts/Montserrat_SemiBold_600.ttf'))

    # Define data and headers
    data = [['', 'Name', 'Amount', 'Unit']]
    lp = 1
    for aisle in shopping_list:
        for item in aisle['items']:
            data.append(
                [str(lp), item['name'], item['measures']['metric']['amount'], item['measures']['metric']['unit']])
            lp += 1

    left_margin = 75
    right_margin = 75

    # Calculate the page width minus margins
    usable_width = A4[0] - (left_margin + right_margin)

    # Proportionally divide width for columns
    num_columns = 4
    col_widths = [usable_width / num_columns] * num_columns

    # Assign width for first and second column
    col_widths[0] = col_widths[0] * 0.35
    col_widths[1] = col_widths[1] * 2

    # Style settings
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'monteserrat_bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Style for data
    style_data = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'monteserrat_regular'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])

    # Create a table
    stock_table = Table(data, colWidths=col_widths)
    stock_table.setStyle(style)
    stock_table.setStyle(style_data)

    # Add a style for the title
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Heading2'],
        fontName='monteserrat_bold',
        fontSize=14,
        alignment=TA_LEFT,
    )

    # Add a style for the platform
    style_platform = ParagraphStyle(
        'CustomPlatform',
        parent=getSampleStyleSheet()['Heading1'],
        fontName='monteserrat_bold',
        fontSize=20,
        alignment=TA_LEFT,
        textColor=HexColor('#247158'),
    )

    platform = Paragraph("CookItUp", style_platform)
    title = Paragraph("Your Shopping List", style_title)

    # Create content
    content = [platform, title, Spacer(1, 10), stock_table, Spacer(1, 10)]

    # Create PDF file in memory
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50, leftMargin=50, rightMargin=50)
    doc.title = "CookItUp_shopping_list"
    doc.build(content, canvasmaker=PageNumCanvas)

    # Set appropriate headers for automatic downloading
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="CookItUp_shopping_list.pdf"'

    # Save the contents of the response buffer
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def generate_recipe_pdf(recipe_detail):
    # Register fonts
    pdfmetrics.registerFont(TTFont('monteserrat_regular', 'Website/static/fonts/Montserrat_Regular_400.ttf'))
    pdfmetrics.registerFont(TTFont('monteserrat_medium', 'Website/static/fonts/Montserrat_Medium_500.ttf'))
    pdfmetrics.registerFont(TTFont('monteserrat_bold', 'Website/static/fonts/Montserrat_SemiBold_600.ttf'))

    title = recipe_detail['title']
    image_url = recipe_detail['image']

    # Download the image from the given URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    new_img_size = (250, 150)  # New image size (width, height)
    img = img.resize(new_img_size)

    # Create PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f"attachment; filename=CookItUp_recipe_{recipe_detail['id']}.pdf"

    # Create PDF object
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Add title
    pdf.setFont("monteserrat_bold", 20)

    title_x = 50
    title_y = 780
    max_title_width = 500

    text_object = pdf.beginText(title_x, title_y)
    text_object.setFont("monteserrat_bold", 20)
    pdf.setFillColor(HexColor("#247158"))

    words = title.split()
    line = ''
    lines = []

    for word in words:
        if pdf.stringWidth(line + word, "monteserrat_bold", 20) < max_title_width:
            line += word + ' '
        else:
            lines.append(line)
            line = word + ' '

    lines.append(line)  # Add last line

    # Count the number of lines and adjust the text position
    num_lines = len(lines)
    line_height = 18
    context_strat = 600 - (num_lines - 1) * line_height

    for line in lines:
        text_object.textLine(line)

    pdf.drawText(text_object)
    pdf.setFillColor(colors.black)

    # Add an image
    pdf.drawInlineImage(img, 50, context_strat)
    end_image = context_strat

    # Add a table with ingredients
    table1_col1_x = 320  # Initial X position for column 1
    table1_col2_x = 400  # Initial X position for column 2
    table1_row_y = context_strat + 140  # Initial Y position

    start_table = context_strat + 140
    end_table = 720

    # Table headers
    pdf.setFont("monteserrat_medium", 15)
    pdf.setFillColor(HexColor("#247158"))
    pdf.drawString(320, start_table, 'Ingredients')
    pdf.setFont("monteserrat_regular", 12)
    pdf.setFillColor(colors.black)
    table1_row_y -= 20  # Line feed

    ingredients_data = []

    # Get ingredient data
    for ingredient in recipe_detail['extendedIngredients']:
        name = ingredient['name']
        amount = round(ingredient['measures']['metric']['amount'], 1)
        unit = ingredient['measures']['metric']['unitShort']

        data = {'name': name, 'amount': amount, 'unit': unit}
        ingredients_data.append(data)

    pdf_width = 595  # width of an A4 page in points

    # Add data with ingredients
    for ingredient in ingredients_data:
        # pdf.drawString(table1_col1_x, table1_row_y,
        #                str(f"{ingredient['amount']} {ingredient['unit']}"))
        # pdf.drawString(table1_col2_x, table1_row_y, ingredient['name'])
        # table1_row_y -= 15  # Przesunięcie wiersza
        # end_table -= 15

        amount_unit_text = f"{ingredient['amount']} {ingredient['unit']}"
        name_text = ingredient['name']

        # Add the value for column 1
        pdf.drawString(table1_col1_x, table1_row_y, str(amount_unit_text))

        # Check the length of the component name
        if pdf.stringWidth(name_text, 'monteserrat_regular', 12) > (pdf_width - table1_col2_x - 50):
            # Split the component name into parts that will fit on one line
            lines = []
            line = ""
            for word in name_text.split():
                if pdf.stringWidth(line + word, 'monteserrat_regular', 12) <= (pdf_width - table1_col2_x - 50):
                    line += word + " "
                else:
                    lines.append(line.rstrip())
                    line = word + " "
            lines.append(line.rstrip())

            # Reverse the order of lines before adding to PDF
            lines.reverse()

            # Add additional lines for the remaining parts of the component name
            for line in lines[1:]:
                pdf.drawString(table1_col2_x, table1_row_y, line)
                table1_row_y -= 15
                end_table -= 15

            # Set the component name as the first line
            name_text = lines[0]

        # Add the value for column 2
        pdf.drawString(table1_col2_x, table1_row_y, name_text)

        # Line feed
        table1_row_y -= 15
        end_table -= 15

    if end_image < end_table:
        end_table = end_image
    else:
        end_table = end_table + 15

    # Add a title for the step list
    pdf.setFont("monteserrat_medium", 15)
    pdf.setFillColor(HexColor("#247158"))
    pdf.drawString(50, end_table - 30, 'Recipe Steps')
    pdf.setFont("monteserrat_regular", 12)
    pdf.setFillColor(colors.black)

    current_y = end_table - 40
    max_width = 500  # Maximum text width
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=normal_style,
        fontName='monteserrat_regular',
        fontSize=12,
        leading=15,  # The value of the vertical spacing between lines
    )

    for step in recipe_detail['analyzedInstructions'][0]['steps']:
        step_text = f"{step['step']}"
        formatted_text = Paragraph(step_text, custom_style)
        width, height = formatted_text.wrap(max_width, pdf.pagesize[1])

        # Check if the text extends beyond the bottom margin
        if current_y - height < 50:
            pdf.showPage()  # Add a new page
            current_y = pdf.pagesize[1] - 50  # Reset current_y to the top of the new page

        formatted_text.drawOn(pdf, 50, current_y - height)
        current_y -= height + 10  # Line feed

    # Finish generating the PDF file
    pdf.showPage()
    pdf.save()

    # Retrieve the content of the PDF file from the buffer and return it as a response
    pdf_content = buffer.getvalue()
    buffer.close()
    response.write(pdf_content)

    return response


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

        if request.method == 'POST':
            if 'email-notification' in request.POST:
                sweetify.success(request, 'Success',
                                 text='Subscribed to the newsletter.',
                                 button='Close', timer=2000, timerProgressBar='true')
                return redirect(request.META['HTTP_REFERER'])

        return render(request, 'home_page.html',
                      {'popular_recipes': popular_recipes, 'latest_recipes': latest_recipes, })

    elif response_popular.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_popular.json()['message'],
                       button='Close')
        return render(request, 'home_page.html')

    elif response_latest.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_latest.json()['message'],
                       button='Close')
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


@login_required(login_url='/login')
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
                                       button='Close')

                if 'download_recipe' in request.POST:
                    if recipe_detail:
                        return_pdf_response = generate_recipe_pdf(recipe_detail)
                        return return_pdf_response
                    else:
                        sweetify.warning(request, 'Warning',
                                         text='No recipe inforamtion!',
                                         button='Close')
                        return redirect(request.META['HTTP_REFERER'])

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
                           button='Close')
            return render(request, 'recipe_detail.html')

        else:
            return render(request, 'recipe_detail.html')

    elif response_recipe.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_recipe.json()['message'],
                       button='Close')
        return render(request, 'recipe_detail.html')

    elif response_similar.status_code == 402:
        sweetify.error(request, 'Request Failed',
                       text=response_similar.json()['message'],
                       button='Close')
        return render(request, 'recipe_detail.html')

    else:
        return render(request, 'recipe_detail.html')


@login_required(login_url='/login')
def shopping_list(request):
    user_profile = request.user.userprofile

    def get_all_shopping_list_items_id(shopping_list):
        ids_list = []
        for _ in shopping_list:
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
                           button='Close')

    # Get API key environment variable
    api_key = os.getenv('SPOONACULAR_API_KEY')
    shopping_list_url = f'https://api.spoonacular.com/mealplanner/{user_profile.spoonacular_username}/shopping-list?hash={user_profile.spoonacular_hash}&apiKey={api_key}'
    response_shopping_list = requests.get(shopping_list_url)

    if response_shopping_list.status_code == 200:
        shopping_list = response_shopping_list.json()
        shopping_list = shopping_list['aisles']

        if request.method == 'POST':
            if 'delete_item' in request.POST:
                item_id = request.POST.get('item_id')
                print(item_id)
                delete_from_shopping_list_url = f'https://api.spoonacular.com/mealplanner/{user_profile.spoonacular_username}/shopping-list/items/{item_id}?hash={user_profile.spoonacular_hash}&apiKey={api_key}'
                response_delete_from_shopping_list = requests.delete(delete_from_shopping_list_url)
                print(response_delete_from_shopping_list)
                if response_delete_from_shopping_list.status_code == 200:
                    sweetify.success(request, 'Success',
                                     text='The item has been removed from your shopping list.',
                                     button='Close', timer=2000, timerProgressBar='true')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    sweetify.error(request, 'Request Failed',
                                   text=response_delete_from_shopping_list.json()['message'],
                                   button='Close')
                    return redirect(request.META['HTTP_REFERER'])

            if 'download_pdf' in request.POST:
                if shopping_list:
                    return_pdf_response = generate_shopping_list_pdf(shopping_list)
                    return return_pdf_response
                else:
                    sweetify.warning(request, 'Warning',
                                     text='Your shopping list is empty',
                                     button='Close')
                    return redirect(request.META['HTTP_REFERER'])

            if 'clear_shopping_list' in request.POST:
                if shopping_list:
                    print(shopping_list)
                    shopping_list_ids = get_all_shopping_list_items_id(shopping_list)
                    clear_shopping_list(shopping_list_ids)
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    sweetify.warning(request, 'Warning',
                                     text='Your shopping list is empty',
                                     button='Close')
                    return redirect(request.META['HTTP_REFERER'])
        context = {
            'user_profile': user_profile,
            'api_key': api_key,
            'shopping_list': shopping_list,
        }

        return render(request, 'shopping_list.html', context)

    sweetify.error(request, 'Request Failed',
                   text=response_shopping_list.json()['message'],
                   button='Close')

    return render(request, 'shopping_list.html')


def contact(request):
    if request.method == 'POST':
        if 'send_message' in request.POST:
            sweetify.success(request, 'Success',
                             text='Message was sent.',
                             button='Close', timer=2000, timerProgressBar='true')
            return redirect(request.META['HTTP_REFERER'])

    return render(request, 'contact.html')


def statute(request):
    return render(request, 'statute.html')


def features(request):
    return render(request, 'features.html')
