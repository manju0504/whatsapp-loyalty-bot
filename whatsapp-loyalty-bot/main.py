from flask import Flask, request
from firestore import update_points, has_uploaded_today, is_valid_bill, check_and_reset_streak
from vision import extract_id_info, extract_bill_info
from utils import allowed_institution, get_current_points, give_reward

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "WhatsApp Loyalty Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    user_id = data.get("user_id")
    message_type = data.get("message_type")
    message = data.get("message")
    image = data.get("image")

    if message_type == "text":
        if message.lower() == "hi":
            return {"reply": "🎉 Welcome to Dosa Bot! Please enter your full name as per your college ID card."}
        elif message.lower() == "points":
            pts = get_current_points(user_id)
            reward_msg = give_reward(user_id, pts)
            return {"reply": f"🎯 You currently have {pts} points.\n{reward_msg}"}

    elif message_type == "id_card":
        result = extract_id_info(image)
        if allowed_institution(result["institution"]):
            return {"reply": f"✅ ID verified for {result['name']} from {result['institution']}. Please send your food bill image now."}
        else:
            return {"reply": "❌ Sorry, only Gitam and Gayatri college IDs are accepted."}

    elif message_type == "bill":
        check_and_reset_streak(user_id)
        if has_uploaded_today(user_id):
            return {"reply": "⚠️ You've already uploaded a bill today. Try again tomorrow!"}
        bill = extract_bill_info(image)
        if not is_valid_bill(bill["bill_no"]):
            return {"reply": "🚫 Duplicate or invalid bill. Each bill can be used only once."}
        points = 2 if bill["amount"] >= 200 else 1
        update_points(user_id, points)
        return {"reply": f"✅ {points} point(s) added for ₹{bill['amount']}!\nUse 'points' anytime to check your total."}

    return {"reply": "❗ Invalid message format. Please type 'hi' to begin."}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
