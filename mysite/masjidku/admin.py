from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.db import models

from import_export.admin import ImportExportModelAdmin

from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter
from unfold.contrib.filters.admin import ChoicesRadioFilter, ChoicesCheckboxFilter, AllValuesCheckboxFilter
from unfold.contrib.forms.widgets import WysiwygWidget


# Register your models here.
from .models import Buku, KategoriTransaksi, SaldoBulan, Transaksi, TransaksiPemasukan, TransaksiPengeluaran, Jamaah, Page


class BukuKasAdmin(ModelAdmin):
    fields = ["name", "deskripsi", "saldo_awal", "saldo_akhir"]
    list_display = ["name", "saldo_awal", "saldo_akhir"]


class SaldoBulanAdmin(ModelAdmin):
    list_display = ["tahun", "bulan", "id_buku", "saldo_awal"]
    list_filter = ("tahun", "bulan", "id_buku")


class KategoriTransaksiAdmin(ModelAdmin):
    list_display = ["kode", "deskripsi", "jenis"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("jenis", AllValuesCheckboxFilter),
    )


class TransaksiAdmin(ModelAdmin):
    list_display = ["tanggal", "id_buku", "id_kategori", "keterangan", "jumlah"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("id_buku__name", AllValuesCheckboxFilter),
        ("tanggal", RangeDateFilter),  # Date filter
    )

    fieldsets = (
        (None, {
            'fields': ('id_buku', 'tanggal', 'id_kategori', 'keterangan', 'jumlah')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filter the queryset for id_kategori based on the transaction type
        if isinstance(self, TransaksiPemasukanAdmin):
            form.base_fields['id_kategori'].queryset = KategoriTransaksi.objects.filter(jenis='Pemasukan')
        elif isinstance(self, TransaksiPengeluaranAdmin):
            form.base_fields['id_kategori'].queryset = KategoriTransaksi.objects.filter(jenis='Pengeluaran')
        return form


class TransaksiPemasukanAdmin(TransaksiAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(id_kategori__jenis='Pemasukan')
        return queryset
    
    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)
 

class TransaksiPengeluaranAdmin(TransaksiAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(id_kategori__jenis='Pengeluaran')
        return queryset
    
    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)


class JamaahAdmin(ModelAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm
    fieldsets = [
        (None, {"fields": ["nama", "alamat", "no_telp", "golongan_darah", "jenis_kelamin", "jenis_jamaah"]}),
        ("Detail", {"fields": ["tempat_lahir", "tanggal_lahir", "url_foto"], "classes": ["collapse"]}),
    ]
    list_display = ["nama", "jenis_kelamin", "jenis_jamaah", "golongan_darah"]


class HalamanAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    list_display = ["jenis", "judul", "tanggal", "pembuat"]
    list_filter = (
        ("jenis", AllValuesCheckboxFilter),
        ("tanggal", RangeDateFilter),  # Date filter
        ("pembuat"),
    )



admin.site.register(Buku, BukuKasAdmin)
admin.site.register(Jamaah, JamaahAdmin)
admin.site.register(KategoriTransaksi, KategoriTransaksiAdmin)
admin.site.register(TransaksiPemasukan, TransaksiPemasukanAdmin)
admin.site.register(TransaksiPengeluaran, TransaksiPengeluaranAdmin)
admin.site.register(SaldoBulan, SaldoBulanAdmin)
admin.site.register(Page, HalamanAdmin)

