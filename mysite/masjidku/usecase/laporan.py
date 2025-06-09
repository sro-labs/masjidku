from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe
from django.db.models import Sum

import random, json
from datetime import datetime, date

from masjidku.models import Buku, TransaksiPemasukan, TransaksiPengeluaran, SaldoBulan, SaldoMingguan


def recalculate_pemasukan(update_list) -> None:
    """
        Kalkulasi ulang buku kas setelah terjadi penghapusan pemasukan 
    """
    for o in update_list:
        kas = Buku.objects.get(pk=o[0])
        kas.saldo_akhir -= o[3]
        kas.save()
        SaldoBulan.update_saldo(o[0], o[1], o[2])
        SaldoMingguan.update_saldo(o[0], o[4])


def recalculate_pengeluaran(update_list) -> None:
    """
        Kalkulasi ulang buku kas setelah terjadi penghapusan pemasukan 
    """
    for o in update_list:
        kas = Buku.objects.get(pk=o[0])
        kas.saldo_akhir += o[3]
        kas.save()
        SaldoBulan.update_saldo(o[0], o[1], o[2])
        SaldoMingguan.update_saldo(o[0], o[4])


def fetch_data(request) -> dict:
    """
        Fetch data untuk laporan keuangan
    """
    MONTH_CHOICES = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember",
    }

    current_year = datetime.now()
    YEAR_CHOICES = [ year for year in range(current_year.year - 5, current_year.year+1) ]

    data = {
        "BUTTON_CARI": {'onclick': 'apply_filter()'},
        "YEAR_CHOICES": YEAR_CHOICES,
        "MONTH_CHOICES": MONTH_CHOICES,
    }
    
    if 'tahun' in request.GET:
        tahun = int(request.GET['tahun'])
        bulan = int(request.GET['bulan'])
    else: # default tahun berjalan
        tahun = current_year.year
        bulan = current_year.month
    data['PERIODE_FILTER'] = {'tahun': tahun, 'bulan': bulan, 'bulan_text': MONTH_CHOICES[bulan]}
    # print(request.GET['periode'])

    tanggal_awal_bulan = date(tahun, bulan, 1)
    if bulan == 12:
        tanggal_akhir_bulan = date(tahun + 1, 1, 1)
    else:
        tanggal_akhir_bulan = date(tahun, bulan + 1, 1)

    laporan = []
    total_saldo = 0
    total_pemasukan = 0
    total_pengeluaran = 0
    for buku in Buku.objects.all():
        pemasukan = TransaksiPemasukan.objects.filter(id_buku=buku.id, tanggal__gte=tanggal_awal_bulan, tanggal__lt=tanggal_akhir_bulan, id_kategori__jenis='Pemasukan')
        pengeluaran = TransaksiPengeluaran.objects.filter(id_buku=buku.id, tanggal__gte=tanggal_awal_bulan, tanggal__lt=tanggal_akhir_bulan, id_kategori__jenis='Pengeluaran')
        subtotal_pemasukan = pemasukan.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        subtotal_pengeluaran = pengeluaran.aggregate(Sum('jumlah'))['jumlah__sum'] or 0

        # Ambil atau buat saldo bulan
        saldo_bulan = SaldoBulan.update_saldo(buku.id, tahun, bulan)
        saldo_akhir = saldo_bulan.saldo_akhir_bulan()
        total_saldo += saldo_akhir
        total_pemasukan += subtotal_pemasukan
        total_pengeluaran += subtotal_pengeluaran

        table_data = pemasukan.values_list("tanggal", "id_kategori__jenis", "id_kategori__deskripsi","keterangan", "jumlah").union(pengeluaran.values_list("tanggal", "id_kategori__jenis", "id_kategori__deskripsi", "keterangan", "jumlah"))

        # only show if there is data
        if len(table_data) > 0:
            laporan.append({
                'id': buku.pk,
                'buku_kas': buku.name,
                'buku': mark_safe(
                        f'Buku Kas: {buku.name}<button id="btn_kas_{buku.pk}" class="bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded" style="float:right" onclick="download_section(\'kas_{buku.id}\')">Download</button>'),
                'table_data': {
                    "headers": ["Tanggal", "Jenis Transaksi", "Kategori", "Keterangan", "Jumlah"],
                    "rows": table_data.order_by("tanggal")
                },
                'table_summary': {
                    "headers": ["", "", "", "", ""],
                    "rows": [
                        ["", "", "", "Saldo Awal", saldo_bulan.saldo_awal],
                        ["", "", "", "Total Pemasukan", subtotal_pemasukan],
                        ["", "", "", "Total Pengeluaran", subtotal_pengeluaran],
                        ["", "", "", "Saldo Akhir", saldo_akhir],
                    ]
                },
                'total_pemasukan': subtotal_pemasukan,
                'total_pengeluaran': subtotal_pengeluaran,
                'saldo_awal': saldo_bulan.saldo_awal,
                'saldo_akhir': saldo_akhir,
                'tahun': tahun,
                'bulan': bulan,
            })
    data['laporan'] = laporan

    data['kpi'] = [
            { 
                "title": "Total Saldo"
                , "metric": f"Rp {intcomma(f'{total_saldo:.02f}')}" 
                , "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400"></strong>&nbsp;'
                ),
            },
            {
                "title": "Total Pemasukan",
                "metric": f"Rp {intcomma(f'{total_pemasukan:.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400"></strong>&nbsp;'
                ),
            },
            {
                "title": "Total Pengeluaran",
                "metric": f"Rp {intcomma(f'{total_pengeluaran:.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400"></strong>&nbsp;'
                ),
            },
        ]
    return data


