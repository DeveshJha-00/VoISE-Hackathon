import cv2
from pyzbar.pyzbar import decode
import requests

class BarcodeScanner:
    def scan_barcode(self, image_path):
        barcode_data = self.decode_barcode(image_path)
        if barcode_data:
            return self.fetch_nutritional_data(barcode_data)
        return None

    def decode_barcode(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not read image at {image_path}")
            return None

        barcodes = decode(img)
        print(f"Found {len(barcodes)} barcode(s) in the image")

        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            print(f"Decoded barcode: {barcode_data}")
            return barcode_data

        print("No barcode detected in the image")
        return None

    def fetch_nutritional_data(self, barcode):
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        print(f"Fetching nutritional data for barcode: {barcode}")
        print(f"API URL: {url}")

        try:
            response = requests.get(url, timeout=10)
            print(f"API Response Status: {response.status_code}")

            if response.status_code == 200:
                json_response = response.json()
                print(f"API Response: {json_response.get('status_verbose', 'No status')}")

                data = json_response.get('product', {})
                if not data:
                    print("Warning: Product data is empty")
                    return {}

                important_ingredients = [ingredient['text'] for ingredient in data.get('ingredients', []) if ingredient.get('percent_estimate', 0) > 5]
                allergens = data.get('allergens_tags', ['None listed'])
                dietary = 'Vegan' if 'en:vegan' in data.get('labels_tags', []) else 'Vegetarian' if 'en:vegetarian' in data.get('labels_tags', []) else 'Non-Vegetarian'

                product_info = {
                    'product_name': data.get('product_name', 'Unknown Product'),
                    'image_url': data.get('image_url', ''),
                    'description': data.get('generic_name', 'No description available'),
                    'expiration_date': data.get('expiration_date', 'Not specified'),
                    'calories': data.get('nutriments', {}).get('energy-kcal_100g', 'Not specified'),
                    'allergens': ', '.join(allergens),
                    'important_ingredients': ', '.join(important_ingredients),
                    'dietary': dietary,
                    'ingredients': ', '.join(important_ingredients)                  }
                print(f"Product found: {product_info['product_name']}")
                return product_info
            else:
                print(f"API request failed with status code: {response.status_code}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching nutritional data: {e}")
            return {}
