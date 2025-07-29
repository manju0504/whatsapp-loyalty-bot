# utils.py

import re

def calculate_points(amount):
    if 100 <= amount < 200:
        return 1
    elif amount >= 200:
        return 2
    return 0

def is_git_college(text):
    text = text.lower()
    return (
        "gitam" in text or
        "gayatri" in text or
        "gitam deemed" in text or
        "gayatri vidya parishad" in text
    )

def extract_amount_and_billno(text):
    # Get bill no
    billno_match = re.search(r"(bill|token)[^\d]*(\d{3,})", text)
    billno = billno_match.group(2) if billno_match else None

    # Get amount
    amount_match = re.findall(r"\d{2,4}", text)
    amount = None
    for val in amount_match:
        try:
            amt = int(val)
            if 50 <= amt <= 500:
                amount = amt
                break
        except:
            continue

    return amount, billno
