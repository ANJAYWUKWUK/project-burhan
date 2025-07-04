from django.db.models.signals import post_migrate, post_save, post_delete
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from keuangan.models import PembayaranSPP, Pembayaran
from django.core.mail import send_mail
from django.conf import settings
from .models import Siswa
from decimal import Decimal
from .functions import generate_tagihan_spp 
from django.utils import timezone
from .models import (
    LaporanKeuangan, PembayaranSPP, DSPCicilan, PPDBCicilan,
    TabunganSiswa, PenarikanTabungan
)

@receiver(post_save, sender=PembayaranSPP)
def update_laporan_keuangan_on_spp_save(sender, instance, created, **kwargs):
    if instance.status_bayar == 'lunas' and not instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal_bayar if instance.tanggal_bayar else timezone.now().date()
        laporan, _ = LaporanKeuangan.objects.get_or_create(tanggal=today)
        
        laporan.pemasukan += instance.jumlah_bayar
        laporan.saldo = laporan.pemasukan - laporan.pengeluaran
        laporan.save()
        
        # Tandai pembayaran ini sudah diposting
        instance.is_posted_to_laporan_keuangan = True
        instance.save(update_fields=['is_posted_to_laporan_keuangan']) # Hindari looping rekursif

@receiver(post_delete, sender=PembayaranSPP)
def update_laporan_keuangan_on_spp_delete(sender, instance, **kwargs):
    if instance.status_bayar == 'lunas' and instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal_bayar if instance.tanggal_bayar else timezone.now().date()
        try:
            laporan = LaporanKeuangan.objects.get(tanggal=today)
            laporan.pemasukan -= instance.jumlah_bayar
            laporan.saldo = laporan.pemasukan - laporan.pengeluaran
            laporan.save()
        except LaporanKeuangan.DoesNotExist:
            pass # Laporan untuk hari itu mungkin sudah tidak ada, abaikan

# Tambahkan signal untuk model Pembayaran (jika masih digunakan)
@receiver(post_save, sender=Pembayaran)
def update_laporan_keuangan_on_pembayaran_save(sender, instance, created, **kwargs):
    if instance.status_bayar and not instance.is_posted_to_laporan_keuangan: # Jika status_bayar True
        today = instance.tanggal_bayar if instance.tanggal_bayar else timezone.now().date()
        laporan, _ = LaporanKeuangan.objects.get_or_create(tanggal=today)
        
        laporan.pemasukan += instance.jumlah_bayar
        laporan.saldo = laporan.pemasukan - laporan.pengeluaran
        laporan.save()
        
        instance.is_posted_to_laporan_keuangan = True
        instance.save(update_fields=['is_posted_to_laporan_keuangan'])

@receiver(post_delete, sender=Pembayaran)
def update_laporan_keuangan_on_pembayaran_delete(sender, instance, **kwargs):
    if instance.status_bayar and instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal_bayar if instance.tanggal_bayar else timezone.now().date()
        try:
            laporan = LaporanKeuangan.objects.get(tanggal=today)
            laporan.pemasukan -= instance.jumlah_bayar
            laporan.saldo = laporan.pemasukan - laporan.pengeluaran
            laporan.save()
        except LaporanKeuangan.DoesNotExist:
            pass

@receiver(post_save, sender=DSPCicilan)
def update_laporan_keuangan_on_dspcicilan_save(sender, instance, created, **kwargs):
    if not instance.is_posted_to_laporan_keuangan: # Anggap setiap cicilan DSP langsung masuk
        today = instance.tanggal if instance.tanggal else timezone.now().date()
        laporan, _ = LaporanKeuangan.objects.get_or_create(tanggal=today)
        
        laporan.pemasukan += instance.jumlah
        laporan.saldo = laporan.pemasukan - laporan.pengeluaran
        laporan.save()
        
        instance.is_posted_to_laporan_keuangan = True
        instance.save(update_fields=['is_posted_to_laporan_keuangan'])

@receiver(post_delete, sender=DSPCicilan)
def update_laporan_keuangan_on_dspcicilan_delete(sender, instance, **kwargs):
    if instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal if instance.tanggal else timezone.now().date()
        try:
            laporan = LaporanKeuangan.objects.get(tanggal=today)
            laporan.pemasukan -= instance.jumlah
            laporan.saldo = laporan.pemasukan - laporan.pengeluaran
            laporan.save()
        except LaporanKeuangan.DoesNotExist:
            pass

@receiver(post_save, sender=PPDBCicilan)
def update_laporan_keuangan_on_ppdbcicilan_save(sender, instance, created, **kwargs):
    if not instance.is_posted_to_laporan_keuangan: # Anggap setiap cicilan PPDB langsung masuk
        today = instance.tanggal if instance.tanggal else timezone.now().date()
        laporan, _ = LaporanKeuangan.objects.get_or_create(tanggal=today)
        
        laporan.pemasukan += instance.jumlah
        laporan.saldo = laporan.pemasukan - laporan.pengeluaran
        laporan.save()
        
        instance.is_posted_to_laporan_keuangan = True
        instance.save(update_fields=['is_posted_to_laporan_keuangan'])

