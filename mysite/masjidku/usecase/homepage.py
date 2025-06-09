import json
from datetime import datetime, date

from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe

from masjidku.models import Page



def fetch_data_beranda() -> dict:
    data = {
        "program": Page.objects.filter(jenis="Program").filter(is_published=True),
        "berita": Page.objects.filter(jenis="Berita").filter(is_published=True).order_by('-tanggal')[:3],
        "artikel": Page.objects.filter(jenis="Artikel").filter(is_published=True).order_by('-tanggal')[:3],
        "galeri": Page.objects.filter(jenis="Galeri").filter(is_published=True).order_by('-tanggal')[:3],
        "donasi": Page.objects.filter(jenis="Donasi").filter(is_published=True).first(),
    }
    return data

