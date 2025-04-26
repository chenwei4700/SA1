const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("menu-toggle");
    const closeBtn = document.getElementById("close-sidebar");

      toggleBtn.addEventListener("click", () => {
        sidebar.classList.add("active");
      });

      closeBtn.addEventListener("click", () => {
        sidebar.classList.remove("active");
      });
      setTimeout(() => {
        const title = document.getElementById("animated-title");
        title.remove(); // 或用 title.style.display = "none";
      }, 15000);