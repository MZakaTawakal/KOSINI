import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# Mengimpor class Database dari file main.py
from main import Database

class KosGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Manajemen Kos-Kosan")
        self.root.geometry("900x600")
        self.db = Database()
        self.user_aktif = None
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Frame Utama
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        self.tampilkan_login()

    def bersihkan_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==================== HALAMAN LOGIN ====================
    def tampilkan_login(self):
        self.bersihkan_frame()
        self.root.title("Login - Sistem Kos")
        
        frame_login = tk.Frame(self.main_frame, padx=50, pady=50)
        frame_login.pack(expand=True)
        
        tk.Label(frame_login, text="SISTEM MANAJEMEN KOS", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        tk.Label(frame_login, text="Username:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", pady=5)
        self.entry_username = ttk.Entry(frame_login, font=("Arial", 12))
        self.entry_username.grid(row=1, column=1, pady=5)
        
        tk.Label(frame_login, text="Password:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", pady=5)
        self.entry_password = ttk.Entry(frame_login, show="*", font=("Arial", 12))
        self.entry_password.grid(row=2, column=1, pady=5)
        
        btn_login = ttk.Button(frame_login, text="Login", command=self.proses_login)
        btn_login.grid(row=3, column=0, columnspan=2, pady=20, ipadx=20)

    def proses_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        user = self.db.ambil_satu("SELECT username, peran FROM pengguna WHERE username = ? AND password = ?", (username, password))
        
        if user:
            self.user_aktif = user[0]
            peran = user[1]
            if peran == 'admin':
                self.tampilkan_dashboard_admin()
            else:
                self.tampilkan_dashboard_penghuni()
        else:
            messagebox.showerror("Error", "Username atau Password salah!")

    def logout(self):
        self.user_aktif = None
        self.tampilkan_login()

    # ==================== DASHBOARD ADMIN ====================
    def tampilkan_dashboard_admin(self):
        self.bersihkan_frame()
        self.root.title(f"KOSINI MANAGEMENT - {self.user_aktif}")
        
        # Header
        header = tk.Frame(self.main_frame, bg="#2c3e50", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="KOSINI MANAGEMENT", fg="white", bg="#2c3e50", font=("Arial", 14, "bold")).pack(side="left", padx=20)
        ttk.Button(header, text="Logout", command=self.logout).pack(side="right", padx=20)
        
        # Notebook (Tabs)
        self.notebook_admin = ttk.Notebook(self.main_frame)
        self.notebook_admin.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_kamar()
        self.tab_penghuni()
        self.tab_pembayaran()
        self.tab_laporan()

    def tab_kamar(self):
        frame = ttk.Frame(self.notebook_admin)
        self.notebook_admin.add(frame, text="Kelola Data Kamar")
        
        # Form Input Kamar
        form_frame = ttk.LabelFrame(frame, text="Form Kamar", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(form_frame, text="No Kamar:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ent_no = ttk.Entry(form_frame)
        ent_no.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Tipe:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        cb_tipe = ttk.Combobox(form_frame, values=["Reguler", "VIP"], state="readonly")
        cb_tipe.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Harga (Rp):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        ent_harga = ttk.Entry(form_frame)
        ent_harga.grid(row=0, column=5, padx=5, pady=5)
        
        def simpan_kamar():
            try:
                self.db.eksekusi("INSERT INTO kamar (nomor_kamar, tipe, harga) VALUES (?, ?, ?)", 
                                 (ent_no.get(), cb_tipe.get(), float(ent_harga.get())))
                messagebox.showinfo("Sukses", "Kamar berhasil ditambahkan!")
                muat_data_kamar()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menambahkan kamar: {str(e)}")

        ttk.Button(form_frame, text="Tambah", command=simpan_kamar).grid(row=0, column=6, padx=10)

        # Tabel Kamar
        cols = ("No Kamar", "Tipe", "Harga", "Status")
        self.tv_kamar = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tv_kamar.heading(col, text=col)
            self.tv_kamar.column(col, width=150, anchor="center")
        self.tv_kamar.pack(fill="both", expand=True, padx=10, pady=10)
        
        def muat_data_kamar():
            for row in self.tv_kamar.get_children():
                self.tv_kamar.delete(row)
            for row in self.db.ambil_semua("SELECT * FROM kamar"):
                self.tv_kamar.insert("", "end", values=(row[0], row[1], f"Rp {row[2]:,.0f}", row[3]))
                
        muat_data_kamar()

    def tab_penghuni(self):
        frame = ttk.Frame(self.notebook_admin)
        self.notebook_admin.add(frame, text="Kelola Data Penghuni")
        
        form_frame = ttk.LabelFrame(frame, text="Form Tambah Penghuni", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # Inputs
        labels = ["Username", "Password", "Nama Lengkap", "No HP"]
        self.ent_penghuni = {}
        for i, text in enumerate(labels):
            tk.Label(form_frame, text=text+":").grid(row=i//2, column=(i%2)*2, padx=5, pady=5, sticky="e")
            ent = ttk.Entry(form_frame, show="*" if text == "Password" else "")
            ent.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5)
            self.ent_penghuni[text] = ent
            
        tk.Label(form_frame, text="Pilih Kamar:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        cb_kamar = ttk.Combobox(form_frame, state="readonly")
        cb_kamar.grid(row=2, column=1, padx=5, pady=5)
        
        def update_cb_kamar():
            kamars = self.db.ambil_semua("SELECT nomor_kamar FROM kamar WHERE status='Kosong'")
            cb_kamar['values'] = [k[0] for k in kamars]
            
        update_cb_kamar() # Load awal
        frame.bind("<Visibility>", lambda e: update_cb_kamar()) # Update setiap tab dibuka

        def tambah_penghuni():
            usr = self.ent_penghuni["Username"].get()
            pwd = self.ent_penghuni["Password"].get()
            nama = self.ent_penghuni["Nama Lengkap"].get()
            hp = self.ent_penghuni["No HP"].get()
            kmr = cb_kamar.get()
            
            if not all([usr, pwd, nama, hp, kmr]):
                messagebox.showwarning("Peringatan", "Semua data harus diisi!")
                return
                
            try:
                self.db.eksekusi("INSERT INTO pengguna (username, password, peran) VALUES (?, ?, 'penghuni')", (usr, pwd))
                self.db.eksekusi("INSERT INTO detail_penghuni (username, nama_lengkap, no_hp, nomor_kamar) VALUES (?, ?, ?, ?)", (usr, nama, hp, kmr))
                self.db.eksekusi("UPDATE kamar SET status='Terisi' WHERE nomor_kamar=?", (kmr,))
                messagebox.showinfo("Sukses", "Penghuni berhasil didaftarkan!")
                muat_data_penghuni()
                update_cb_kamar()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username sudah digunakan!")

        ttk.Button(form_frame, text="Daftarkan", command=tambah_penghuni).grid(row=2, column=2, columnspan=2, pady=10)

        # Tabel Penghuni
        cols = ("Username", "Nama Lengkap", "No HP", "Kamar", "Harga/Bulan")
        self.tv_penghuni = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tv_penghuni.heading(col, text=col)
            self.tv_penghuni.column(col, width=120)
        self.tv_penghuni.pack(fill="both", expand=True, padx=10, pady=10)
        
        def muat_data_penghuni():
            for row in self.tv_penghuni.get_children():
                self.tv_penghuni.delete(row)
            data = self.db.ambil_semua("""
                SELECT dp.username, dp.nama_lengkap, dp.no_hp, dp.nomor_kamar, k.harga 
                FROM detail_penghuni dp LEFT JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar
            """)
            for d in data:
                harga = f"Rp {d[4]:,.0f}" if d[4] else "-"
                self.tv_penghuni.insert("", "end", values=(d[0], d[1], d[2], d[3], harga))
                
        muat_data_penghuni()
        
        def hapus_penghuni():
            selected = self.tv_penghuni.selection()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih penghuni yang akan dihapus!")
                return
            
            item = self.tv_penghuni.item(selected[0])
            usr = item['values'][0]
            kmr = item['values'][3]
            
            if messagebox.askyesno("Konfirmasi", f"Yakin hapus penghuni {usr}?"):
                if kmr and kmr != 'None':
                    self.db.eksekusi("UPDATE kamar SET status='Kosong' WHERE nomor_kamar=?", (kmr,))
                self.db.eksekusi("DELETE FROM pengguna WHERE username=?", (usr,))
                muat_data_penghuni()
                update_cb_kamar()
                messagebox.showinfo("Sukses", "Penghuni dihapus.")

        ttk.Button(frame, text="Hapus Penghuni Terpilih", command=hapus_penghuni).pack(pady=5)

    def tab_pembayaran(self):
        frame = ttk.Frame(self.notebook_admin)
        self.notebook_admin.add(frame, text="Input Pembayaran")
        
        form_frame = tk.Frame(frame, pady=20)
        form_frame.pack()
        
        tk.Label(form_frame, text="Username Penghuni:", font=("Arial", 11)).grid(row=0, column=0, pady=10, sticky="e")
        cb_usr = ttk.Combobox(form_frame, state="readonly", width=25)
        cb_usr.grid(row=0, column=1, pady=10, padx=10)
        
        lbl_info = tk.Label(form_frame, text="-", fg="blue", font=("Arial", 10))
        lbl_info.grid(row=1, column=0, columnspan=2)
        
        tk.Label(form_frame, text="Jumlah Bayar (Rp):", font=("Arial", 11)).grid(row=2, column=0, pady=10, sticky="e")
        ent_jumlah = ttk.Entry(form_frame, width=28)
        ent_jumlah.grid(row=2, column=1, pady=10, padx=10)
        
        def update_cb_usr():
            usrs = self.db.ambil_semua("SELECT username FROM detail_penghuni")
            cb_usr['values'] = [u[0] for u in usrs]
            
        def get_tagihan(event):
            usr = cb_usr.get()
            info = self.db.ambil_satu("""SELECT k.harga FROM detail_penghuni dp 
                                       JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar WHERE dp.username = ?""", (usr,))
            if info:
                lbl_info.config(text=f"Tagihan Bulanan: Rp {info[0]:,.0f}")
                ent_jumlah.delete(0, tk.END)
                ent_jumlah.insert(0, str(int(info[0])))
                
        cb_usr.bind('<<ComboboxSelected>>', get_tagihan)
        frame.bind("<Visibility>", lambda e: update_cb_usr())
        
        def proses_bayar():
            usr = cb_usr.get()
            jumlah = ent_jumlah.get()
            tgl = date.today().strftime("%Y-%m-%d")
            
            if not usr or not jumlah:
                messagebox.showwarning("Peringatan", "Data tidak lengkap!")
                return
                
            self.db.eksekusi("INSERT INTO pembayaran (username, jumlah, tanggal) VALUES (?, ?, ?)", (usr, float(jumlah), tgl))
            messagebox.showinfo("Sukses", "Pembayaran berhasil dicatat!")
            ent_jumlah.delete(0, tk.END)
            cb_usr.set('')
            lbl_info.config(text="-")

        ttk.Button(form_frame, text="Simpan Pembayaran", command=proses_bayar).grid(row=3, column=0, columnspan=2, pady=20)

    def tab_laporan(self):
        frame = ttk.Frame(self.notebook_admin)
        self.notebook_admin.add(frame, text="Laporan Keuangan")
        
        cols = ("ID", "Username", "Jumlah", "Tanggal", "Status")
        self.tv_laporan = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tv_laporan.heading(col, text=col)
        self.tv_laporan.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_total = tk.Label(text="Total Pendapatan: Rp 0", font=("Arial", 14, "bold"))
        self.lbl_total.pack(pady=10)
        
        def muat_laporan():
            for row in self.tv_laporan.get_children():
                self.tv_laporan.delete(row)
            
            riwayat = self.db.ambil_semua("SELECT * FROM pembayaran ORDER BY id_pembayaran DESC")
            for r in riwayat:
                self.tv_laporan.insert("", "end", values=(r[0], r[1], f"Rp {r[2]:,.0f}", r[3], r[4]))
                
            total = self.db.ambil_satu("SELECT SUM(jumlah) FROM pembayaran")[0]
            self.lbl_total.config(text=f"Total Pendapatan: Rp {total if total else 0:,.0f}")
            
        frame.bind("<Visibility>", lambda e: muat_laporan())
        ttk.Button(frame, text="Refresh Data", command=muat_laporan).pack(pady=5)

    # ==================== DASHBOARD PENGHUNI ====================
    def tampilkan_dashboard_penghuni(self):
        self.bersihkan_frame()
        self.root.title(f"Dashboard Penghuni - {self.user_aktif}")
        
        # Header
        header = tk.Frame(self.main_frame, bg="#27ae60", pady=10)
        header.pack(fill="x")
        tk.Label(header, text=f"SELAMAT DATANG, {self.user_aktif.upper()}", fg="white", bg="#27ae60", font=("Arial", 14, "bold")).pack(side="left", padx=20)
        ttk.Button(header, text="Logout", command=self.logout).pack(side="right", padx=20)
        
        self.notebook_penghuni = ttk.Notebook(self.main_frame)
        self.notebook_penghuni.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_profil_penghuni()
        self.tab_riwayat_penghuni()

    def tab_profil_penghuni(self):
        frame = ttk.Frame(self.notebook_penghuni)
        self.notebook_penghuni.add(frame, text="Profil & Informasi Kamar")
        
        info = self.db.ambil_satu("""
            SELECT dp.nama_lengkap, dp.no_hp, dp.nomor_kamar, k.tipe, k.harga 
            FROM detail_penghuni dp
            LEFT JOIN kamar k ON dp.nomor_kamar = k.nomor_kamar
            WHERE dp.username = ?""", (self.user_aktif,))
            
        if info:
            data_tampil = [
                ("Nama Lengkap", info[0]),
                ("No. HP", info[1]),
                ("Nomor Kamar", info[2] if info[2] else "Belum mendapat kamar"),
                ("Tipe Kamar", info[3] if info[3] else "-"),
                ("Biaya Bulanan", f"Rp {info[4]:,.0f}" if info[4] else "-")
            ]
            
            kartu = tk.Frame(frame, bd=2, relief="groove", padx=30, pady=30)
            kartu.pack(expand=True)
            
            for i, (label, nilai) in enumerate(data_tampil):
                tk.Label(kartu, text=label, font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="w", pady=10, padx=10)
                tk.Label(kartu, text=":", font=("Arial", 12)).grid(row=i, column=1, pady=10)
                tk.Label(kartu, text=nilai, font=("Arial", 12)).grid(row=i, column=2, sticky="w", pady=10, padx=10)
        else:
            tk.Label(frame, text="Data profil Anda belum dilengkapi oleh Admin.", font=("Arial", 12)).pack(pady=50)

    def tab_riwayat_penghuni(self):
        frame = ttk.Frame(self.notebook_penghuni)
        self.notebook_penghuni.add(frame, text="Riwayat Pembayaran")
        
        cols = ("Tanggal", "Jumlah", "Status")
        tv_riwayat = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tv_riwayat.heading(col, text=col)
            tv_riwayat.column(col, anchor="center")
        tv_riwayat.pack(fill="both", expand=True, padx=20, pady=20)
        
        riwayat = self.db.ambil_semua("SELECT tanggal, jumlah, status_bayar FROM pembayaran WHERE username = ? ORDER BY id_pembayaran DESC", (self.user_aktif,))
        for r in riwayat:
            tv_riwayat.insert("", "end", values=(r[0], f"Rp {r[1]:,.0f}", r[2]))

if __name__ == "__main__":
    root = tk.Tk()
    app = KosGUI(root)
    root.mainloop()