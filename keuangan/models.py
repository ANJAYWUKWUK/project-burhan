from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

STATUS_CHOICES = [
    ('belum lunas', 'Belum Lunas'),
    ('lunas', 'Lunas'),
]

BULAN_CHOICES = [
    ('01', 'Januari'),
    ('02', 'Februari'),
    ('03', 'Maret'),
    ('04', 'April'),
    ('05', 'Mei'),
    ('06', 'Juni'),
    ('07', 'Juli'),
    ('08', 'Agustus'),
    ('09', 'September'),
    ('10', 'Oktober'),
    ('11', 'November'),
    ('12', 'Desember'),
]

class Bank(models.Model):
    nama = models.CharField(max_length=255)
    nomor = models.CharField(max_length=255)
    pemilik = models.CharField(max_length=255)
    saldo = models.BigIntegerField()

    def __str__(self):
        return self.nama

class Hutang(models.Model):
    tanggal = models.DateField()
    nominal = models.IntegerField()
    keterangan = models.TextField()

    def __str__(self):
        return f"Hutang {self.nominal} pada {self.tanggal}"

class Kategori(models.Model):
    nama = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

class Piutang(models.Model):
    tanggal = models.DateField()
    nominal = models.IntegerField()
    keterangan = models.TextField()

    def __str__(self):
        return f"Piutang {self.nominal} pada {self.tanggal}"

class Transaksi(models.Model):
    JENIS_CHOICES = [
        ('pemasukan', 'Pemasukan'),
        ('pengeluaran', 'Pengeluaran')
    ]
    tanggal = models.DateTimeField()
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES)
    kategori = models.ForeignKey("Kategori", on_delete=models.CASCADE)
    jumlah = models.IntegerField()
    keterangan = models.TextField()
    bukti = models.CharField(max_length=255, blank=True, null=True)
    bank = models.ForeignKey("Bank", on_delete=models.CASCADE)
    nominal = models.BigIntegerField(default=0) 

    def save(self, *args, **kwargs):
        # Cek apakah instance baru atau edit transaksi
        if self.pk is None:
            if self.jenis == 'pemasukan':
                self.bank.saldo += self.nominal  # Tambah saldo bank
            elif self.jenis == 'pengeluaran':
                self.bank.saldo -= self.nominal  # Kurangi saldo bank
            self.bank.save()  # Simpan perubahan saldo
        print(self.nominal)
        super().save(*args, **kwargs)  # Simpan transaksi

    def __str__(self):
        return f"{self.jenis} - {self.nominal}"




class HutangPiutang(models.Model):
    TipeChoices = [
        ('hutang', 'Hutang'),
        ('piutang', 'Piutang'),
    ]

    tanggal = models.DateField()
    nominal = models.IntegerField()
    keterangan = models.TextField()
    tipe = models.CharField(max_length=10, choices=TipeChoices)

    def __str__(self):
        return f"{self.tipe.title()} - {self.nominal}"
    
class Siswa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)
    kelas = models.CharField(max_length=50)
    no_rekening = models.CharField(max_length=20)

    def __str__(self):
        return self.nama

class PembayaranSPP(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    bulan = models.CharField(max_length=2, choices=BULAN_CHOICES)
    jumlah_bayar = models.DecimalField(max_digits=10, decimal_places=2)
    status_bayar = models.CharField(max_length=20, choices=STATUS_CHOICES, default='belum lunas')
    tanggal_bayar = models.DateField(auto_now_add=True)
    bukti_pembayaran = models.ImageField(upload_to='bukti_pembayaran/', blank=True, null=True)
    # Tambahkan field ini
    is_posted_to_laporan_keuangan = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.siswa.nama} - {self.get_bulan_display()} - {self.status_bayar}"

# Model Pembayaran ini masih ambigu jika sudah ada PembayaranSPP, DSPCicilan, PPDBCicilan.
# Pertimbangkan untuk menghapus atau menggabungkan jika tujuannya sama.
# Jika tetap ingin pakai, tambahkan is_posted_to_laporan_keuangan juga
class Pembayaran(models.Model):
    siswa = models.ForeignKey(User, on_delete=models.CASCADE)
    jumlah_bayar = models.DecimalField(max_digits=10, decimal_places=2)
    status_bayar = models.BooleanField(default=False)
    tanggal_bayar = models.DateField(auto_now_add=True)
    bukti_pembayaran = models.FileField(upload_to='bukti_pembayaran/', null=True, blank=True)
    tanggal_verifikasi = models.DateField(null=True, blank=True)
    is_posted_to_laporan_keuangan = models.BooleanField(default=False) # Tambahkan field ini
    
    def __str__(self):
        return f'{self.siswa.username} - {self.jumlah_bayar}'

