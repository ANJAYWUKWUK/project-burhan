# Generated by Django 5.0.13 on 2025-05-21 07:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("keuangan", "0008_dspcicilan"),
    ]

    operations = [
        migrations.CreateModel(
            name="PPDB",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_tagihan", models.PositiveIntegerField(default=0)),
                ("total_terbayar", models.PositiveIntegerField(default=0)),
                ("sisa_tagihan", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[("Belum Lunas", "Belum Lunas"), ("Lunas", "Lunas")],
                        default="Belum Lunas",
                        max_length=20,
                    ),
                ),
                (
                    "siswa",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="keuangan.siswa"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PPDBCicilan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tanggal", models.DateField(auto_now_add=True)),
                ("jumlah", models.PositiveIntegerField()),
                (
                    "bukti_pembayaran",
                    models.FileField(blank=True, null=True, upload_to="bukti_ppdb/"),
                ),
                (
                    "ppdb",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="keuangan.ppdb"
                    ),
                ),
            ],
        ),
    ]
