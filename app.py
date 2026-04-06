from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from datetime import datetime, date
import calendar
from functools import wraps
import bcrypt
from secrets import token_hex

app = Flask(__name__)
app.secret_key = token_hex(16)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_absensi'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Decorator untuk cek login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Halaman Login
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s ", (username, ))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login berhasil!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'siswa':
                return redirect(url_for('siswa_dashboard'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('login.html')
@app.route('/seeder')
def seeder():
    username = 'ishaq'
    password = '123'
    role = 'admin'
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT IGNORE INTO users (username,password,role) VALUES (%s,%s,%s)",
        (username, hashed.decode('utf-8'), role)
    )
    mysql.connection.commit()
    cursor.close()
    
    return "Seeder berhasil dijalankan"
# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('login'))

# ============= HALAMAN ADMIN =============
@app.route('/admin/dashboard',methods=['POST','GET'])
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    

    cursor = mysql.connection.cursor()
    today = date.today()
    
    # Hitung total
    cursor.execute("SELECT COUNT(*) as total FROM siswa")
    total_siswa = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM kelas")
    total_kelas = cursor.fetchone()['total']
    
    # Absensi hari ini
    cursor.execute("""
        SELECT a.*,a.status, s.nama, s.nis,k.nama_kelas 
        FROM absensi a 
        JOIN siswa s ON a.id_siswa = s.id_siswa 
        LEFT JOIN kelas k ON s.id_kelas = k.id_kelas 
        WHERE a.tanggal = %s
    """, (today,))
    absensi = cursor.fetchall()
    
    hadir = sum(1 for a in absensi if a['status'] == 'hadir')
    sakit = sum(1 for a in absensi if a['status'] == 'sakit')
    izin = sum(1 for a in absensi if a['status'] == 'izin')
    alfa = sum(1 for a in absensi if a['status'] == 'alfa')
    
    cursor.close()
    
    return render_template('admin/dashboard.html', 
                          total_siswa=total_siswa,
                          total_kelas=total_kelas,
                          hadir=hadir, sakit=sakit, izin=izin, alfa=alfa,
                          today=today.strftime('%d %B %Y'))

# Manajemen Siswa
@app.route('/admin/siswa')
@login_required
def admin_siswa():
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    cursor = mysql.connection.cursor()
    
    # Ambil semua siswa
    cursor.execute("""
        SELECT s.*, k.nama_kelas 
        FROM siswa s 
        LEFT JOIN kelas k ON s.id_kelas = k.id_kelas 
        ORDER BY s.nama
    """)
    siswa = cursor.fetchall()
    
    # Ambil semua kelas
    cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas")
    kelas = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/siswa.html', siswa=siswa, kelas=kelas)

# Tambah Siswa
@app.route('/admin/siswa/tambah', methods=['POST'])
@login_required
def tambah_siswa():
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    nama = request.form['nama']
    nis = request.form['nis']
    id_kelas = request.form['id_kelas']
    password=request.form['password']
    
    cursor = mysql.connection.cursor()
    
    hashed=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Cek NIS duplikat
    cursor.execute("SELECT * FROM siswa WHERE nis = %s", (nis,))
    if cursor.fetchone():
        flash('NIS sudah terdaftar', 'danger')
        return redirect(url_for('admin_siswa'))
    
    # Tambah siswa
    cursor.execute(
        "INSERT INTO siswa (nama, nis, id_kelas) VALUES (%s, %s, %s)",
        (nama, nis, id_kelas)
    )
    
    # Buat user untuk login siswa
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, 'siswa')",
        (nama,hashed.decode('utf-8'))
    )
    
    mysql.connection.commit()
    cursor.close()
    flash('Siswa berhasil ditambahkan', 'success')
    return redirect(url_for('admin_siswa'))
