-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Waktu pembuatan: 06 Apr 2026 pada 02.34
-- Versi server: 8.0.30
-- Versi PHP: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Basis data: `db_absensi`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `absensi`
--

CREATE TABLE `absensi` (
  `id_absensi` int NOT NULL,
  `id_siswa` int DEFAULT NULL,
  `tanggal` date NOT NULL,
  `status` enum('tidak hadir','hadir','izin','sakit','alfa') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'tidak hadir',
  `keterangan` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `absensi`
--

INSERT INTO `absensi` (`id_absensi`, `id_siswa`, `tanggal`, `status`, `keterangan`) VALUES
(7, 7, '2026-03-18', 'hadir', ''),
(8, 7, '2026-04-02', 'izin', 'adalah'),
(9, 8, '2026-04-02', 'sakit', ''),
(10, 9, '2026-04-02', 'hadir', ''),
(11, 10, '2026-04-02', 'hadir', ''),
(12, 8, '2026-04-03', 'hadir', ''),
(13, 9, '2026-04-03', 'sakit', ''),
(14, 7, '2026-04-03', 'alfa', ''),
(15, 10, '2026-04-03', 'izin', ''),
(16, 8, '2026-04-04', 'sakit', ''),
(17, 9, '2026-04-04', 'hadir', ''),
(18, 7, '2026-04-04', 'izin', ''),
(19, 10, '2026-04-04', 'alfa', ''),
(20, 11, '2026-04-04', 'hadir', '');

-- --------------------------------------------------------

--
-- Struktur dari tabel `kelas`
--

CREATE TABLE `kelas` (
  `id_kelas` int NOT NULL,
  `nama_kelas` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `kelas`
--

INSERT INTO `kelas` (`id_kelas`, `nama_kelas`) VALUES
(1, 'X DKV'),
(2, 'XI RPL'),
(3, 'XII RPL'),
(4, 'X AMP');

-- --------------------------------------------------------

--
-- Struktur dari tabel `siswa`
--

CREATE TABLE `siswa` (
  `id_siswa` int NOT NULL,
  `nama` varchar(100) NOT NULL,
  `nis` varchar(20) DEFAULT NULL,
  `id_kelas` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `siswa`
--

INSERT INTO `siswa` (`id_siswa`, `nama`, `nis`, `id_kelas`) VALUES
(7, 'ihsan', '00000000', 2),
(8, 'hafiz', '345665456', 4),
(9, 'dio', '98767656765', 1),
(10, 'ishaq', '09865699', 2),
(11, 'ahmad', '765432345', 3);

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','siswa') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`) VALUES
(4, 'ishaq', '$2b$12$lvlS1cJ9GsbZc/o3m6VFj.pZid7ZnFFB9unEnn93TfkP3mHmBon.i', 'admin'),
(7, 'ihsan', '$2b$12$hUoW1Tr15f/MpJA7TyvQg.aunHhUj150hIvqXNCI5Bp9HX7gp/90.', 'siswa'),
(8, 'hafiz', '$2b$12$In80grpsZ.jC6gGs2fBU7eWdu6GZU0B4uPWWdwm1ZQF/9DaF7QesG', 'siswa'),
(9, 'dio', '$2b$12$zXVESy.adRYJVvE6s1jwxOMiEhGu1J9x/wvhdEYr01c3vVO/bgTTS', 'siswa'),
(10, 'ishaq', '$2b$12$y22Wt8d4n/VY09S2vlZbHOFIk/esdIybfUCWVemOpLiRm2HTLe6jm', 'siswa'),
(11, 'ahmad', '$2b$12$vejdlREoMbfTyn/f.s8sT.0j5F1f0TIJl/mFjCAdoSQ5vPFMzdvLK', 'siswa');

--
-- Indeks untuk tabel yang dibuang
--

--
-- Indeks untuk tabel `absensi`
--
ALTER TABLE `absensi`
  ADD PRIMARY KEY (`id_absensi`),
  ADD KEY `id_siswa` (`id_siswa`);

--
-- Indeks untuk tabel `kelas`
--
ALTER TABLE `kelas`
  ADD PRIMARY KEY (`id_kelas`);

--
-- Indeks untuk tabel `siswa`
--
ALTER TABLE `siswa`
  ADD PRIMARY KEY (`id_siswa`),
  ADD UNIQUE KEY `nis` (`nis`),
  ADD KEY `id_kelas` (`id_kelas`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `absensi`
--
ALTER TABLE `absensi`
  MODIFY `id_absensi` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT untuk tabel `kelas`
--
ALTER TABLE `kelas`
  MODIFY `id_kelas` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `siswa`
--
ALTER TABLE `siswa`
  MODIFY `id_siswa` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `absensi`
--
ALTER TABLE `absensi`
  ADD CONSTRAINT `absensi_ibfk_1` FOREIGN KEY (`id_siswa`) REFERENCES `siswa` (`id_siswa`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `siswa`
--
ALTER TABLE `siswa`
  ADD CONSTRAINT `siswa_ibfk_1` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
