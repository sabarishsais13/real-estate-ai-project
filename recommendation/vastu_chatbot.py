import json
import os
from rapidfuzz import process

# -------------------------------
# LOAD DATA
# -------------------------------
try:
    # Get absolute path to vastu_data.json
    json_path = os.path.join(os.path.dirname(__file__), "vastu_data.json")
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
except Exception as e:
    print("Error loading JSON file:", e)
    exit()

# Extract all questions
questions = [item["question"].lower().strip() for item in data]


# -------------------------------
# FUNCTION TO GET ANSWER
# -------------------------------
def get_answer(user_input):
    user_input = user_input.lower().strip()

    # Find best match using fuzzy matching
    match, score, index = process.extractOne(user_input, questions)

    # Debug (optional - remove later)
    # print(f"DEBUG -> Match: {match}, Score: {score}")

    # If similarity is good enough
    if score >= 60:
        return data[index]["answer"]
    else:
        return "Sorry, I don't understand your question."


# -------------------------------
# CHATBOT LOOP (Only runs if executed as script)
# -------------------------------
if __name__ == "__main__":
    print("Vastu Chatbot is running... (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye!")
            break

        answer = get_answer(user_input)
        print("Bot:", answer)
# CHATBOT LOOP (Only runs if executed as script)
# -------------------------------
if __name__ == "__main__":
    print("Vastu Chatbot is running... (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye!")
            break

        answer = get_vastu_advice(user_input)
        print("Bot:", answer)