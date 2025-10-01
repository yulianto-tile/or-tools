# 🎓 Sistem Penjadwalan Skripsi dengan Google OR-Tools

API untuk optimasi penjadwalan ujian skripsi mahasiswa menggunakan Google OR-Tools Constraint Programming (CP-SAT Solver).

## 🚀 Fitur Utama

- **Penjadwalan Otomatis**: Menjadwalkan ujian skripsi dengan mempertimbangkan berbagai constraint
- **Constraint Programming**: Menggunakan CP-SAT solver untuk masalah scheduling yang kompleks
- **RESTful API**: Interface yang mudah digunakan dengan FastAPI
- **Auto Documentation**: Swagger UI dan ReDoc terintegrasi

## 📋 Prerequisites

- Python 3.8+
- pip atau conda

## 🔧 Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Setup Virtual Environment

#### Menggunakan venv (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

#### Menggunakan conda

```bash
conda create -n thesis-scheduler python=3.9
conda activate thesis-scheduler
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
ortools==9.8.3296
numpy==1.24.3
psutil==5.9.6
```

### 4. Jalankan Server

```bash
uvicorn main:app --reload
```

Server akan berjalan di: `http://127.0.0.1:8000`

## 📚 Dokumentasi API

### Akses Dokumentasi Interaktif

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## 🏥 Endpoint: Health Check

### `GET /health`

