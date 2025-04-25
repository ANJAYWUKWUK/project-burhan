from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('accounts/login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', views.dashboard, name='dashboard_admin'),
    path('dashboard/siswa/', views.dashboard_siswa, name='dashboard_siswa'),
    path('transaksi/', views.daftar_transaksi, name='daftar_transaksi'),
    path('transaksi/tambah/', views.tambah_transaksi, name='tambah_transaksi'),
    path('transaksi/edit/<int:pk>/', views.edit_transaksi, name='edit_transaksi'),
    path('transaksi/hapus/<int:pk>/', views.hapus_transaksi, name='hapus_transaksi'),
    path('rekening-bank/', views.rekening_bank, name='rekening_bank'),
    
    path('logout/', views.logout_view, name='logout'),
    path('kategori/', views.kategori_list, name='kategori_list'),
    path('kategori/tambah/', views.tambah_kategori, name='tambah_kategori'),
    path('kategori/edit/<int:pk>/', views.edit_kategori, name='edit_kategori'),
    path('kategori/hapus/<int:pk>/', views.hapus_kategori, name='hapus_kategori'),
    path('hutang-piutang/', views.hutang_piutang, name='hutang_piutang'),
    path('edit-hutang/<int:id>/', views.edit_hutang, name='edit_hutang'),
    path('hapus-hutang/<int:id>/', views.hapus_hutang, name='hapus_hutang'),
    path('edit-piutang/<int:id>/', views.edit_piutang, name='edit_piutang'),
    path('hapus-piutang/<int:id>/', views.hapus_piutang, name='hapus_piutang'),
    path('dashboard-admin/pembayaran/', views.kelola_pembayaran, name='kelola_pembayaran'),
    path('siswa/tagihan/', views.tagihan_spp, name='tagihan_spp'),
    path('test-email/', views.test_email, name='test_email'),       

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)