## ============= EDIT SISWA (Perbaikan) =============
@app.route('/admin/siswa/edit', methods=['POST'])
@login_required
def edit_siswa():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Ambil dari form (hidden input)
    id_siswa = request.form['id_siswa']
    nis = request.form['nis']
    nama = request.form['nama']
    id_kelas = request.form['id_kelas']
    
    # Validasi
    if not id_siswa or not nis or not nama:
        flash('Semua field harus diisi', 'danger')
        return redirect(url_for('admin_siswa'))
    
    cur = mysql.connection.cursor()
    
    # Cek duplikat NIS (kecuali untuk siswa ini sendiri)
    cur.execute("SELECT * FROM siswa WHERE nis = %s AND id_siswa != %s", (nis, id_siswa))
    if cur.fetchone():
        flash('NIS sudah digunakan siswa lain', 'danger')
        cur.close()
        return redirect(url_for('admin_siswa'))
    
    # Ambil NIS lama untuk update username di tabel users
    cur.execute("SELECT nis FROM siswa WHERE id_siswa = %s", (id_siswa,))
    siswa_lama = cur.fetchone()
    nis_lama = siswa_lama['nis'] if siswa_lama else None
    
    # Update siswa
    cur.execute(
        "UPDATE siswa SET nis=%s, nama=%s, id_kelas=%s WHERE id_siswa=%s",
        (nis, nama, id_kelas, id_siswa)
    )
    
    # Update username di tabel users berdasarkan NIS lama
    if nis_lama:
        cur.execute(
            "UPDATE users SET username=%s WHERE username=%s AND role='siswa'",
            (nis, nis_lama)
        )
    
    mysql.connection.commit()
    cur.close()
    
    flash('Data siswa berhasil diupdate', 'success')
    return redirect(url_for('admin_siswa'))


# ============= UBAH PASSWORD SENDIRI (untuk user yang login) =============
@app.route('/ubah_password', methods=['GET', 'POST'])
@login_required
def ubah_password():
    if request.method == 'POST':
        password_lama = request.form['password_lama'].encode('utf-8')
        password_baru = request.form['password_baru']
        konfirmasi = request.form['konfirmasi_password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()

        # Cek password lama dengan bcrypt
        if not bcrypt.checkpw(password_lama, user['password'].encode('utf-8')):
            flash('Password lama salah', 'danger')
            cursor.close()
            return redirect(url_for('admin_siswa' if session.get('role') == 'admin' else 'siswa_dashboard'))

        if password_baru != konfirmasi:
            flash('Konfirmasi password tidak cocok', 'danger')
            cursor.close()
            return redirect(url_for('admin_siswa' if session.get('role') == 'admin' else 'siswa_dashboard'))

        # Hash password baru
        hashed = bcrypt.hashpw(password_baru.encode('utf-8'), bcrypt.gensalt())

        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (hashed.decode('utf-8'), session['user_id'])
        )
        mysql.connection.commit()
        cursor.close()

        flash('Password berhasil diubah', 'success')
        
        if session.get('role') == 'admin':
            return redirect(url_for('admin_siswa'))
        else:
            return redirect(url_for('siswa_dashboard'))
    
    # Untuk GET request, redirect ke halaman yang sesuai
    if session.get('role') == 'admin':
        return redirect(url_for('admin_siswa'))
    else:
        return redirect(url_for('siswa_dashboard'))
# Hapus Siswa
@app.route('/admin/siswa/hapus/<int:id>')
@login_required
def hapus_siswa(id):
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    cursor = mysql.connection.cursor()
    
    # Ambil NIS untuk hapus user
    cursor.execute("SELECT nis FROM siswa WHERE id_siswa = %s", (id,))
    siswa = cursor.fetchone()
    
    if siswa:
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        cursor.execute("DELETE FROM siswa WHERE id_siswa = %s", (id,))
        mysql.connection.commit()
        flash('Siswa berhasil dihapus', 'success')
    
    cursor.close()
    return redirect(url_for('admin_siswa'))

