async function sendMessage() {
    const question = document.getElementById("question").value;
    const responseDiv = document.getElementById("response");
    const loading = document.getElementById("loading");

    if (!question) {
      responseDiv.innerHTML += `<div class="message bot">請輸入問題！</div>`;
      return;
    }

    // 顯示使用者輸入、清空欄位、顯示 loading
    responseDiv.innerHTML += `<div class="message user">${question}</div>`;
    document.getElementById("question").value = "";
    loading.style.display = "block";

    try {
      const response = await fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();

      // 處理回應前先隱藏 loading
      loading.style.display = "none";

      if (response.ok) {
        // 去除回答中的 ** 符號
        const cleanText = data.response.replace(/\*\*/g, "");
        responseDiv.innerHTML += `<div class="message bot">${cleanText}</div>`;
      } else {
        responseDiv.innerHTML += `<div class="message bot">發生錯誤，請稍後再試。</div>`;
      }

      responseDiv.scrollTop = responseDiv.scrollHeight;
    } catch (err) {
      loading.style.display = "none";
      responseDiv.innerHTML += `<div class="message bot">連線錯誤，請稍後再試。</div>`;
    }
  }

  
  function clearHistory() {
    fetch("/clear_history", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data.message);
        document.getElementById("response").innerHTML = "";
      })
      .catch((error) => console.error("Error:", error));
  }

    