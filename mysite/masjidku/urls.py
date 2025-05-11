from django.urls import path, reverse
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("konfirmasi-donasi", views.konfirmasi_donasi, name="konfirmasi_donasi"),
    # path("laporan/download", views.download_section, name="download"),
    path("berita", views.BeritaListView.as_view(), name="berita_list"),
    path("artikel", views.ArtikelListView.as_view(), name="artikel_list"),
    path("<slug:slug>", views.PageDetailView.as_view(), name="page_view"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

