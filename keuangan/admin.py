from django.contrib import admin
from .models import Bank, Hutang, Kategori, Piutang, Transaksi, Siswa,PembayaranSPP

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'nomor', 'pemilik', 'saldo')
    search_fields = ('nama', 'pemilik')

@admin.register(Hutang)
class HutangAdmin(admin.ModelAdmin):
    list_display = ('id', 'tanggal', 'nominal', 'keterangan')
    search_fields = ('keterangan',)
    list_filter = ('tanggal',)

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama',)
    search_fields = ('nama',)

@admin.register(Piutang)
class PiutangAdmin(admin.ModelAdmin):
    list_display = ('id', 'tanggal', 'nominal', 'keterangan')
    search_fields = ('keterangan',)
    list_filter = ('tanggal',)

@admin.register(Transaksi)
class TransaksiAdmin(admin.ModelAdmin):
    list_display = ('id', 'tanggal', 'jenis', 'kategori', 'jumlah', 'keterangan', 'bank')
    search_fields = ('keterangan', 'jenis')
    list_filter = ('tanggal', 'jenis', 'kategori')


admin.site.register(Siswa)

class PembayaranSPPAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'bulan', 'jumlah_bayar', 'status_bayar', 'tanggal_bayar', 'bukti_pembayaran')
    list_filter = ('bulan', 'status_bayar')  # Filter berdasarkan bulan dan status bayar
    search_fields = ('siswa__nama', 'bulan')  # Search berdasarkan nama siswa dan bulan
    list_editable = ('status_bayar',)  # Bisa langsung edit status bayar dari list view

admin.site.register(PembayaranSPP, PembayaranSPPAdmin)

# Bisa juga pakai admin.site.register(Bank), admin.site.register(Transaksi), dll.
