document.addEventListener("DOMContentLoaded", function() {
    console.log("Dashboard.js loaded!");

    var pemasukanElement = document.getElementById("pemasukanData");
    var pengeluaranElement = document.getElementById("pengeluaranData");

    if (!pemasukanElement || !pengeluaranElement) {
        console.error("Elemen pemasukanData atau pengeluaranData tidak ditemukan!");
        return;
    }

    var pemasukanBulan = JSON.parse(pemasukanElement.textContent || "[]");
    var pengeluaranBulan = JSON.parse(pengeluaranElement.textContent || "[]");

    console.log("Pemasukan Bulanan:", pemasukanBulan);
    console.log("Pengeluaran Bulanan:", pengeluaranBulan);

    var ctx = document.getElementById("grafikKeuangan").getContext("2d");

    var labels = pemasukanBulan.map(item => "Bulan " + item.tanggal__month);
    var pemasukanData = pemasukanBulan.map(item => item.total);
    var pengeluaranData = pengeluaranBulan.map(item => item.total);

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Pemasukan",
                    data: pemasukanData,
                    backgroundColor: "green"
                },
                {
                    label: "Pengeluaran",
                    data: pengeluaranData,
                    backgroundColor: "red"
                }
            ]
        }
    });
});
