from django.db import models

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

class User(models.Model):
    nama = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    foto = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=20)

    def __str__(self):
        return self.username

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
