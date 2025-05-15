document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("menu-toggle");
    const closeBtn = document.getElementById("close-sidebar");

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.add("active");
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener("click", () => {
            sidebar.classList.remove("active");
        });
    }

    setTimeout(() => {
        const title = document.getElementById("animated-title");
        if (title) {
            title.remove(); // 或 title.style.display = "none";
        }
    }, 15000);
});
