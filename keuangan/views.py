from django.db import models 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Bank, Transaksi, Hutang, Piutang, Kategori, HutangPiutang,PembayaranSPP, Siswa, LaporanKeuangan, TabunganSiswa , PenarikanTabungan 
from .forms import TransaksiForm, HutangForm, PiutangForm, BankForm, KategoriForm, HutangPiutangForm,BuktiPembayaranForm,PilihKelasForm, PilihBulanForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib import messages
from .forms import KategoriForm, BankForm
from django.db.models import Sum
from django.utils import timezone
import json
import calendar
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.http import HttpResponse
import openpyxl
from io import BytesIO
from .functions import generate_tagihan_spp
from datetime import datetime
from django.core.files.storage import FileSystemStorage

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # HARUS ADA INI
            return redirect('dashboard_redirect')  # pastikan 'dashboard' ini ada di urls.py
    else:
        form = AuthenticationForm()
    return render(request, 'keuangan/login.html', {'form': form})

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.groups.filter(name='Admin').exists():
        return redirect('dashboard_admin')
    elif user.groups.filter(name='Siswa').exists():
        return redirect('dashboard_siswa')
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    if not user.groups.filter(name='Admin').exists():
        return redirect('dashboard_siswa')
    
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
def dashboard_siswa(request):
    user = request.user
    # Cek apakah user termasuk grup Siswa
    if not user.groups.filter(name='Siswa').exists():
        return redirect('dashboard_admin')  # atau redirect ke mana pun kalau bukan siswa

    tagihan_saya = PembayaranSPP.objects.filter(siswa__user=request.user)
    return render(request, 'keuangan/siswa/dashboard_siswa.html', {'tagihan': tagihan_saya})

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
            return redirect('dashboard_admin')  # Kembali ke dashboard setelah transaksi ditambahkan
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


@login_required
def kelola_pembayaran(request):
    kelas_list = Siswa.objects.values_list('kelas', flat=True).distinct()

    kelas_terpilih = request.GET.get('kelas')
    siswa_id = request.GET.get('siswa_id')
    search_nama = request.GET.get('search_nama')

    pembayaran_list = None
    siswa_list = []
    siswa_terpilih = None

    if kelas_terpilih:
        siswa_list = Siswa.objects.filter(kelas=kelas_terpilih)

        if siswa_id:
            siswa_terpilih = get_object_or_404(Siswa, id=siswa_id)
            pembayaran_list = PembayaranSPP.objects.filter(siswa=siswa_terpilih).order_by('bulan')

    if request.method == 'POST':
        pembayaran_id = request.POST.get('pembayaran_id')
        pembayaran = get_object_or_404(PembayaranSPP, id=pembayaran_id)

        pembayaran.status_bayar = 'lunas'
        pembayaran.save()

        # redirect tetap jaga query string supaya tetap di halaman yang sama
        redirect_url = request.path
        query_params = []
        if kelas_terpilih:
            query_params.append(f'kelas={kelas_terpilih}')
        if siswa_id:
            query_params.append(f'siswa_id={siswa_id}')
        if search_nama:
            query_params.append(f'search_nama={search_nama}')
        if query_params:
            redirect_url += '?' + '&'.join(query_params)

        return redirect(redirect_url)

    return render(request, 'keuangan/admin/kelola_pembayaran.html', {
        'kelas_list': kelas_list,
        'kelas_terpilih': kelas_terpilih,
        'siswa_list': siswa_list,
        'siswa_terpilih': siswa_terpilih,
        'pembayaran_list': pembayaran_list,
        'search_nama': search_nama,
    })



def is_siswa(user):
    return hasattr(user, 'siswa')
