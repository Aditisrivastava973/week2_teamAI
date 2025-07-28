from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import os
from dotenv import load_dotenv

# ✅ Load .env from same folder as actions.py
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# ✅ Read API key from .env
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/inference"

# ✅ Debug print to confirm key loading
if not TOGETHER_API_KEY:
    print(f"❌ TOGETHER_API_KEY not loaded from: {env_path}")
else:
    print(f"✅ TOGETHER_API_KEY loaded: {TOGETHER_API_KEY[:5]}...")

class ActionFallbackLLM(Action):
    def name(self) -> Text:
        return "action_fallback_llm"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text", "")
        prompt = f"You are a helpful cybersecurity assistant.\n\nUser: {user_message}\nAssistant:"

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1
        }

        try:
            print("📤 Sending request to Together API...")
            response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)

            print(f"📬 Response status: {response.status_code}")
            print(f"📬 Response body: {response.text}")

            output = response.json().get("output", {})
            choices = output.get("choices", [])

            if choices and isinstance(choices[0], dict) and "text" in choices[0]:
                response_text = choices[0]["text"].strip()
            else:
                response_text = "I'm sorry, I couldn't understand that. Could you please rephrase?"

            dispatcher.utter_message(text=response_text)

        except Exception as e:
            print(f"❌ Exception: {e}")
            dispatcher.utter_message(text="⚠️ Something went wrong while contacting the LLM.")

        return []


class ActionStoreIncident(Action):
    def name(self) -> Text:
        return "action_store_incident"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message['intent'].get('name')
        dispatcher.utter_message(text=f"Thanks for reporting. I've logged this as a '{intent}' incident. We'll provide guidance shortly.")
        return []

class ActionExplainLaw(Action):
    def name(self) -> Text:
        return "action_explain_law"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        law = tracker.get_slot("law_section")
        explanations = {
            "66C": "Section 66C of the IT Act deals with identity theft — using someone else’s digital signature, password or other unique identification.",
            "66D": "Section 66D covers cheating by impersonation using computer resources — like online scams.",
            "67": "Section 67 deals with publishing or transmitting obscene material in electronic form.",
        }

        explanation = explanations.get(law, "Sorry, I don't have information on that section.")
        dispatcher.utter_message(text=explanation)
        return []

class ActionCybersecurityEducation(Action):
    def name(self) -> Text:
        return "action_cybersecurity_education"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = (
            "Here are some cybersecurity tips:\n"
            "- Use strong, unique passwords for each site.\n"
            "- Enable 2FA (Two-Factor Authentication).\n"
            "- Be cautious with email links and attachments.\n"
            "- Regularly update your software and OS.\n"
            "- Backup your data frequently."
        )
        dispatcher.utter_message(text=message)
        return []

class ActionTechHelp(Action):
    def name(self) -> Text:
        return "action_tech_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic = tracker.get_slot("tech_topic")
        if topic:
            dispatcher.utter_message(text=f"Here’s some guidance on {topic}. (More detailed help is coming soon!)")
        else:
            dispatcher.utter_message(text="Can you tell me what technical topic you need help with?")
        return []
