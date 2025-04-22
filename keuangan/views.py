from django.db import models 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Bank, Transaksi, Hutang, Piutang, Kategori, HutangPiutang
from .forms import TransaksiForm, HutangForm, PiutangForm, BankForm, KategoriForm, HutangPiutangForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib import messages
from .forms import KategoriForm, BankForm
from django.db.models import Sum
from django.utils import timezone
import json
from .forms import HutangPiutangForm

@login_required
def dashboard(request):
    today = timezone.now().date()
    this_month = timezone.now().month
    this_year = timezone.now().year

    # Pemasukan
    pemasukan_hari_ini = Transaksi.objects.filter(jenis="pemasukan", tanggal__gte=today).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    pemasukan_bulan_ini = Transaksi.objects.filter(jenis="pemasukan", tanggal__month=this_month).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    pemasukan_tahun_ini = Transaksi.objects.filter(jenis="pemasukan", tanggal__year=this_year).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    total_pemasukan = Transaksi.objects.filter(jenis="pemasukan").aggregate(Sum('jumlah'))['jumlah__sum'] or 0

    # Pengeluaran
    pengeluaran_hari_ini = Transaksi.objects.filter(jenis="pengeluaran", tanggal__gte=today).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    pengeluaran_bulan_ini = Transaksi.objects.filter(jenis="pengeluaran", tanggal__month=this_month).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    pengeluaran_tahun_ini = Transaksi.objects.filter(jenis="pengeluaran", tanggal__year=this_year).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    total_pengeluaran = Transaksi.objects.filter(jenis="pengeluaran").aggregate(Sum('jumlah'))['jumlah__sum'] or 0

    # **Tambahkan Data Bulanan untuk Grafik**
    pemasukan_bulanan = list(Transaksi.objects.filter(
        jenis="pemasukan", tanggal__year=this_year
    ).values("tanggal__month").annotate(total=Sum("jumlah")))

    pengeluaran_bulanan = list(Transaksi.objects.filter(
        jenis="pengeluaran", tanggal__year=this_year
    ).values("tanggal__month").annotate(total=Sum("jumlah")))

    print(" Pemasukan Bulanan:", pemasukan_bulanan)
    print(" Pengeluaran Bulanan:", pengeluaran_bulanan)

    context = {
        'pemasukan_hari_ini': pemasukan_hari_ini,
        'pemasukan_bulan_ini': pemasukan_bulan_ini,
        'pemasukan_tahun_ini': pemasukan_tahun_ini,
        'total_pemasukan': total_pemasukan,

        'pengeluaran_hari_ini': pengeluaran_hari_ini,
        'pengeluaran_bulan_ini': pengeluaran_bulan_ini,
        'pengeluaran_tahun_ini': pengeluaran_tahun_ini,
        'total_pengeluaran': total_pengeluaran,

        # **Tambahkan ke Template**
        'pemasukan_bulanan': json.dumps(pemasukan_bulanan),
        'pengeluaran_bulanan': json.dumps(pengeluaran_bulanan),
    }
    return render(request, 'keuangan/dashboard.html', context)

@login_required
def daftar_transaksi(request):
    transaksi_list = Transaksi.objects.all().order_by('-tanggal')
    return render(request, 'keuangan/daftar_transaksi.html', {'transaksi_list': transaksi_list})

@login_required
def tambah_transaksi(request):
    if request.method == 'POST':
        form = TransaksiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Kembali ke dashboard setelah transaksi ditambahkan
    else:
        form = TransaksiForm()

    return render(request, 'keuangan/tambah_transaksi.html', {'form': form})