# Siswa View: Lihat tagihan pribadi & upload bukti
@user_passes_test(is_siswa, login_url='/login/')
@login_required
def tagihan_spp(request):
    # Ambil data siswa berdasarkan user yang login
    siswa = get_object_or_404(Siswa, user=request.user)

    # Ambil semua tagihan siswa tersebut
    pembayaran_list = PembayaranSPP.objects.filter(siswa=siswa).order_by('bulan')

    if request.method == 'POST':
        pembayaran_id = request.POST.get('pembayaran_id')
        pembayaran = get_object_or_404(PembayaranSPP, id=pembayaran_id, siswa=siswa)

        form = BuktiPembayaranForm(request.POST, request.FILES, instance=pembayaran)
        if form.is_valid():
            # Simpan bukti pembayaran dan ubah status jadi "pending" atau lainnya
            pembayaran.status = 'pending'  # optional: kalau lo ada field status
            form.save()

             # Update laporan keuangan
            laporan = LaporanKeuangan.objects.latest('tanggal')
            laporan.update_pemasukan(pembayaran.jumlah_bayar)

            send_mail(
                subject=f'Bukti Pembayaran SPP Masuk - {pembayaran.siswa.nama}',
                message=f'Siswa {pembayaran.siswa.nama} telah mengupload bukti pembayaran untuk bulan {pembayaran.bulan}. Jumlah yang dibayar: {pembayaran.jumlah_bayar}.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            return redirect('tagihan_spp')
    else:
        form = BuktiPembayaranForm()

    return render(request, 'keuangan/siswa/tagihan_spp.html', {
        'pembayaran_list': pembayaran_list,
        'form': form
    })

def test_email(request):
    send_mail(
        subject='[TEST] Bukti Pembayaran Masuk',
        message='Ini adalah simulasi notifikasi: Siswa Fulan sudah upload bukti pembayaran.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=False,
    )
    return HttpResponse("Email test berhasil dikirim.")

@login_required
def export_pembayaran_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pembayaran SPP"

    # Header
    ws.append(['Nama Siswa', 'Kelas', 'Bulan', 'Jumlah Bayar', 'Status', 'Tanggal Bayar'])

    # Data
    pembayaran_list = PembayaranSPP.objects.all().order_by('siswa__nama')
    for bayar in pembayaran_list:
        ws.append([
            bayar.siswa.nama,
            bayar.siswa.kelas,
            bayar.get_bulan_display(),
            bayar.jumlah_bayar,
            bayar.status_bayar,
            bayar.tanggal_bayar.strftime("%d-%m-%Y") if bayar.tanggal_bayar else '-'
        ])

    # Simpan workbook ke dalam memory (BytesIO)
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Response download file
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=pembayaran_spp.xlsx'
    return response

def daftar_siswa(request):
    siswa_list = Siswa.objects.all()

    if request.method == "POST":
        siswa_id = request.POST.get("siswa_id")
        kelas_baru = request.POST.get("kelas_baru")
        siswa = get_object_or_404(Siswa, id=siswa_id)
        siswa.kelas = kelas_baru
        siswa.save()
        return redirect('daftar_siswa')  # ganti dengan nama URL kamu

    return render(request, 'keuangan/admin/daftar_siswa.html', {'siswa_list': siswa_list})

def generate_tagihan(request, siswa_id):
    siswa = Siswa.objects.get(id=siswa_id)
    generate_tagihan_spp(siswa)
    return redirect('siswa_detail', siswa_id=siswa.id)


def input_tabungan(request):
    kelas_form = PilihKelasForm(request.POST or None)
    bulan_form = PilihBulanForm(request.POST or None)
    siswa_list = []
    tanggal_list = []
    selected_kelas = None
    selected_bulan = None
    selected_tahun = None

    if request.method == 'POST':
        selected_kelas = request.POST.get('kelas')
        selected_bulan = int(request.POST.get('bulan'))
        selected_tahun = int(request.POST.get('tahun'))

        siswa_list = Siswa.objects.filter(kelas=selected_kelas)
        _, last_day = calendar.monthrange(selected_tahun, selected_bulan)
        tanggal_list = list(range(1, last_day + 1))

        if 'simpan' in request.POST:
            for siswa in siswa_list:
                tanggal_terpilih = request.POST.getlist(f'tanggal_{siswa.id}')
                for tanggal in tanggal_terpilih:
                    tanggal_full = datetime(selected_tahun, selected_bulan, int(tanggal)).date()

                    # Cek apakah sudah ada tabungan di tanggal itu, kalau belum, buat
                    TabunganSiswa.objects.get_or_create(
                        siswa=siswa,
                        tanggal=tanggal_full,
                        defaults={'nominal': 5000}
                    )

            messages.success(request, "Tabungan berhasil disimpan.")
            return redirect('input_tabungan')

    context = {
        'kelas_form': kelas_form,
        'bulan_form': bulan_form,
        'siswa_list': siswa_list,
        'tanggal_list': tanggal_list,
        'selected_bulan': selected_bulan,
        'selected_tahun': selected_tahun,
    }
    return render(request, 'keuangan/admin/input_tabungan.html', context)


def riwayat_tabungan(request):
    kelas_list = Siswa.objects.values_list('kelas', flat=True).distinct()
    selected_kelas = request.GET.get('kelas')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    siswa_tabungan = TabunganSiswa.objects.all()

    # Filter berdasarkan kelas jika ada
    if selected_kelas:
        siswa_tabungan = siswa_tabungan.filter(siswa__kelas=selected_kelas)

    # Filter berdasarkan rentang tanggal jika ada
    if start_date and end_date:
        siswa_tabungan = siswa_tabungan.filter(tanggal__range=[start_date, end_date])

    # Mengambil data siswa dan total tabungannya
    siswa_tabungan = siswa_tabungan.values('siswa__nama', 'siswa').annotate(total_tabungan=Sum('nominal'))

    return render(request, 'keuangan/admin/riwayat_tabungan.html', {
        'kelas_list': kelas_list,
        'selected_kelas': selected_kelas,
        'siswa_tabungan': siswa_tabungan,
    })

from django.core.files.storage import FileSystemStorage  # jangan lupa import

def penarikan_tabungan(request):
    siswa_tabungan = TabunganSiswa.objects.select_related('siswa') \
        .values('siswa__id', 'siswa__nama') \
        .annotate(total_tabungan=Sum('nominal'))

    if request.method == 'POST':
        tanggal_penarikan = request.POST.get('tanggal_penarikan')
        siswa_ditarik_ids = request.POST.getlist('siswa_ditarik')

        for siswa_id in siswa_ditarik_ids:
            if not siswa_id.isdigit():
                continue

            try:
                siswa = Siswa.objects.get(id=siswa_id)
            except Siswa.DoesNotExist:
                continue

            nominal_str = request.POST.get(f'nominal_{siswa_id}', '0').replace('.', '').replace(',', '')
            nominal = int(nominal_str) if nominal_str.isdigit() else 0

            if nominal <= 0:
                continue  # Nominal tidak boleh kosong / 0

            # Cek total tabungan siswa
            total_tabungan = TabunganSiswa.objects.filter(siswa=siswa, tarik=False).aggregate(Sum('nominal'))['nominal__sum'] or 0

            if nominal > total_tabungan:
                messages.error(request, f"Nominal penarikan melebihi saldo tabungan {siswa.nama}.")
                continue

            # 1. Simpan ke PenarikanTabungan
            PenarikanTabungan.objects.create(
                siswa=siswa,
                tanggal_penarikan=tanggal_penarikan,
                jumlah_ditarik=nominal,
                keterangan=f"Penarikan sebesar Rp{nominal:,}"
            )

            # 2. Kurangi saldo tabungan
            # Hapus data TabunganSiswa atau tandai sebagai sudah ditarik
            tabungan_entries = TabunganSiswa.objects.filter(siswa=siswa, tarik=False).order_by('tanggal')

            sisa_tarik = nominal
            for entry in tabungan_entries:
                if sisa_tarik <= 0:
                    break
                if entry.nominal <= sisa_tarik:
                    sisa_tarik -= entry.nominal
                    entry.nominal = 0
                    entry.tarik = True
                else:
                    entry.nominal -= sisa_tarik
                    sisa_tarik = 0
                entry.save()

        messages.success(request, "Penarikan berhasil disimpan.")
        return redirect('penarikan_tabungan')

    return render(request, 'keuangan/admin/penarikan_tabungan.html', {
        'siswa_tabungan': siswa_tabungan
    })

