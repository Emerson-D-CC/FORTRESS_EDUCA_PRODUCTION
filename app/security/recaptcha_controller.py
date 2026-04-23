import requests
from app.settings import Config_Security


def validar_recaptcha(token):
    secret = Config_Security.RECAPTCHA_SECRET_KEY
    
    if not secret:
        print("[ERROR] RECAPTCHA_SECRET_KEY no configurado")
        return False

    if not token:
        return False

    try:
        payload = {"secret": secret, "response": token}
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload,
            timeout=5
        )

        data = r.json()
        return data.get("success", False)

    except requests.exceptions.RequestException as e:
        print("[ERROR] reCAPTCHA conexión:", e)
        return False

    except Exception as e:
        print("[ERROR] reCAPTCHA general:", e)
        return False