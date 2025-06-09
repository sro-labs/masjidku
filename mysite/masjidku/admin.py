import logging

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
from .models import Buku, KategoriTransaksi, SaldoBulan, SaldoMingguan, Transaksi, TransaksiPemasukan, TransaksiPengeluaran, Jamaah, Page, Galeri, Laporan, Donasi
from masjidku.usecase.laporan import recalculate_pemasukan, recalculate_pengeluaran


class BukuKasAdmin(ModelAdmin):
    fields = ["name", "deskripsi", "saldo_awal", "saldo_akhir"]
    list_display = ["name", "saldo_awal", "saldo_akhir"]


class SaldoBulanAdmin(ModelAdmin):
    list_display = ["tahun", "bulan", "id_buku", "saldo_awal"]
    list_filter = ("tahun", "bulan", "id_buku")


class SaldoMingguanAdmin(ModelAdmin):
    list_display = ["tanggal_jumat", "id_buku", "saldo_awal"]
    list_filter = ("tanggal_jumat", "id_buku")


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

    def delete_model(self, request, obj):
        logging.info('delete_model is being called.')
        update_list = [ (obj.id_buku.pk, obj.tanggal.year, obj.tanggal.month, obj.jumlah, obj.tanggal.date()) ]
        super().delete_model(request, obj)
        recalculate_pemasukan(update_list)

    def delete_queryset(self, request, obj):
        logging.info('delete_queryset is being called.')
        update_list = [ (o.id_buku.pk, o.tanggal.year, o.tanggal.month, o.jumlah, o.tanggal.date()) for o in obj ]
        super().delete_model(request, obj)
        recalculate_pemasukan(update_list)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(id_kategori__jenis='Pemasukan')
        return queryset
    
    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)


class TransaksiPengeluaranAdmin(TransaksiAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm

    def delete_model(self, request, obj):
        logging.info('delete_model is being called.')
        update_list = [ (obj.id_buku.pk, obj.tanggal.year, obj.tanggal.month, obj.jumlah, obj.tanggal.date()) ]
        super().delete_model(request, obj)
        recalculate_pengeluaran(update_list)

    def delete_queryset(self, request, obj):
        logging.info('delete_queryset is being called.')
        update_list = [ (o.id_buku.pk, o.tanggal.year, o.tanggal.month, o.jumlah, o.tanggal.date()) for o in obj ]
        super().delete_model(request, obj)
        recalculate_pengeluaran(update_list)

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
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("jenis_jamaah"),
        ("jenis_kelamin"),
        ("golongan_darah"),
    )

    def delete_model(self, request, obj):
        if obj.url_foto:
            obj.url_foto.delete(save=False)
        super().delete_model(request, obj)

    def delete_queryset(self, request, obj):
        for o in obj:
            if o.url_foto:
                o.url_foto.delete(save=False)
        super().delete_model(request, obj)



class HalamanAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    fieldsets = [
        (None, {"fields": ["judul", "jenis", "pembuat", "konten", "is_published"]}),
        (None, {"fields": ["foto"]}),
    ]
    list_display = ["jenis", "judul", "tanggal", "pembuat", "terpublikasi"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("jenis", AllValuesCheckboxFilter),
        ("tanggal", RangeDateFilter),  # Date filter
        ("pembuat"),
    )

    def delete_model(self, request, obj):
        if obj.foto:
            obj.foto.delete(save=False)
        super().delete_model(request, obj)

    def delete_queryset(self, request, obj):
        for o in obj:
            if o.foto:
                o.foto.delete(save=False)
        super().delete_model(request, obj)


class GalleryAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    fieldsets = [
        (None, {"fields": ["judul", "is_published"]}),
        (None, {"fields": ["foto"]}),
    ]
    list_display = ["tanggal", "foto", "judul", "terpublikasi"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(jenis='Galeri')
        return queryset

    def save_model(self, request, obj, form, change):
        obj.jenis = 'Galeri'
        obj.pembuat = request.user.username
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if obj.foto:
            obj.foto.delete(save=False)
        super().delete_model(request, obj)

    def delete_queryset(self, request, obj):
        for o in obj:
            if o.foto:
                o.foto.delete(save=False)
        super().delete_model(request, obj)


class LaporanAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    fieldsets = [
        (None, {"fields": ["judul", "is_published"]}),
        (None, {"fields": ["foto"]}),
    ]
    list_display = ["tanggal", "foto", "judul", "terpublikasi"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(jenis='Laporan')
        return queryset

    def save_model(self, request, obj, form, change):
        obj.jenis = 'Laporan'
        obj.pembuat = request.user.username
        super().save_model(request, obj, form, change)


class DonasiAdmin(ModelAdmin):
    readonly_fields = ["tanggal", "nama", "no_telp", "email", "nilai", "keterangan"]
    fieldsets = [
        ("Apakah donasi berikut sudah diterima ?", {"fields": ["tanggal", "nama", "no_telp", "email", "nilai", "keterangan"]}),
        (None, {"fields": ["is_confirm"]}),
    ]
    list_display = ["tanggal", "nama", "no_telp", "nilai", "terkonfirmasi"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("tanggal", RangeDateFilter),  # Date filter
        ("is_confirm"),
    )

    @admin.display(description=_("Terkonfirmasi"))
    def terkonfirmasi(self, obj):
        return 'Ya' if obj.is_confirm else 'Belum' 


admin.site.register(Buku, BukuKasAdmin)
admin.site.register(Jamaah, JamaahAdmin)
admin.site.register(KategoriTransaksi, KategoriTransaksiAdmin)
admin.site.register(TransaksiPemasukan, TransaksiPemasukanAdmin)
admin.site.register(TransaksiPengeluaran, TransaksiPengeluaranAdmin)
admin.site.register(SaldoBulan, SaldoBulanAdmin)
admin.site.register(SaldoMingguan, SaldoMingguanAdmin)
admin.site.register(Page, HalamanAdmin)
admin.site.register(Galeri, GalleryAdmin)
admin.site.register(Laporan, LaporanAdmin)
admin.site.register(Donasi, DonasiAdmin)

