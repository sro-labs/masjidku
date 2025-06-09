from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView

from masjidku.usecase.laporan import fetch_data
from masjidku.usecase.homepage import fetch_data_beranda
from masjidku.usecase.donasi import konfirmasi_donasi as confirm_donasi
from masjidku.models import Page


class BeritaListView(ListView):
    model = Page
    template_name = "homepage/artikel_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(jenis="Berita").filter(is_published=True).order_by("-tanggal")
        return queryset


class ArtikelListView(ListView):
    model = Page
    template_name = "homepage/artikel_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(jenis="Artikel").filter(is_published=True).order_by("-tanggal")
        return queryset


class LaporanListView(ListView):
    model = Page
    template_name = "homepage/laporan_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(jenis="Laporan").filter(is_published=True).order_by("-tanggal")
        return queryset


class PageDetailView(DetailView):
    model = Page
    template_name = 'homepage/artikel.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        return queryset


def index(request):
    data = fetch_data_beranda()
    return render(request, 'homepage/index.html', data)


def konfirmasi_donasi(request):
    if request.method == "GET":
        return render(request, 'homepage/konfirmasi_donasi.html', {'success': None})
    elif request.method == "POST":
        post_data = request.POST
        result =  confirm_donasi(post_data)
        return render(request, 'homepage/konfirmasi_donasi.html', {'success': result})


def download_section(request):
    data = fetch_data(request)
    return render(request, 'superuser/laporan_keuangan.html', data)


def dashboard_callback(request, context):
    data = fetch_data(request)
    context.update(data)
    return context

