import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class ChatBot:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = "llama-3.3-70b-versatile"
        self.client = Groq(api_key=self.api_key)

    def get_response(self, personal_info, product_info, user_question):
        try:
            print(f"ChatBot received:")
            print(f"  Personal info: {personal_info}")
            print(f"  Product info: {product_info}")
            print(f"  Question: {user_question}")

            system_context = (
                "You are a helpful nutritional assistant that provides personalized recommendations "
                "about food items based on personal information and user queries. "
                "Keep responses concise (around 150 words). "
                "Use markdown formatting: **bold** for important terms (nutrients, food names, allergens), "
                "bullet points (-) for lists, and clear structure. "
                "Never provide any links to images. "
                "You are KenShoku AI.\n\n"
            )

            personal_context = ""
            if personal_info and any(personal_info.values()):
                personal_context = "Personal Information:\n"
                if personal_info.get('name'):
                    personal_context += f"- Name: {personal_info.get('name')}\n"
                if personal_info.get('age'):
                    personal_context += f"- Age: {personal_info.get('age')}\n"
                if personal_info.get('gender'):
                    personal_context += f"- Gender: {personal_info.get('gender')}\n"
                if personal_info.get('goals'):
                    personal_context += f"- Nutritional Goals: {personal_info.get('goals')}\n"
                if personal_info.get('allergens'):
                    personal_context += f"- Allergies: {personal_info.get('allergens')}\n"
                if personal_info.get('dietary'):
                    personal_context += f"- Dietary preference: {personal_info.get('dietary')}\n"
                personal_context += "\n"

            product_context = ""
            if product_info and any(product_info.values()):
                product_context = "Food Item Information:\n"
                if product_info.get('product_name'):
                    product_context += f"- Food: {product_info.get('product_name')}\n"
                if product_info.get('quantity'):
                    product_context += f"- Quantity: {product_info.get('quantity')}\n"
                if product_info.get('calories'):
                    product_context += f"- Calories: {product_info.get('calories')}\n"
                if product_info.get('allergens'):
                    product_context += f"- Allergens: {product_info.get('allergens')}\n"
                if product_info.get('dietary'):
                    product_context += f"- Dietary type: {product_info.get('dietary')}\n"
                product_context += "\n"

            user_query = f"User Question: {user_question}\n"

            full_prompt = system_context + personal_context + product_context + user_query

            print(f"Full prompt sent to Groq:\n{full_prompt}\n")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": personal_context + product_context + user_query}
                ],
                temperature=0.7,
                max_tokens=250,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"ChatBot error: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"


chatbot = ChatBot()