@receiver(post_delete, sender=PPDBCicilan)
def update_laporan_keuangan_on_ppdbcicilan_delete(sender, instance, **kwargs):
    if instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal if instance.tanggal else timezone.now().date()
        try:
            laporan = LaporanKeuangan.objects.get(tanggal=today)
            laporan.pemasukan -= instance.jumlah
            laporan.saldo = laporan.pemasukan - laporan.pengeluaran
            laporan.save()
        except LaporanKeuangan.DoesNotExist:
            pass

@receiver(post_save, sender=TabunganSiswa)
def update_laporan_keuangan_on_tabungansiswa_save(sender, instance, created, **kwargs):
    if not instance.tarik and not instance.is_posted_to_laporan_keuangan: # Hanya untuk setoran
        today = instance.tanggal if instance.tanggal else timezone.now().date()
        laporan, _ = LaporanKeuangan.objects.get_or_create(tanggal=today)
        
        laporan.pemasukan += Decimal(instance.nominal) # Pastikan tipe Decimal
        laporan.saldo = laporan.pemasukan - laporan.pengeluaran
        laporan.save()
        
        instance.is_posted_to_laporan_keuangan = True
        instance.save(update_fields=['is_posted_to_laporan_keuangan'])

@receiver(post_delete, sender=TabunganSiswa)
def update_laporan_keuangan_on_tabungansiswa_delete(sender, instance, **kwargs):
    if not instance.tarik and instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal if instance.tanggal else timezone.now().date()
        try:
            laporan = LaporanKeuangan.objects.get(tanggal=today)
            laporan.pemasukan -= Decimal(instance.nominal)
            laporan.saldo = laporan.pemasukan - laporan.pengeluaran
            laporan.save()
        except LaporanKeuangan.DoesNotExist:
            pass

# --- Signal untuk PENGELUARAN ---

@receiver(post_save, sender=PenarikanTabungan)
def update_laporan_keuangan_on_penarikan_save(sender, instance, created, **kwargs):
    if not instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal_penarikan if instance.tanggal_penarikan else timezone.now().date()
        laporan, _ = LaporanKeuangan.objects.get_or_create(tanggal=today)
        
        laporan.pengeluaran += Decimal(instance.jumlah_ditarik) # Pastikan tipe Decimal
        laporan.saldo = laporan.pemasukan - laporan.pengeluaran
        laporan.save()
        
        instance.is_posted_to_laporan_keuangan = True
        instance.save(update_fields=['is_posted_to_laporan_keuangan'])

@receiver(post_delete, sender=PenarikanTabungan)
def update_laporan_keuangan_on_penarikan_delete(sender, instance, **kwargs):
    if instance.is_posted_to_laporan_keuangan:
        today = instance.tanggal_penarikan if instance.tanggal_penarikan else timezone.now().date()
        try:
            laporan = LaporanKeuangan.objects.get(tanggal=today)
            laporan.pengeluaran -= Decimal(instance.jumlah_ditarik)
            laporan.saldo = laporan.pemasukan - laporan.pengeluaran
            laporan.save()
        except LaporanKeuangan.DoesNotExist:
            pass


@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    # ===== BUAT GROUP ADMIN =====
    admin_group, created = Group.objects.get_or_create(name='Admin')
    if created:
        # Admin: kasih semua permission dari app 'keuangan'
        for content_type in ContentType.objects.filter(app_label='keuangan'):
            permissions = Permission.objects.filter(content_type=content_type)
            admin_group.permissions.add(*permissions)
        print("✅ Group Admin dibuat dan diberikan full access.")

    # ===== BUAT GROUP SISWA =====
    siswa_group, created = Group.objects.get_or_create(name='Siswa')
    if created:
        # Khusus model PembayaranSPP → siswa hanya bisa view dan add (buat bukti bayar)
        content_type = ContentType.objects.get_for_model(PembayaranSPP)
        view_perm = Permission.objects.get(codename='view_pembayaranspp', content_type=content_type)
        add_perm = Permission.objects.get(codename='add_pembayaranspp', content_type=content_type)

        siswa_group.permissions.add(view_perm, add_perm)
        print("✅ Group Siswa dibuat dengan hak akses lihat & tambah bukti bayar.")

@receiver(post_save, sender=Pembayaran)
def kirim_notifikasi_admin(sender, instance, created, **kwargs):
    if instance.bukti_pembayaran and not instance.status_bayar:
        # Kirim email ke admin jika bukti pembayaran baru diupload
        admin_email = settings.ADMIN_EMAIL  # Pastikan ada setting admin email di settings.py
        send_mail(
            'Bukti Pembayaran Baru Diupload',
            f'Siswa {instance.siswa.username} telah mengunggah bukti pembayaran SPP. Segera verifikasi.',
            'no-reply@yourwebsite.com',  # Pengirim
            [admin_email],
            fail_silently=False,
        )

@receiver(post_save, sender=Siswa)
def buat_tagihan_siswa(sender, instance, created, **kwargs):
    if created:
        generate_tagihan_spp(instance)