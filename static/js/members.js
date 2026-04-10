const { apiUrl, showToast, unwrapData, apiFetch } = window.AppCommon;

// Load members list
async function loadMembers() {
  const loading = document.getElementById('loadingIndicator');
  const tbody = document.getElementById('membersBody');
  const searchTerm = document.getElementById('searchTerm').value.trim();

  loading.classList.add('active');

  try {
    let url = `${apiUrl}/members`;
    if (searchTerm) {
      // Client-side filtering for now as API might not support it yet
      // Ideally backend should support filtering
    }

    const response = await fetch(url);
    const result = await response.json();
    let members = unwrapData(result);

    // Client-side filter
    if (Array.isArray(members) && searchTerm) {
      const q = String(searchTerm);
      members = members.filter(m => {
        const name = m?.name ? String(m.name) : '';
        const phone = m?.phone ? String(m.phone) : '';
        return name.includes(q) || phone.includes(q);
      });
    }

    tbody.replaceChildren();

    if (!Array.isArray(members) || members.length === 0) {
      const row = tbody.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 4;
      cell.className = 'empty-state';
      const p = document.createElement('p');
      p.textContent = '查無會友資料';
      cell.appendChild(p);
    } else {
      members.forEach(member => {
        const row = tbody.insertRow();

        const nameCell = row.insertCell();
        const strong = document.createElement('strong');
        strong.textContent = member.name ?? '';
        nameCell.appendChild(strong);

        const phoneCell = row.insertCell();
        phoneCell.textContent = member.phone || '-';

        const groupCell = row.insertCell();
        groupCell.textContent = member.group || '-';

        const actionCell = row.insertCell();

        const qrBtn = document.createElement('button');
        qrBtn.className = 'btn btn-secondary btn-sm';
        qrBtn.type = 'button';
        qrBtn.textContent = '📱 QR';
        qrBtn.dataset.memberName = member.name ?? '';
        qrBtn.dataset.qrData = member.qr_data ?? '';
        qrBtn.addEventListener('click', () => showQRCode(qrBtn.dataset.memberName, qrBtn.dataset.qrData));

        const delBtn = document.createElement('button');
        delBtn.className = 'btn btn-danger btn-sm';
        delBtn.type = 'button';
        delBtn.textContent = '刪除';
        delBtn.dataset.memberId = member._id ?? '';
        delBtn.addEventListener('click', () => deleteMember(delBtn.dataset.memberId));

        actionCell.appendChild(qrBtn);
        actionCell.appendChild(document.createTextNode(' '));
        actionCell.appendChild(delBtn);
      });
    }
  } catch (error) {
    console.error('Error:', error);
    showToast('載入失敗', 'error');
  } finally {
    loading.classList.remove('active');
  }
}

// Search handler
let searchTimeout;
document.getElementById('searchTerm').addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadMembers, 500);
});

// Modal functions
function openAddModal() {
  document.getElementById('memberForm').reset();
  document.getElementById('memberId').value = '';
  document.getElementById('modalTitle').textContent = '新增會友';
  document.getElementById('memberModal').classList.add('show');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('show');
}

// Save member
async function saveMember() {
  const form = document.getElementById('memberForm');
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);

  // Validate
  if (!data.name) {
    showToast('請輸入姓名', 'error');
    return;
  }

  try {
    const response = await fetch(`${apiUrl}/members`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (response.ok) {
      showToast('儲存成功');
      closeModal('memberModal');
      loadMembers();
    } else {
      showToast(result.error || '儲存失敗', 'error');
    }
  } catch (error) {
    console.error('Error:', error);
    showToast('發生錯誤', 'error');
  }
}

// Delete member
async function deleteMember(id) {
  if (!confirm('確定要刪除此會友？相關出勤記錄將被保留。')) {
    return;
  }

  try {
    const response = await fetch(`${apiUrl}/members/${id}`, {
      method: 'DELETE'
    });

    if (response.ok) {
      showToast('刪除成功');
      loadMembers();
    } else {
      const result = await response.json();
      showToast(result.error || '刪除失敗', 'error');
    }
  } catch (error) {
    console.error('Error:', error);
    showToast('發生錯誤', 'error');
  }
}

// QR Code functions
let qrcodeObj = null;

function showQRCode(name, qrData) {
  document.getElementById('qrName').textContent = name;
  const qrContainer = document.getElementById('qrcode');
  qrContainer.innerHTML = ''; // Clear previous

  if (qrData) {
    qrcodeObj = new QRCode(qrContainer, {
      text: qrData,
      width: 200,
      height: 200
    });
    document.getElementById('qrModal').classList.add('show');
  } else {
    showToast('無法取得 QR Code 資料', 'error');
  }
}

function downloadQRCode() {
  const img = document.querySelector('#qrcode img');
  if (img) {
    const link = document.createElement('a');
    link.href = img.src;
    const rawName = document.getElementById('qrName').textContent || '';
    const safeName = rawName
      .replaceAll('/', '_')
      .replaceAll('\\', '_')
      .replaceAll(':', '_')
      .replaceAll('*', '_')
      .replaceAll('?', '_')
      .replaceAll('"', '_')
      .replaceAll('<', '_')
      .replaceAll('>', '_')
      .replaceAll('|', '_')
      .trim();
    link.download = `qrcode_${safeName || 'member'}.png`;
    link.click();
  }
}

// Close modals when clicking outside
window.onclick = function (event) {
  if (event.target.classList.contains('modal')) {
    event.target.classList.remove('show');
  }
}

// Initial load
window.onload = loadMembers;