Melakukan pengecekan kesehatan sistem secara komprehensif.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-10-01T10:30:00.123456",
  "service": "thesis-scheduling-api",
  "version": "2.0.0",
  "checks": {
    "python": {
      "status": "ok",
      "version": "3.9.7",
      "platform": "Windows-10-10.0.19045-SP0"
    },
    "ortools_cp_sat": {
      "status": "ok",
      "message": "CP-SAT solver operational",
      "solver_available": true
    },
    "ortools_routing": {
      "status": "ok",
      "message": "Routing solver operational",
      "solver_available": true
    },
    "ortools_linear": {
      "status": "ok",
      "message": "Linear solver operational",
      "solver_available": true
    },
    "memory": {
      "status": "ok",
      "usage_percent": 45.2,
      "available_mb": 8192.5,
      "total_mb": 16384.0
    },
    "disk": {
      "status": "ok",
      "usage_percent": 65.8,
      "free_gb": 125.3,
      "total_gb": 500.0
    }
  },
  "summary": {
    "total_checks": 6,
    "errors": 0,
    "warnings": 0
  }
}
```

#### Status Codes

- **healthy**: Semua komponen berjalan normal
- **degraded**: Ada warning (memory/disk usage tinggi)
- **unhealthy**: Ada error pada komponen kritis

#### Pengecekan yang Dilakukan

1. ✅ **Python Version**: Versi Python dan platform
2. ✅ **Memory Usage**: Penggunaan RAM sistem
3. ✅ **Disk Space**: Kapasitas disk

---

## 🎯 Endpoint: Penjadwalan Skripsi

### `POST /api/penjadwalan-skripsi`

Endpoint utama untuk menjadwalkan ujian skripsi mahasiswa dengan constraint programming.

#### Request Body

```json
{
  "mahasiswa": [
    {
      "nama": "Budi Santoso",
      "judul": "Pemanfaatan AI untuk Kehidupan",
      "bidang": "Machine Learning",
      "pembimbing1": "Dr. Eko Junirianto",
      "pembimbing2": "Dr. Imron"
    },
    {
      "nama": "Siti Nurhaliza",
      "judul": "Aplikasi Mobile E-Commerce",
      "bidang": "Pemrograman Mobile",
      "pembimbing1": "Dr. Eko Junirianto",
      "pembimbing2": "Dr. Annafi Frans"
    }
  ],
  "dosen": [
    {
      "nama": "Dr. Eko Junirianto",
      "bidang": ["Machine Learning", "Pemrograman Mobile"]
    },
    {
      "nama": "Dr. Imron",
      "bidang": ["Machine Learning", "IoT Programming"]
    },
    {
      "nama": "Dr. Yulianto",
      "bidang": ["Machine Learning", "Data Science"]
    },
    {
      "nama": "Dr. Annafi Frans",
      "bidang": ["Pemrograman Mobile", "Web Development"]
    }
  ],
  "availabilitas_dosen": [
    {
      "nama": "Dr. Eko Junirianto",
      "available": [
        "Senin 08.00-10.00",
        "Senin 10.00-12.00",
        "Selasa 08.00-10.00",
        "Rabu 13.00-15.00"
      ]
    },
    {
      "nama": "Dr. Imron",
      "available": [
        "Senin 10.00-12.00",
        "Selasa 08.00-10.00",
        "Rabu 08.00-10.00"
      ]
    }
  ],
  "ruangan": ["Lab RPL", "Lab Jarkom"],
  "hari": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"],
  "waktu": ["08.00-10.00", "10.00-12.00", "13.00-15.00", "15.00-17.00"],
  "max_time_seconds": 60
}
```

#### Response

```json
{
  "status": "success",
  "message": "Berhasil menjadwalkan 2 dari 2 mahasiswa",
  "total_mahasiswa": 2,
  "mahasiswa_terjadwal": 2,
  "jadwal": [
    {
      "nama": "Budi Santoso",
      "judul": "Pemanfaatan AI untuk Kehidupan",
      "bidang": "Machine Learning",
      "pembimbing1": "Dr. Eko Junirianto",
      "pembimbing2": "Dr. Imron",
      "penguji1": "Dr. Yulianto",
      "penguji2": "Dr. Annafi Frans",
      "sesi": "Senin 08.00-10.00",
      "ruang": "Lab RPL"
    },
    {
      "nama": "Siti Nurhaliza",
      "judul": "Aplikasi Mobile E-Commerce",
      "bidang": "Pemrograman Mobile",
      "pembimbing1": "Dr. Eko Junirianto",
      "pembimbing2": "Dr. Annafi Frans",
      "penguji1": "Dr. Rudi",
      "penguji2": "Dr. Bambang",
      "sesi": "Senin 10.00-12.00",
      "ruang": "Lab Jarkom"
    }
  ]
}
```

#### Constraint yang Diterapkan

1. ✅ Setiap mahasiswa dijadwalkan **tepat 1 kali**
2. ✅ Setiap mahasiswa memiliki **2 penguji** dengan bidang riset yang sesuai
3. ✅ Penguji **tidak boleh** sama dengan pembimbing
4. ✅ Kedua penguji harus **berbeda**
5. ✅ Dosen hanya bisa di **1 tempat** per sesi
6. ✅ Semua dosen (pembimbing & penguji) harus **tersedia** di sesi tersebut
7. ✅ Setiap sesi-ruangan maksimal untuk **1 ujian**

#### Error Handling

**Status 400 - Bad Request:**

```json
{
  "detail": "Pembimbing 1 'Dr. Eko' untuk mahasiswa 'Budi' tidak ditemukan di daftar dosen"
}
```

**Status Infeasible:**

```json
{
  "status": "infeasible",
  "message": "Tidak ditemukan solusi yang memenuhi semua constraint...",
  "total_mahasiswa": 5,
  "mahasiswa_terjadwal": 0,
  "jadwal": []
}
```

---

## 💻 Contoh Penggunaan dengan cURL

### Penjadwalan Skripsi

```bash
curl -X POST "http://127.0.0.1:8000/api/penjadwalan-skripsi" \
  -H "Content-Type: application/json" \
  -d '{
    "mahasiswa": [
      {
        "nama": "Budi Santoso",
        "judul": "AI untuk Prediksi Cuaca",
        "bidang": "Machine Learning",
        "pembimbing1": "Dr. Eko",
        "pembimbing2": "Dr. Imron"
      }
    ],
    "dosen": [
      {
        "nama": "Dr. Eko",
        "bidang": ["Machine Learning", "Data Science"]
      },
      {
        "nama": "Dr. Imron",
        "bidang": ["Machine Learning"]
      },
      {
        "nama": "Dr. Yulianto",
        "bidang": ["Machine Learning"]
      }
    ],
    "availabilitas_dosen": [
      {
        "nama": "Dr. Eko",
        "available": ["Senin 08.00-10.00", "Selasa 10.00-12.00"]
      },
      {
        "nama": "Dr. Imron",
        "available": ["Senin 08.00-10.00", "Rabu 08.00-10.00"]
      },
      {
        "nama": "Dr. Yulianto",
        "available": ["Senin 08.00-10.00"]
      }
    ],
    "ruangan": ["Lab RPL", "Lab Jarkom"],
    "max_time_seconds": 30
  }'
