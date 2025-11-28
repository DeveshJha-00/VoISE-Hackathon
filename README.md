# PPT : https://www.canva.com/design/DAG59pprk9Q/iiYN_L9_3ExjjyCpf_WZtQ/view?utm_content=DAG59pprk9Q&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h30874c70b8



# 🍎 KenShoku - Smart Nutrition Assistant

KenShoku is an AI-powered nutrition assistant that helps users analyze food items and receive personalized dietary recommendations based on their health profile.

## ✨ Features

- **Barcode Scanning** - Scan packaged food barcodes to instantly retrieve nutritional information from OpenFoodFacts and USDA databases
- **AI Food Recognition** - Take photos of fresh foods and let Google Gemini AI identify and analyze them
- **Personalized Analysis** - Get tailored nutritional advice based on your allergies, dietary preferences, and health goals
- **Smart Alternatives** - Receive healthier food alternatives that align with your dietary needs
- **Interactive Chat** - Ask questions and get detailed nutritional guidance from the AI assistant
- **Real-time Camera Feed** - Live video preview for capturing food images

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **AI/ML**: Google Gemini 2.0 Flash (Vision & Chat)
- **Computer Vision**: OpenCV, pyzbar
- **APIs**: USDA FoodData Central, OpenFoodFacts
- **Frontend**: HTML, CSS, JavaScript

## 📋 Prerequisites

- Python 3.8+
- Webcam (for scanning features)
- Google Gemini API Key
- USDA API Key (optional, for enhanced food data)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/kenshoku.git
   cd kenshoku
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   USDA_API_KEY=your_usda_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**

   Navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```
kenshoku/
├── app.py                 # Main Flask application
├── barcode.py             # Barcode scanning functionality
├── food_recognizer.py     # AI-powered food recognition
├── chatbot.py             # Gemini AI chatbot integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not tracked)
├── static/
│   └── styles.css         # Application styles
├── templates/
│   ├── entry.html         # User profile entry page
│   ├── scan.html          # Food scanning interface
│   ├── product.html       # Product analysis results
│   └── chat.html          # AI chat interface
└── barcode_scans/         # Temporary storage for scanned images
```

## 🔄 User Flow

1. **Enter Profile** - Input your health information (allergies, dietary preferences, goals)
2. **Scan Food** - Choose between barcode scanning or food photo mode
3. **View Analysis** - Get detailed nutritional breakdown and personalized recommendations
4. **Chat with AI** - Ask follow-up questions for deeper nutritional insights

## 🔑 API Keys

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### USDA FoodData Central API (Optional)
1. Visit [USDA FoodData Central](https://fdc.nal.usda.gov/api-key-signup.html)
2. Sign up for a free API key
3. Add it to your `.env` file as `USDA_API_KEY`

## 📝 License

This project was created for the VoISE Hackathon.

## 🤝 Contributing


Contributions are welcome! Please feel free to submit a Pull Request.
