from google.cloud import firestore

db = firestore.Client()

def allowed_institution(text):
    text = text.lower()
    return any(keyword in text for keyword in ["gitam", "gayatri"])

def get_current_points(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict().get("points", 0)
    return 0

def give_reward(user_id, points):
    if points >= 25:
        return "🎁 You're eligible for a FREE Chicken Keema Dosa!"
    elif points >= 15:
        return "🎁 You're eligible for a FREE Upma or Masala Dosa!"
    return "Earn more points to unlock dosa rewards! 🔥"
