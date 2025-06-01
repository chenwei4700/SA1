-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： localhost
-- 產生時間： 2025 年 04 月 30 日 15:57
-- 伺服器版本： 10.4.28-MariaDB
-- PHP 版本： 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `Sa2-2`
--

-- --------------------------------------------------------

--
-- 資料表結構 `comments`
--

CREATE TABLE `comments` (
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `comment_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `comments`
--

INSERT INTO `comments` (`post_id`, `user_id`, `content`, `created_at`, `comment_id`) VALUES
(1, 1, '這是留言測試用的內容', '2025-04-22 21:11:21', 1),
(5, 3, '這是文章 10 的留言 10', '2025-04-28 17:34:59', 2),
(6, 2, '這是文章 8 的留言 11', '2025-04-28 17:34:59', 3);

-- --------------------------------------------------------

--
-- 資料表結構 `faq`
--

CREATE TABLE `faq` (
  `faq_id` int(11) NOT NULL,
  `question` text DEFAULT NULL,
  `answer` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `faq`
--

INSERT INTO `faq` (`faq_id`, `question`, `answer`) VALUES
(1, 'AI 是什麼？', 'AI 是人工智慧的縮寫，指的是能模擬人類智能的系統。'),
(2, 'Flask 是什麼？', 'Flask 是一個用 Python 編寫的輕量級 Web 應用框架。');

-- --------------------------------------------------------

--
-- 資料表結構 `hashtag`
--

CREATE TABLE `hashtag` (
  `hashtag_id` int(11) NOT NULL,
  `hashtag_name` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `hashtag`
--

INSERT INTO `hashtag` (`hashtag_id`, `hashtag_name`) VALUES
(1, 'hashtag_1'),
(2, 'hashtag_2');

-- --------------------------------------------------------

--
-- 資料表結構 `images`
--

CREATE TABLE `images` (
  `file_path` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `uploadtime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `file_name` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `images`
--

INSERT INTO `images` (`file_path`, `uploadtime`, `file_name`, `user_id`) VALUES
('static/uploads/412401501@fju.com_2025-04-03_2.25.10.png', '2025-04-23 22:32:27', NULL, NULL),
('static/uploads/test@example.com_IMG_8648.HEIC', '2025-04-23 09:33:40', NULL, NULL),
('static/uploads/ph309218@gmail.com_IMG_6023.jpeg', '2025-04-24 15:22:32', NULL, NULL),
('static/uploads/test1.png', '2025-04-30 06:00:00', 'test1.png', 1),
('static/uploads/test2.jpg', '2025-04-30 07:00:00', 'test2.jpg', 2);

-- --------------------------------------------------------

--
-- 資料表結構 `posts`
--

CREATE TABLE `posts` (
  `post_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `title` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `is_alert` tinyint(1) DEFAULT 0,
  `hashtag_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `posts`
--

INSERT INTO `posts` (`post_id`, `user_id`, `title`, `content`, `created_at`, `is_alert`, `hashtag_id`) VALUES
(1, 1, '第一篇測試文章', '這是一篇測試文章的內容', '2025-04-22 21:09:04', 0, NULL),
(5, 2, '第5篇測試文章', '這是第5篇的測試內容', '2025-04-30 13:34:59', 1, 1),
(6, 3, '第6篇測試文章', '這是第6篇的測試內容', '2025-04-28 13:34:59', 0, 2);

-- --------------------------------------------------------

--
-- 資料表結構 `unanswer`
--

CREATE TABLE `unanswer` (
  `unanswer_id` int(11) NOT NULL,
  `unanswer_q` text DEFAULT NULL,
  `unanswer_a` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `unanswer`
--

INSERT INTO `unanswer` (`unanswer_id`, `unanswer_q`, `unanswer_a`) VALUES
(1, '為什麼地球會轉？', NULL),
(2, '月亮上有水嗎？', NULL);

-- --------------------------------------------------------

--
-- 資料表結構 `Users`
--

CREATE TABLE `Users` (
  `user_id` int(11) NOT NULL,
  `account` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `user_name` varchar(30) DEFAULT NULL,
  `role` varchar(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `Users`
--

INSERT INTO `Users` (`user_id`, `account`, `password`, `user_name`, `role`) VALUES
(1, 'test@example.com', '12345678', '測試使用者', 'M'),
(2, 'ph309218@gmail.com', 'aa1234', 'tttt', 'm'),
(3, 'ng0904280208@gmail.com', '123456', 'lo', 'U'),
(4, 'user4@example.com', 'password4', '用戶4', 'U'),
(5, 'user5@example.com', 'password5', '用戶5', 'U');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`comment_id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `faq`
--
ALTER TABLE `faq`
  ADD PRIMARY KEY (`faq_id`);

--
-- 資料表索引 `hashtag`
--
ALTER TABLE `hashtag`
  ADD PRIMARY KEY (`hashtag_id`);

--
-- 資料表索引 `images`
--
ALTER TABLE `images`
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`post_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `hashtag_id` (`hashtag_id`);

--
-- 資料表索引 `unanswer`
--
ALTER TABLE `unanswer`
  ADD PRIMARY KEY (`unanswer_id`);

--
-- 資料表索引 `Users`
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`account`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `comments`
--
ALTER TABLE `comments`
  MODIFY `comment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `faq`
--
ALTER TABLE `faq`
  MODIFY `faq_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `posts`
--
ALTER TABLE `posts`
  MODIFY `post_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `unanswer`
--
ALTER TABLE `unanswer`
  MODIFY `unanswer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `Users`
--
ALTER TABLE `Users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `comments`
--
ALTER TABLE `comments`
  ADD CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`post_id`),
  ADD CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`);

--
-- 資料表的限制式 `images`
--
ALTER TABLE `images`
  ADD CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`);

--
-- 資料表的限制式 `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `hashtag_id` FOREIGN KEY (`hashtag_id`) REFERENCES `hashtag` (`hashtag_id`),
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
