from enum import Enum


class AccreditationTypes(str, Enum):
    VerifiableAuthorisationToOnboard = "VerifiableAuthorisationToOnboard"
    VerifiableAccreditationToAttest = "VerifiableAccreditationToAttest"
    VerifiableAccreditationToAccredit = "VerifiableAccreditationToAccredit"
    VerifiableAccreditationForTrustChain = "VerifiableAuthorisationForTrustChain"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    @classmethod
    def values(cls):
        return [item.value for item in cls]


class EbsiDidDocumentsRelationships(str, Enum):
    Authentication = "authentication"
    AssertionMethod = "assertionMethod"
    CapabilityInvocation = "capabilityInvocation"
