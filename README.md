# CookItUp

CookItUp, powered by the Spoonacular API, is a user-friendly web application designed for discovering, exploring, and organizing recipes. 
This project seamlessly integrates the art of cooking with technology, offering features such as recipe browsing, detailed dish information, suggested wine pairings, and a convenient shopping list. 
Users can easily search for recipes, add ingredients to their shopping list, and engage with the community through a contact form and newsletter subscription. 
Whether you're a seasoned chef or a home cook, CookItUp provides a practical and efficient platform for culinary exploration.

## Features

### **1. Home Page**
   
  Embark on a culinary journey from our vibrant home page, featuring:
  - **Featured Chefs:** Immerse yourself in the culinary world by getting to know the talented chefs behind our curated recipes.
  - **Browse Recipes:** Explore a diverse range of dishes carefully curated to tantalize your taste buds and spark your culinary creativity.
  - **Recent Favorites:** Discover the recipes currently making waves among our community, providing inspiration for your next meal.
  - **Latest Additions:** Stay up-to-date with the newest additions to our extensive recipe collection, ensuring you're always in the loop.
  - **Newsletter Signup:** Become a part of our ever-growing community and subscribe to our newsletter for the latest culinary updates and exclusive content.

### **2. Recipes Page**
   
  Dive deeper into the world of gastronomy with our Recipes page, offering:
  - **Recent Popular Recipes:** Uncover a curated list of the most sought-after recipes, providing a pulse on the current culinary trends.
  - **Search Bar:** Effortlessly find your desired dish with our user-friendly search functionality, making recipe exploration a breeze.
  - **Filter Options:** Refine your search using filters such as dish type, cuisine, and more, tailoring your culinary adventure to your preferences.

### **3. Recipe Details**
   
  Explore the intricate details of each recipe on its dedicated page, discovering:
  - **Dish Information:** Uncover key details such as type, preparation time, servings, and nutritional value, ensuring a comprehensive understanding.
  - **Ingredients:** Access a detailed list of ingredients required for the recipe, making your cooking experience seamless and organized.
  - **Cooking Instructions:** Follow a step-by-step guide to craft the perfect dish, empowering even novice chefs to create culinary masterpieces.
  - **Wine Pairing:** Elevate your dining experience with suggested wine pairings, enhancing the overall flavor profile of your chosen dish.
  - **Similar Recipes:** Expand your culinary repertoire by exploring related recipes, encouraging you to try new and exciting dishes.
  - **Add to Shopping List:** Streamline your grocery shopping by adding recipe ingredients to your list with a single click, ensuring a hassle-free cooking experience.

### **4. Shopping List**
   
  Efficiently manage your grocery shopping with the Shopping List page, featuring:
  - **View List:** Easily review and organize your saved shopping list, ensuring you have everything you need for your culinary creations.
  - **Clear List:** Start fresh by clearing your current shopping list, providing flexibility for your ever-changing meal plans.
  - **Download as PDF:** Conveniently download your shopping list as a PDF file, allowing for easy access and reference while on the go.

### **5. Contact Page**
   
  Connect with us seamlessly using the Contact page, boasting:
  - **Contact Form:** Engage with us directly through a simple and efficient form, making it easy to reach out with any inquiries, feedback, or suggestions.
      

## Getting Started
Follow these steps to set up Recipe Explorer on your local machine:

1. Clone the repository to your local machine.
    ```bash
    git clone https://github.com/Szaneron/CookItUp.git
    ```
    
2. Navigate to the project directory.
    ```bash
    cd CookItUp
    ```

3. Install the required dependencies using the provided requirements file.
    ```bash
    pip install -r requirements.txt
    ```

4. Create Environment Variables (.env):
    ```bash
    SECRET_KEY="Your django secret key"
    SPOONACULAR_API_KEY="Your spoonacular api key"
    ```

5. Apply migrations to set up the database.
    ```bash
    python manage.py migrate
    ```

6. Start the development server.
    ```bash
    python manage.py runserver
    ```

7. Open your browser and navigate to http://localhost:8000 to embark on your culinary journey with CookItUp!


## Requirements
- **Python 3.7+**
- **Django**~=4.2.7
- **requests**~=2.31.0
- **python-dotenv**~=1.0.0
- **reportlab**~=4.0.7
- **sweetify**~=2.3.1
- **Pillow**~=10.1.0


