from .models import PembayaranSPP

def generate_tagihan_spp(siswa):
    BULAN_LIST = [
        ('01', 'Januari'), ('02', 'Februari'), ('03', 'Maret'), ('04', 'April'),
        ('05', 'Mei'), ('06', 'Juni'), ('07', 'Juli'), ('08', 'Agustus'),
        ('09', 'September'), ('10', 'Oktober'), ('11', 'November'), ('12', 'Desember'),
    ]

    # Nominal per bulan
    NOMINAL_SPP_PER_BULAN = {
        '01': 500000,
        '02': 500000,
        '03': 500000,
        '04': 500000,
        '05': 500000,
        '06': 500000,
        '07': 750000,  # Juli daftar ulang lebih mahal
        '08': 500000,
        '09': 500000,
        '10': 500000,
        '11': 500000,
        '12': 500000,
    }


    for kode_bulan, nama_bulan in BULAN_LIST:
        if not PembayaranSPP.objects.filter(siswa=siswa, bulan=kode_bulan).exists():
            PembayaranSPP.objects.create(
                siswa=siswa,
                bulan=kode_bulan,
                jumlah_bayar=NOMINAL_SPP_PER_BULAN.get(kode_bulan, 500000),  # default 500rb kalau bulan gak ketemu
                status_bayar='belum lunas',
            )
