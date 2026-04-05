import json
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 📁 Load JSON file
file_path = os.path.join(os.path.dirname(__file__), "vastu_data.json")

with open(file_path, "r") as file:
    vastu_rules = json.load(file)

# 🧠 Extract questions
questions = [rule["question"] for rule in vastu_rules]

# 🔢 Vectorization
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(questions)

# 🤖 Chatbot function
def get_vastu_advice(user_query):
    user_vec = vectorizer.transform([user_query])
    similarity = cosine_similarity(user_vec, X)

    best_match = similarity.argmax()
    score = similarity[0][best_match]

    if score < 0.3:
        return "Sorry, I don't understand your question."

    return vastu_rules[best_match]["answer"]