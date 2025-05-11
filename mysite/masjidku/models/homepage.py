from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import path, reverse


JENIS_HALAMAN = (
    ("Artikel", "Artikel"),
    ("Berita", "Berita"),
    ("Donasi", "Donasi"),
    ("Galeri", "Galeri"),
    ("Kepengurusan", "Kepengurusan"),
    ("Program", "Program"),
    ("QR Donasi", "QR Donasi"),
    ("Sejarah", "Sejarah"),
)

BLACKLIST = ["Donasi", "Kepengurusan", "QR Donasi", "Sejarah"]


class Page(models.Model):
    jenis = models.CharField(("Jenis Halaman"), max_length=50, choices=JENIS_HALAMAN)
    tanggal = models.DateField(("Tanggal"), default=date.today)
    pembuat = models.CharField(("Dibuat Oleh"), max_length=50)
    foto = models.ImageField(("Ilustrasi"), upload_to='images/', null=True, blank=True)
    judul = models.CharField(("Judul"), max_length=250)
    konten = models.TextField(("Konten"), null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)


    class Meta:
        verbose_name = _("Halaman")
        verbose_name_plural = _("Halaman")

    def __str__(self):
        return self.judul

    def clean(self):
        # Beberapa jenis halaman tidak boleh duplicate
        if self.jenis in BLACKLIST:
            isExists = Page.objects.filter(jenis=self.jenis).first()
            if isExists != None and isExists.pk != self.id:
                raise ValidationError(_("Halaman sudah ada, silakan edit halaman sebelumnya."))
        
        return super().clean()

    def get_absolute_url(self):
        return reverse("page_view", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.judul)
        super(Page, self).save(*args, **kwargs)


class Galeri(Page):
    class Meta:
        proxy = True
        verbose_name = ("Galeri")
        verbose_name_plural = ("Galeri")

