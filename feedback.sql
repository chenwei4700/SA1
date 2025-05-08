-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-05-08 15:56:02
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `sa2-2`
--

-- --------------------------------------------------------

--
-- 資料表結構 `feedback`
--

CREATE TABLE `feedback` (
  `time` int(11) NOT NULL DEFAULT current_timestamp(),
  `question` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `suggest` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `solved` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `feedback`
--

INSERT INTO `feedback` (`time`, `question`, `answer`, `suggest`, `solved`) VALUES
(2025, '', '問題：交換\n回答：您好，關於輔仁大學資管系學生申請交換學生的問題，以下是根據您提供的資料所整理的詳細申請流程說明：\n\n申請交換學生流程\n\n輔仁大學的交換學生分為兩種：校級和院/系級。\n\n* 校級交換學生：由國際及兩岸教育處（國際學生中心）統籌辦理，名額開放全校符合資格的學生申請。申請資訊主要透過國際學生中心的網站公告。\n* 院/系級交換學生：由各院、系或中心自行辦理，名額分配及是否開放由各院系決定，請洽詢資管系辦公室。\n\n以下主要針對校級交換學生進行說明，建議您也同時向資管系詢問院/系級交換的相關資訊。\n\n校級交換學生申請流程\n\n1. 確認申請資格:\n* 學籍：申請時為輔仁大學在學的學士班（含進修部）二、三年級及應屆畢業生(限雙主修、輔系、學分學程未修畢者)，或碩、博士班一年級(含)以上學生。\n* 成績：學士班學位生於入學後學期成績總平均皆在70分(含)以上，操行成績在86分(含)以上，且無任何大過、小過等不良紀錄。\n* 語言檢定：\n* 若申請交換學校課程以英語授課者，需檢附英文檢定成績，達以下其一標準：TOEFL iBT 79、IELTS 6.5、TOEIC 750。成績需於申請截止日前兩年內有效。\n* 若申請非英語授課的學校，需符合該交換學校的語言要求（如日文、法文等）。\n* 申請時至少須有網路成績，僅完成報考但未有成績者不得申請。\n* 其他限制：修業年限內限交換一次 (經院系審查通過者不在此限)。\n2. 關注公告訊息：密切注意輔仁大學國際及兩岸教育處國際學生中心的網站公告。\n* 公告網址：請參考輔仁大學國際及兩岸教育處國際學生中心網站。\n3. 參加申請說明會：國際學生中心會舉辦申請說明會，簡報檔通常會在活動結束後提供下載。請參考網站上的公告，了解說明會時間地點，並踴躍參加。\n4. 報名繳件：在規定的時間內繳交校內備審文件。\n5. 校內審查：國際學術交流審議委員會會根據同學填寫的志願分發。\n6. 行前說明會：參加行前說明會，確認預選課程學分抵免、住宿、機票、簽證等注意事項。\n7. 遞交申請件至姊妹校：按照姊妹校的規定繳交相關申請文件。\n8. 姊妹校審查：姊妹校會審查您的申請文件。\n9. 入學許可和行前準備：收到姊妹校的入學許可後，開始進行行前準備。\n10. 前往交換：按照各校開學日期前往交換學校，並完成出國回報。\n11. 學成歸國：繳交心得、領取成績單、經驗分享。\n\n重要時程（請注意，以下是示例，實際時間請參考國際學生中心公告）\n\n| 階段 | 2025秋季班(114-1) | 備註 |\n|------------|--------------------|---------------------------------------------------------|\n| 公告訊息 | 2024年10月 | 須密切注意國際學生中心公告 |\n| 申請說明會 | 2024年10月 | 簡報檔於活動結束後提供下載 |\n| 報名繳件 | 2024年12月 (12/23截止) | 校內審查：繳交校內備審文件 |\n| 審查結果 | 2025年1月 (非日語組) & 3月 (日語組) | 依國際學術交流審議委員會決議，按照同學填寫志願分發 |\n| 行前說明會 | 2025年3月 | 參加行前說明會、確認預選課程學分抵免、住宿、機票、簽證等注意事項 |\n| 遞交申請件至姐妹校 | 2025年2-5月 | 姐妹校審查：依姐妹校規定繳交相關申請文件 |\n| 入學許可和行前準備 | 2025年5-7月 | 視各國姊妹校作業時間 |\n| 前往交換 | 2025年8月 - 2026年2月 | 視各校開學日期而定，並完成出國回報。 |\n\n聯絡方式\n\n如有任何問題，可以聯繫計畫承辦人：\n\n* 林姿儀 Olly Lin\n* 輔仁大學國際及兩岸教育處國際學生中心\n* 宜聖大樓一樓多功能會議室\n* TEL 02-2905-2386\n* EMAIL 088837@mail.fju.edu.tw\n\n建議您隨時關注國際學生中心的網站公告，並積極參加說明會，以獲取最新的申請資訊。祝您申請順利！', '好爛', 'yes');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