# Halaman Absensi
@app.route('/admin/absensi')
@login_required
def admin_absensi():
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    cursor = mysql.connection.cursor()
    today = date.today()
    
    # Ambil filter
    tanggal = request.args.get('tanggal', today.strftime('%Y-%m-%d'))
    id_kelas = request.args.get('id_kelas', '')
    
    # Ambil semua kelas
    cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas")
    kelas = cursor.fetchall()
    
    # Ambil data siswa dengan status absensi
    if id_kelas:
        cursor.execute("""
            SELECT s.*, k.nama_kelas,
                   a.id_absensi, a.status, a.keterangan
            FROM siswa s
            LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
            LEFT JOIN absensi a ON s.id_siswa = a.id_siswa AND a.tanggal = %s
            WHERE s.id_kelas = %s
            ORDER BY s.nama
        """, (tanggal, id_kelas))
    else:
        cursor.execute("""
            SELECT s.*, k.nama_kelas,
                   a.id_absensi, a.status, a.keterangan
            FROM siswa s
            LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
            LEFT JOIN absensi a ON s.id_siswa = a.id_siswa AND a.tanggal = %s
            ORDER BY k.nama_kelas, s.nama
        """, (tanggal,))
    
    siswa = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/absensi.html', 
                          siswa=siswa, 
                          kelas=kelas, 
                          tanggal=tanggal, 
                          id_kelas=id_kelas)

