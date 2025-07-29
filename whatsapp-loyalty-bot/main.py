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
    incoming_data = request.form

    # Extract WhatsApp message content
    from_number = incoming_data.get("From")
    body = incoming_data.get("Body")
    media_url = incoming_data.get("MediaUrl0")

    # Simplified state for example logic
    user_id = from_number

    if body.lower() == "hi":
        return respond("🎉 Ayyo! Welcome ra brother... 👋\nPlease enter your full name as per your student ID.")
    
    elif body.lower() == "points":
        pts = get_current_points(user_id)
        reward_msg = give_reward(user_id, pts)
        return respond(f"🎯 You currently have {pts} points.\n{reward_msg}")
    
    # For ID card (simple check — assume image = ID for demo)
    if media_url and "id" in body.lower():
        result = extract_id_info(media_url)
        if allowed_institution(result["institution"]):
            return respond(f"✅ ID verified for {result['name']} from {result['institution']}.\nPlease upload your food bill now.")
        else:
            return respond("❌ Only Gitam and Gayatri college IDs are allowed.")
    
    # For bill image
    if media_url and "bill" in body.lower():
        check_and_reset_streak(user_id)
        if has_uploaded_today(user_id):
            return respond("⚠️ You've already uploaded a bill today. Try again tomorrow!")
        
        bill = extract_bill_info(media_url)
        if not is_valid_bill(bill["bill_no"]):
            return respond("🚫 This bill has already been used or is invalid.")

        points = 2 if bill["amount"] >= 200 else 1
        update_points(user_id, points)
        return respond(f"✅ {points} point(s) added for ₹{bill['amount']}!\nSend 'points' anytime to check your total.")

    return respond("❗ I didn't understand that. Please type 'hi' to begin.")

def respond(message):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>""", 200, {'Content-Type': 'application/xml'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
