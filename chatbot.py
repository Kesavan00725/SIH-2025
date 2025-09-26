import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

USERS_FILE = "data/users.json"
INTERNSHIP_FILE = "data/internships.json"

# Load internships
with open(INTERNSHIP_FILE, "r") as f:
    internships = json.load(f)

# Load and save users
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Validate phone
def verify_phone(phone):
    return re.match(r"^[6-9]\d{9}$", phone) is not None

# OpenAI wrapper
def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You are a friendly AI chatbot helping students find internships in India."},
            {"role":"user","content":prompt}
        ]
    )
    return response.choices[0].message.content

# Chatbot main
def chatbot():
    print("🤖 Internship Finder Chatbot\n")

    # Name
    name = input("👤 Enter your name: ").strip().capitalize()
    while not name.isalpha():
        name = input("❌ Invalid name. Enter alphabets only: ").strip().capitalize()

    # Phone
    phone = input("📱 Enter your 10-digit phone number: ").strip()
    while not verify_phone(phone):
        phone = input("❌ Please enter a valid 10-digit phone number starting with 6–9: ").strip()

    # Load users
    users = load_users()
    existing_user = next((u for u in users if u["phone"] == phone), None)
    if existing_user:
        print(f"✅ Welcome back, {existing_user['name']}!")
        user = existing_user
    else:
        user = {"name": name, "phone": phone, "skills": [], "location": ""}
        users.append(user)

    # Skills
    skills_input = input("💡 Enter your skills (comma separated): ")
    user["skills"] = [s.strip().capitalize() for s in skills_input.split(",")]

    # Location
    location = input("📍 Preferred internship location: ").strip().capitalize()
    user["location"] = location

    save_users(users)

    # Match internships
    matched = []
    for i in internships:
        if (user["location"].lower() in i["location"].lower()) or (
            any(skill.lower() in [s.lower() for s in i["skills"]] for skill in user["skills"])
        ):
            matched.append(i)

    # Show matches
    if matched:
        result_text = "Based on your profile, these internships are available:\n\n"
        for idx, i in enumerate(matched, 1):
            result_text += f"{idx}. {i['title']} at {i['company']} ({i['location']})\n   🔗 Apply: {i['link']}\n\n"
    else:
        result_text = "⚠️ Sorry, no internships found matching your skills/location."

    bot_reply = ask_gpt(f"User: {user}\nResults:\n{result_text}\nRespond politely and concisely.")
    print("\n🤖 " + bot_reply)

# Run
if __name__ == "__main__":
    chatbot()
