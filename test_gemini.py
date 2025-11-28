import base64
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:20]}...")

client = genai.Client(api_key=api_key)
model = "gemini-2.0-flash-live-001"

print("\n=== Testing Gemini API with text prompt ===")
try:
    response = client.models.generate_content(
        model=model,
        contents="Say 'Hello, Gemini is working!' if you can read this.",
    )
    print(f"Response: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\n=== Checking for captured images ===")
image_paths = ["barcode_scans/food_image.jpg", "barcode_scans/captured_frame.jpg"]

for image_path in image_paths:
    if os.path.exists(image_path):
        print(f"\nFound image: {image_path}")
        print(f"Testing Gemini Vision with this image...")

        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            response = client.models.generate_content(
                model=model,
                contents=[
                    "What do you see in this image? Describe it briefly.",
                    {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(image_data).decode("utf-8"),
                    },
                ],
            )
            print(f"Gemini Vision Response:\n{response.text}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback

            traceback.print_exc()
        break
else:
    print("No captured images found to test with.")
