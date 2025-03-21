from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transaksi/', views.daftar_transaksi, name='daftar_transaksi'),
    path('transaksi/tambah/', views.tambah_transaksi, name='tambah_transaksi'),
    path('rekening-bank/', views.rekening_bank, name='rekening_bank'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('kategori/', views.kategori_list, name='kategori_list'),
    path('kategori/tambah/', views.tambah_kategori, name='tambah_kategori'),
    path('hutang-piutang/', views.hutang_piutang, name='hutang_piutang'),
]
