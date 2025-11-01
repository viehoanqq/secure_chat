-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th10 01, 2025 lúc 03:06 PM
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
-- Cấu trúc bảng cho bảng `accounts`
--

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `public_key` text NOT NULL,
  `status` enum('online','offline') DEFAULT 'offline',
  `last_seen` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `accounts`
--

INSERT INTO `accounts` (`id`, `username`, `password_hash`, `public_key`, `status`, `last_seen`, `created_at`) VALUES
(1, 'admin', 'scrypt:32768:8:1$EHzc6AVxGvfbzl3X$0a2bed853e401959750e66c2f7fe4bc09ba4b6bce58405c13ecf27b9f282b51ce424060ae025a16deacefe3cbdc9115418a7d3ca854231c42a490d3e713142c6', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvgseqn4RJr0SNLpN4B8R\np1aldfuK+EPjKHoQD8DhY1HsbJP038U8HUlqMf8a/xQScBYTJLZutEdRFOYyBgYB\nvgK4K5zwICzP7h8rFcdnAcKy0rqzPYwfhwpINeS7QKRjWmQgb7VBK9ARmzcKxf/4\nUWl37gIRdUNI6peynslRcZc/UzIilL5ix8Dd5aHYCqNnpyAyVYBUEEvk9eZevyev\nzJLUzl4HS0WdoeP7GBvoaTu5eQmB1/OD/RSnyvM4jhRD6ht6rY338CYX5aVrKmHc\nMhTgDkD4RYuqskH0vhp+VmfvHDJgIwoaPKTdpSVy/usOHLp5TYtQJGAWWBgR/wMZ\npwIDAQAB\n-----END PUBLIC KEY-----', 'online', '2025-11-01 14:05:46', '2025-11-01 14:05:40'),
(2, 'test', 'scrypt:32768:8:1$jDwp4IBFh3jSFvDU$b4086aaff6a9adc3ae4c4ed05ce9591e16a04d20a69e2b6f067c5ea2de8f322acb96ac76f0c84b197faef14b697d4ecf402c873f3fc83fedd27b31fcd9f5c5f2', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0dUbNFG6oflC+3WomQf4\n5v8JOi5k716KUg6i2VcCMLbMqwHEscyX+zIm4OK6q/9za9rtvTwFoP/UUlS2zIZQ\nPmlM7UcQ4jjz4dZwQQVyyXZmFpEezvqGRnNkQtIxdEtGCk8tmackuOn3zwJHC4o5\nJNCrSZWsIFFqJr0YyzgWw9iWNIUuyBLCn+1JhrNHYOuIGgwKgUje5CqV3200WJnC\nnousokqXE0mRx+cl21umQ0aHvsxGv+j4fF/rjul2zBiEdGBxXxXe2tX8xVZ+y+Hn\ndmXKSp6XejtgNmJWkJ67qKYrfFK4xPH3LkJ+qr2kkS33kO3LZCGBc44irjj9Ukpn\nuwIDAQAB\n-----END PUBLIC KEY-----', 'online', '2025-11-01 14:06:18', '2025-11-01 14:06:11');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chats`
--

CREATE TABLE `chats` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `is_group` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `chats`
--

INSERT INTO `chats` (`id`, `name`, `is_group`, `created_at`) VALUES
(1, 'nguyen viet hoang', 0, '2025-11-01 14:06:22');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chat_members`
--

CREATE TABLE `chat_members` (
  `id` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `joined_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `chat_members`
--

INSERT INTO `chat_members` (`id`, `chat_id`, `account_id`, `joined_at`) VALUES
(1, 1, 2, '2025-11-01 14:06:22'),
(2, 1, 1, '2025-11-01 14:06:22');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `aes_key_encrypted` text NOT NULL,
  `iv` text NOT NULL,
  `tag` text NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `messages`
--

INSERT INTO `messages` (`id`, `chat_id`, `sender_id`, `content`, `aes_key_encrypted`, `iv`, `tag`, `timestamp`) VALUES
(1, 1, 2, '0KY=', '{\"2\": \"NWzyJDvoWgsRZg3r+b/2+OH8RsJ2BTDFQda/epJSvfwp8HG7ljLGDHxNQB5dm4ZNAR80IRPURL5qwkyVAf2hnQDskObzv6++mr5FNUciiHhbCHnWppU3EcHcWkotq0OD+RtJw9lbYoO+jQsYhrK1CXIFagTeQDDTTXaNMfFp76SUyticXZt03cxcgJQEp9dnCV/RmP24ZffWRNkMdDFt3n2btpFkaeyjnD3HlWxh7WVf6uKk7GNSn4Mg48mGgt7sDZP8D737H6+F8otC/eCfV+IOgqAf0zxj+QUgURp4dnGhph11xsAYzxe+JCdGiClDe1dzbs361ubiAZP+BKiBtg==\", \"1\": \"rKuT+pIvW1dPSVfKtGbWaNAReUg2uE+1NVIWNMI1+DqafldIQVXspndufQkp+YfKHuAtq0JwAKRaeE1WI9N5VzAwBga6CUOEFoIy4vEMcE8gqz5bKSy6rfuN1SVt5HToApuMiTreqQ0sDNz1OBRiathPiXJ2agUPDMnddgLRmy/FF+OUvijjJ7G2SongqduLqpH30xPwBdS7y96HEkjiQp76YEFVpEwjO7ErViadQcrq7YvxGQhXL739hiIVrv3VH1trmTDcmjDVQglgDqwFh2ycrCSmKh6exRUN4brBRhR0ktbscezoZOy1tJDRsVXrfwXQsyq2BTK9fHqcnz+FNQ==\"}', '4WzXpgSB6FoRBYtXiRwJRg==', '7ybhA5AaCaGrS/NROy5f9Q==', '2025-11-01 14:06:27'),
(2, 1, 1, 'Mmg=', '{\"2\": \"NYW+dt79SHWeFLicfFiI0CaNL3EtI9qd7ddB1MD1odlIIudLJ6NwTsuFMzUJoblNUm7kKs8qB/d5voH6NqlDuG17xIT95+Mtedg57Tqw5Re7m17IDenxzh6qweaFilnDVxDdz3JPuKo7m5n7NWTj/tCDIgC0iBltwv0REpF1zvklIGtDISKh7Fw+Y5YY0Vvr7TMLcVMGSK+tXQ1w6/qBDPb7bvC0j2ru104GpjJh5/izDgQ7afOasUFnHsfwpSEoqhS3sjgbqqhBrykXFI8qGwdvEwGgO2TioHEthPEZWEeDsIm0jfYGTMxcLD3Ev1HXKC0Ru8sI6cFUlNsHqKkhNg==\", \"1\": \"a8ks+1uvWqGWa7QUTl+5wfDf6aF5/3Ta5Yd2vJUgLpXJYbEslIf7NllKv6P00SIGH8fYmMAUFBtBPBKk1EcQjz1nPy/N5QE4elYArbyVNH45mPWzfaHXWXsrO+1imTDjqtlIhY4vA7DtjDTJiQiW5FRfuzvMhUO1cz+IG4nhTS8/OU9CUOkPirNWeSEN1Teh2emPtWbYu+YKWdWCIMYMvFOs2oxNwtcw3w564lOnMQ5QWsWnMe+XsI4GuS4bWgy/SInxrfvbG3cbNp1fbZq5+qDllizHqwyMhgP4btthL0bljPGWLfnDMSHAuXH4AH+hqDRcFzh6T1V1kaZXKqLW6A==\"}', 'GJcR8s8O+OmZj4ddIEy31w==', 'CIlGhFo/VeCH27hmnELiYg==', '2025-11-01 14:06:34');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `message_recipients`
--

CREATE TABLE `message_recipients` (
  `id` int(11) NOT NULL,
  `message_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `read_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `message_recipients`
--

INSERT INTO `message_recipients` (`id`, `message_id`, `receiver_id`, `read_at`) VALUES
(1, 1, 2, NULL),
(2, 1, 1, '2025-11-01 14:06:32'),
(3, 2, 2, '2025-11-01 14:06:34'),
(4, 2, 1, NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `gender` enum('male','female','other') DEFAULT 'other',
  `date_of_birth` date DEFAULT NULL,
  `avatar_url` varchar(255) DEFAULT NULL,
  `bio` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
--

INSERT INTO `users` (`id`, `account_id`, `full_name`, `gender`, `date_of_birth`, `avatar_url`, `bio`) VALUES
(1, 1, 'nguyen viet hoang', 'other', '2007-11-01', NULL, NULL),
(2, 2, 'test', 'other', '2007-11-01', NULL, NULL);

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Chỉ mục cho bảng `chats`
--
ALTER TABLE `chats`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `chat_members`
--
ALTER TABLE `chat_members`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `chat_id` (`chat_id`,`account_id`),
  ADD KEY `account_id` (`account_id`);

--
-- Chỉ mục cho bảng `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chat_id` (`chat_id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Chỉ mục cho bảng `message_recipients`
--
ALTER TABLE `message_recipients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `message_id` (`message_id`,`receiver_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account_id` (`account_id`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `accounts`
--
ALTER TABLE `accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT cho bảng `chats`
--
ALTER TABLE `chats`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT cho bảng `chat_members`
--
ALTER TABLE `chat_members`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT cho bảng `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT cho bảng `message_recipients`
--
ALTER TABLE `message_recipients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT cho bảng `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `chat_members`
--
ALTER TABLE `chat_members`
  ADD CONSTRAINT `chat_members_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `chats` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `chat_members_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `chats` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `message_recipients`
--
ALTER TABLE `message_recipients`
  ADD CONSTRAINT `message_recipients_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `message_recipients_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
