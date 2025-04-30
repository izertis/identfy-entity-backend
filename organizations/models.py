import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from organizations.enums import FormatEnum, TypeEnum


class OrganizationKeys(models.Model):
    # TODO: MODIFY TO ONLY ALLOW ONE OF EACH TYPE
    id = models.CharField(default=uuid.uuid4, editable=False, max_length=36)
    name = models.CharField(_("Name"), max_length=200, null=True, blank=True)
    type = models.CharField(
        _("Type"),
        max_length=20,
        primary_key=True,
        choices=TypeEnum.choices(),
        default=TypeEnum.secp256k1.value,
    )
    format = models.CharField(
        _("Format"),
        max_length=100,
        choices=FormatEnum.choices(),
        default=FormatEnum.jwk.value,
    )
    value = models.JSONField(
        _("Value"),
        max_length=2000,
        help_text=_("Add here you Private Key or your information"),
        default=dict,
    )

    class Meta:
        verbose_name = _("Organization Keys")
        verbose_name_plural = _("Organization Keys")

    def __str__(self) -> str:
        return f"{self.name}"
