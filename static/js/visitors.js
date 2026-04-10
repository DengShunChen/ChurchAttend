const apiUrl = '/api';

// Toast notification function
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// Load visitors list
async function loadVisitors() {
  const loading = document.getElementById('loadingIndicator');
  const tbody = document.getElementById('visitorsBody');
  const searchTerm = document.getElementById('searchTerm').value.trim();

  loading.classList.add('active');

  try {
    let url = `${apiUrl}/visitors`;

    const response = await fetch(url);
    const result = await response.json();
    // Handle both new paginated format and old array format
    let visitors = result.data || result;

    // Client-side filter
    if (Array.isArray(visitors) && searchTerm) {
      const q = String(searchTerm);
      visitors = visitors.filter(v => {
        const name = v?.name ? String(v.name) : '';
        const phone = v?.phone ? String(v.phone) : '';
        return name.includes(q) || phone.includes(q);
      });
    }

    tbody.replaceChildren();

    if (!Array.isArray(visitors) || visitors.length === 0) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 5;
      td.className = 'empty-state';
      const p = document.createElement('p');
      p.textContent = '查無訪客資料';
      td.appendChild(p);
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }

    visitors.forEach((visitor) => {
      const row = document.createElement('tr');

      const nameCell = document.createElement('td');
      const strong = document.createElement('strong');
      strong.textContent = visitor?.name ?? '';
      nameCell.appendChild(strong);

      const phoneCell = document.createElement('td');
      phoneCell.textContent = visitor?.phone || '-';

      const howCell = document.createElement('td');
      howCell.textContent = visitor?.how_to_know || '-';

      const firstCell = document.createElement('td');
      firstCell.textContent = visitor?.first_visit_date ?? '';

      const countCell = document.createElement('td');
      const badge = document.createElement('span');
      badge.className = 'badge';
      badge.textContent = String(visitor?.visit_count ?? '');
      countCell.appendChild(badge);

      row.appendChild(nameCell);
      row.appendChild(phoneCell);
      row.appendChild(howCell);
      row.appendChild(firstCell);
      row.appendChild(countCell);
      tbody.appendChild(row);
    });
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
  searchTimeout = setTimeout(loadVisitors, 500);
});

// Modal functions
function openCheckinModal() {
  document.getElementById('checkinForm').reset();
  document.getElementById('checkinModal').classList.add('show');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('show');
}

// Submit check-in
async function submitCheckin() {
  const form = document.getElementById('checkinForm');
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);

  // Validate
  if (!data.name) {
    showToast('請輸入姓名', 'error');
    return;
  }

  try {
    const response = await fetch(`${apiUrl}/visitors/checkin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (response.ok) {
      let msg = '訪客簽到成功';
      if (result.is_return_visitor) {
        msg = `歡迎回來！${result.name} (第 ${result.visit_count} 次來訪)`;
      }
      showToast(msg);
      closeModal('checkinModal');
      loadVisitors();
    } else {
      showToast(result.error || '簽到失敗', 'error');
    }
  } catch (error) {
    console.error('Error:', error);
    showToast('發生錯誤', 'error');
  }
}

// Close modals when clicking outside
window.onclick = function (event) {
  if (event.target.classList.contains('modal')) {
    event.target.classList.remove('show');
  }
}

// Initial load
window.onload = loadVisitors;
