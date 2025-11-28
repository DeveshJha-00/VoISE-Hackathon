import base64
import os

import cv2
import numpy as np
from barcode import BarcodeScanner
from food_recognizer import FoodRecognizer
from chatbot import ChatBot
from flask import Flask, Response, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

user_data = {}
scanned_data = {}
scanner = BarcodeScanner()
food_recognizer = FoodRecognizer()
chatbot = ChatBot()

SAVE_PATH = os.path.join(os.getcwd(), "barcode_scans")
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


@app.route("/")
def entry():
    return render_template("entry.html")


@app.route("/save_user_data", methods=["POST"])
def save_user_data():
    global user_data
    user_data = request.form.to_dict()
    print(f"User data saved: {user_data}")
    return redirect(url_for("scan"))


@app.route("/scan", methods=["GET", "POST"])
def scan():
    global scanned_data

    if request.method == "POST":
        try:
            if 'image' not in request.files and 'image' not in request.form:
                return jsonify({
                    "message": "No image provided. Please include 'image' in your request.",
                    "status": "failed"
                }), 400

            if 'image' in request.files:
                file = request.files['image']
                if file.filename == '':
                    return jsonify({
                        "message": "No selected file",
                        "status": "failed"
                    }), 400

                image_path = os.path.join(SAVE_PATH, "uploaded_image.jpg")
                file.save(image_path)

                product_info = scanner.scan_barcode(image_path)
                if product_info:
                    scanned_data = product_info
                    return jsonify({
                        "status": "success",
                        "product": product_info
                    }), 200
                else:
                    return jsonify({
                        "message": "No barcode found in the image",
                        "status": "failed"
                    }), 400

            elif 'image' in request.form or request.is_json:
                if request.is_json:
                    data = request.json.get("image", "")
                else:
                    data = request.form.get("image", "")

                if not data:
                    return jsonify({
                        "message": "Image data is empty",
                        "status": "failed"
                    }), 400

                if "," in data:
                    image_data = base64.b64decode(data.split(",")[1])
                else:
                    image_data = base64.b64decode(data)

                np_arr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    return jsonify({
                        "message": "Failed to decode image",
                        "status": "failed"
                    }), 400

                image_path = os.path.join(SAVE_PATH, "uploaded_image.jpg")
                cv2.imwrite(image_path, frame)

                product_info = scanner.scan_barcode(image_path)
                if product_info:
                    scanned_data = product_info
                    return jsonify({
                        "status": "success",
                        "product": product_info
                    }), 200
                else:
                    return jsonify({
                        "message": "No barcode found in the image",
                        "status": "failed"
                    }), 400

        except Exception as e:
            print(f"Error in /scan endpoint: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "message": f"Failed to process image: {str(e)}",
                "status": "failed"
            }), 500

    return render_template("scan.html")


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/capture_frame", methods=["POST"])
def capture_frame():
    global scanned_data

    try:
        if not request.json or "image" not in request.json:
            return jsonify({
                "message": "No image data provided. Expected JSON with 'image' field.",
                "status": "failed"
            }), 400

        data = request.json["image"]
        mode = request.json.get("mode", "barcode")  

        print(f"Capture mode: {mode}")

        if not data:
            return jsonify({
                "message": "Image data is empty",
                "status": "failed"
            }), 400

        if "," in data:
            image_data = base64.b64decode(data.split(",")[1])
        else:
            image_data = base64.b64decode(data)

        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({
                "message": "Failed to decode image data",
                "status": "failed"
            }), 400

        image_filename = "captured_frame.jpg" if mode == "barcode" else "food_image.jpg"
        image_path = os.path.join(SAVE_PATH, image_filename)
        cv2.imwrite(image_path, frame)
        print(f"Image saved to: {image_path}")

        if mode == "barcode":
            print("Processing in BARCODE mode...")
            product_info = scanner.scan_barcode(image_path)
            if product_info:
                scanned_data = product_info
                return jsonify({"status": "success", "product": product_info}), 200
            else:
                return jsonify({
                    "message": "No barcode found in the captured image. Try switching to 'Food Photo' mode for fresh foods.",
                    "status": "failed"
                }), 400

        elif mode == "food":
            print("Processing in FOOD RECOGNITION mode...")
            product_info = food_recognizer.recognize_food(image_path)
            if product_info:
                scanned_data = product_info
                return jsonify({"status": "success", "product": product_info}), 200
            else:
                return jsonify({
                    "message": "Could not identify the food item. Please ensure the food is clearly visible and well-lit.",
                    "status": "failed"
                }), 400

        else:
            return jsonify({
                "message": f"Invalid mode: {mode}. Expected 'barcode' or 'food'.",
                "status": "failed"
            }), 400

    except Exception as e:
        print(f"Error in /capture_frame: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "message": f"Failed to process image: {str(e)}",
            "status": "failed"
        }), 500


