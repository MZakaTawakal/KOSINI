import sqlite3
from getpass import getpass
import os



class Database:
    def __init__(self, db_name="kosan.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.buat_tabel()

    def buat_tabel(self): # untuk semua user
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pengguna (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                peran TEXT NOT NULL CHECK(peran IN ('admin', 'penghuni'))
            )
        ''')
        
        # kamar
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kamar (
                nomor_kamar TEXT PRIMARY KEY,
                tipe TEXT NOT NULL,
                harga REAL NOT NULL,
                status TEXT DEFAULT 'Kosong' CHECK(status IN ('Kosong', 'Terisi'))
            )
        ''')
        
        # detail penghuni
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detail_penghuni (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                nama_lengkap TEXT NOT NULL,
                no_hp TEXT NOT NULL,
                nomor_kamar TEXT,
                FOREIGN KEY (username) REFERENCES pengguna(username) ON DELETE CASCADE,
                FOREIGN KEY (nomor_kamar) REFERENCES kamar(nomor_kamar) ON DELETE SET NULL
            )
        ''')
        
        # form pembayaran (admin side)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pembayaran (
                id_pembayaran INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                jumlah REAL NOT NULL,
                tanggal TEXT NOT NULL,
                status_bayar TEXT DEFAULT 'Lunas',
                FOREIGN KEY (username) REFERENCES pengguna(username)
            )
        ''')
        
        # akun admin dummy
        try:
            self.cursor.execute("INSERT INTO pengguna (username, password, peran) VALUES (?, ?, ?)", 
                                ('admin', 'admin123', 'admin'))
        except sqlite3.IntegrityError:
            pass
            
        self.conn.commit()

    def eksekusi(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor

    def ambil_semua(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def ambil_satu(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()


class KosApp:
    def __init__(self):
        self.db = Database()
        self.user_aktif = None
        self.peran_aktif = None

    def bersihkan_layar(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def menu_utama(self):
        while True:
            self.bersihkan_layar()
            print("=== SISTEM MANAJEMEN KOS-KOSAN ===")
            print("1. Login")
            print("2. Keluar")
            pilihan = input("Pilih menu [1-2]: ")
            
            if pilihan == '1':
                if self.login():
                    if self.peran_aktif == 'admin':
                        self.menu_admin()
                    elif self.peran_aktif == 'penghuni':
                        self.menu_penghuni()
            elif pilihan == '2':
                print("\nTerima kasih telah menggunakan aplikasi ini!")
                break
            else:
                input("Pilihan tidak valid. Tekan Enter untuk mencoba lagi...")

    def login(self):
        self.bersihkan_layar()
        print("=== HALAMAN LOGIN ===")
        username = input("Username: ")
        password = getpass("Password: ")
        
        user = self.db.ambil_satu("SELECT username, peran FROM pengguna WHERE username = ? AND password = ?", (username, password))
        
        if user:
            self.user_aktif = user[0]
            self.peran_aktif = user[1]
            return True
        else:
            input("Username atau Password salah! Tekan Enter...")
            return False

    # menu (admin)
    def menu_admin(self):
        while True:
            self.bersihkan_layar()
            print(f"=== DASHBOARD ADMIN (Login sebagai: {self.user_aktif}) ===")
            print("1. Kelola Data Kamar (CRUD)")
            print("2. Kelola Data Penghuni (CRUD)")
            print("3. Input Pembayaran")
            print("4. Laporan Keuangan")
            print("5. Logout")
            pilihan = input("Pilih menu [1-5]: ")

            if pilihan == '1':
                self.crud_kamar()
            elif pilihan == '2':
                self.crud_penghuni()
            elif pilihan == '3':
                self.input_pembayaran()
            elif pilihan == '4':
                self.laporan_keuangan()
            elif pilihan == '5':
                self.user_aktif, self.peran_aktif = None, None
                break

    def crud_kamar(self):
        while True:
            self.bersihkan_layar()
            print("=== KELOLA DATA KAMAR ===")
            print("1. Tambah Kamar")
            print("2. Lihat Semua Kamar")
            print("3. Update Data Kamar")
            print("4. Kembali")
            pilih = input("Pilih [1-4]: ")

            if pilih == '1':
                no = input("Nomor Kamar: ")
                tipe = input("Tipe Kamar (Reguler/VIP): ")
                harga = float(input("Harga per Bulan: Rp "))
                try:
                    self.db.eksekusi("INSERT INTO kamar (nomor_kamar, tipe, harga) VALUES (?, ?, ?)", (no, tipe, harga))
                    input("Kamar berhasil ditambahkan! Tekan Enter...")
                except sqlite3.IntegrityError:
                    input("Gagal! Nomor kamar sudah ada. Tekan Enter...")
            elif pilih == '2':
                kamars = self.db.ambil_semua("SELECT * FROM kamar")
                print("\nList Kamar:")
                print(f"{'No Kamar':<12} | {'Tipe':<10} | {'Harga':<12} | {'Status':<10}")
                print("-" * 50)
                for k in kamars:
                    print(f"{k[0]:<12} | {k[1]:<10} | Rp{k[2]:<10,.0f} | {k[3]:<10}")
                input("\nTekan Enter untuk kembali...")
            elif pilih == '3':
                no = input("Masukkan Nomor Kamar yang ingin diubah: ")
                tipe = input("Tipe Baru: ")
                harga = float(input("Harga Baru: Rp "))
                status = input("Status Baru (Kosong/Terisi): ")
                self.db.eksekusi("UPDATE kamar SET tipe=?, harga=?, status=? WHERE nomor_kamar=?", (tipe, harga, status, no))
                input("Data kamar berhasil diperbarui! Tekan Enter...")
            elif pilih == '4':
                break

    def crud_penghuni(self):
        while True:
            self.bersihkan_layar()
            print("=== KELOLA DATA PENGHUNI ===")
            print("1. Registrasi Penghuni Baru")
            print("2. Lihat Semua Penghuni")
            print("3. Edit Data Penghuni")
            print("4. Hapus Penghuni")
            print("5. Kembali")
            pilih = input("Pilih [1-5]: ")

            if pilih == '1':
                username = input("Buat Username Penghuni: ")
                password = input("Buat Password Penghuni: ")
                nama = input("Nama Lengkap: ")
                hp = input("No HP: ")
                
                # Tampilkan kamar kosong
                kamars = self.db.ambil_semua("SELECT nomor_kamar FROM kamar WHERE status='Kosong'")
                print("Kamar yang tersedia:", [k[0] for k in kamars])
                no_kamar = input("Pilih Nomor Kamar: ")

                try:
                    # Input ke tabel pengguna sistem
                    self.db.eksekusi("INSERT INTO pengguna (username, password, peran) VALUES (?, ?, 'penghuni')", (username, password))
                    # Input ke data detail
                    self.db.eksekusi("INSERT INTO detail_penghuni (username, nama_lengkap, no_hp, nomor_kamar) VALUES (?, ?, ?, ?)", (username, nama, hp, no_kamar))
                    # Update status kamar
                    self.db.eksekusi("UPDATE kamar SET status='Terisi' WHERE nomor_kamar=?", (no_kamar,))
                    input("Penghuni berhasil didaftarkan! Tekan Enter...")
                except sqlite3.IntegrityError:
                    input("Gagal! Username mungkin sudah digunakan. Tekan Enter...")

            elif pilih == '2':
                penghunis = self.db.ambil_semua("""
                    SELECT dp.username, dp.nama_lengkap, dp.no_hp, dp.nomor_kamar, k.harga 
                    FROM detail_penghuni dp 
                    LEFT JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar
                """)
                print("\nData Penghuni Aktif:")
                print(f"{'Username':<12} | {'Nama':<20} | {'No HP':<13} | {'Kamar':<8}")
                print("-" * 60)
                for p in penghunis:
                    print(f"{p[0]:<12} | {p[1]:<20} | {p[2]:<13} | {p[3] if p[3] else 'Belum Ada':<8}")
                input("\nTekan Enter...")

            elif pilih == '3':
                username = input("Masukkan Username penghuni yang akan diedit: ")
                nama = input("Nama Lengkap Baru: ")
                hp = input("No HP Baru: ")
                self.db.eksekusi("UPDATE detail_penghuni SET nama_lengkap=?, no_hp=? WHERE username=?", (nama, hp, username))
                input("Data berhasil diperbarui! Tekan Enter...")

            elif pilih == '4':
                username = input("Masukkan Username penghuni yang akan dihapus: ")
                # Cari tau kamarnya dulu untuk dikosongkan kembali
                info = self.db.ambil_satu("SELECT nomor_kamar FROM detail_penghuni WHERE username=?", (username,))
                if info and info[0]:
                    self.db.eksekusi("UPDATE kamar SET status='Kosong' WHERE nomor_kamar=?", (info[0],))
                
                self.db.eksekusi("DELETE FROM pengguna WHERE username=?", (username,))
                self.db.eksekusi("DELETE FROM detail_penghuni WHERE username=?", (username,))
                input("Penghuni berhasil dihapus dan kamar dikosongkan kembali! Tekan Enter...")
                
            elif pilih == '5':
                break

    def input_pembayaran(self):
        self.bersihkan_layar()
        print("=== INPUT PEMBAYARAN KOS ===")
        username = input("Masukkan Username Penghuni: ")
        
        # Cek tagihan berdasarkan kamar
        info = self.db.ambil_satu("""
            SELECT k.harga FROM detail_penghuni dp 
            JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar 
            WHERE dp.username = ?""", (username,))
        
        if info:
            print(f"Tagihan bulanan kamar: Rp {info[0]:,.0f}")
            jumlah = float(input("Jumlah bayar: Rp "))
            tanggal = input("Tanggal Bayar (YYYY-MM-DD): ")
            
            self.db.eksekusi("INSERT INTO pembayaran (username, jumlah, tanggal) VALUES (?, ?, ?)", (username, jumlah, tanggal))
            input("Pembayaran berhasil dicatat! Tekan Enter...")
        else:
            input("Username tidak ditemukan atau belum sewa kamar! Tekan Enter...")

    def laporan_keuangan(self):
        self.bersihkan_layar()
        print("=== LAPORAN KEUANGAN KOS-KOSAN ===")
        riwayat = self.db.ambil_semua("SELECT * FROM pembayaran")
        total = self.db.ambil_satu("SELECT SUM(jumlah) FROM pembayaran")[0]
        
        print(f"{'ID':<5} | {'Username':<12} | {'Jumlah':<15} | {'Tanggal':<12}")
        print("-" * 55)
        for r in riwayat:
            print(f"{r[0]:<5} | {r[1]:<12} | Rp{r[2]:<13,.0f} | {r[3]:<12}")
        print("-" * 55)
        print(f"TOTAL PENDAPATAN : Rp {total if total else 0:,.0f}")
        input("\nTekan Enter untuk kembali ke menu...")


    # ==================== MENU PENGHUNI ====================
    def menu_penghuni(self):
        while True:
            self.bersihkan_layar()
            print(f"=== DASHBOARD PENGHUNI (Selamat datang, {self.user_aktif}) ===")
            print("1. Lihat Profil & Informasi Kamar")
            print("2. Riwayat Pembayaran Saya")
            print("3. Logout")
            pilihan = input("Pilih menu [1-3]: ")

            if pilihan == '1':
                self.bersihkan_layar()
                info = self.db.ambil_satu("""
                    SELECT dp.nama_lengkap, dp.no_hp, dp.nomor_kamar, k.tipe, k.harga 
                    FROM detail_penghuni dp
                    LEFT JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar
                    WHERE dp.username = ?""", (self.user_aktif,))
                print("=== INFORMASI SEWA ===")
                if info:
                    print(f"Nama Lengkap : {info[0]}")
                    print(f"No. HP       : {info[1]}")
                    print(f"Nomor Kamar  : {info[2] if info[2] else 'Belum memilih'}")
                    print(f"Tipe Kamar   : {info[3] if info[3] else '-'}")
                    print(f"Biaya Bulanan: Rp {info[4] if info[4] else 0:,.0f}")
                else:
                    print("Data profil belum dilengkapi oleh Admin.")
                input("\nTekan Enter...")
                
            elif pilihan == '2':
                self.bersihkan_layar()
                print("=== RIWAYAT PEMBAYARAN ANDA ===")
                riwayat = self.db.ambil_semua("SELECT tanggal, jumlah, status_bayar FROM pembayaran WHERE username = ?", (self.user_aktif,))
                print(f"{'Tanggal':<12} | {'Jumlah':<15} | {'Status':<10}")
                print("-" * 45)
                for r in riwayat:
                    print(f"{r[0]:<12} | Rp{r[1]:<13,.0f} | {r[2]:<10}")
                input("\nTekan Enter...")
                
            elif pilihan == '3':
                self.user_aktif, self.peran_aktif = None, None
                break

if __name__ == "__main__":
    aplikasi = KosApp()
    aplikasi.menu_utama()