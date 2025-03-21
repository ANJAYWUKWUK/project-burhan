from django import forms
from .models import Transaksi, Hutang, Piutang, Bank, Kategori

class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['tanggal', 'jenis', 'kategori', 'jumlah', 'keterangan', 'bukti', 'bank']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'jenis': forms.Select(choices=Transaksi.JENIS_CHOICES, attrs={'class': 'form-control'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bukti': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bank': forms.Select(attrs={'class': 'form-control'}),
        }

class HutangForm(forms.ModelForm):
    class Meta:
        model = Hutang
        fields = ['tanggal', 'nominal', 'keterangan']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nominal': forms.NumberInput(attrs={'class': 'form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PiutangForm(forms.ModelForm):
    class Meta:
        model = Piutang
        fields = ['tanggal', 'nominal', 'keterangan']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nominal': forms.NumberInput(attrs={'class': 'form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class HutangPiutangForm(forms.Form):
    TIPE_CHOICES = [
        ('hutang', 'Hutang'),
        ('piutang', 'Piutang'),
    ]
    tipe = forms.ChoiceField(choices=TIPE_CHOICES, widget=forms.RadioSelect)
    tanggal = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    nominal = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    keterangan = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['nama', 'nomor', 'pemilik', 'saldo']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Bank'}),
            'nomor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Rekening'}),
            'pemilik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Pemilik'}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Saldo Awal'}),
        }

class KategoriForm(forms.ModelForm):
    class Meta:
        model = Kategori
        fields = ['nama']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama kategori'}),
        }
