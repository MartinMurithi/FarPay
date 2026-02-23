import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_pesapal_token():
    """
    Implements Pesapal V3 Authentication.
    Generates a 5-minute Bearer token.
    """
    url = os.getenv("PESAPAL_AUTH_URL")

    # 1. Safety Check: If URL is missing, stop early
    if not url:
        print("Error: PESAPAL_AUTH_URL not found in .env file")
        return None

    # HTTP request headers as per documentation
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    key = os.getenv("PESAPAL_CONSUMER_KEY", "").strip()
    secret = os.getenv("PESAPAL_CONSUMER_SECRET", "").strip()

    # Request Parameters
    payload = {
        "consumer_key": key,
        "consumer_secret": secret,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        # Log the raw response if it fails so we can see why
        if response.status_code != 200:
            print(f"FAILED! Status: {response.status_code}, Response: {response.text}")
            return None

        data = response.json()
        token = data.get("token")

        if token:
            print("SUCCESS: Token received!")
            return token
        else:
            print(f"FAILED: No token in JSON. Response was: {data}")
            return None

    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return None


def register_ipn(token, ngrok_url):
    """
    Tells Pesapal where to send payment confirmation signals.
    """
    url = "https://cybqa.pesapal.com/pesapalv3/api/URLSetup/RegisterIPN"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "url": f"{ngrok_url}/api/v1/payments/callback",
        "ipn_notification_type": "GET",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()  # This contains IPN_ID
    except Exception as e:
        print(f"IPN Registration Error: {e}")
        return None


def submit_order(token, order_details):
    """
    Submits an order to Pesapal and returns the payment URL.
    """
    url = "https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # Structure required by Pesapal V3
    payload = {
        "id": order_details["merchant_reference"],
        "currency": "KES",
        "amount": order_details["amount"],
        "description": "Payment for FarPay Order",
        "callback_url": os.getenv("NGROK_URL"),
        "notification_id": os.getenv("PESAPAL_IPN_ID"),
        "billing_address": {
            "email_address": order_details["email"],
            "first_name": order_details["first_name"],
            "last_name": order_details["last_name"],
            "phone_number": order_details["phone"],
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Submit Order Error: {e}")
        return None


def get_transaction_status(token, tracking_id):
    """
    Queries Pesapal to see if the payment was successful.
    """
    url = f"https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus?orderTrackingId={tracking_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Status Check Error: {e}")
        return None