@app.route("/product")
def product():
    ai_summary = None
    ai_alternatives = None
    enhanced_ingredients = None
    enhanced_allergens = None
    enhanced_calories = None

    if scanned_data and user_data:
        try:
            summary_prompt = f"""Based on this person's profile and the food item, provide a brief personalized analysis (max 100 words):
- Is this food good for their health goals?
- Any concerns based on their allergies or dietary preferences?
- Brief recommendation.

Use **bold** for important nutrients, allergens, or food names. Keep it friendly and concise."""
            ai_summary = chatbot.get_response(user_data, scanned_data, summary_prompt)
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            ai_summary = None

        try:
            alternatives_prompt = f"""Based on the scanned food and user's profile, suggest alternatives (max 120 words):

If the food is already healthy for their goals: Start with "This food is good enough, no alternatives needed. But if you want variety, try:" then list 2-3 similar healthy options.

If the food is unhealthy or doesn't align with their goals: Suggest 3-4 better alternatives that match their dietary preferences and health goals.

Format with **bold** food names and brief explanation why each alternative is better."""
            ai_alternatives = chatbot.get_response(user_data, scanned_data, alternatives_prompt)
        except Exception as e:
            print(f"Error generating alternatives: {e}")
            ai_alternatives = None

        try:
            ingredients_prompt = f"""Provide detailed information about the key ingredients in this food (max 100 words):
- List main ingredients with **bold** names
- Brief health benefits or concerns for each
- Note any processing or additives if applicable

Format with bullet points."""
            enhanced_ingredients = chatbot.get_response({}, scanned_data, ingredients_prompt)
        except Exception as e:
            print(f"Error generating ingredients: {e}")
            enhanced_ingredients = scanned_data.get('important_ingredients', 'Not specified')

        try:
            allergens_prompt = f"""Provide comprehensive allergen information for this food (max 80 words):
- List all potential allergens with **bold** names
- Include common cross-contamination risks
- Note hidden allergens in processing

If no allergens: Say "No major allergens detected, but always check labels for cross-contamination" """
            enhanced_allergens = chatbot.get_response({}, scanned_data, allergens_prompt)
        except Exception as e:
            print(f"Error generating allergens: {e}")
            enhanced_allergens = scanned_data.get('allergens', 'None listed')

        try:
            calories_prompt = f"""Provide detailed calorie and macronutrient breakdown (max 100 words):
- Total calories per serving with **bold** number
- Breakdown: **Protein**, **Carbs**, **Fats** with amounts
- Compare to daily recommended intake
- Note if high/low in any macronutrient

Format clearly with bullet points."""
            enhanced_calories = chatbot.get_response({}, scanned_data, calories_prompt)
        except Exception as e:
            print(f"Error generating calories: {e}")
            enhanced_calories = f"{scanned_data.get('calories', 'Not specified')} kcal per 100g"

    return render_template("product.html", product=scanned_data, user=user_data,
                         ai_summary=ai_summary, ai_alternatives=ai_alternatives,
                         enhanced_ingredients=enhanced_ingredients,
                         enhanced_allergens=enhanced_allergens,
                         enhanced_calories=enhanced_calories)


@app.route("/get_captured_image")
def get_captured_image():
    """Serve the captured/uploaded image"""
    try:
        image_files = ["food_image.jpg", "captured_frame.jpg", "uploaded_image.jpg"]

        for img_file in image_files:
            image_path = os.path.join(SAVE_PATH, img_file)
            if os.path.exists(image_path):
                from flask import send_file
                return send_file(image_path, mimetype='image/jpeg')

        return "No image found", 404
    except Exception as e:
        print(f"Error serving image: {e}")
        return "Error loading image", 500


@app.route("/chat")
def chat():
    return render_template("chat.html", user=user_data, product=scanned_data)


@app.route("/ask_chatgpt", methods=["POST"])
def ask_chatgpt():
    user_question = request.form["question"]
    personal_info = user_data
    product_info = scanned_data

    print(f"\n=== CHAT REQUEST ===")
    print(f"User question: {user_question}")
    print(f"Personal info: {personal_info}")
    print(f"Product info: {product_info}")
    print(f"===================\n")

    response = chatbot.get_response(personal_info, product_info, user_question)

    return jsonify({"answer": response})


if __name__ == "__main__":
    app.run(debug=True)