```

### Health Check

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

---

## 🐍 Contoh Penggunaan dengan Python

### Install Client Library

```bash
pip install requests
```

### Script Python

```python
import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Data penjadwalan
data = {
    "mahasiswa": [
        {
            "nama": "Ahmad Hidayat",
            "judul": "Sistem Rekomendasi E-Commerce",
            "bidang": "Machine Learning",
            "pembimbing1": "Dr. Eko Junirianto",
            "pembimbing2": "Dr. Imron"
        },
        {
            "nama": "Dewi Lestari",
            "judul": "Aplikasi Mobile Banking",
            "bidang": "Pemrograman Mobile",
            "pembimbing1": "Dr. Annafi Frans",
            "pembimbing2": "Dr. Rudi"
        }
    ],
    "dosen": [
        {
            "nama": "Dr. Eko Junirianto",
            "bidang": ["Machine Learning", "Data Science"]
        },
        {
            "nama": "Dr. Imron",
            "bidang": ["Machine Learning", "IoT Programming"]
        },
        {
            "nama": "Dr. Annafi Frans",
            "bidang": ["Pemrograman Mobile", "Web Development"]
        },
        {
            "nama": "Dr. Rudi",
            "bidang": ["Pemrograman Mobile", "UI/UX"]
        },
        {
            "nama": "Dr. Yulianto",
            "bidang": ["Machine Learning"]
        }
    ],
    "availabilitas_dosen": [
        {
            "nama": "Dr. Eko Junirianto",
            "available": ["Senin 08.00-10.00", "Senin 10.00-12.00", "Selasa 08.00-10.00"]
        },
        {
            "nama": "Dr. Imron",
            "available": ["Senin 08.00-10.00", "Selasa 10.00-12.00"]
        },
        {
            "nama": "Dr. Annafi Frans",
            "available": ["Senin 10.00-12.00", "Rabu 08.00-10.00"]
        },
        {
            "nama": "Dr. Rudi",
            "available": ["Senin 10.00-12.00", "Rabu 08.00-10.00"]
        },
        {
            "nama": "Dr. Yulianto",
            "available": ["Senin 08.00-10.00", "Kamis 08.00-10.00"]
        }
    ],
    "ruangan": ["Lab RPL", "Lab Jarkom"],
    "max_time_seconds": 60
}

# Kirim request
response = requests.post(f"{BASE_URL}/api/penjadwalan-skripsi", json=data)

# Print hasil
if response.status_code == 200:
    result = response.json()
    print(f"Status: {result['status']}")
    print(f"Mahasiswa terjadwal: {result['mahasiswa_terjadwal']}/{result['total_mahasiswa']}")
    print("\nJadwal:")
    print("-" * 100)

    for jadwal in result['jadwal']:
        print(f"Mahasiswa: {jadwal['nama']}")
        print(f"  Judul: {jadwal['judul']}")
        print(f"  Pembimbing: {jadwal['pembimbing1']}, {jadwal['pembimbing2']}")
        print(f"  Penguji: {jadwal['penguji1']}, {jadwal['penguji2']}")
        print(f"  Waktu: {jadwal['sesi']}")
        print(f"  Ruang: {jadwal['ruang']}")
        print("-" * 100)
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

---

## 🔍 Troubleshooting

### Problem: Tidak Ada Solusi (Infeasible)

**Kemungkinan penyebab:**

1. **Availabilitas dosen terlalu terbatas**
   - Solusi: Tambahkan lebih banyak slot waktu untuk dosen
2. **Tidak cukup penguji dengan bidang riset yang sesuai**
   - Solusi: Tambahkan dosen dengan bidang riset yang dibutuhkan
3. **Tidak cukup slot waktu/ruangan**
   - Solusi: Tambahkan ruangan atau perpanjang periode penjadwalan
4. **Konflik availabilitas pembimbing**
   - Solusi: Pastikan kedua pembimbing memiliki overlap waktu yang cukup

### Problem: Solver Timeout

**Solusi:**

- Tingkatkan `max_time_seconds` di request body
- Kurangi jumlah mahasiswa per batch
- Tambahkan lebih banyak ruangan untuk mengurangi constraint

