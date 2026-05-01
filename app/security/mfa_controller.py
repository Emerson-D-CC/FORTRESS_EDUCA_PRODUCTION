import pyotp
import qrcode
import io
import base64

class MFA_Controller:
    """Maneja la generación y validación de TOTP compatible con Microsoft Authenticator"""

    ISSUER = "Fortress Educa"

    @staticmethod
    def generar_secret() -> str:
        """Genera un nuevo secret TOTP aleatorio (base32)"""
        return pyotp.random_base32()

    @staticmethod
    def generar_uri(secret: str, username: str) -> str:
        """Genera el URI otpauth para el QR"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=username,
            issuer_name=MFA_Controller.ISSUER
        )

    @staticmethod
    def generar_qr_base64(uri: str) -> str:
        """Genera imagen QR en base64 para embeber en HTML"""
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    @staticmethod
    def verificar_codigo(secret: str, codigo: str) -> bool:
        try:
            # Decodificar si llega como bytes desde la BD
            if isinstance(secret, (bytes, bytearray)):
                secret = secret.decode("utf-8")
            if isinstance(codigo, (bytes, bytearray)):
                codigo = codigo.decode("utf-8")

            totp = pyotp.TOTP(secret.strip())
            
            return totp.verify(codigo.strip(), valid_window=6)
        except Exception as e:
            print(f"[ERROR] verificar_codigo: {e}")
            return False