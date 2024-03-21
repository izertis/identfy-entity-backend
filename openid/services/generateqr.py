import qrcode
from PIL import Image, ImageDraw


class GenerateQr:
    def __init__(self, url):
        self.credential_offer: str = url

    def generate_qr(self) -> str:
        qr_image = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_image.add_data(self.credential_offer)
        qr_image.make(fit=True)
        qr_offset = qr_image.make_image(fill_color="black", back_color="white")
        return qr_offset
