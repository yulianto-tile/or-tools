from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from ortools.sat.python import cp_model
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp
import numpy as np

app = FastAPI(
    title="Sistem Penjadwalan Skripsi Mahasiswa Berbasis Google OR-Tools",
    version="2.0.0",
    description="API untuk penjadwalan ujian skripsi dengan constraint programming"
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Mahasiswa(BaseModel):
    nama: str = Field(..., description="Nama mahasiswa")
    judul: str = Field(..., description="Judul skripsi")
    bidang: str = Field(..., description="Bidang riset skripsi")
    pembimbing1: str = Field(..., description="Nama dosen pembimbing 1")
    pembimbing2: str = Field(..., description="Nama dosen pembimbing 2")

class Dosen(BaseModel):
    nama: str = Field(..., description="Nama dosen")
    bidang: List[str] = Field(..., description="List bidang riset yang dikuasai")

class AvailabilitasDosen(BaseModel):
    nama: str = Field(..., description="Nama dosen")
    available: List[str] = Field(..., description="List sesi yang tersedia (format: 'Hari HH.MM-HH.MM')")

class PenjadwalanRequest(BaseModel):
    mahasiswa: List[Mahasiswa] = Field(..., description="Daftar mahasiswa yang akan ujian")
    dosen: List[Dosen] = Field(..., description="Daftar dosen dengan bidang riset")
    availabilitas_dosen: List[AvailabilitasDosen] = Field(..., description="Availabilitas setiap dosen")
    ruangan: List[str] = Field(default=["Lab RPL", "Lab Jarkom"], description="Daftar ruangan tersedia")
    hari: List[str] = Field(default=["Senin", "Selasa", "Rabu", "Kamis", "Jumat"], description="Hari kerja")
    waktu: List[str] = Field(
        default=["08.00-10.00", "10.00-12.00", "13.00-15.00", "15.00-17.00"],
        description="Slot waktu per hari"
    )
    max_time_seconds: Optional[int] = Field(default=60, description="Maksimal waktu solving (detik)")

class JadwalUjian(BaseModel):
    nama: str
    judul: str
    bidang: str
    pembimbing1: str
    pembimbing2: str
    penguji1: str
    penguji2: str
    sesi: str
    ruang: str

class PenjadwalanResponse(BaseModel):
    status: str
    message: str
    total_mahasiswa: int
    mahasiswa_terjadwal: int
    jadwal: List[JadwalUjian]

class DistanceMatrix(BaseModel):
    matrix: list[list[float]]
    num_vehicles: int = 1
    depot: int = 0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_dosen_dengan_bidang(bidang_riset: str, dosen_data: List[Dict]) -> List[str]:
    """Mendapatkan daftar dosen yang memiliki bidang riset tertentu"""
    return [d["nama"] for d in dosen_data if bidang_riset in d["bidang"]]

def is_dosen_available(nama_dosen: str, sesi: str, availabilitas: Dict[str, List[str]]) -> bool:
    """Mengecek apakah dosen tersedia di sesi tertentu"""
    return sesi in availabilitas.get(nama_dosen, [])

# ============================================================================
# CORE SCHEDULING FUNCTION
# ============================================================================

def solve_penjadwalan_skripsi_internal(
    mahasiswa_data: List[Dict],
    dosen_data: List[Dict],
    availabilitas_dosen: Dict[str, List[str]],
    sesi_data: List[str],
    ruangan_data: List[str],
    max_time_seconds: int = 60
) -> Optional[List[Dict]]:
    """
    Fungsi internal untuk menyelesaikan masalah penjadwalan skripsi
    """
    
    # Inisialisasi model
    model = cp_model.CpModel()
    
    # Indices
    num_mahasiswa = len(mahasiswa_data)
    num_sesi = len(sesi_data)
    num_ruangan = len(ruangan_data)
    num_dosen = len(dosen_data)
    
    # Validasi: cek apakah ada mahasiswa
    if num_mahasiswa == 0:
        return []
    
    # ========================================================================
    # VARIABEL KEPUTUSAN
    # ========================================================================
    
    # jadwal[m][s][r] = 1 jika mahasiswa m dijadwalkan di sesi s dan ruang r
    jadwal = {}
    for m in range(num_mahasiswa):
        for s in range(num_sesi):
            for r in range(num_ruangan):
                jadwal[(m, s, r)] = model.NewBoolVar(f'jadwal_m{m}_s{s}_r{r}')
    
    # penguji[m][d][i] = 1 jika dosen d adalah penguji ke-i untuk mahasiswa m
    penguji = {}
    for m in range(num_mahasiswa):
        bidang_mhs = mahasiswa_data[m]["bidang"]
        dosen_eligible = get_dosen_dengan_bidang(bidang_mhs, dosen_data)
        
        for d_idx, dosen_info in enumerate(dosen_data):
            if dosen_info["nama"] in dosen_eligible:
                for i in range(2):  # 2 penguji
                    penguji[(m, d_idx, i)] = model.NewBoolVar(f'penguji_m{m}_d{d_idx}_p{i}')
    
    # ========================================================================
    # CONSTRAINTS
    # ========================================================================
    
    # 1. Setiap mahasiswa dijadwalkan TEPAT 1 kali
    for m in range(num_mahasiswa):
        model.Add(sum(jadwal[(m, s, r)] for s in range(num_sesi) for r in range(num_ruangan)) == 1)
    
    # 2. Setiap sesi dan ruangan hanya untuk 1 mahasiswa
    for s in range(num_sesi):
        for r in range(num_ruangan):
            model.Add(sum(jadwal[(m, s, r)] for m in range(num_mahasiswa)) <= 1)
    
    # 3. Setiap mahasiswa memiliki TEPAT 2 penguji
    for m in range(num_mahasiswa):
        bidang_mhs = mahasiswa_data[m]["bidang"]
        dosen_eligible = get_dosen_dengan_bidang(bidang_mhs, dosen_data)
        
        # Tepat 1 penguji pertama
        eligible_vars_p1 = []
        for d_idx, dosen in enumerate(dosen_data):
            if dosen["nama"] in dosen_eligible:
                if (m, d_idx, 0) in penguji:
                    eligible_vars_p1.append(penguji[(m, d_idx, 0)])
        
        if eligible_vars_p1:
            model.Add(sum(eligible_vars_p1) == 1)
        
        # Tepat 1 penguji kedua
        eligible_vars_p2 = []
        for d_idx, dosen in enumerate(dosen_data):
            if dosen["nama"] in dosen_eligible:
                if (m, d_idx, 1) in penguji:
                    eligible_vars_p2.append(penguji[(m, d_idx, 1)])
        
        if eligible_vars_p2:
            model.Add(sum(eligible_vars_p2) == 1)
    
    # 4. Penguji TIDAK BOLEH sama dengan Pembimbing
    for m in range(num_mahasiswa):
        pembimbing1 = mahasiswa_data[m]["pembimbing1"]
        pembimbing2 = mahasiswa_data[m]["pembimbing2"]
        
        for d_idx, dosen in enumerate(dosen_data):
            if dosen["nama"] == pembimbing1 or dosen["nama"] == pembimbing2:
                for i in range(2):
                    if (m, d_idx, i) in penguji:
                        model.Add(penguji[(m, d_idx, i)] == 0)
    
    # 5. Kedua penguji harus BERBEDA
    for m in range(num_mahasiswa):
        for d_idx in range(num_dosen):
            if (m, d_idx, 0) in penguji and (m, d_idx, 1) in penguji:
                model.Add(penguji[(m, d_idx, 0)] + penguji[(m, d_idx, 1)] <= 1)
    
    # 6. Availabilitas Dosen
    for m in range(num_mahasiswa):
        pembimbing1 = mahasiswa_data[m]["pembimbing1"]
        pembimbing2 = mahasiswa_data[m]["pembimbing2"]
        
        for s in range(num_sesi):
            sesi_nama = sesi_data[s]
            
            # Pembimbing harus tersedia
            if not is_dosen_available(pembimbing1, sesi_nama, availabilitas_dosen):
                for r in range(num_ruangan):
                    model.Add(jadwal[(m, s, r)] == 0)
            
            if not is_dosen_available(pembimbing2, sesi_nama, availabilitas_dosen):
                for r in range(num_ruangan):
                    model.Add(jadwal[(m, s, r)] == 0)
            
            # Penguji harus tersedia
            for d_idx, dosen in enumerate(dosen_data):
                if not is_dosen_available(dosen["nama"], sesi_nama, availabilitas_dosen):
                    for i in range(2):
                        if (m, d_idx, i) in penguji:
                            for r in range(num_ruangan):
                                model.Add(jadwal[(m, s, r)] + penguji[(m, d_idx, i)] <= 1)
    
    # 7. Dosen tidak boleh di 2 tempat sekaligus
    for s in range(num_sesi):
        for d_idx, dosen_info in enumerate(dosen_data):
            dosen_nama = dosen_info["nama"]
            keterlibatan = []
            
            for m in range(num_mahasiswa):
                pembimbing1 = mahasiswa_data[m]["pembimbing1"]
                pembimbing2 = mahasiswa_data[m]["pembimbing2"]
                
                for r in range(num_ruangan):
                    if dosen_nama == pembimbing1 or dosen_nama == pembimbing2:
                        keterlibatan.append(jadwal[(m, s, r)])
                    
                    for i in range(2):
                        if (m, d_idx, i) in penguji:
                            is_both = model.NewBoolVar(f'both_m{m}_s{s}_r{r}_d{d_idx}_p{i}')
                            model.Add(jadwal[(m, s, r)] + penguji[(m, d_idx, i)] == 2).OnlyEnforceIf(is_both)
                            model.Add(jadwal[(m, s, r)] + penguji[(m, d_idx, i)] < 2).OnlyEnforceIf(is_both.Not())
                            keterlibatan.append(is_both)
            
            if keterlibatan:
                model.Add(sum(keterlibatan) <= 1)
    
    # ========================================================================
    # SOLVING
    # ========================================================================
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(max_time_seconds)
    status = solver.Solve(model)
    
    # ========================================================================
    # EXTRACT SOLUTION
    # ========================================================================
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        hasil = []
        
        for m in range(num_mahasiswa):
            for s in range(num_sesi):
                for r in range(num_ruangan):
                    if solver.Value(jadwal[(m, s, r)]) == 1:
                        # Cari penguji
                        penguji_list = []
                        for d_idx, dosen in enumerate(dosen_data):
                            for i in range(2):
                                if (m, d_idx, i) in penguji:
                                    if solver.Value(penguji[(m, d_idx, i)]) == 1:
                                        penguji_list.append((i, dosen["nama"]))
                        
                        penguji_list.sort()
                        
                        result = {
                            "nama": mahasiswa_data[m]["nama"],
                            "judul": mahasiswa_data[m]["judul"],
                            "bidang": mahasiswa_data[m]["bidang"],
                            "pembimbing1": mahasiswa_data[m]["pembimbing1"],
                            "pembimbing2": mahasiswa_data[m]["pembimbing2"],
                            "penguji1": penguji_list[0][1] if len(penguji_list) > 0 else "N/A",
                            "penguji2": penguji_list[1][1] if len(penguji_list) > 1 else "N/A",
                            "sesi": sesi_data[s],
                            "ruang": ruangan_data[r]
                        }
                        hasil.append(result)
        
        return hasil
    
    return None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    return {
        "message": "Sistem Penjadwalan Skripsi Mahasiswa Berbasis Google OR-Tools",
        "status": "running",
        "version": "2.0.0",
        "ortools_version": "9.12.4544",
        "endpoints": {
            "penjadwalan_skripsi": "/api/penjadwalan-skripsi",
            "health": "/health",
        }
    }

@app.get("/health")
def health_check():
    """
    Comprehensive health check untuk memastikan semua komponen sistem berjalan
    """
    import sys
    import platform
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "thesis-scheduling-api",
        "version": "2.0.0",
        "checks": {}
    }
    
    # 1. Check Python Version
    try:
        python_version = sys.version.split()[0]
        health_status["checks"]["python"] = {
            "status": "ok",
            "version": python_version,
            "platform": platform.platform()
        }
    except Exception as e:
        health_status["checks"]["python"] = {
            "status": "error",
            "message": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # 2. Check Memory Usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        health_status["checks"]["memory"] = {
            "status": "ok" if memory.percent < 90 else "warning",
            "usage_percent": round(memory.percent, 2),
            "available_mb": round(memory.available / (1024 * 1024), 2),
            "total_mb": round(memory.total / (1024 * 1024), 2)
        }
        if memory.percent >= 90:
            health_status["status"] = "degraded"
    except ImportError:
        health_status["checks"]["memory"] = {
            "status": "info",
            "message": "psutil not installed, memory check skipped"
        }
    except Exception as e:
        health_status["checks"]["memory"] = {
            "status": "error",
            "message": str(e)
        }
    
    # 3. Check Disk Space (optional)
    try:
        import psutil
        disk = psutil.disk_usage('/')
        health_status["checks"]["disk"] = {
            "status": "ok" if disk.percent < 90 else "warning",
            "usage_percent": round(disk.percent, 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2)
        }
        if disk.percent >= 90:
            health_status["status"] = "degraded"
    except ImportError:
        pass  # Skip if psutil not available
    except Exception as e:
        health_status["checks"]["disk"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Determine overall status
    error_count = sum(1 for check in health_status["checks"].values() 
                     if check.get("status") == "error")
    warning_count = sum(1 for check in health_status["checks"].values() 
                       if check.get("status") == "warning")
    
    if error_count > 0:
        health_status["status"] = "unhealthy"
    elif warning_count > 0:
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "healthy"
    
    health_status["summary"] = {
        "total_checks": len(health_status["checks"]),
        "errors": error_count,
        "warnings": warning_count
    }
    
    return health_status

@app.post("/api/penjadwalan-skripsi", response_model=PenjadwalanResponse)
def penjadwalan_skripsi(request: PenjadwalanRequest):
    """
    Endpoint untuk menyelesaikan masalah penjadwalan ujian skripsi.
    
    **Input:**
    - `mahasiswa`: List mahasiswa dengan nama, judul, bidang, dan 2 pembimbing
    - `dosen`: List dosen dengan nama dan bidang riset yang dikuasai
    - `availabilitas_dosen`: Availabilitas setiap dosen per sesi
    - `ruangan`: Daftar ruangan yang tersedia (default: Lab RPL, Lab Jarkom)
    - `hari`: Hari kerja (default: Senin-Jumat)
    - `waktu`: Slot waktu per hari (default: 4 slot)
    - `max_time_seconds`: Maksimal waktu solving (default: 60 detik)
    
    **Output:**
    - Status penjadwalan
    - Jadwal lengkap dengan penguji, sesi, dan ruangan
    
    **Constraints:**
    - Setiap mahasiswa dijadwalkan tepat 1 kali
    - Setiap mahasiswa memiliki 2 penguji dengan bidang riset yang sesuai
    - Penguji tidak boleh sama dengan pembimbing
    - Dosen hanya bisa di 1 tempat per sesi
    - Semua dosen yang terlibat harus tersedia di sesi tersebut
    """
    try:
        # Konversi Pydantic models ke dict
        mahasiswa_data = [
            {
                "nama": m.nama,
                "judul": m.judul,
                "bidang": m.bidang,
                "pembimbing1": m.pembimbing1,
                "pembimbing2": m.pembimbing2
            }
            for m in request.mahasiswa
        ]
        
        dosen_data = [
            {
                "nama": d.nama,
                "bidang": d.bidang
            }
            for d in request.dosen
        ]
        
        # Buat dict availabilitas
        availabilitas_dict = {
            av.nama: av.available
            for av in request.availabilitas_dosen
        }
        
        # Generate sesi
        sesi_data = [f"{h} {w}" for h in request.hari for w in request.waktu]
        
        # Validasi input
        if not mahasiswa_data:
            raise HTTPException(status_code=400, detail="Daftar mahasiswa tidak boleh kosong")
        
        if not dosen_data:
            raise HTTPException(status_code=400, detail="Daftar dosen tidak boleh kosong")
        
        if not request.ruangan:
            raise HTTPException(status_code=400, detail="Daftar ruangan tidak boleh kosong")
        
        # Validasi pembimbing ada di daftar dosen
        nama_dosen_set = {d["nama"] for d in dosen_data}
        for mhs in mahasiswa_data:
            if mhs["pembimbing1"] not in nama_dosen_set:
                raise HTTPException(
                    status_code=400,
                    detail=f"Pembimbing 1 '{mhs['pembimbing1']}' untuk mahasiswa '{mhs['nama']}' tidak ditemukan di daftar dosen"
                )
            if mhs["pembimbing2"] not in nama_dosen_set:
                raise HTTPException(
                    status_code=400,
                    detail=f"Pembimbing 2 '{mhs['pembimbing2']}' untuk mahasiswa '{mhs['nama']}' tidak ditemukan di daftar dosen"
                )
        
        # Solve
        hasil = solve_penjadwalan_skripsi_internal(
            mahasiswa_data=mahasiswa_data,
            dosen_data=dosen_data,
            availabilitas_dosen=availabilitas_dict,
            sesi_data=sesi_data,
            ruangan_data=request.ruangan,
            max_time_seconds=request.max_time_seconds
        )
        
        if hasil is not None:
            return PenjadwalanResponse(
                status="success",
                message=f"Berhasil menjadwalkan {len(hasil)} dari {len(mahasiswa_data)} mahasiswa",
                total_mahasiswa=len(mahasiswa_data),
                mahasiswa_terjadwal=len(hasil),
                jadwal=hasil
            )
        else:
            return PenjadwalanResponse(
                status="infeasible",
                message="Tidak ditemukan solusi yang memenuhi semua constraint. Kemungkinan: availabilitas dosen terbatas, kurang penguji dengan bidang yang sesuai, atau tidak cukup slot waktu/ruangan.",
                total_mahasiswa=len(mahasiswa_data),
                mahasiswa_terjadwal=0,
                jadwal=[]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")