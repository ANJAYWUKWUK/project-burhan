from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from keuangan.models import PembayaranSPP, Pembayaran
from django.core.mail import send_mail
from django.conf import settings
from .models import Siswa
from .functions import generate_tagihan_spp 

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