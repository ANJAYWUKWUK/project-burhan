from django.contrib import admin
from .models import Bank, Hutang, Kategori, Piutang, Transaksi, Siswa,PembayaranSPP, LaporanKeuangan,TabunganSiswa, PenarikanTabungan,DSP,DSPCicilan,PPDB, PPDBCicilan
from .functions import generate_tagihan_spp

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

class PembayaranSPPAdmin(admin.ModelAdmin):
    list_display = ('id','siswa', 'bulan', 'jumlah_bayar', 'status_bayar', 'tanggal_bayar', 'bukti_pembayaran')
    list_filter = ('bulan', 'status_bayar')  # Filter berdasarkan bulan dan status bayar
    search_fields = ('siswa__nama', 'bulan')  # Search berdasarkan nama siswa dan bulan
    list_editable = ('status_bayar',)  # Bisa langsung edit status bayar dari list view

admin.site.register(PembayaranSPP, PembayaranSPPAdmin)

@admin.register(Siswa)
class SiswaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kelas', 'no_rekening')
    search_fields = ('nama', 'kelas')
    actions = ['naik_kelas']

    @admin.action(description='Naikkan kelas siswa terpilih')
    def naik_kelas(self, request, queryset):
        for siswa in queryset:
            siswa.kelas = self.get_kelas_baru(siswa.kelas)
            siswa.save()

    def get_kelas_baru(self, kelas_sekarang):
        # Logika kenaikan kelas
        kelas_mapping = {
            '1A': '2A',
            '1B': '2B',
            '2A': '3A',
            '2B': '3B',
            '3A': '4A',
            '3B': '4B',
            '4A': '5A',
            '4B': '5B',
            '5A': '6A',
            '5B': '6B',
            # Tambahkan kelas lain jika ada
        }
        return kelas_mapping.get(kelas_sekarang, kelas_sekarang)  # Default: tetap kelas lama

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # Jika siswa baru p
            generate_tagihan_spp(obj)
# Bisa juga pakai admin.site.register(Bank), admin.site.register(Transaksi), dll.

@admin.register(LaporanKeuangan)
class LaporanKeuanganAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'pemasukan', 'pengeluaran', 'saldo')
    search_fields = ('tanggal',)
    ordering = ('-tanggal',)
    
@admin.register(TabunganSiswa)
class TabunganSiswaAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'tanggal', 'nominal', 'tarik')
    list_filter = ('tarik', 'tanggal')
    search_fields = ('siswa__nama',)
    ordering = ('-tanggal',)

@admin.register(PenarikanTabungan)
class PenarikanTabunganAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'tanggal_penarikan', 'jumlah_ditarik', 'keterangan')
    list_filter = ('tanggal_penarikan',)
    search_fields = ('siswa__nama',)
    ordering = ('-tanggal_penarikan',)

class DSPCicilanInline(admin.TabularInline):
    model = DSPCicilan
    extra = 0
    readonly_fields = ['tanggal']
    can_delete = False

class DSPAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'total_tagihan', 'total_terbayar', 'sisa_tagihan', 'status', 'jatuh_tempo')
    list_filter = ('status', 'siswa__kelas')
    search_fields = ('siswa__nama', 'siswa__kelas')
    inlines = [DSPCicilanInline]
    readonly_fields = ('total_terbayar', 'sisa_tagihan')

    def total_terbayar(self, obj):
        return obj.total_terbayar()

    def sisa_tagihan(self, obj):
        return obj.sisa_tagihan()
    
class DSPCicilanAdmin(admin.ModelAdmin):
    list_display = ('dsp', 'jumlah', 'tanggal')
    list_filter = ('tanggal',)
    search_fields = ('dsp__siswa__nama',)

admin.site.register(DSP, DSPAdmin)
admin.site.register(DSPCicilan, DSPCicilanAdmin)

@admin.register(PPDB)
class PPDBAdmin(admin.ModelAdmin):
    list_display = ['siswa', 'total_tagihan', 'total_terbayar', 'sisa_tagihan', 'status']

@admin.register(PPDBCicilan)
class PPDBCicilanAdmin(admin.ModelAdmin):
    list_display = ['ppdb', 'tanggal', 'jumlah', 'bukti_pembayaran']
