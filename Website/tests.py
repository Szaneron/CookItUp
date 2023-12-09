from io import BytesIO

from django.test import TestCase, Client
from django.contrib.auth.models import User

from django.urls import reverse
from .models import UserProfile
from .views import generate_shopping_list_pdf, generate_recipe_pdf
import unittest
from unittest.mock import MagicMock, patch, mock_open
from django.http import HttpResponse


class RecipeDetailTests(TestCase):
    def setUp(self):
        # Create a test user and user profile
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user, spoonacular_username='testuser',
                                                       spoonacular_hash='testhash')

    def test_recipe_detail_view_success(self):
        # Create a client to simulate requests
        client = Client()

        # Log in the user
        client.login(username='testuser', password='testpassword')

        # Make a GET request to the recipe_detail view with a valid recipe_id
        recipe_id = 638248  # Valid recipe ID
        response = client.get(f'/recipe/{recipe_id}/')

        # Check if the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)

        # Check if the necessary context variables are present in the response
        self.assertIn('recipe_detail', response.context)
        self.assertIn('selected_nutrients', response.context)
        self.assertIn('recipe_steps', response.context)
        self.assertIn('similar_recipes', response.context)
        self.assertIn('product_matches', response.context)
        self.assertIn('product_matches_price', response.context)

    def test_recipe_detail_view_failure(self):
        # Create a client to simulate requests
        client = Client()

        # Log in the user
        client.login(username='testuser', password='testpassword')

        # Make a GET request to the recipe_detail view with an invalid recipe_id
        recipe_id = 'zxc'  # Invalid recipe ID
        response = client.get(f'/recipe/{recipe_id}/')

        # Check if the response is not successful (status code 200)
        self.assertNotEqual(response.status_code, 200)

        # Check if the necessary context variables are not present in the response
        self.assertNotIn('recipe_detail', response.context)
        self.assertNotIn('selected_nutrients', response.context)
        self.assertNotIn('recipe_steps', response.context)
        self.assertNotIn('similar_recipes', response.context)
        self.assertNotIn('product_matches', response.context)
        self.assertNotIn('product_matches_price', response.context)


class ShoppingListViewTests(TestCase):
    def setUp(self):
        # Create a test user and login
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_shopping_list_view_get(self):
        # Test GET request to the shopping_list view
        response = self.client.get('/shopping_list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopping_list.html')

    def test_shopping_list_view_post_delete_item(self):
        # Test POST request to delete an item from the shopping list
        item_id = '12412'
        response = self.client.post('/shopping_list/', {'delete_item': True, 'item_id': item_id})
        self.assertEqual(response.status_code, 200)

    def test_shopping_list_view_post_download_pdf(self):
        # Test POST request to download PDF
        response = self.client.post('/shopping_list/', {'download_pdf': True})
        self.assertEqual(response.status_code, 200)

    def test_shopping_list_view_post_clear_shopping_list(self):
        # Test POST request to clear the shopping list
        response = self.client.post('/shopping_list/', {'clear_shopping_list': True})
        self.assertEqual(response.status_code, 200)


class TestGenerateShoppingListPDF(unittest.TestCase):
    def test_generate_shopping_list_pdf(self):
        # Mock the shopping list data
        shopping_list = [
            {
                'aisle': 'Produce',
                'items': [
                    {'name': 'Carrot', 'measures': {'metric': {'amount': 2, 'unit': 'kg'}}},
                    {'name': 'Tomato', 'measures': {'metric': {'amount': 3, 'unit': 'units'}}}
                ]
            },
            {
                'aisle': 'Dairy',
                'items': [
                    {'name': 'Milk', 'measures': {'metric': {'amount': 1, 'unit': 'L'}}},
                    {'name': 'Cheese', 'measures': {'metric': {'amount': 200, 'unit': 'g'}}}
                ]
            }
        ]

        # Mock HttpResponse
        response_mock = HttpResponse()

        # Mock the SimpleDocTemplate
        doc_mock = MagicMock()

        # Mock the Buffer
        buffer_mock = MagicMock()
        buffer_mock.getvalue.return_value = b'PDF Content'

        # Patch the necessary modules and classes
        with unittest.mock.patch('Website.views.SimpleDocTemplate', return_value=doc_mock):
            with unittest.mock.patch('Website.views.BytesIO', return_value=buffer_mock):
                with unittest.mock.patch('Website.views.PageNumCanvas'):
                    with unittest.mock.patch('Website.views.HttpResponse',
                                             return_value=response_mock):
                        # Call the function
                        result = generate_shopping_list_pdf(shopping_list)

        # Check if HttpResponse is returned
        self.assertEqual(result, response_mock)

        # Check if the HttpResponse content is set correctly
        self.assertEqual(response_mock.content, b'PDF Content')

        # Check if the necessary methods are called
        buffer_mock.close.assert_called_once()

        # Check if the 'Content-Disposition' header is set
        self.assertIn('Content-Disposition', response_mock)
        self.assertEqual(response_mock['Content-Disposition'], 'attachment; filename="CookItUp_shopping_list.pdf"')


if __name__ == '__main__':
    unittest.main()
