// 公告相關函數
function showAddAnnouncementForm() {
    // 如果已經有一個 modal，就不再創建
    if (document.querySelector('.modal-overlay')) return;
    const form = document.createElement('div');
    form.className = 'modal-overlay';
    form.innerHTML = `
        <div class="modal-box">
            <h5>📝 新增公告</h5>
            <form id="addAnnouncementForm" onsubmit="submitNewAnnouncement(event)">
                <div style="margin-bottom: 15px;">
                    <label for="title" style="display: block; margin-bottom: 5px;">標題：</label>
                    <input type="text" id="title" name="title" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="content" style="display: block; margin-bottom: 5px;">內容：</label>
                    <textarea id="content" name="content" required style="width: 100%; height: 150px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"></textarea>
                </div>
                <div class="admin-actions">
                    <button type="submit">發布公告</button>
                    <button type="button" onclick="closeAddAnnouncementForm()" class="edit">取消</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(form);

    // 按 ESC 關閉
    document.addEventListener('keydown', handleEscapeClose);
}

function submitNewAnnouncement(event) {
    event.preventDefault(); // ← 防止預設送出跳轉
    const title = document.getElementById('title').value;
    const content = document.getElementById('content').value;

    fetch('/announcement/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        closeAddAnnouncementForm();
        location.reload();
    })
    .catch(err => {
        alert("送出失敗：" + err);
        console.error(err);
    });
}

function closeAddAnnouncementForm() {
    const overlay = document.querySelector('.modal-overlay');
    if (overlay) {
        overlay.remove();
    }
    document.removeEventListener('keydown', handleEscapeClose);
}

function handleEscapeClose(e) {
    if (e.key === "Escape") {
        closeAddAnnouncementForm();
    }
}


window.onload = function () {
  const modal = document.getElementById("admin-announcement");
  if (modal) {
    modal.style.display = "flex";
  }
}




function editAnnouncement(id) {
    const newContent = prompt("請輸入新的公告內容：");
    if (newContent) {
      fetch(`/announcement/edit/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: newContent })
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        location.reload();
      });
    }
  }

  function deleteAnnouncement(id) {
    if (confirm("確定要刪除這則公告嗎？")) {
      fetch(`/announcement/delete/${id}`, {
        method: 'DELETE'
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        location.reload();
      });
    }
  }
  
  
  function showEditAnnouncementForm(id, currentTitle, currentContent) {
    const form = document.createElement('div');
    form.className = 'modal-overlay';
    form.innerHTML = `
        <div class="modal-box">
            <h5>✏️ 編輯公告</h5>
            <form id="editAnnouncementForm" onsubmit="submitEditAnnouncement(event, ${id})">
                <div style="margin-bottom: 15px;">
                    <label for="editTitle" style="display: block; margin-bottom: 5px;">標題：</label>
                    <input type="text" id="editTitle" name="title" value="${currentTitle}" required
                        style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="editContent" style="display: block; margin-bottom: 5px;">內容：</label>
                    <textarea id="editContent" name="content" required
                        style="width: 100%; height: 150px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">${currentContent}</textarea>
                </div>
                <div class="admin-actions">
                    <button type="submit">儲存變更</button>
                    <button type="button" onclick="closeEditAnnouncementForm()" class="edit">取消</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(form);
}

function submitEditAnnouncement(event, id) {
    event.preventDefault();
    const title = document.getElementById('editTitle').value;
    const content = document.getElementById('editContent').value;

    fetch(`/announcement/edit/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: title, content: content })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        closeEditAnnouncementForm();
        location.reload();
    });
}

function closeEditAnnouncementForm() {
    const overlay = document.querySelector('.modal-overlay');
    if (overlay) {
        overlay.remove();
    }
}


// 頁面載入時自動顯示 modal
window.addEventListener('DOMContentLoaded', function () {
    document.getElementById('admin-announcement').style.display = 'block';
  });

  // 關閉 modal 的函式
  function closeAnnouncement() {
    document.getElementById('admin-announcement').style.display = 'none';
  }