@login_required
def edit_transaksi(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    if request.method == 'POST':
        form = TransaksiForm(request.POST, instance=transaksi)
        if form.is_valid():
            form.save()
            return redirect('daftar_transaksi')
    else:
        form = TransaksiForm(instance=transaksi)
    return render(request, 'keuangan/tambah_transaksi.html', {'form': form})

@login_required
def hapus_transaksi(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    transaksi.delete()
    return redirect('daftar_transaksi')

@login_required
def rekening_bank(request):
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rekening_bank')  # Redirect setelah berhasil menambah

    else:
        form = BankForm()

    bank_list = Bank.objects.all()  # Mengambil semua data rekening bank

    return render(request, 'keuangan/rekening_bank.html', {
        'bank_list': bank_list,
        'form': form
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Ganti dengan halaman setelah login
    else:
        form = AuthenticationForm()
    return render(request, 'keuangan/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Ganti 'login' dengan halaman tujuan setelah logout

def kategori_list(request):
    kategori = Kategori.objects.all()
    return render(request, 'keuangan/kategori_list.html', {'kategori': kategori})

def tambah_kategori(request):
    if request.method == "POST":
        form = KategoriForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kategori_list')  # Pastikan ada url 'kategori_list'
    else:
        form = KategoriForm()

    return render(request, 'keuangan/tambah_kategori.html', {'form': form})


def edit_kategori(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    form = KategoriForm(request.POST or None, instance=kategori)
    if form.is_valid():
        form.save()
        return redirect('kategori_list')
    return render(request, 'keuangan/tambah_kategori.html', {'form': form})

def hapus_kategori(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    kategori.delete()
    return redirect('kategori_list')

def hutang_piutang(request):
    if request.method == 'POST':
        print("Data yang diterima:", request.POST)  # Debugging

        tipe = request.POST.get('tipe')  # Cek apakah hutang atau piutang
        if tipe == 'hutang':
            form = HutangForm(request.POST)
            if form.is_valid():
                form.save()
                print("Hutang berhasil disimpan!")  # Debugging
                return redirect('hutang_piutang')
            else:
                print("Error hutang:", form.errors)  # Debugging
        else:
            form = PiutangForm(request.POST)
            if form.is_valid():
                form.save()
                print("Piutang berhasil disimpan!")  # Debugging
                return redirect('hutang_piutang')
            else:
                print("Error piutang:", form.errors)  # Debugging

    # Ambil data hutang & piutang dari database
    hutang_list = Hutang.objects.all()
    piutang_list = Piutang.objects.all()

    return render(request, 'keuangan/hutang_piutang.html', {
        'hutang_list': hutang_list,
        'piutang_list': piutang_list,
        'hutang_form': HutangForm(),  # Tambahkan form ke context
        'piutang_form': PiutangForm(),  # Tambahkan form ke context
    })


# Edit Hutang
def edit_hutang(request, id):
    hutang = get_object_or_404(HutangPiutang, id=id, tipe='hutang')  # pastikan ID ini memang hutang
    if request.method == 'POST':
        form = HutangPiutangForm(request.POST, instance=hutang)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data hutang berhasil diperbarui.')
            return redirect('hutang_piutang')
    else:
        form = HutangPiutangForm(instance=hutang)
    return render(request, 'keuangan/edit_hutang_piutang.html', {
        'form': form,
        'judul': 'Edit Hutang'
    })

# Edit Piutang
def edit_piutang(request, id):
    piutang = get_object_or_404(HutangPiutang, id=id, tipe='piutang')
    if request.method == 'POST':
        form = HutangPiutangForm(request.POST, instance=piutang)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data piutang berhasil diperbarui.')
            return redirect('hutang_piutang')
    else:
        form = HutangPiutangForm(instance=piutang)
    return render(request, 'keuangan/edit_hutang_piutang.html', {
        'form': form,
        'judul': 'Edit Piutang'
    })

# Hapus Hutang
def hapus_hutang(request, id):
    hutang = get_object_or_404(HutangPiutang, id=id, tipe='hutang')
    hutang.delete()
    messages.success(request, 'Data hutang berhasil dihapus.')
    return redirect('hutang_piutang')

# Hapus Piutang
def hapus_piutang(request, id):
    piutang = get_object_or_404(HutangPiutang, id=id, tipe='piutang')
    piutang.delete()
    messages.success(request, 'Data piutang berhasil dihapus.')
    return redirect('hutang_piutang')