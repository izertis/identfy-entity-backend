from enum import Enum


class OpenidSwitches(str, Enum):
    OpenidSwitch = "openid services"


class ScopeResponseType(str, Enum):
    vp_token = "vp_token"
    id_token = "id_token"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class RevocationTypes(str, Enum):
    status_list_2021 = "StatusList2021"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
