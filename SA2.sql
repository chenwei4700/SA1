-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： localhost
-- 產生時間： 2025 年 04 月 01 日 07:21
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
-- 資料庫： `SA2`
--

-- --------------------------------------------------------

--
-- 資料表結構 `catched_content`
--

CREATE TABLE `catched_content` (
  `id` int(11) NOT NULL,
  `keyword` text DEFAULT NULL,
  `url` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `catched_content`
--

INSERT INTO `catched_content` (`id`, `keyword`, `url`, `content`, `time`) VALUES
(2, '教師', 'https://www.im.fju.edu.tw/專任教師/', 'Skip to content\n碩士在職專班\n課程大綱查詢\n學生自我檢核畢業學分系統\n跨領域學程/自主學習\n產業實習課程計畫\n學生實習心得\n教師教學成果\nEnglish\nToggle website search\n董惟鳳 教授\n呂奇傑 教授\n廖建翔 教授\n葉承達 教授\n黃曜輝 教授\n許嘉霖 教授\n胡俊之 副教授\n張銀益 副教授\n吳濟聰 助理教授\n林湘霖 助理教授\n黃智榮 助理教授\n林青峰 助理教授\n鄭美娟 助理教授\n石佳惠 助理教授\n王冠云 助理教授\n歐思鼎 助理教授\n董惟鳳 教授\n呂奇傑 教授\n廖建翔 教授\n葉承達 教授\n黃曜輝 教授\n許嘉霖 教授\n胡俊之 副教授\n張銀益 副教授\n吳濟聰 助理教授\n林湘霖 助理教授\n黃智榮 助理教授\n林青峰 助理教授\n鄭美娟 助理教授\n石佳惠 助理教授\n王冠云 助理教授\n歐思鼎 助理教授\n076144@mail.fju.edu.tw\n059099@mail.fju.edu.tw\n052122@mail.fju.edu.tw\nAI and System Optimization Lab\n145712@mail.fju.edu.tw\n140485@mail.fju.edu.tw\n157287@mail.fju.edu.tw\n026385@mail.fju.edu.tw\n042833@mail.fju.edu.tw\n053792@mail.fju.edu.tw\n146414@mail.fju.edu.tw\n154231@mail.fju.edu.tw\n154327@mail.fju.edu.tw\n155360@mail.fju.edu.tw\n155379@mail.fju.edu.tw\n159931@mail.fju.edu.tw\n162944@mail.fju.edu.tw\n156567@mail.fju.edu.tw', '2025-04-01 04:17:19');

-- --------------------------------------------------------

--
-- 資料表結構 `faq`
--

CREATE TABLE `faq` (
  `id` int(11) NOT NULL,
  `question` text DEFAULT NULL,
  `answer` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `faq`
--

INSERT INTO `faq` (`id`, `question`, `answer`) VALUES
(8, '教師', '根據輔仁大學資訊管理學系網站（https://www.im.fju.edu.tw/專任教師/）的資料，該系所的專任教師名單如下：\n\n**教授:**\n\n*   董惟鳳\n*   呂奇傑\n*   廖建翔\n*   葉承達\n*   黃曜輝\n*   許嘉霖\n\n**副教授:**\n\n*   胡俊之\n*   張銀益\n\n**助理教授:**\n\n*   吳濟聰\n*   林湘霖\n*   黃智榮\n*   林青峰\n*   鄭美娟\n*   石佳惠\n*   王冠云\n*   歐思鼎\n\n**教師電子郵件 (依照上方教師順序):**\n\n*   076144@mail.fju.edu.tw\n*   059099@mail.fju.edu.tw\n*   052122@mail.fju.edu.tw\n*   145712@mail.fju.edu.tw\n*   140485@mail.fju.edu.tw\n*   157287@mail.fju.edu.tw\n*   026385@mail.fju.edu.tw\n*   042833@mail.fju.edu.tw\n*   053792@mail.fju.edu.tw\n*   146414@mail.fju.edu.tw\n*   154231@mail.fju.edu.tw\n*   154327@mail.fju.edu.tw\n*   155360@mail.fju.edu.tw\n*   155379@mail.fju.edu.tw\n*   159931@mail.fju.edu.tw\n*   162944@mail.fju.edu.tw\n*   156567@mail.fju.edu.tw'),
(10, '有關教師', '好的，根據您提供的資料，我整理出以下關於教師的資訊：\n\n**1. 重點摘要**\n\n這份資料列出了多位教授和副教授/助理教授的姓名及聯絡方式。主要提供教師的名稱及電子郵件地址，方便學生聯繫。此外，還有一個實驗室名稱 \"AI and System Optimization Lab\"。\n\n**2. 詳細內容**\n\n*   **教授 (Professors):**\n    *   董惟鳳\n    *   呂奇傑\n    *   廖建翔\n    *   葉承達\n    *   黃曜輝\n    *   許嘉霖\n\n*   **副教授 (Associate Professors):**\n    *   胡俊之\n    *   張銀益\n\n*   **助理教授 (Assistant Professors):**\n    *   吳濟聰\n    *   林湘霖\n    *   黃智榮\n    *   林青峰\n    *   鄭美娟\n    *   石佳惠\n    *   王冠云\n    *   歐思鼎\n\n*   **電子郵件 (Email Addresses):**\n    *   董惟鳳: 076144@mail.fju.edu.tw\n    *   呂奇傑: 059099@mail.fju.edu.tw\n    *   廖建翔: 052122@mail.fju.edu.tw\n    *   葉承達: 145712@mail.fju.edu.tw\n    *   黃曜輝: 140485@mail.fju.edu.tw\n    *   許嘉霖: 157287@mail.fju.edu.tw\n    *   胡俊之: 026385@mail.fju.edu.tw\n    *   張銀益: 042833@mail.fju.edu.tw\n    *   吳濟聰: 053792@mail.fju.edu.tw\n    *   林湘霖: 146414@mail.fju.edu.tw\n    *   黃智榮: 154231@mail.fju.edu.tw\n    *   林青峰: 154327@mail.fju.edu.tw\n    *   鄭美娟: 155360@mail.fju.edu.tw\n    *   石佳惠: 155379@mail.fju.edu.tw\n    *   王冠云: 159931@mail.fju.edu.tw\n    *   歐思鼎: 162944@mail.fju.edu.tw\n    *   實驗室聯絡資訊: 156567@mail.fju.edu.tw\n\n*   **實驗室 (Laboratory):**\n    *   AI and System Optimization Lab\n\n**3. 補充說明或建議**\n\n*   如果您需要聯繫特定的老師，請使用他們提供的電子郵件地址。\n*   如果您的問題與 \"AI and System Optimization Lab\" 相關，可以使用提供的實驗室聯絡資訊。\n*   為了更有效地與老師溝通，建議您在郵件中清楚地說明您的問題或需求。\n*   請注意教授與副教授/助理教授的職稱，以便正確稱呼。\n*   如果需要更詳細的教師資訊（如研究領域、辦公室地點等），可能需要查詢學校官方網站或其他相關資源。'),
(11, '關於教師', '好的，根據您提供的資料，我為您整理出關於教師的資訊如下：\n\n**教授**\n\n*   董惟鳳 教授\n*   呂奇傑 教授\n*   廖建翔 教授\n*   葉承達 教授\n*   黃曜輝 教授\n*   許嘉霖 教授\n\n**副教授**\n\n*   胡俊之 副教授\n*   張銀益 副教授\n\n**助理教授**\n\n*   吳濟聰 助理教授\n*   林湘霖 助理教授\n*   黃智榮 助理教授\n*   林青峰 助理教授\n*   鄭美娟 助理教授\n*   石佳惠 助理教授\n*   王冠云 助理教授\n*   歐思鼎 助理教授\n\n**教師Email**\n\n*   董惟鳳 教授: 076144@mail.fju.edu.tw\n*   呂奇傑 教授: 059099@mail.fju.edu.tw\n*   廖建翔 教授: 052122@mail.fju.edu.tw\n*   葉承達 教授: 145712@mail.fju.edu.tw\n*   黃曜輝 教授: 140485@mail.fju.edu.tw\n*   許嘉霖 教授: 157287@mail.fju.edu.tw\n*   胡俊之 副教授: 026385@mail.fju.edu.tw\n*   張銀益 副教授: 042833@mail.fju.edu.tw\n*   吳濟聰 助理教授: 053792@mail.fju.edu.tw\n*   林湘霖 助理教授: 146414@mail.fju.edu.tw\n*   黃智榮 助理教授: 154231@mail.fju.edu.tw\n*   林青峰 助理教授: 154327@mail.fju.edu.tw\n*   鄭美娟 助理教授: 155360@mail.fju.edu.tw\n*   石佳惠 助理教授: 155379@mail.fju.edu.tw\n*   王冠云 助理教授: 159931@mail.fju.edu.tw\n*   歐思鼎 助理教授: 162944@mail.fju.edu.tw\n*   Email: 156567@mail.fju.edu.tw （此Email沒有對應的教師姓名）\n\n**其他資訊**\n\n*   **教師教學成果：** 資料中包含教師教學成果的連結，可能可以找到更多關於教師的資訊。\n*   **AI and System Optimization Lab:** 廖建翔教授的資訊旁有備註AI and System Optimization Lab。\n\n希望這些資訊對您有所幫助！'),
(12, '教師問題', '根據您提供的資料，以下整理出教師資訊：\n\n**教授 (Professors)**\n\n*   董惟鳳 教授\n*   呂奇傑 教授\n*   廖建翔 教授\n*   葉承達 教授\n*   黃曜輝 教授\n*   許嘉霖 教授\n\n**副教授 (Associate Professors)**\n\n*   胡俊之 副教授\n*   張銀益 副教授\n\n**助理教授 (Assistant Professors)**\n\n*   吳濟聰 助理教授\n*   林湘霖 助理教授\n*   黃智榮 助理教授\n*   林青峰 助理教授\n*   鄭美娟 助理教授\n*   石佳惠 助理教授\n*   王冠云 助理教授\n*   歐思鼎 助理教授\n\n**教師聯絡信箱**\n*   董惟鳳 教授: 076144@mail.fju.edu.tw\n*   呂奇傑 教授: 059099@mail.fju.edu.tw\n*   廖建翔 教授: 052122@mail.fju.edu.tw\n*   葉承達 教授: 145712@mail.fju.edu.tw\n*   黃曜輝 教授: 140485@mail.fju.edu.tw\n*   許嘉霖 教授: 157287@mail.fju.edu.tw\n*   胡俊之 副教授: 026385@mail.fju.edu.tw\n*   張銀益 副教授: 042833@mail.fju.edu.tw\n*   吳濟聰 助理教授: 053792@mail.fju.edu.tw\n*   林湘霖 助理教授: 146414@mail.fju.edu.tw\n*   黃智榮 助理教授: 154231@mail.fju.edu.tw\n*   林青峰 助理教授: 154327@mail.fju.edu.tw\n*   鄭美娟 助理教授: 155360@mail.fju.edu.tw\n*   石佳惠 助理教授: 155379@mail.fju.edu.tw\n*   王冠云 助理教授: 159931@mail.fju.edu.tw\n*   歐思鼎 助理教授: 162944@mail.fju.edu.tw\n*   信箱: 156567@mail.fju.edu.tw\n**實驗室**\n*   廖建翔 教授: AI and System Optimization Lab\n\n希望以上資訊對您有所幫助！'),
(13, '教師有誰', '根據您提供的資料，以下是該專班的教師名單：\n\n**教授**\n\n*   董惟鳳 教授\n*   呂奇傑 教授\n*   廖建翔 教授\n*   葉承達 教授\n*   黃曜輝 教授\n*   許嘉霖 教授\n\n**副教授**\n\n*   胡俊之 副教授\n*   張銀益 副教授\n\n**助理教授**\n\n*   吳濟聰 助理教授\n*   林湘霖 助理教授\n*   黃智榮 助理教授\n*   林青峰 助理教授\n*   鄭美娟 助理教授\n*   石佳惠 助理教授\n*   王冠云 助理教授\n*   歐思鼎 助理教授'),
(14, '教師聯絡資訊', '好的，根據您提供的資料，我整理出以下教師聯絡資訊：\n\n**教授**\n\n*   **董惟鳳 教授:** 076144@mail.fju.edu.tw\n*   **呂奇傑 教授:** 059099@mail.fju.edu.tw\n*   **廖建翔 教授:** 052122@mail.fju.edu.tw\n*   **葉承達 教授:** 145712@mail.fju.edu.tw\n*   **黃曜輝 教授:** 140485@mail.fju.edu.tw\n*   **許嘉霖 教授:** 157287@mail.fju.edu.tw\n\n**副教授**\n\n*   **胡俊之 副教授:** 026385@mail.fju.edu.tw\n*   **張銀益 副教授:** 042833@mail.fju.edu.tw\n\n**助理教授**\n\n*   **吳濟聰 助理教授:** 053792@mail.fju.edu.tw\n*   **林湘霖 助理教授:** 146414@mail.fju.edu.tw\n*   **黃智榮 助理教授:** 154231@mail.fju.edu.tw\n*   **林青峰 助理教授:** 154327@mail.fju.edu.tw\n*   **鄭美娟 助理教授:** 155360@mail.fju.edu.tw\n*   **石佳惠 助理教授:** 155379@mail.fju.edu.tw\n*   **王冠云 助理教授:** 159931@mail.fju.edu.tw\n*   **歐思鼎 助理教授:** 162944@mail.fju.edu.tw\n\n**其他**\n\n*   AI and System Optimization Lab: 156567@mail.fju.edu.tw\n\n希望以上資訊對您有幫助！');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `catched_content`
--
ALTER TABLE `catched_content`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `faq`
--
ALTER TABLE `faq`
  ADD PRIMARY KEY (`id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `catched_content`
--
ALTER TABLE `catched_content`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `faq`
--
ALTER TABLE `faq`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
