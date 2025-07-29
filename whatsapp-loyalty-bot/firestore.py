from google.cloud import firestore
from datetime import datetime

db = firestore.Client()

def update_points(user_id, points):
    ref = db.collection("users").document(user_id)
    doc = ref.get()
    today = datetime.now().strftime("%Y-%m-%d")

    if doc.exists:
        data = doc.to_dict()
        total = data.get("points", 0) + points
        streak = data.get("streak", 0) + 1
        ref.update({
            "points": total,
            "last_upload_date": today,
            "streak": streak
        })
    else:
        ref.set({
            "points": points,
            "last_upload_date": today,
            "streak": 1
        })

def has_uploaded_today(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        last_date = doc.to_dict().get("last_upload_date")
        return last_date == datetime.now().strftime("%Y-%m-%d")
    return False

def is_valid_bill(bill_no):
    ref = db.collection("bills").document(bill_no)
    if ref.get().exists:
        return False
    ref.set({"used": True})
    return True

def check_and_reset_streak(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        data = doc.to_dict()
        last_upload = data.get("last_upload_date")
        if last_upload:
            last_date = datetime.strptime(last_upload, "%Y-%m-%d").date()
            days = (datetime.now().date() - last_date).days
            if days >= 3:
                db.collection("users").document(user_id).update({
                    "points": 0,
                    "streak": 0
                })