# Simpan Absensi
@app.route('/admin/absensi/simpan', methods=['POST'])
@login_required
def simpan_absensi():
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    tanggal = request.form['tanggal']
    
    cursor = mysql.connection.cursor()
    
    # Proses setiap siswa
    for key in request.form:
        if key.startswith('status_'):
            id_siswa = key.replace('status_', '')
            status = request.form[key]
            keterangan = request.form.get(f'keterangan_{id_siswa}', '')
            
            # Cek apakah sudah ada
            cursor.execute(
                "SELECT * FROM absensi WHERE id_siswa = %s AND tanggal = %s",
                (id_siswa, tanggal)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update
                cursor.execute(
                    "UPDATE absensi SET status = %s, keterangan = %s WHERE id_absensi = %s",
                    (status, keterangan, existing['id_absensi'])
                )
            else:
                # Insert
                cursor.execute(
                    "INSERT INTO absensi (id_siswa, tanggal, status, keterangan) VALUES (%s, %s, %s, %s)",
                    (id_siswa, tanggal, status, keterangan)
                )
    
    mysql.connection.commit()
    cursor.close()
    flash('Absensi berhasil disimpan', 'success')
    return redirect(url_for('admin_absensi', tanggal=tanggal))

# Halaman Laporan
@app.route('/admin/laporan')
@login_required
def admin_laporan():
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    cursor = mysql.connection.cursor()
    
    # Filter
    bulan = int(request.args.get('bulan', date.today().month))
    tahun = int(request.args.get('tahun', date.today().year))
    id_kelas = request.args.get('id_kelas', '')
    
    # Ambil semua kelas
    cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas")
    kelas = cursor.fetchall()
    
    # Ambil data laporan
    if id_kelas:
        cursor.execute("""
            SELECT 
                s.nama, s.nis, k.nama_kelas,
                SUM(CASE WHEN a.status = 'hadir' THEN 1 ELSE 0 END) as hadir,
                SUM(CASE WHEN a.status = 'sakit' THEN 1 ELSE 0 END) as sakit,
                SUM(CASE WHEN a.status = 'izin' THEN 1 ELSE 0 END) as izin,
                SUM(CASE WHEN a.status = 'alfa' THEN 1 ELSE 0 END) as alfa
            FROM siswa s
            LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
            LEFT JOIN absensi a ON s.id_siswa = a.id_siswa 
                AND MONTH(a.tanggal) = %s AND YEAR(a.tanggal) = %s
            WHERE s.id_kelas = %s
            GROUP BY s.id_siswa
            ORDER BY s.nama
        """, (bulan, tahun, id_kelas))
    else:
        cursor.execute("""
            SELECT 
                s.nama, s.nis, k.nama_kelas,
                SUM(CASE WHEN a.status = 'hadir' THEN 1 ELSE 0 END) as hadir,
                SUM(CASE WHEN a.status = 'sakit' THEN 1 ELSE 0 END) as sakit,
                SUM(CASE WHEN a.status = 'izin' THEN 1 ELSE 0 END) as izin,
                SUM(CASE WHEN a.status = 'alfa' THEN 1 ELSE 0 END) as alfa
            FROM siswa s
            LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
            LEFT JOIN absensi a ON s.id_siswa = a.id_siswa 
                AND MONTH(a.tanggal) = %s AND YEAR(a.tanggal) = %s
            GROUP BY s.id_siswa
            ORDER BY k.nama_kelas, s.nama
        """, (bulan, tahun))
    
    laporan = cursor.fetchall()
    cursor.close()
    
    # Fungsi untuk nama bulan
    def nama_bulan(b):
        bulan_list = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                     'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        return bulan_list[b-1]
    
    return render_template('admin/laporan.html', 
                          laporan=laporan,
                          kelas=kelas,
                          bulan=bulan,
                          tahun=tahun,
                          id_kelas=id_kelas,
                          bulan_list=range(1, 13),
                          tahun_list=range(2020, 2031),
                          nama_bulan=nama_bulan)

# ============= HALAMAN SISWA =============
@app.route('/siswa/dashboard')
@login_required
def siswa_dashboard():
    if session.get('role') != 'siswa':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    username = session.get('username')
    today = date.today()
    
    # Ambil data siswa
    cursor.execute("""
        SELECT s.*, k.nama_kelas 
        FROM siswa s 
        LEFT JOIN kelas k ON s.id_kelas = k.id_kelas 
        WHERE nama = %s
    """, (username,))
    siswa = cursor.fetchone()
    
    if not siswa:
        flash('Data siswa tidak ditemukan', 'danger')
        return redirect(url_for('logout'))
    
    # Statistik bulan ini
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN status = 'hadir' THEN 1 ELSE 0 END) as hadir,
            SUM(CASE WHEN status = 'sakit' THEN 1 ELSE 0 END) as sakit,
            SUM(CASE WHEN status = 'izin' THEN 1 ELSE 0 END) as izin,
            SUM(CASE WHEN status = 'alfa' THEN 1 ELSE 0 END) as alfa
        FROM absensi 
        WHERE id_siswa = %s AND MONTH(tanggal) = %s AND YEAR(tanggal) = %s
    """, (siswa['id_siswa'], today.month, today.year))
    stat = cursor.fetchone()
    
    # Absensi hari ini
    cursor.execute("""
        SELECT * FROM absensi 
        WHERE id_siswa = %s AND tanggal = %s
    """, (siswa['id_siswa'], today))
    absensi_hari_ini = cursor.fetchone()
    
    # Riwayat 5 terakhir
    cursor.execute("""
        SELECT * FROM absensi 
        WHERE id_siswa = %s 
        ORDER BY tanggal DESC LIMIT 5
    """, (siswa['id_siswa'],))
    riwayat = cursor.fetchall()
    
    cursor.close()
    
    total_hari = calendar.monthrange(today.year, today.month)[1]
    hadir = stat['hadir'] or 0
    persentase = round((hadir / total_hari) * 100, 2) if total_hari > 0 else 0
    
    return render_template('siswa/dashboard.html',
                          siswa=siswa,
                          hadir=hadir,
                          sakit=stat['sakit'] or 0,
                          izin=stat['izin'] or 0,
                          alfa=stat['alfa'] or 0,
                          persentase=persentase,
                          absensi_hari_ini=absensi_hari_ini,
                          riwayat=riwayat,
                          today=today)
# ============= ROUTES MANAJEMEN KELAS =============
@app.route('/admin/kelas')
@login_required
def admin_kelas():
    """Halaman manajemen kelas"""
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    cursor = mysql.connection.cursor()
    
    # Ambil semua kelas dengan jumlah siswa
    cursor.execute("""
        SELECT k.*, COUNT(s.id_siswa) as jumlah_siswa 
        FROM kelas k 
        LEFT JOIN siswa s ON k.id_kelas = s.id_kelas 
        GROUP BY k.id_kelas 
        ORDER BY k.nama_kelas
    """)
    kelas = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/kelas.html', kelas=kelas)

@app.route('/admin/kelas/tambah', methods=['POST'])
@login_required
def admin_tambah_kelas():
    """Tambah kelas baru"""
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    nama_kelas = request.form['nama_kelas'].strip()
    
    if not nama_kelas:
        flash('Nama kelas harus diisi', 'danger')
        return redirect(url_for('admin_kelas'))
    
    cursor = mysql.connection.cursor()
    
    # Cek apakah kelas sudah ada
    cursor.execute("SELECT * FROM kelas WHERE nama_kelas = %s", (nama_kelas,))
    if cursor.fetchone():
        cursor.close()
        flash(f'Kelas {nama_kelas} sudah terdaftar', 'danger')
        return redirect(url_for('admin_kelas'))
    
    # Insert kelas
    cursor.execute("INSERT INTO kelas (nama_kelas) VALUES (%s)", (nama_kelas,))
    mysql.connection.commit()
    cursor.close()
    
    flash(f'Kelas {nama_kelas} berhasil ditambahkan', 'success')
    return redirect(url_for('admin_kelas'))

@app.route('/admin/kelas/edit/<int:id_kelas>', methods=['POST'])
@login_required
def admin_edit_kelas(id_kelas):
    """Edit kelas"""
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    nama_kelas = request.form['nama_kelas'].strip()
    
    if not nama_kelas:
        flash('Nama kelas harus diisi', 'danger')
        return redirect(url_for('admin_kelas'))
    
    cursor = mysql.connection.cursor()
    
    # Cek apakah nama kelas sudah digunakan kelas lain
    cursor.execute("SELECT * FROM kelas WHERE nama_kelas = %s AND id_kelas != %s", (nama_kelas, id_kelas))
    if cursor.fetchone():
        cursor.close()
        flash(f'Kelas {nama_kelas} sudah ada', 'danger')
        return redirect(url_for('admin_kelas'))
    
    # Update kelas
    cursor.execute("UPDATE kelas SET nama_kelas = %s WHERE id_kelas = %s", (nama_kelas, id_kelas))
    mysql.connection.commit()
    cursor.close()
    
    flash(f'Kelas berhasil diupdate menjadi {nama_kelas}', 'success')
    return redirect(url_for('admin_kelas'))

@app.route('/admin/kelas/hapus/<int:id_kelas>')
@login_required
def admin_hapus_kelas(id_kelas):
    """Hapus kelas"""
    if session.get('role') != 'admin':
        return redirect(url_for('siswa_dashboard'))
    
    cursor = mysql.connection.cursor()
    
    # Cek apakah ada siswa di kelas ini
    cursor.execute("SELECT COUNT(*) as jumlah FROM siswa WHERE id_kelas = %s", (id_kelas,))
    result = cursor.fetchone()
    jumlah_siswa = result['jumlah'] if result else 0
    
    if jumlah_siswa > 0:
        cursor.close()
        flash(f'Tidak dapat menghapus kelas karena masih ada {jumlah_siswa} siswa', 'danger')
        return redirect(url_for('admin_kelas'))
    
    # Hapus kelas
    cursor.execute("DELETE FROM kelas WHERE id_kelas = %s", (id_kelas,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Kelas berhasil dihapus', 'success')
    return redirect(url_for('admin_kelas'))
if __name__ == '__main__':
    app.run(debug=True)