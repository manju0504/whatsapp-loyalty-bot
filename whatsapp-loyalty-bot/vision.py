# vision.py
import os
from google.cloud import vision

# Make sure you set GOOGLE_APPLICATION_CREDENTIALS to the path of your serviceAccount.json
# e.g. on Render: add it in the Environment tab
# locally (Linux/Mac): export GOOGLE_APPLICATION_CREDENTIALS="./serviceAccount.json"
# locally (Windows PowerShell): $env:GOOGLE_APPLICATION_CREDENTIALS="./serviceAccount.json"

def extract_text_from_image(image_url: str) -> str:
    """
    Given a public image URL (Twilio MediaUrl), return all detected text.
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_url

    response = client.text_detection(image=image)
    if response.error.message:
        raise RuntimeError(response.error.message)

    if response.full_text_annotation and response.full_text_annotation.text:
        return response.full_text_annotation.text
    return ""
