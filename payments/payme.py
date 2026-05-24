"""
Payme Cards API (direct card integration).
Docs: https://developer.paycom.uz/ru/cardsapi
Flow:
  1. cards.create   → get card token
  2. cards.get_verify_code → trigger SMS to cardholder's phone
  3. cards.verify   → confirm with SMS code → card becomes verified
  4. receipts.create → create a receipt for the amount
  5. receipts.pay   → charge the card
"""
import requests
import base64
from .models import PaymentSettings


def _get_headers(test_mode=True):
    cfg = PaymentSettings.get()
    key = cfg.payme_secret_key
    encoded = base64.b64encode(f"Paycom:{key}".encode()).decode()
    return {
        "X-Auth": encoded,
        "Content-Type": "application/json",
    }


def _base_url(test_mode=True):
    if test_mode:
        return "https://checkout.test.paycom.uz/api"
    return "https://checkout.paycom.uz/api"


def _rpc(method, params, test_mode=True):
    """Generic JSON-RPC call to Payme."""
    payload = {
        "id": 1,
        "method": method,
        "params": params,
    }
    try:
        resp = requests.post(_base_url(test_mode), json=payload, headers=_get_headers(test_mode), timeout=15)
        data = resp.json()
        if "error" in data:
            return None, data["error"].get("message", "Payme error")
        return data.get("result"), None
    except Exception as e:
        return None, str(e)


def create_card(card_number, expire, test_mode=True):
    """
    Step 1: Register a card. Returns card token.
    expire format: 'MMYY' e.g. '0325'
    """
    params = {
        "card": {
            "number": card_number.replace(" ", ""),
            "expire": expire,
        },
        "save": False,
    }
    result, error = _rpc("cards.create", params, test_mode)
    if error:
        return None, error
    return result.get("card", {}).get("token"), None


def send_sms(token, test_mode=True):
    """Step 2: Send SMS verification code to the card's linked phone."""
    params = {"token": token}
    result, error = _rpc("cards.get_verify_code", params, test_mode)
    if error:
        return False, error
    # result contains phone (masked) the SMS was sent to
    phone = result.get("sent_to", "")
    return phone or True, None


def verify_card(token, code, test_mode=True):
    """Step 3: Verify card with SMS code. Returns verified card token."""
    params = {"token": token, "code": code}
    result, error = _rpc("cards.verify", params, test_mode)
    if error:
        return None, error
    card = result.get("card", {})
    if card.get("verify"):
        return card.get("token"), None
    return None, "Card verification failed"


def create_receipt(amount_tiyin, order_id, description, test_mode=True):
    """Step 4: Create a payment receipt."""
    cfg = PaymentSettings.get()
    params = {
        "amount": amount_tiyin,
        "account": {
            "order_id": str(order_id),
        },
        "description": description,
    }
    result, error = _rpc("receipts.create", params, test_mode)
    if error:
        return None, error
    receipt = result.get("receipt", {})
    return receipt.get("_id"), None


def pay_receipt(receipt_id, card_token, test_mode=True):
    """Step 5: Charge the card using the receipt."""
    params = {
        "id": receipt_id,
        "token": card_token,
        "payer": {},
    }
    result, error = _rpc("receipts.pay", params, test_mode)
    if error:
        return False, error
    receipt = result.get("receipt", {})
    # state 4 = paid
    if receipt.get("state") == 4:
        return True, None
    return False, f"Unexpected receipt state: {receipt.get('state')}"