### Problem: Memory Error

**Solusi:**

```bash
# Tingkatkan memory limit untuk uvicorn
uvicorn main:app --reload --limit-concurrency 10 --timeout-keep-alive 30
```

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                 │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │   Penjadwalan Skripsi Endpoint         │    │
│  │   - Validasi Input                     │    │
│  │   - Generate Constraints               │    │
│  │   - CP-SAT Solving                     │    │
│  │   - Extract Solution                   │    │
│  └────────────────────────────────────────┘    │
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │   VRP Endpoint (Routing)               │    │
│  └────────────────────────────────────────┘    │
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │   Linear Programming Endpoint          │    │
│  └────────────────────────────────────────┘    │
│                                                   │
│  ┌────────────────────────────────────────┐    │
│  │   Health Check (Comprehensive)         │    │
│  └────────────────────────────────────────┘    │
│                                                   │
└─────────────────────────────────────────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │   Google OR-Tools         │
        ├───────────────────────────┤
        │ - CP-SAT Solver           │
        │ - Routing Solver          │
        │ - Linear Solver (GLOP)    │
        └───────────────────────────┘
```

---

## 🧪 Testing

### Manual Testing dengan Swagger UI

1. Buka browser: http://127.0.0.1:8000/docs
2. Klik endpoint `/api/penjadwalan-skripsi`
3. Klik "Try it out"
4. Masukkan data sample
5. Klik "Execute"

### Automated Testing dengan pytest

```bash
pip install pytest httpx

# Buat file test_main.py
```

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()

def test_penjadwalan_basic():
    data = {
        "mahasiswa": [
            {
                "nama": "Test Student",
                "judul": "Test Thesis",
                "bidang": "Machine Learning",
                "pembimbing1": "Dr. A",
                "pembimbing2": "Dr. B"
            }
        ],
        "dosen": [
            {"nama": "Dr. A", "bidang": ["Machine Learning"]},
            {"nama": "Dr. B", "bidang": ["Machine Learning"]},
            {"nama": "Dr. C", "bidang": ["Machine Learning"]}
        ],
        "availabilitas_dosen": [
            {"nama": "Dr. A", "available": ["Senin 08.00-10.00"]},
            {"nama": "Dr. B", "available": ["Senin 08.00-10.00"]},
            {"nama": "Dr. C", "available": ["Senin 08.00-10.00"]}
        ]
    }

    response = client.post("/api/penjadwalan-skripsi", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] in ["success", "infeasible"]
```

```bash
# Jalankan test
pytest test_main.py -v
```

---

## 📈 Performance Tips

### 1. Batching

Untuk dataset besar, jadwalkan dalam batch:

```python
# Jadwalkan 10-20 mahasiswa per batch
for i in range(0, len(all_mahasiswa), 15):
    batch = all_mahasiswa[i:i+15]
    response = requests.post(url, json={"mahasiswa": batch, ...})
```

### 2. Caching

Untuk availabilitas dosen yang sama:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_schedule(mahasiswa_hash, dosen_hash):
    # Return cached result if available
    pass
```

### 3. Async Processing

Untuk multiple requests:

```python
import asyncio
import aiohttp

async def schedule_batch(session, data):
    async with session.post(url, json=data) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [schedule_batch(session, batch) for batch in batches]
        results = await asyncio.gather(*tasks)
```

---

## 📝 Changelog

### Version 2.0.0

- ✨ Menambahkan endpoint penjadwalan skripsi dengan CP-SAT
- ✨ Health check yang comprehensive
- ✨ Full validation untuk input data
- 📚 Dokumentasi lengkap dengan contoh

### Version 1.0.0

- 🎉 Initial release dengan VRP dan Linear Programming

---

## 🤝 Contributing

Kontribusi selalu welcome! Silakan:

1. Fork repository
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

---

## 📄 License

MIT License - Lihat file LICENSE untuk detail

---

## 👥 Authors

- **Tim Development** - Ridho, Fikri, Fariz, and Yulianto!

---

## 🙏 Acknowledgments

- Google OR-Tools Team
- FastAPI Framework
- Python Community

---

## 📞 Support

Untuk pertanyaan atau issues:

- 📧 Email: yulianto@politanisamarinda.ac.id
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Happy Scheduling! 🎓📅**
