from flask import Flask, request
from vision import extract_text_from_image
from firestore import (
    save_user_name, verify_and_store_id, process_bill_upload, get_user_points,
    check_and_reset_streak, redeem_rewards, store_skip_day, is_skip_day
)
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '').split(':')[-1]

    # Store session data in memory (production: use Firestore)
    session = request.environ.setdefault('session', {})
    user_state = session.get(from_number, {"step": "welcome"})

    step = user_state["step"]

    if step == "welcome":
        session[from_number] = {"step": "get_name"}
        return send_message("🎉 Welcome to Dosa Points Bot!\nPlease enter your full name as per your college ID card.")
    
    elif step == "get_name":
        session[from_number] = {"step": "upload_id", "name": incoming_msg}
        save_user_name(from_number, incoming_msg)
        return send_message("📸 Now, please upload your College ID card photo.")

    elif step == "upload_id" and 'MediaUrl0' in request.values:
        image_url = request.values['MediaUrl0']
        name = session[from_number]["name"]
        valid = verify_and_store_id(from_number, name, image_url)
        if valid:
            session[from_number] = {"step": "upload_bill", "name": name}
            return send_message("✅ ID Verified!\nNow send your bill to get loyalty points.")
        else:
            return send_message("❌ Sorry, only Gitam or Gayatri student IDs are allowed.\nPlease try again.")

    elif step == "upload_bill" and 'MediaUrl0' in request.values:
        image_url = request.values['MediaUrl0']
        today_skipped = is_skip_day()

        if today_skipped:
            return send_message("😴 Restaurant is closed today. Points will not be affected.")

        msg = process_bill_upload(from_number, image_url)
        return send_message(msg)

    elif incoming_msg.lower() == "points":
        points = get_user_points(from_number)
        return send_message(f"💰 You have *{points}* points.")

    elif incoming_msg.lower() == "redeem":
        msg = redeem_rewards(from_number)
        return send_message(msg)

    elif incoming_msg.lower().startswith("skipday") and from_number in os.getenv("ADMINS", "").split(','):
        # Admin command like: skipday 2025-07-28
        try:
            _, date = incoming_msg.strip().split()
            store_skip_day(date)
            return send_message(f"✅ Marked {date} as a skip day.")
        except:
            return send_message("❌ Format: skipday YYYY-MM-DD")
    
    return send_message("🤖 Invalid input or image. Try sending 'points' or 'redeem'.")

def send_message(msg):
    return f"""<Response><Message>{msg}</Message></Response>"""

if __name__ == "__main__":
    app.run(debug=True)
