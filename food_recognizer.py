import base64
import os

import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class FoodRecognizer:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"  
        
        self.usda_api_key = os.getenv(
            "USDA_API_KEY", "DEMO_KEY"
        )  
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1"

    def recognize_food(self, image_path):
        print(f"Recognizing food from image: {image_path}")

        food_items = self.identify_food_with_gemini(image_path)

        if not food_items:
            print("No food items identified")
            return None

        print(f"Identified food items: {food_items}")

        nutrition_data = self.get_nutrition_from_usda(food_items)

        return nutrition_data

    def identify_food_with_gemini(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            prompt = """Analyze this food image and provide:
1. The name of the food item(s) you see
2. Estimated portion size or quantity (in grams if possible)
3. If multiple items, list each separately

Format your response as:
Food: [food name]
Quantity: [estimated amount in grams]

If you see multiple items, separate each with a newline.
Be specific (e.g., "grilled chicken breast" not just "chicken").
"""

            print("Sending image to Groq Vision API...")

            base64_image = base64.b64encode(image_data).decode('utf-8')

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.4,
                max_tokens=500,
            )

            gemini_response = response.choices[0].message.content
            print(f"Groq Vision Response:\n{gemini_response}")

            food_items = self.parse_gemini_response(gemini_response)

            return food_items

        except Exception as e:
            print(f"Error in Groq Vision recognition: {e}")
            import traceback

            traceback.print_exc()
            return None

    def parse_gemini_response(self, response_text):
        try:
            lines = response_text.strip().split("\n")
            food_name = ""
            quantity = ""
            found_first = False

            for line in lines:
                line = line.strip()
                if line.startswith("Food:"):
                    if not found_first:
                        food_name = line.replace("Food:", "").strip()
                        found_first = True
                elif line.startswith("Quantity:") and found_first and not quantity:
                    quantity = line.replace("Quantity:", "").strip()
                    break  

            if food_name:
                print(f"Parsed main food: {food_name} ({quantity})")
                return {
                    "name": food_name,
                    "quantity": quantity,
                    "raw_response": response_text,
                }

            print("Could not parse structured response, using entire text")
            return {
                "name": response_text.strip(),
                "quantity": "Unknown",
                "raw_response": response_text,
            }

        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return None

    def get_nutrition_from_usda(self, food_items):
        try:
            food_name = food_items["name"]
            quantity = food_items["quantity"]

            print(f"Searching USDA database for: {food_name}")

            search_url = f"{self.usda_base_url}/foods/search"
            params = {
                "api_key": self.usda_api_key,
                "query": food_name,
                "pageSize": 1,
                "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"],
            }

            response = requests.get(search_url, params=params, timeout=10)
            print(f"USDA API Response Status: {response.status_code}")

            if response.status_code != 200:
                print(f"USDA API Error: {response.text}")
                return self.create_fallback_response(food_name, quantity)

            data = response.json()

            if not data.get("foods") or len(data["foods"]) == 0:
                print("No matching food found in USDA database")
                return self.create_fallback_response(food_name, quantity)

            food = data["foods"][0]

            nutrients = {}
            for nutrient in food.get("foodNutrients", []):
                nutrient_name = nutrient.get("nutrientName", "")
                nutrient_value = nutrient.get("value", "Not specified")
                nutrients[nutrient_name] = nutrient_value

            product_info = {
                "product_name": food.get("description", food_name),
                "image_url": "",  
                "description": f"{food_name} - {quantity}",
                "expiration_date": "Not applicable (fresh food)",
                "calories": nutrients.get("Energy", "Not specified"),
                "allergens": "Please check ingredients - common allergens may include dairy, nuts, soy, gluten",
                "important_ingredients": food_name,
                "dietary": self.determine_dietary_type(food_name),
                "ingredients": food_name,
                "protein": nutrients.get("Protein", "Not specified"),
                "carbs": nutrients.get("Carbohydrate, by difference", "Not specified"),
                "fat": nutrients.get("Total lipid (fat)", "Not specified"),
                "fiber": nutrients.get("Fiber, total dietary", "Not specified"),
                "sugar": nutrients.get("Sugars, total including NLEA", "Not specified"),
                "sodium": nutrients.get("Sodium, Na", "Not specified"),
                "quantity": quantity,
                "source": "USDA FoodData Central",
                "gemini_raw_response": food_items.get("raw_response", ""),
            }

            print(
                f"Successfully retrieved nutrition data for: {product_info['product_name']}"
            )
            return product_info

        except Exception as e:
            print(f"Error fetching USDA data: {e}")
            import traceback

            traceback.print_exc()
            return self.create_fallback_response(
                food_items["name"], food_items["quantity"]
            )

    def determine_dietary_type(self, food_name):
        food_lower = food_name.lower()

        meat_keywords = [
            "chicken",
            "beef",
            "pork",
            "fish",
            "meat",
            "lamb",
            "turkey",
            "bacon",
            "ham",
        ]
        dairy_keywords = ["cheese", "milk", "yogurt", "butter", "cream"]

        is_meat = any(keyword in food_lower for keyword in meat_keywords)
        is_dairy = any(keyword in food_lower for keyword in dairy_keywords)

        if is_meat:
            return "Non-Vegetarian"
        elif is_dairy:
            return "Vegetarian"
        else:
            return "Likely Vegan (please verify ingredients)"

    def create_fallback_response(self, food_name, quantity):
        return {
            "product_name": food_name,
            "image_url": "",
            "description": f"{food_name} - {quantity}",
            "expiration_date": "Not applicable",
            "calories": "Not available - please consult a nutrition database",
            "allergens": "Unable to determine - please verify based on ingredients",
            "important_ingredients": food_name,
            "dietary": self.determine_dietary_type(food_name),
            "ingredients": food_name,
            "protein": "Not specified",
            "carbs": "Not specified",
            "fat": "Not specified",
            "quantity": quantity,
            "source": "AI Recognition (nutrition data unavailable)",
            "note": "Nutritional information could not be retrieved. Please consult a nutrition database for accurate values.",
        }
