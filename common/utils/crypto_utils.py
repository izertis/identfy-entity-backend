import base64
import hashlib
import json


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def calculate_jwk_thumbprint(jwk: dict) -> str:
    kty = jwk.get("kty")

    if kty == "EC":
        required_fields = {"crv", "kty", "x", "y"}
    else:
        raise ValueError(f"Unsupported kty: {kty}")

    thumbprint_input = {k: jwk[k] for k in sorted(required_fields)}
    json_repr = json.dumps(thumbprint_input, separators=(",", ":"), sort_keys=True)
    thumbprint_bytes = hashlib.sha256(json_repr.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(thumbprint_bytes).rstrip(b"=").decode("utf-8")
