-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th10 30, 2025 lúc 04:34 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `secure_chat`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `message`
--

CREATE TABLE `message` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `aes_key_encrypted` text NOT NULL,
  `iv` text DEFAULT NULL,
  `tag` text DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `message`
--

INSERT INTO `message` (`id`, `sender_id`, `receiver_id`, `content`, `aes_key_encrypted`, `iv`, `tag`, `timestamp`) VALUES
(14, 46, 47, 'iFme', 'E35MgDWmAeBVm0n6Y8lUHY9oz6NcYZbysgvJtYFmvRHDRn7MAqD6lZ05kMI+INIluDCsTUoiac55JzyMjYD5capo+MFbQmHxXc40BkS1rpaK3u+80ICqACYh33oQrhCX3lt9b7Nd3iSNizeeVj4EXzEmnSdfpePyeQrOyPhGKGU=', 'B2oRRUV8217dbgJf', 'jNLS1c/fasM+PEYOTBZlzw==', '2025-10-30 14:41:04'),
(15, 48, 49, 'npcpRQY=', 'ZsoINOqwrWvcIEQD6OaUYVuP8XuXPAHHMDM1GFKQ55HJqzBvmq92DZnmof/FsyIXSaVyuNd9uFAmEyFS4gCfTlcI3Gvlec1SY18JsWgJTXJBta8RzMhbSXF/I0QFmXTgwH3RSvCr0ZTyNEIjSl5pDrkkgNPIY8ODT7wdpoTB6ceTgU32Hgl40Q0S/y5Gl8SKWTFU38u8y7jOgijI93xD8Hf8Z4JtYcUvOI4yi+e4qZo2QGCFSxLhWToyogrhoWy27+bbAqKWAIbOkA3hwN1DNej7i2aYZM5cy2K51ROH7vOObT0lqhVhLw9nMtGqHUySAhbbBVtMxbQIpU8HAu9e9g==', 'W8JXo+cI13N4PbaqOw/56A==', 'WNCwFeEe9q4foJwQIu2MQg==', '2025-10-30 14:45:56');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `public_key` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `user`
--

INSERT INTO `user` (`id`, `username`, `password_hash`, `public_key`, `created_at`) VALUES
(46, 'dsgđ', 'scrypt:32768:8:1$mDVByq8QBOGTVEN3$f816c38f92e7885025c2934a55cf1fa08b4fefe2b5147ce3a03b7597dd480f920eab030c822a0664848dddbf802714097864809e5fe4c253b3576d5e37171aab', '(65537, 24150705651729062677592603431929500035815870108418766788135740513909520234005240924608810970968792281523981397952567046748808887224503713498372680840359568650436759689903540587557319091048256339957829996989103782490600891219421626258327308596736418059075381376039369384824893857668752577136948919643522245291)', '2025-10-30 14:41:02'),
(47, '3253454', 'scrypt:32768:8:1$LPbGIaSVdIkqIH2R$91027d55ea4270936f92d7fb0da9eb38a37422899ca2779b9ebacbe1a40ce1a57cb5456c7c4c741574c052db52599195541db00b919c8ad4d0971495f62ea64f', '(65537, 29872576268859902046885000272094254295725993576635622497704533294391611768941536958670372840510989344779002571158173514357276088334168337443092711810391697888185526496956145528619784396011206386287690533845230904389677595532846517179843672447128344695161343758333334184097987085772787347123617433327572939817)', '2025-10-30 14:41:02'),
(48, 'dsdsdsdsdsd', 'scrypt:32768:8:1$VVX4wqQoiMT5OCqm$bdbd5ed0a55e356443f19dba731a08df55ce0277f3dbe637affa95f6176541d25aa9d9035ceb2e8fc54ee383c391cf5cbc63d76b0259ef3f115b09891baceb93', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5DZnnFiJ0uj095DwuLj2\nb9ehD/miCWzn99GeQ7/NwphS/1Lxg6XpUynSi2lYRS0f9dvBb7V46WZP9sjRVrHK\nXWRK6HDkqBv1c9LFIVhl6jgVTCcZ/blRp59vtCX32H1C9v6hAkZMvlwuaAr3IW2c\n8GzHSXdmUL+JnLh9pVP0pflb/4FBZbBexF5USqFm8uufgy0qCayrnxVStabr5NKh\nBQgpC7sixRk5ct9lvr2nlSkgGihvGAAmpNvQrIrFMhuV8D491osgDfWHKin+fTwA\nd88RG5/dplaOnyM83OL4sx/4y20RkbqyxXX7uul+ybrAS/cmtWdq3mmHAj1yR+FK\nEQIDAQAB\n-----END PUBLIC KEY-----', '2025-10-30 14:45:52'),
(49, 'đfdf', 'scrypt:32768:8:1$z6QewryVsx6C8OjC$28afe51d9b4785fa0cbdd83b2c45df6d6441706450e5079507deee9d85de0fb3300b39bbd6d73dd564893ec65fa47134655497ab37cd1fb5ef07191d53b7e0d3', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvkzi2LFjzvsxkGDu8gFL\nxLXwx1AztYxsKqrUM9qiriMfxgWP72NY7ETNdGkMApvsQL5ZXHlI7SfClqTCigf7\npmgLUjFPtFQ7xZwjbnMTJO5DUqlYdMQiBUCtt7d6CIozUz3KgwVzgmBlxFpEAy0V\noktpWb1p+kXrSSFISIBVeUicFlSHULKqf/WqQNWMneMXU/Pz05MuHmd22UojFY7L\nnbkUtvHhsOMPMwJVRg6eQPDkH0Jge4L1GOzjreaV4FqZyemBQ2+jjaqNDx2uwN7W\nqxqtzEjh1yjIeDvPoJ2qdu6CUdzY45xjzOehL5vuWKGLvpywplUHN8Q29K283Lu1\nwQIDAQAB\n-----END PUBLIC KEY-----', '2025-10-30 14:45:52');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Chỉ mục cho bảng `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `message`
--
ALTER TABLE `message`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT cho bảng `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `message_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `message_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
