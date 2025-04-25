from django.contrib import admin
from .models import Bank, Hutang, Kategori, Piutang, Transaksi, UserProfile, Siswa

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

admin.site.register(UserProfile)
admin.site.register(Siswa)

# Bisa juga pakai admin.site.register(Bank), admin.site.register(Transaksi), dll.
