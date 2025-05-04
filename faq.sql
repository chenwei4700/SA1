-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-05-04 15:23:15
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
(2, 'Flask 是什麼？', 'Flask 是一個用 Python 編寫的輕量級 Web 應用框架。'),
(4, '交換學生怎麼申請？', 'https://iscoie.fju.edu.tw/generalServices.jsp?labelID=39'),
(5, '如何開通輔大Email帳號?', '請至 http://whoami.fju.edu.tw 啟用你在本校「單一帳號(LDAP) 」'),
(6, '校園考試報名專區', 'https://www.examservice.com.tw/Home/preindex?setStoreID=B6026'),
(7, '怎麼請假', 'https://www.im.fju.edu.tw/學生請假流程電子化'),
(8, '如何休學', 'https://academic.fju.edu.tw/generalServices.jsp?labelID=38\nhttps://docsacademic.fju.edu.tw/application/學生申請休學作業.pdf'),
(9, '退學要做什麼', 'https://docsacademic.fju.edu.tw/form/學生退學作業.pdf\nhttps://academic.fju.edu.tw/generalServices.jsp?labelID=38'),
(10, '要如何轉學', 'https://docsacademic.fju.edu.tw/form/申請轉學修業證明書作業.pdf\nhttps://academic.fju.edu.tw/generalServices.jsp?labelID=38'),
(11, '如何學分抵免', 'https://docsacademic.fju.edu.tw/about%20graduate/學生申請抵免科目作業.pdf\nhttps://docsacademic.fju.edu.tw/edulaw/學生抵免科目規則.pdf\nhttps://academic.fju.edu.tw/generalServices.jsp?labelID=37'),
(12, '學生證不見怎麼辦', 'https://docsacademic.fju.edu.tw/application/申請補發學生證作業.pdf'),
(13, '如何更改個人資料', 'https://academic.fju.edu.tw/generalServices.jsp?labelID=36'),
(14, '怎麼申請在學證明', 'https://docsacademic.fju.edu.tw/application/申請中英文在學證明書作業.pdf'),
(15, '畢業證書、學業證書補發', 'https://docsacademic.fju.edu.tw/about%20status/中文學位證書遺失損毀補發作業.pdf'),
(16, '英文畢業證書', 'https://docsacademic.fju.edu.tw/about%20status/申請英文學位證明書作業.pdf'),
(17, '註冊須知', 'https://academic.fju.edu.tw/generalServices.jsp?labelID=40'),
(18, '男生服兵役相關問題', 'https://docsacademic.fju.edu.tw/edulaw/學士班就學期間服務彈性修業實施要點.pdf'),
(19, '要怎麼外校選課', 'https://docsacademic.fju.edu.tw/about%20course/校際選課作業(本校生至外校).pdf'),
(20, '怎麼申請暑修', 'https://summercourse.fju.edu.tw/#/news/56'),
(21, '暑修開放哪些課程', 'https://summercourse.fju.edu.tw/#/course 查詢詳情'),
(22, '若大三上學期結束前未達多益標準者如何處理', '須於大四參加管理學院舉辦之 8 次英語自學方案測驗（上學期 4 次、下學期 4 次，如上學期或下學期 4 次測驗成績平均高於 80 分者，則免參加次一學期之測驗；如累計 4 次 80 分者，亦可免參加其餘測驗）或再次參加英文檢定考試，且成績達 CEFR 之 B2 高階級始有畢業資格。\nhttps://www.management.fju.edu.tw/zh-tw/about/law-detail.php?AID=9&SID=10'),
(23, '英文免修門檻是多少', '適用111學年度起入學學生（只須符合以下其中一項標準即可）：\n(一) 入學英文學測成績達頂標(含)以上。\n(二) 擁有下列英語檢定證照者，應依每學年選課須知之規定期限內上傳證照資料 https://reurl.cc/eWA4Zx 進行申請及審核，審核通過者將於本中心最新消息網頁中公告之。\n1. 全民英檢(GEPT)：中高級(含以上)複試通過\n2. 多益(TOEIC)聽力與閱讀：800分(含)以上\n3. 多益(TOEIC)口說與寫作：310分(含)以上\n4. 劍橋BULATS：ALTE Level 3(含)以上\n5. 托福(TOEFL)：ITP 543；iBT 87(含)以上\n6. 雅思(IELTS)：6.5(含)以上\n7. 劍橋主流(Main Suite)：FCE、CAE、CPE\n8. CSEPT：第二級330\n9. CEFR：B2(高階級)含以上'),
(24, '英文畢業門檻是什麼', '學生於畢業前需至少修畢 5 門（或 15 學分）本院開設之「以英語授課的專業課程」。\n112學年度入學新生適用之各項英語能力檢測與 CEFR B2 高階級對應如下：\nCEFR B2：TOEIC 785+；TOEFL iBT 72+；IELTS 6.0+；OPT 61+；全民英檢中高級複試通過。\nhttps://www.management.fju.edu.tw/zh-tw/about/law-detail.php?AID=9&SID=9\nhttps://www.management.fju.edu.tw/zh-tw/about/law-detail.php?AID=9&SID=10'),
(25, '英語授課要多少學分才能畢業?', '學生於畢業前需至少修畢 5 門（或 15 學分）本院開設之「以英語授課的專業課程」。\nhttps://www.im.fju.edu.tw/wp-content/uploads/2024/10/113資訊管理學系修業規則適用113學年度新生.pdf'),
(26, '如何上傳英文檢定成績', '請至學生資訊入口網 https://portal.fju.edu.tw/student/ → 校內系統選單 → 網路．服務 → 學生證照管理系統，上傳掃描或拍照的成績單或證書圖檔。（可使用濟時樓圖書館、資訊中心自由上機機房或系辦公室掃描機）'),
(27, '若機測未能一次通過 有什麼其他方式嗎', '學生於畢業前需通過「程式語言機測」，未通過者若已累計通過 3 題機測題目，得修畢一門本系選修之程式設計相關課程，始有畢業資格。\nhttps://www.im.fju.edu.tw/wp-content/uploads/2024/10/113資訊管理學系修業規則適用113學年度新生.pdf'),
(28, '機測要對幾題', '每一次機測考試共有五題，需答對3題。\nhttps://www.im.fju.edu.tw/wp-content/uploads/2024/10/113資訊管理學系修業規則適用113學年度新生.pdf'),
(29, '機測題庫', '請至 http://140.136.155.169'),
(30, '哪些課程有擋修', '（一）「系統分析與設計」擋修「資訊系統專題一」。\n（二）「資訊系統專題二」成績不及格，需重修「資訊系統專題一」及「資訊系統專題二」。\nhttps://www.im.fju.edu.tw/wp-content/uploads/2024/10/113資訊管理學系修業規則適用113學年度新生.pdf'),
(31, '怎麼加入系學會', 'https://www.instagram.com/fjuim/'),
(32, '輔大資管課程介紹', 'https://www.im.fju.edu.tw/%E8%AA%B2%E7%A8%8B%E4%BB%8B%E7%B4%B9-2/'),
(33, '資管系的獎助學金', 'https://www.im.fju.edu.tw/%e7%8d%8e%e5%8a%a9%e5%ad%b8%e9%87%91-2/'),
(34, '資管系必修科目', 'https://www.im.fju.edu.tw/wp-content/uploads/2024/12/114學年度必選修科目表_資管系學士班_中英對照.pdf'),
(35, '113年雙主修資管系要修哪些科目', 'https://www.im.fju.edu.tw/wp-content/uploads/2024/07/113學年度必修科目表雙主修_資管系.pdf\nhttps://www.im.fju.edu.tw/%e5%a4%a7%e5%ad%b8%e9%83%a8%e8%aa%b2%e7%a8%8b%e8%b3%87%e8%a8%8a/'),
(36, '輔系資管系要修哪些科目', 'https://www.im.fju.edu.tw/wp-content/uploads/2025/03/114學年度輔系必修科目表.pdf'),
(37, '資管系課表', 'https://www.im.fju.edu.tw/大學部課程資訊/'),
(38, '資管系上資源', 'https://www.im.fju.edu.tw/系所介紹/空間與設備'),
(39, '哪裡可以查到輔大資管系在職教師', 'https://www.im.fju.edu.tw/%e5%b0%88%e4%bb%bb%e6%95%99%e5%b8%ab/'),
(40, '董惟鳳(系主任)', 'https://www.im.fju.edu.tw/%E8%91%A3%E6%83%9F%E9%B3%B3/'),
(41, '呂奇傑', 'https://www.im.fju.edu.tw/呂奇傑/'),
(42, '吳濟聰教授的資料', 'https://www.im.fju.edu.tw/吳濟聰/\nhttps://sites.google.com/view/jitsungwu/'),
(43, '廖建祥', 'https://www.im.fju.edu.tw/%e5%bb%96%e5%bb%ba%e7%bf%94/'),
(44, '葉承達', 'https://www.im.fju.edu.tw/%E8%91%89%E6%89%BF%E9%81%94/'),
(45, '黃曜輝', 'https://www.im.fju.edu.tw/%E9%BB%83%E6%9B%9C%E8%BC%9D/'),
(46, '王冠云', 'https://www.im.fju.edu.tw/%E7%8E%8B%E5%86%A0%E4%BA%91/'),
(47, '蔡明志', 'https://www.im.fju.edu.tw/%E8%94%A1%E6%98%8E%E5%BF%97/'),
(48, '退休教師', 'https://www.im.fju.edu.tw/%e9%80%80%e4%bc%91%e6%95%99%e5%b8%ab/'),
(49, '蔡幸蓁', 'https://www.im.fju.edu.tw/%E8%94%A1%E5%B9%B8%E8%93%81/'),
(50, '資管系行政同仁', 'https://www.im.fju.edu.tw/%e8%a1%8c%e6%94%bf%e5%90%8c%e4%bb%81/'),
(51, '教師教學成果', 'https://www.im.fju.edu.tw/%e6%95%99%e5%b8%ab%e6%95%99%e5%ad%b8%e6%88%90%e6%9e%9c%e7%8d%8e/'),
(52, '碩士班招生資訊', 'https://www.im.fju.edu.tw/%e7%a2%a9%e5%a3%ab%e7%8f%ad%e6%8b%9b%e7%94%9f%e6%9c%80%e6%96%b0%e6%b6%88%e6%81%af/'),
(53, '張銀益(副教授)', 'https://www.im.fju.edu.tw/%E5%BC%B5%E9%8A%80%E7%9B%8A/'),
(54, '胡俊之(副教授)', 'https://www.im.fju.edu.tw/%E8%83%A1%E4%BF%8A%E4%B9%8B/'),
(55, '林湘霖(助理教授)', 'https://www.im.fju.edu.tw/%E6%9E%97%E6%B9%98%E9%9C%96/'),
(56, '黃智榮(助理教授)', 'https://www.im.fju.edu.tw/%E9%BB%83%E6%99%BA%E6%A6%AE/'),
(57, '林雅文(助理教授)', 'https://www.im.fju.edu.tw/%E6%9E%97%E9%9B%85%E6%96%87/'),
(58, '鄭美娟(助理教授)', 'https://www.im.fju.edu.tw/%E9%84%AD%E7%BE%8E%E5%A8%9F/'),
(59, '石佳惠(助理教授)', 'https://www.im.fju.edu.tw/%E7%9F%B3%E4%BD%B3%E6%83%A0/'),
(60, '資管行政人員聯絡方式', '242 新北市新莊區中正路510號利瑪竇大樓LM306\n大學部秘書TEL：+886-2-2905-2666\n碩士班秘書TEL：+886-2-2905-2940\n碩職班秘書TEL：+886-2-2905-2626\nFAX：+886-2-2905-2182'),
(61, '林青峰', 'https://www.im.fju.edu.tw/林青峰/'),
(62, '許嘉霖', 'https://www.im.fju.edu.tw/許嘉霖/'),
(63, '歐思鼎', 'https://www.im.fju.edu.tw/歐思鼎/'),
(64, '專題規則', 'https://project.im.fju.edu.tw/Rule'),
(65, '輔仁大學學生資訊專題管理系統', 'https://project.im.fju.edu.tw/'),
(66, '產學合作列表', 'https://project.im.fju.edu.tw/Company/List'),
(67, '資管系的實習工作內容', '程式設計、電子商務系統設計，行銷處的資訊行銷專案或CRM專案為主，軟體業務助理、系統測試、文件撰寫等工作也可以。\n\n(工作的內容希望能讓學生接觸到實際系統的維護、運作、甚至是開發。)\n\n學生遴選，採推薦與媒合制，所有要參加實習的學生，均需要有老師的推薦信，大四學生由畢業專題指導老師寫推薦信給予推薦，研二學生，則由碩士論文指導教授寫推薦信，獲得老師推薦，方能修課，然後由學生選填想要實習企業與工作，每個學生可以依其意願選填一到多個企業。然後開始由企業進行面談，面談時，學生需要提供自傳、簡歷、在校成績，畢業專題作品，供企業審查，由企業最後決定是否錄取學生。'),
(68, '系上有什麼實習機會', 'https://www.im.fju.edu.tw/實習快訊/ ，其會更新各產業的實習招募資訊。'),
(69, '畢業學分是多少', '（一）修滿全人教育核心課程 8 學分\n（二）修滿基本能力課程 12 學分\n（三）修滿通識涵養課程 12 學分\n（四）修滿專業必修課程 64 學分。\n（五）選修課程中包含本系專業選修課程至少 10 學分。\n（六）畢業學分數為全人教育核心課程、基本能力課程、通識涵養課程、專業必修課程及選修課程五者之學分數，至少 128 學分。\nhttps://www.im.fju.edu.tw/wp-content/uploads/2024/10/113資訊管理學系修業規則適用113學年度新生.pdf'),
(70, '學生自我檢核畢業學分系統', '可利用以下網站進行檢核：https://learningcounseling.fju.edu.tw/Student/Account/Login?ReturnUrl=%2FStudent%2F'),
(71, '112之前的修業規則', '（一）修滿全人教育核心課程8學分\n（二）修滿基本能力課程12學分\n（三）修滿通識涵養課程12學分\n（四）修滿專業必修課程64學分(同註1)。\n（五）選修課程中包含本系專業選修課程至少10學分\n（六）畢業學分數為全人教育核心課程、基本能力課程、通識涵養課程、專業必修課程及選修課程五者之學分數，至少128學分。\n學生須參加英文檢定考試達 CEFR B2 高階級（如 TOEIC 750 分以上）或參加自學測驗，並需修至少3學分英語授課課程與通過程式語言機測。'),
(72, '112之後的修業規則', '（一）修滿全人教育核心課程 8 學分\n（二）修滿基本能力課程 12 學分\n（三）修滿通識涵養課程 12 學分\n（四）修滿專業必修課程 64 學分。\n（五）選修課程中包含本系專業選修課程至少 10 學分。\n（六）畢業學分總數至少為 128 學分。\n學生須於畢業前至少修畢 5 門（或 15 學分）以英語授課的專業課程，並通過英文檢定考試（如 TOEIC 785 分以上、IELTS 6.0 以上等 CEFR B2 高階級），以及通過程式語言機測。\nhttps://www.im.fju.edu.tw/wp-content/uploads/2024/10/113資訊管理學系修業規則適用113學年度新生.pdf'),
(73, '畢業生離校手續', 'https://academic.fju.edu.tw/generalServices.jsp?labelID=38\nhttps://docsacademic.fju.edu.tw/application/畢業生辦理離校核發中英文學位證書作業.pdf'),
(74, '畢業審核流程', 'https://docsacademic.fju.edu.tw/about%20graduate/學士班學生畢業資格審核作業.pdf\nhttps://academic.fju.edu.tw/generalServices.jsp?labelID=37'),
(75, '雲端趨勢服務學程資訊', 'http://csrc.fju.edu.tw/\nhttp://csrc.fju.edu.tw/113%E9%9B%B2%E7%AB%AF%E6%9C%8D%E5%8B%99%E5%AD%B8%E7%A8%8B%E8%AA%B2%E7%A8%8B%E4%B8%80%E8%A6%BD%E8%A1%A8.pdf'),
(76, '電子商務學程資訊', 'https://www.management.fju.edu.tw/subweb/ecprogram/subindex.php\nhttps://www.management.fju.edu.tw/subweb/ecprogram/class.php?CID=102'),
(77, '跨領域學程與自主學習', 'https://interdisciplinary.fju.edu.tw/about-3'),
(78, 'AI微學程資訊', 'https://www.management.fju.edu.tw/subweb/ai/'),
(79, '如何申請AI微學程', 'https://www.management.fju.edu.tw/subweb/ai/news-detail.php?NID=3116'),
(80, '未來出路：執照相關需要、錄取分數佔比、未來薪資', '大部分資訊相關工作都不需要證照、執照，不過，有些資訊人員在特定行業中 （例如：金融業），公司會要求相關證照。\r\n錄取方式、薪資也依工作、公司而不同，有些公司會有筆試、面試，甚至要求當場寫程式，也有些公司會要求準備作品，有些會有多次的筆試、面試。\r\n\r\n錄取方式、薪資會受大環境的影響而不同，有時候職缺較求職者少，錄取的資格相對高、薪資相對就低，職缺較求職者多，錄取的資格相對高、薪資相對就高。近幾年，資訊管理相關的職業職缺較求職者多，也因此會吸引同學來報考。');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `faq`
--
ALTER TABLE `faq`
  ADD PRIMARY KEY (`faq_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `faq`
--
ALTER TABLE `faq`
  MODIFY `faq_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=81;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
