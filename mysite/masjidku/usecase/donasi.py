import json
from datetime import datetime, date

from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe

from masjidku.models import Donasi


def konfirmasi_donasi(post_data):
    try:
        nama = post_data.get("name")
        no_telp = post_data.get("phone")
        email = post_data.get("email")
        nilai = post_data.get("value")
        keterangan = post_data.get("note")
        donasi = Donasi(nama=nama, no_telp=no_telp, email=email, nilai=nilai, keterangan=keterangan)
        donasi.save()
        return True
    except:
        return False
