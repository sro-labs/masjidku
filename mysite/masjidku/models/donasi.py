from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import path, reverse


class Donasi(models.Model):
    nama = models.CharField(_("Nama Lengkap"), max_length=50)
    no_telp = models.CharField(_("Nomor Telp"), max_length=15)
    email = models.EmailField(_("Email"), max_length=254)
    nilai = models.IntegerField(_("Nilai Donasi"))
    tanggal = models.DateField(_("Tanggal"), default=date.today)
    keterangan = models.TextField(_("Keterangan"))
    is_confirm = models.BooleanField(_("Terkonfirmasi"), default=False)
    tanggal_confirm = models.DateField(_("Tanggal Konfirmasi"), blank=True, null=True)

    class Meta:
        verbose_name = ("Donasi")
        verbose_name_plural = ("Donasi")

    def __str__(self):
        return self.nama

    def clean(self):
        # Jika sudah terkonfirmasi tidak boleh dirubah kembali
        isExists = Donasi.objects.get(pk=self.id)
        if isExists != None:
            if isExists.is_confirm:
                raise ValidationError(_("Data yang sudah terkonfirmasi tidak dapat diubah kembali!."))
        return super().clean()

    def get_absolute_url(self):
        return reverse("donasi", kwargs={"pk": self.pk})

