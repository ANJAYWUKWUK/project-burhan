from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f"{self.siswa.nama} - {self.get_bulan_display()} - {self.status_bayar}"

class Pembayaran(models.Model):
    siswa = models.ForeignKey(User, on_delete=models.CASCADE)
    jumlah_bayar = models.DecimalField(max_digits=10, decimal_places=2)
    status_bayar = models.BooleanField(default=False)
    tanggal_bayar = models.DateField(auto_now_add=True)
    bukti_pembayaran = models.FileField(upload_to='bukti_pembayaran/', null=True, blank=True)
    tanggal_verifikasi = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.siswa.username} - {self.jumlah_bayar}'
# models.py

class LaporanKeuangan(models.Model):
    tanggal = models.DateField(auto_now_add=True)
    pemasukan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pengeluaran = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def update_pemasukan(self, jumlah):
        self.pemasukan += jumlah
        self.saldo += jumlah
        self.save()

    def __str__(self):
        return f"Laporan Keuangan {self.tanggal}"
