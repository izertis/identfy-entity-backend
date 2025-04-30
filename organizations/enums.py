from enum import Enum


class TypeEnum(Enum):
    secp256k1 = "secp256k1"
    secp256r1 = "secp256r1"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class FormatEnum(Enum):
    jwk = "jwk"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
