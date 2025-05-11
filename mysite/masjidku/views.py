from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView

from masjidku.usecase.laporan import fetch_data
from masjidku.usecase.homepage import fetch_data_beranda
from masjidku.models import Page


class BeritaListView(ListView):
    model = Page
    template_name = "homepage/artikel_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(jenis="Berita").order_by("-tanggal")
        return queryset


class ArtikelListView(ListView):
    model = Page
    template_name = "homepage/artikel_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(jenis="Artikel").order_by("-tanggal")
        return queryset


class PageDetailView(DetailView):
    model = Page
    template_name = 'homepage/artikel.html'


def index(request):
    data = fetch_data_beranda()
    return render(request, 'homepage/index.html', data)


def konfirmasi_donasi(request):
    return render(request, 'homepage/konfirmasi_donasi.html', {})


def download_section(request):
    data = fetch_data(request)
    return render(request, 'superuser/laporan_keuangan.html', data)


def dashboard_callback(request, context):
    data = fetch_data(request)
    context.update(data)
    return context

