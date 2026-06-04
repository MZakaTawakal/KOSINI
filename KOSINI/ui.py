import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# ==================== LOGIKA DATABASE (Sama seperti milik Anda) ====================
class Database:
    def __init__(self, db_name="kosan.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.buat_tabel()

    def buat_tabel(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pengguna (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                peran TEXT NOT NULL CHECK(peran IN ('admin', 'penghuni'))
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kamar (
                nomor_kamar TEXT PRIMARY KEY,
                tipe TEXT NOT NULL,
                harga REAL NOT NULL,
                status TEXT DEFAULT 'Kosong' CHECK(status IN ('Kosong', 'Terisi'))
            )
        ''')
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


# ==================== ANTARMUKA / UI (TKINTER) ====================
class KosAppGUI:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("Sistem Manajemen Kos-Kosan")
        self.root.geometry("600x500")
        
        self.user_aktif = None
        self.peran_aktif = None
        
        # Container utama untuk berganti halaman
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.buka_halaman_login()

    def bersihkan_frame(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # 1. HALAMAN LOGIN
    def buka_halaman_login(self):
        self.bersihkan_frame()
        
        tk.Label(self.main_container, text="SISTEM MANAJEMEN KOS", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Input Username
        tk.Label(self.main_container, text="Username:").pack(anchor="w", pady=2)
        entry_user = tk.Entry(self.main_container, font=("Arial", 11))
        entry_user.pack(fill="x", pady=5)
        
        # Input Password
        tk.Label(self.main_container, text="Password:").pack(anchor="w", pady=2)
        entry_pass = tk.Entry(self.main_container, show="*", font=("Arial", 11))
        entry_pass.pack(fill="x", pady=5)
        
        def proses_login():
            username = entry_user.get()
            password = entry_pass.get()
            user = self.db.ambil_satu("SELECT username, peran FROM pengguna WHERE username = ? AND password = ?", (username, password))
            
            if user:
                self.user_aktif = user[0]
                self.peran_aktif = user[1]
                if self.peran_aktif == 'admin':
                    self.buka_dashboard_admin()
                else:
                    self.buka_dashboard_penghuni()
            else:
                messagebox.showerror("Error", "Username atau Password salah!")

        tk.Button(self.main_container, text="Login", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), command=proses_login).pack(fill="x", pady=20)

    # 2. DASHBOARD ADMIN
    def buka_dashboard_admin(self):
        self.bersihkan_frame()
        tk.Label(self.main_container, text=f"Dashboard Admin ({self.user_aktif})", font=("Arial", 14, "bold"), fg="blue").pack(pady=10)
        
        # Tombol Fitur Admin
        tk.Button(self.main_container, text="Tambah Kamar Baru", command=self.ui_tambah_kamar).pack(fill="x", pady=5)
        tk.Button(self.main_container, text="Registrasi Penghuni Baru", command=self.ui_tambah_penghuni).pack(fill="x", pady=5)
        tk.Button(self.main_container, text="Input Pembayaran Kos", command=self.ui_input_pembayaran).pack(fill="x", pady=5)
        tk.Button(self.main_container, text="Lihat Laporan Keuangan", command=self.ui_laporan_keuangan).pack(fill="x", pady=5)
        
        tk.Button(self.main_container, text="Logout", bg="#f44336", fg="white", command=self.buka_halaman_login).pack(fill="x", pady=20)

    # 2a. Fitur Admin: Tambah Kamar
    def ui_tambah_kamar(self):
        win = tk.Toplevel(self.root)
        win.title("Tambah Kamar")
        win.geometry("300x250")
        
        tk.Label(win, text="Nomor Kamar:").pack(anchor="w", padx=10)
        e_no = tk.Entry(win)
        e_no.pack(fill="x", padx=10, pady=2)
        
        tk.Label(win, text="Tipe Kamar (Reguler/VIP):").pack(anchor="w", padx=10)
        e_tipe = tk.Entry(win)
        e_tipe.pack(fill="x", padx=10, pady=2)
        
        tk.Label(win, text="Harga per Bulan:").pack(anchor="w", padx=10)
        e_harga = tk.Entry(win)
        e_harga.pack(fill="x", padx=10, pady=2)
        
        def simpan():
            try:
                self.db.eksekusi("INSERT INTO kamar (nomor_kamar, tipe, harga) VALUES (?, ?, ?)", (e_no.get(), e_tipe.get(), float(e_harga.get())))
                messagebox.showinfo("Sukses", "Kamar Berhasil Ditambahkan!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Gagal", f"Error: {e}")
                
        tk.Button(win, text="Simpan", bg="green", fg="white", command=simpan).pack(pady=15)

    # 2b. Fitur Admin: Registrasi Penghuni
    def ui_tambah_penghuni(self):
        win = tk.Toplevel(self.root)
        win.title("Registrasi Penghuni")
        win.geometry("350x350")
        
        tk.Label(win, text="Username Baru:").pack(anchor="w", padx=10)
        e_user = tk.Entry(win)
        e_user.pack(fill="x", padx=10, pady=2)
        
        tk.Label(win, text="Password Baru:").pack(anchor="w", padx=10)
        e_pass = tk.Entry(win)
        e_pass.pack(fill="x", padx=10, pady=2)
        
        tk.Label(win, text="Nama Lengkap:").pack(anchor="w", padx=10)
        e_nama = tk.Entry(win)
        e_nama.pack(fill="x", padx=10, pady=2)
        
        tk.Label(win, text="No HP:").pack(anchor="w", padx=10)
        e_hp = tk.Entry(win)
        e_hp.pack(fill="x", padx=10, pady=2)
        
        # Pilihan Kamar Kosong
        tk.Label(win, text="Pilih Kamar yang Tersedia:").pack(anchor="w", padx=10)
        kamars = [k[0] for k in self.db.ambil_semua("SELECT nomor_kamar FROM kamar WHERE status='Kosong'")]
        combo_kamar = ttk.Combobox(win, values=kamars, state="readonly")
        combo_kamar.pack(fill="x", padx=10, pady=2)
        
        def simpan():
            try:
                self.db.eksekusi("INSERT INTO pengguna (username, password, peran) VALUES (?, ?, 'penghuni')", (e_user.get(), e_pass.get()))
                self.db.eksekusi("INSERT INTO detail_penghuni (username, nama_lengkap, no_hp, nomor_kamar) VALUES (?, ?, ?, ?)", (e_user.get(), e_nama.get(), e_hp.get(), combo_kamar.get()))
                self.db.eksekusi("UPDATE kamar SET status='Terisi' WHERE nomor_kamar=?", (combo_kamar.get(),))
                messagebox.showinfo("Sukses", "Penghuni berhasil didaftarkan!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Gagal", f"Error: {e}")
                
        tk.Button(win, text="Daftarkan", bg="green", fg="white", command=simpan).pack(pady=15)

    # 2c. Fitur Admin: Input Pembayaran
    def ui_input_pembayaran(self):
        win = tk.Toplevel(self.root)
        win.title("Input Pembayaran")
        win.geometry("300x250")
        
        tk.Label(win, text="Username Penghuni:").pack(anchor="w", padx=10)
        e_user = tk.Entry(win)
        e_user.pack(fill="x", padx=10, pady=2)
        
        tk.Label(win, text="Jumlah Bayar (Rp):").pack(anchor="w", padx=10)
        e_jumlah = tk.Entry(win)
        e_jumlah.pack(fill="x", padx=10, pady=2)
        
        tk.Label(win, text="Tanggal (YYYY-MM-DD):").pack(anchor="w", padx=10)
        e_tgl = tk.Entry(win)
        e_tgl.pack(fill="x", padx=10, pady=2)
        
        def proses():
            info = self.db.ambil_satu("SELECT k.harga FROM detail_penghuni dp JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar WHERE dp.username = ?", (e_user.get(),))
            if info:
                self.db.eksekusi("INSERT INTO pembayaran (username, jumlah, tanggal) VALUES (?, ?, ?)", (e_user.get(), float(e_jumlah.get()), e_tgl.get()))
                messagebox.showinfo("Sukses", f"Pembayaran Berhasil Dicatat!\nTagihan Bulanan: Rp {info[0]:,.0f}")
                win.destroy()
            else:
                messagebox.showerror("Gagal", "Username tidak ditemukan atau belum sewa kamar!")
                
        tk.Button(win, text="Catat Pembayaran", bg="green", fg="white", command=proses).pack(pady=15)

    # 2d. Fitur Admin: Laporan Keuangan
    def ui_laporan_keuangan(self):
        win = tk.Toplevel(self.root)
        win.title("Laporan Keuangan")
        win.geometry("500x350")
        
        # Tabel
        tree = ttk.Treeview(win, columns=("ID", "Username", "Jumlah", "Tanggal"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Username", text="Username")
        tree.heading("Jumlah", text="Jumlah")
        tree.heading("Tanggal", text="Tanggal")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        riwayat = self.db.ambil_semua("SELECT * FROM pembayaran")
        for r in riwayat:
            tree.insert("", "end", values=(r[0], r[1], f"Rp {r[2]:,.0f}", r[3]))
            
        total = self.db.ambil_satu("SELECT SUM(jumlah) FROM pembayaran")[0]
        total_val = total if total else 0
        tk.Label(win, text=f"TOTAL PENDAPATAN: Rp {total_val:,.0f}", font=("Arial", 12, "bold"), fg="green").pack(pady=10)

    # 3. DASHBOARD PENGHUNI
    def buka_dashboard_penghuni(self):
        self.bersihkan_frame()
        tk.Label(self.main_container, text=f"Selamat Datang, {self.user_aktif}", font=("Arial", 14, "bold"), fg="green").pack(pady=10)
        
        # Ambil info profil & Kamar
        info = self.db.ambil_satu("""
            SELECT dp.nama_lengkap, dp.no_hp, dp.nomor_kamar, k.tipe, k.harga 
            FROM detail_penghuni dp
            LEFT JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar
            WHERE dp.username = ?""", (self.user_aktif,))
        
        # Tampilkan Informasi
        frame_info = tk.LabelFrame(self.main_container, text="Informasi Sewa Anda", padx=10, pady=10)
        frame_info.pack(fill="x", pady=10)
        
        if info:
            tk.Label(frame_info, text=f"Nama Lengkap: {info[0]}").pack(anchor="w")
            tk.Label(frame_info, text=f"No. HP: {info[1]}").pack(anchor="w")
            tk.Label(frame_info, text=f"Nomor Kamar: {info[2] if info[2] else 'Belum Memilih'}").pack(anchor="w")
            tk.Label(frame_info, text=f"Tipe Kamar: {info[3] if info[3] else '-'}").pack(anchor="w")
            tk.Label(frame_info, text=f"Biaya Bulanan: Rp {info[4] if info[4] else 0:,.0f}").pack(anchor="w")
        else:
            tk.Label(frame_info, text="Data Anda belum dilengkapi oleh Admin.").pack(anchor="w")
            
        # Tombol Riwayat Pembayaran Mandiri
        def lihat_riwayat_saya():
            win = tk.Toplevel(self.root)
            win.title("Riwayat Pembayaran Saya")
            win.geometry("400x250")
            
            tree = ttk.Treeview(win, columns=("Tanggal", "Jumlah", "Status"), show="headings")
            tree.heading("Tanggal", text="Tanggal")
            tree.heading("Jumlah", text="Jumlah")
            tree.heading("Status", text="Status")
            tree.pack(fill="both", expand=True, padx=10, pady=10)
            
            riwayat = self.db.ambil_semua("SELECT tanggal, jumlah, status_bayar FROM pembayaran WHERE username = ?", (self.user_aktif,))
            for r in riwayat:
                tree.insert("", "end", values=(r[0], f"Rp {r[1]:,.0f}", r[2]))
                
        tk.Button(self.main_container, text="Lihat Riwayat Pembayaran Saya", command=lihat_riwayat_saya).pack(fill="x", pady=5)
        tk.Button(self.main_container, text="Logout", bg="#f44336", fg="white", command=self.buka_halaman_login).pack(fill="x", pady=15)


if __name__ == "__main__":
    root = tk.Tk()
    app = KosAppGUI(root)
    root.mainloop()