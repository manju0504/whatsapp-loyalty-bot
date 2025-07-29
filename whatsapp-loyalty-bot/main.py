from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from firestore import update_points, has_uploaded_today, is_valid_bill, check_and_reset_streak
from vision import extract_id_info, extract_bill_info
from utils import allowed_institution, get_current_points, give_reward

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "WhatsApp Loyalty Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    user_id = request.values.get('From')
    resp = MessagingResponse()

    if incoming_msg == "hi":
        msg = "🎉 Welcome to Dosa Bot! Please enter your full name as per your college ID card."
        resp.message(msg)
    elif incoming_msg == "points":
        pts = get_current_points(user_id)
        reward_msg = give_reward(user_id, pts)
        resp.message(f"🎯 You currently have {pts} points.\n{reward_msg}")
    else:
        resp.message("❗ Invalid message. Please type 'hi' to begin or 'points' to check your total.")

    return str(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
