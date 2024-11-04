import math

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusList2021(models.Model):
    content = models.BinaryField()
    current_index = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(131071),  # 16 * 1024 * 8 - 1
        ],
        null=True,
    )

    class Meta:
        verbose_name = "StatusList2021"
        verbose_name_plural = "StatusLists2021"

    def __str__(self) -> str:
        return f"{self.id}"

    def save(self, *args, **kwargs):
        if not self.content:
            self.content = bytearray(16 * 1024)
        return super().save(*args, **kwargs)


class IssuedVerifiableCredential(models.Model):
    vc_id = models.CharField(
        _("VC Identifier"), max_length=4000, null=False, primary_key=True
    )
    vc_type = ArrayField(models.CharField(max_length=4000), verbose_name=_("VC Types"))
    hash = models.CharField(
        _("Credential hash"), max_length=4000, null=True, blank=True
    )
    issuance_date = models.DateTimeField(_("Issuance Date"), null=False)
    status = models.BooleanField(_("Revocation status"), default=False)
    revocation_type = models.CharField(
        _("Revocation Type"), max_length=4000, null=True, blank=True
    )
    revocation_info = models.JSONField(
        _("Revocation Information"), null=True, blank=True
    )

    def clean(self):
        if not self.status:
            # Check if the data was set to true before
            current_model = IssuedVerifiableCredential.objects.filter(
                vc_id=self.vc_id
            ).last()
            if current_model.status:
                raise ValidationError("Can't restore the status of a revoked VC")
        else:
            if not self.revocation_type:
                raise ValidationError(_("This credential cannot revoke"))

    def save(self, *args, **kwargs):
        if self.status:
            revocation_info = self.revocation_info
            list_array = revocation_info["statusListCredential"].split("/")
            status_list_id = list_array[len(list_array) - 1]
            index = int(revocation_info["statusListIndex"])
            status_list = StatusList2021.objects.filter(id=status_list_id).last()
            byte_index = math.floor(index / 8)
            bit_index = int(index) % 8
            list_data = bytearray(status_list.content)
            list_data[byte_index] |= 128 >> bit_index
            status_list.content = list_data
            status_list.save()

        return super().save(*args, **kwargs)
