import json
from datetime import datetime, date

from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe

from masjidku.models import Page



def fetch_data_beranda() -> dict:
    data = {
        "program": Page.objects.filter(jenis="Program"),
        "berita": Page.objects.filter(jenis="Berita").order_by('-tanggal')[:3],
        "artikel": Page.objects.filter(jenis="Artikel").order_by('-tanggal')[:3],
        "galeri": Page.objects.filter(jenis="Galeri").order_by('-tanggal')[:3],
        "donasi": Page.objects.filter(jenis="Donasi").first(),
    }
    return data