class LaporanKeuangan(models.Model):
    tanggal = models.DateField(auto_now_add=True)
    pemasukan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pengeluaran = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"Laporan Keuangan {self.tanggal}"

class TabunganSiswa(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    tanggal = models.DateField()
    nominal = models.IntegerField(default=5000)
    tarik = models.BooleanField(default=False)
    is_posted_to_laporan_keuangan = models.BooleanField(default=False) # Tambahkan field ini
    class Meta:
        unique_together = ('siswa', 'tanggal') # Anda bisa mempertimbangkan ('siswa', 'tanggal', 'tarik') jika satu model untuk setor & tarik
                                                # atau cukup ('siswa', 'tanggal') jika ini hanya untuk setoran.
                                                # Jika ini hanya SETORAN, maka PenarikanTabungan adalah PENGELUARAN.
                                                # Saya asumsikan TabunganSiswa hanya setoran (pemasukan), PenarikanTabungan adalah pengeluaran.

    def __str__(self):
        return f"{self.siswa.nama} - {self.tanggal} - {self.nominal}"

class PenarikanTabungan(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    tanggal_penarikan = models.DateField(auto_now_add=True)
    jumlah_ditarik = models.IntegerField()
    keterangan = models.TextField(blank=True, null=True)
    is_posted_to_laporan_keuangan = models.BooleanField(default=False) # Tambahkan field ini

    def __str__(self):
        return f"{self.siswa.nama} - Rp{self.jumlah_ditarik} - {self.tanggal_penarikan}"
    
class DSP(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    total_tagihan = models.DecimalField(max_digits=10, decimal_places=2, default=3000000)
    tanggal_mulai = models.DateField(default=timezone.now)
    jatuh_tempo = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('belum lunas', 'Belum Lunas'),
            ('lunas', 'Lunas')
        ],
        default='belum lunas'
    )

    def total_terbayar(self):
        from django.db.models import Sum # Import di sini agar tidak ada circular import
        return self.dspcicilan_set.aggregate(Sum('jumlah'))['jumlah__sum'] or 0

    def sisa_tagihan(self):
        return self.total_tagihan - self.total_terbayar()

    def update_status(self):
        if self.sisa_tagihan() <= 0:
            self.status = 'lunas'
        else:
            self.status = 'belum lunas'
        self.save()

    def __str__(self):
        return f"{self.siswa.nama} - DSP"

class DSPCicilan(models.Model):
    dsp = models.ForeignKey(DSP, on_delete=models.CASCADE)
    tanggal = models.DateField(auto_now_add=True)
    jumlah = models.DecimalField(max_digits=10, decimal_places=2)
    bukti_pembayaran = models.ImageField(upload_to='bukti_dsp/')
    is_posted_to_laporan_keuangan = models.BooleanField(default=False) # Tambahkan field ini

    def __str__(self):
        return f"Cicilan {self.jumlah} - {self.dsp.siswa.nama}"

class PPDB(models.Model):
    siswa = models.OneToOneField('Siswa', on_delete=models.CASCADE)
    total_tagihan = models.PositiveIntegerField(default=0)
    total_terbayar = models.PositiveIntegerField(default=0)
    sisa_tagihan = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[("Belum Lunas", "Belum Lunas"), ("Lunas", "Lunas")], default="Belum Lunas")

    def __str__(self):
        return f"PPDB - {self.siswa.nama}"

    @property
    def calculate_sisa_tagihan(self):
        return self.total_tagihan - self.total_terbayar
    
    def update_status(self):
        if self.calculate_sisa_tagihan <= 0:
            self.status = 'Lunas'
        else:
            self.status = 'Belum Lunas'
        self.save()


class PPDBCicilan(models.Model):
    ppdb = models.ForeignKey(PPDB, on_delete=models.CASCADE)
    tanggal = models.DateField(auto_now_add=True)
    jumlah = models.PositiveIntegerField()
    bukti_pembayaran = models.FileField(upload_to='bukti_ppdb/', null=True, blank=True)
    is_posted_to_laporan_keuangan = models.BooleanField(default=False) # Tambahkan field ini

    def __str__(self):
        return f"Cicilan {self.jumlah} - {self.ppdb.siswa.nama}"