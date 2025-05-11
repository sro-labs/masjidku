from datetime import date

from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

# Create your models here.
JENIS_TRANSAKSI = (
    ("Pemasukan", "Pemasukan"),
    ("Pengeluaran", "Pengeluaran"),
)

JENIS_KELAMIN = (
    ("LK", "Laki-Laki"),
    ("PR", "Perempuan"),
)

JENIS_JAMAAH = (
    ("Mampu", "Mampu"),
    ("Fakir", "Fakir"),
    ("Miskin", "Miskin"),
    ("Amil", "Amil"),
    ("Mualaf", "Mualaf"),
    ("Riqab", "Riqab (budak)"),
    ("Gharimin", "Gharimin (orang yang berhutang)"),
    ("Fisabilillah", "Fisabilillah (orang yang berjuang dijalan Allah)"),
    ("Ibnu Samil", "Ibnu Samil (orang dalam perjalanan)"),
)

GOLONGAN_DARAH = (
    ("A", "A"),
    ("A+", "A+"),
    ("B", "B"),
    ("B+", "B+"),
    ("AB", "AB"),
    ("AB+", "AB+"),
    ("O", "O"),
)


class Buku(models.Model):
    name = models.CharField(("Nama"), max_length=50)
    deskripsi = models.TextField(("Deskripsi"))
    saldo_awal = models.IntegerField(("Saldo Awal"), default=0)
    saldo_akhir = models.IntegerField(("Saldo Akhir"), default=0)

    class Meta:
        verbose_name = ("Buku Kas")
        verbose_name_plural = ("Buku Kas")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Buku_detail", kwargs={"pk": self.pk})



class KategoriTransaksi(models.Model):
    kode = models.CharField(("Kode"), max_length=5)
    deskripsi = models.CharField(("Deskripsi"), max_length=50)
    jenis = models.CharField(("Jenis"), max_length=50, choices=JENIS_TRANSAKSI)

    class Meta:
        verbose_name = ("Kategori Transaksi")
        verbose_name_plural = ("Kategori Transaksi")

    def __str__(self):
        return self.deskripsi

    def get_absolute_url(self):
        return reverse("KategoriTransaksi_detail", kwargs={"pk": self.pk})


class SaldoBulan(models.Model):
    bulan = models.IntegerField()
    tahun = models.IntegerField()
    id_buku = models.ForeignKey("masjidku.Buku", verbose_name=("Buku Kas"), on_delete=models.CASCADE, null=True)
    saldo_awal = models.IntegerField()

    def __str__(self):
        return f"{self.tahun}-{self.bulan} Saldo Awal:{self.saldo_awal}"

    @classmethod
    def update_saldo(cls, buku, tahun, bulan):
        #cek saldo bulan sebelumnya ada atau tidak
        if bulan == 1:
            bulan_sebelumnya = 12
            tahun_sebelumnya = tahun - 1
        else :
            bulan_sebelumnya = bulan - 1
            tahun_sebelumnya = tahun

        saldo_sebelumnya = cls.objects.filter(id_buku=buku, tahun=tahun_sebelumnya, bulan=bulan_sebelumnya).first()

        if not saldo_sebelumnya:
            saldo_awal = 0
        else :
            saldo_awal = saldo_sebelumnya.saldo_akhir_bulan()

        # Create or update saldo bulan
        bukuObj = Buku.objects.get(pk=buku)
        saldo_bulan, created = cls.objects.get_or_create(
            id_buku=bukuObj, tahun=tahun, bulan=bulan, defaults={'saldo_awal': saldo_awal}
        )

        if not created:
            saldo_bulan.saldo_awal = saldo_awal
            saldo_bulan.save()
        return saldo_bulan

    def saldo_akhir_bulan(self):
        """Menghitung dan mengembalikan saldo akhir bulan."""
        tanggal_awal_bulan = date(self.tahun, self.bulan, 1)
        if self.bulan == 12:
            tanggal_akhir_bulan = date(self.tahun + 1, 1, 1)
        else:
            tanggal_akhir_bulan = date(self.tahun, self.bulan + 1, 1)

        pemasukan = TransaksiPemasukan.objects.filter(id_buku=self.id_buku, tanggal__gte=tanggal_awal_bulan, tanggal__lt=tanggal_akhir_bulan, id_kategori__jenis='Pemasukan')
        pengeluaran = TransaksiPengeluaran.objects.filter(id_buku=self.id_buku, tanggal__gte=tanggal_awal_bulan, tanggal__lt=tanggal_akhir_bulan, id_kategori__jenis='Pengeluaran')
        total_pemasukan = pemasukan.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        total_pengeluaran = pengeluaran.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        return self.saldo_awal + (total_pemasukan - total_pengeluaran)


