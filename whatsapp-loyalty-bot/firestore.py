# firestore.py

import firebase_admin
from firebase_admin import credentials, firestore
from vision import extract_text_from_image
from utils import calculate_points, is_git_college, extract_amount_and_billno
import datetime

# Initialize Firestore
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_user_name(user_id, name):
    db.collection("users").document(user_id).set({
        "name": name,
        "points": 0,
        "last_upload": "",
        "streak": 0,
        "referred_by": "",
    }, merge=True)

def verify_and_store_id(user_id, typed_name, image_url):
    text = extract_text_from_image(image_url).lower()
    if not is_git_college(text):
        return False
    if typed_name.lower() not in text:
        return False
    db.collection("users").document(user_id).update({
        "id_verified": True,
        "id_image": image_url
    })
    return True

def process_bill_upload(user_id, image_url):
    user_ref = db.collection("users").document(user_id)
    user = user_ref.get().to_dict()

    if not user.get("id_verified"):
        return "❌ ID not verified. Please upload a valid student ID first."

    today = str(datetime.date.today())

    if user.get("last_upload") == today:
        return "📛 You've already uploaded a bill today."

    bill_text = extract_text_from_image(image_url).lower()
    amount, billno = extract_amount_and_billno(bill_text)

    if not amount or not billno:
        return "🧾 Couldn't detect bill amount or bill number. Please upload a clear bill."

    # Check duplicate bill
    existing = db.collection("bills").where("billno", "==", billno).stream()
    if any(existing):
        return "🚫 This bill has already been used. Try another one."

    # Calculate points
    points = calculate_points(amount)

    # Streak logic
    yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
    streak = user.get("streak", 0)
    last = user.get("last_upload", "")
    if last == yesterday:
        streak += 1
        if streak == 2:
            points += 1  # bonus for 2-day streak
    else:
        streak = 1

    # Save bill
    db.collection("bills").add({
        "user_id": user_id,
        "billno": billno,
        "amount": amount,
        "image": image_url,
        "date": today,
    })

    # Update user
    user_ref.update({
        "points": user.get("points", 0) + points,
        "last_upload": today,
        "streak": streak
    })

    return f"✅ Bill accepted!\n🪙 Earned {points} points.\n🔥 Current streak: {streak} day(s)."

def get_user_points(user_id):
    user = db.collection("users").document(user_id).get().to_dict()
    return user.get("points", 0)

def redeem_rewards(user_id):
    user_ref = db.collection("users").document(user_id)
    user = user_ref.get().to_dict()
    pts = user.get("points", 0)

    if pts >= 25:
        reward = "🍗 Free Chicken Keema Dosa!"
    elif pts >= 15:
        reward = "🥞 Free Upma or Masala Dosa!"
    else:
        return f"🚫 Not enough points. You need 15+ to redeem."

    user_ref.update({"points": 0, "streak": 0})
    return f"🎁 Reward claimed: {reward}\n🔄 Points reset to 0."

def store_skip_day(date_str):
    db.collection("skipdays").document(date_str).set({"skip": True})

def is_skip_day():
    today = str(datetime.date.today())
    ref = db.collection("skipdays").document(today).get()
    return ref.exists
