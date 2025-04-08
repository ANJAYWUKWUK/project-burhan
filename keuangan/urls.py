from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transaksi/', views.daftar_transaksi, name='daftar_transaksi'),
    path('transaksi/tambah/', views.tambah_transaksi, name='tambah_transaksi'),
    path('transaksi/edit/<int:pk>/', views.edit_transaksi, name='edit_transaksi'),
    path('transaksi/hapus/<int:pk>/', views.hapus_transaksi, name='hapus_transaksi'),
    path('rekening-bank/', views.rekening_bank, name='rekening_bank'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('kategori/', views.kategori_list, name='kategori_list'),
    path('kategori/tambah/', views.tambah_kategori, name='tambah_kategori'),
    path('kategori/edit/<int:pk>/', views.edit_kategori, name='edit_kategori'),
    path('kategori/hapus/<int:pk>/', views.hapus_kategori, name='hapus_kategori'),
    path('hutang-piutang/', views.hutang_piutang, name='hutang_piutang'),
    path('login/', views.login_view, name='login'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)