class Transaksi(models.Model):
    id_buku = models.ForeignKey("masjidku.Buku", verbose_name=("Buku Kas"), on_delete=models.CASCADE)
    tanggal = models.DateTimeField(("Tanggal"), auto_now=False, auto_now_add=False)
    id_kategori = models.ForeignKey("masjidku.KategoriTransaksi", verbose_name=("Kategori Transaksi"), on_delete=models.CASCADE)
    jumlah = models.IntegerField(("Jumlah"))
    keterangan = models.TextField(("Keterangan"))

    def __str__(self):
        return f"{self.tanggal} - {self.jumlah}"

    def get_absolute_url(self):
        return reverse("Transaksi_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # get buku kas model
        # update saldo_akhir
        kas = Buku.objects.get(pk=self.id_buku.pk)
        if self.id_kategori.jenis == "Pemasukan":
            kas.saldo_akhir += self.jumlah
        else:
            kas.saldo_akhir -= self.jumlah
        kas.save()
        super(Transaksi, self).save(*args, **kwargs)
        SaldoBulan.update_saldo(self.id_buku.pk, self.tanggal.year, self.tanggal.month)


class TransaksiPemasukan(Transaksi):
    class Meta:
        proxy = True
        verbose_name = ("Pemasukan")
        verbose_name_plural = ("Pemasukan")


class TransaksiPengeluaran(Transaksi):
    class Meta:
        proxy = True
        verbose_name = ("Pengeluaran")
        verbose_name_plural = ("Pengeluaran")



class Jamaah(models.Model):
    nama = models.CharField(("Nama"), max_length=50)
    alamat = models.CharField(("Alamat"), max_length=150)
    id_provinsi = models.CharField(("Provinsi"), max_length=10, null=True, blank=True)
    id_kabupaten = models.CharField(("Kabupaten"), max_length=10, null=True, blank=True)
    id_kecamatan = models.CharField(("Kecamatan"), max_length=10, null=True, blank=True)
    id_kelurahan = models.CharField(("Kelurahan"), max_length=10, null=True, blank=True)
    kode_pos = models.CharField(("Kode Pos"), max_length=8, null=True, blank=True)
    no_telp = models.CharField(("Nomor HP"), max_length=15, null=True, blank=True)
    jenis_kelamin = models.CharField(("Jenis Kelamin"), max_length=50, choices=JENIS_KELAMIN)
    jenis_jamaah = models.CharField(("Jenis Jamaah"), max_length=50, choices=JENIS_JAMAAH)
    golongan_darah = models.CharField(("Golongan Darah"), max_length=4, choices=GOLONGAN_DARAH, null=True, blank=True)
    tempat_lahir = models.CharField(("Tempat Lahir"), max_length=20, null=True, blank=True)
    tanggal_lahir = models.DateTimeField(("Tanggal Lahir"), auto_now=False, auto_now_add=False, null=True, blank=True)
    url_foto = models.ImageField(("Foto"), upload_to='images/', null=True, blank=True)


    class Meta:
        verbose_name = _("Jamaah")
        verbose_name_plural = _("Jamaah")

    def __str__(self):
        return self.nama

    def get_absolute_url(self):
        return reverse("Jamaah_detail", kwargs={"pk": self.pk})


