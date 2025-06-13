from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import export_pembayaran_excel
from django.shortcuts import redirect


urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', views.dashboard, name='dashboard_admin'),
    path('dashboard/siswa/', views.dashboard_siswa, name='dashboard_siswa'),
    path('siswa/', views.daftar_siswa, name='daftar_siswa'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard-admin/pembayaran/', views.kelola_pembayaran, name='kelola_pembayaran'),
    path('dsp/tambah/', views.form_dsp, name='dsp_tambah'),
    path('dsp/edit/<int:dsp_id>/', views.form_dsp, name='dsp_edit'),
    path('get-siswa-by-kelas/', views.get_siswa_by_kelas, name='get_siswa_by_kelas'),
    path('get-pembayaran-by-siswa/', views.get_pembayaran_by_siswa, name='get_pembayaran_by_siswa'),

    # Tambah dan Edit Cicilan DSP
    path('dsp/', views.dsp_list, name='dsp_list'),
    path('dsp/form/', views.form_dsp, name='form_dsp_baru'),  # untuk tambah DSP
    path('dsp/form/<int:dsp_id>/', views.form_dsp, name='form_dsp'),  # untuk edit DSP
    path('dsp/<int:dsp_id>/ubah-status/<str:status>/', views.ubah_status_dsp, name='ubah_status_dsp'),
    path('dsp/<int:dsp_id>/cicilan/', views.dsp_cicilan_list, name='dsp_cicilan_list'),
    path('dsp/<int:dsp_id>/cicilan/tambah/', views.form_cicilan_dsp, name='dsp_cicilan_tambah'),
    path('dsp/<int:dsp_id>/cicilan/edit/<int:cicilan_id>/', views.form_cicilan_dsp, name='dsp_cicilan_edit'),
    path('dsp/<int:dsp_id>/hapus/', views.dsp_delete, name='dsp_delete'),

    path('ppdb/', views.ppdb_list, name='ppdb_list'),
    path('ppdb/tambah/', views.form_ppdb, name='ppdb_tambah'),
    path('ppdb/edit/<int:ppdb_id>/', views.form_ppdb, name='ppdb_edit'),
    path('ppdb/<int:ppdb_id>/', views.ppdb_detail, name='ppdb_detail'),
    path('ppdb/<int:ppdb_id>/cicilan/tambah/', views.form_cicilan_ppdb, name='ppdb_cicilan_tambah'),
    path('ppdb/<int:ppdb_id>/cicilan/edit/<int:cicilan_id>/', views.form_cicilan_ppdb, name='ppdb_cicilan_edit'),
    path('ppdb/hapus/<int:ppdb_id>/', views.ppdb_delete, name='ppdb_delete'),

    # ========== HALAMAN SISWA ==========
    path('dsp/saya/', views.dsp_siswa_detail, name='dsp_siswa_detail'),
    path('siswa/tagihan/', views.tagihan_spp, name='tagihan_spp'),
    path('test-email/', views.test_email, name='test_email'),
    path('export-pembayaran/', export_pembayaran_excel, name='export_pembayaran_excel'),  
    path('tabungan/kelola-tabungan/', views.tabungan_view, name='kelola_tabungan'),
    path('tabungan/', lambda request: redirect('kelola_tabungan')),
    path('ppdb/saya/', views.siswa_ppdb_detail, name='siswa_ppdb_detail'),
    path('ppdb/saya/tambah/<int:ppdb_id>/', views.siswa_ppdb_cicilan_tambah, name='siswa_ppdb_cicilan_tambah'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)