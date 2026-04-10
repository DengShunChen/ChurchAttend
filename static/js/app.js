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

// Set today's date
function setTodayDate() {
  const currentDate = new Date().toISOString().split('T')[0];
  document.getElementById('date').value = currentDate;
}

// Load statistics
async function loadStatistics() {
  try {
    const response = await fetch(`${apiUrl}/stats`);
    const stats = await response.json();

    document.getElementById('todayCount').textContent = stats.today_count || 0;
    document.getElementById('totalCount').textContent = stats.total_count || 0;
    document.getElementById('lastUpdate').textContent = stats.latest_date || '-';
  } catch (error) {
    console.error('Error loading statistics:', error);
  }
}

// Refresh attendance list
async function refreshAttendance(params = {}) {
  const loadingIndicator = document.getElementById('loadingIndicator');
  const tableBody = document.getElementById('attendanceBody');

  loadingIndicator.classList.add('active');

  try {
    const queryString = new URLSearchParams(params).toString();
    const url = `${apiUrl}/attendance${queryString ? '?' + queryString : ''}`;

    const response = await fetch(url);
    const result = await response.json();
    // Handle both new paginated format and old array format
    const data = result.data || result;

    tableBody.innerHTML = '';

    if (!Array.isArray(data) || data.length === 0) {
      tableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="empty-state">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        <p>目前沒有記錄</p>
                    </td>
                </tr>
            `;
    } else {
      data.forEach(entry => {
        const row = tableBody.insertRow();

        const dateCell = row.insertCell();
        dateCell.textContent = entry.date ?? '';

        const nameCell = row.insertCell();
        const strong = document.createElement('strong');
        strong.textContent = entry.name ?? '';
        nameCell.appendChild(strong);

        const actionCell = row.insertCell();
        actionCell.style.textAlign = 'center';

        const btn = document.createElement('button');
        btn.className = 'btn btn-danger';
        btn.type = 'button';
        btn.textContent = '🗑️ 刪除';
        btn.dataset.attendanceId = entry._id ?? '';
        btn.addEventListener('click', () => deleteAttendance(btn.dataset.attendanceId));
        actionCell.appendChild(btn);
      });
    }
  } catch (error) {
    console.error('Error:', error);
    showToast('載入資料失敗', 'error');
  } finally {
    loadingIndicator.classList.remove('active');
  }
}

// Apply filters
function applyFilters() {
  const searchName = document.getElementById('searchName').value.trim();
  const dateFrom = document.getElementById('filterDateFrom').value;
  const dateTo = document.getElementById('filterDateTo').value;

  const params = {};
  if (searchName) params.search = searchName;
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;

  refreshAttendance(params);
}

// Real-time search
document.getElementById('searchName').addEventListener('input', function () {
  clearTimeout(this.searchTimeout);
  this.searchTimeout = setTimeout(() => {
    applyFilters();
  }, 500);
});

// Form submission
document.getElementById('attendanceForm').addEventListener('submit', async function (event) {
  event.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);

  try {
    const response = await fetch(`${apiUrl}/attendance`, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const result = await response.json();

    if (response.ok) {
      showToast('報到成功！', 'success');
      this.reset();
      setTodayDate();
      document.getElementById('name').focus();
      refreshAttendance();
      loadStatistics();
    } else {
      showToast(result.error || '報到失敗', 'error');
    }
  } catch (error) {
    console.error('Error:', error);
    showToast('發生錯誤，請稍後再試', 'error');
  }
});

// Delete attendance
async function deleteAttendance(attendanceId) {
  if (!confirm('確定要刪除這筆記錄嗎？')) {
    return;
  }

  try {
    const response = await fetch(`${apiUrl}/attendance/${attendanceId}`, {
      method: 'DELETE'
    });

    const result = await response.json();

    if (response.ok) {
      showToast('刪除成功！', 'success');
      refreshAttendance();
      loadStatistics();
    } else {
      showToast(result.error || '刪除失敗', 'error');
    }
  } catch (error) {
    console.error('Error:', error);
    showToast('發生錯誤，請稍後再試', 'error');
  }
}

// Refresh page
function refreshPage() {
  document.getElementById('searchName').value = '';
  document.getElementById('filterDateFrom').value = '';
  document.getElementById('filterDateTo').value = '';
  setTodayDate();
  refreshAttendance();
  loadStatistics();
  showToast('頁面已更新！', 'success');
}

// Export to CSV
async function exportToCSV() {
  try {
    const response = await fetch(`${apiUrl}/attendance`);
    const result = await response.json();
    const data = result.data || result; // Handle both formats

    const csv = convertToCSV(data);
    const csvData = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const csvUrl = window.URL.createObjectURL(csvData);
    const link = document.createElement('a');
    link.href = csvUrl;
    const filename = `attendance_${new Date().toISOString().split('T')[0]}.csv`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('CSV 檔案已下載！', 'success');
  } catch (error) {
    console.error('Error:', error);
    showToast('下載失敗', 'error');
  }
}

// Convert to CSV
function convertToCSV(data) {
  const header = ['日期', '姓名'];
  const csvRows = [];
  csvRows.push(header.join(','));
  data.forEach(entry => {
    const row = [entry.date, entry.name];
    csvRows.push(row.join(','));
  });
  return csvRows.join('\n');
}

// Auto-focus name field on Enter
document.getElementById('date').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    document.getElementById('name').focus();
  }
});

// QR Scanner Logic
let videoStream;
let isScanning = false;

function toggleScanner() {
  const wrapper = document.getElementById('scanner-wrapper');
  if (wrapper.classList.contains('active')) {
    stopCamera();
  } else {
    startCamera();
  }
}

async function startCamera() {
  const wrapper = document.getElementById('scanner-wrapper');
  const video = document.getElementById('scanner-video');
  const resultDiv = document.getElementById('scan-result');

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
    videoStream = stream;
    video.srcObject = stream;
    video.setAttribute("playsinline", true);
    video.play();

    wrapper.classList.add('active');
    resultDiv.style.display = 'none';

    isScanning = true;
    requestAnimationFrame(tick);
  } catch (error) {
    console.error('Error accessing camera:', error);
    showToast('無法存取相機，請確認權限或使用 HTTPS', 'error');
  }
}

function stopCamera() {
  if (videoStream) {
    videoStream.getTracks().forEach(track => track.stop());
    videoStream = null;
  }
  isScanning = false;
  document.getElementById('scanner-wrapper').classList.remove('active');
}

function tick() {
  if (!isScanning) return;

  const video = document.getElementById('scanner-video');
  const canvasElement = document.getElementById('scanner-canvas');
  const canvas = canvasElement.getContext('2d');

  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvasElement.height = video.videoHeight;
    canvasElement.width = video.videoWidth;
    canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

    const imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: "dontInvert",
    });

    if (code) {
      processQRCode(code.data);
    }
  }

  if (isScanning) requestAnimationFrame(tick);
}

async function processQRCode(qrData) {
  isScanning = false; // Pause scanning
  const resultDiv = document.getElementById('scan-result');
  resultDiv.style.display = 'block';
  resultDiv.textContent = '🔄 處理中...';

  try {
    const response = await fetch(`${apiUrl}/attendance/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        qr_data: qrData,
        session: 'noon' // Default to noon session
      })
    });

    const result = await response.json();

    if (response.ok) {
      resultDiv.textContent = `✅ ${result.name} 簽到成功！`;
      resultDiv.style.background = '#e8f5e9';
      resultDiv.style.color = '#2e7d32';
      showToast(`${result.name} 簽到成功！`, 'success');

      // Update stats and list
      refreshAttendance();
      loadStatistics();

      // Resume scanning after 2 seconds
      setTimeout(() => {
        resultDiv.style.display = 'none';
        isScanning = true;
        requestAnimationFrame(tick);
      }, 2000);
    } else {
      throw new Error(result.error || '簽到失敗');
    }
  } catch (error) {
    resultDiv.textContent = `❌ ${error.message}`;
    resultDiv.style.background = '#ffebee';
    resultDiv.style.color = '#c62828';
    showToast(error.message, 'error');

    // Resume scanning after 3 seconds
    setTimeout(() => {
      resultDiv.style.display = 'none';
      isScanning = true;
      requestAnimationFrame(tick);
    }, 3000);
  }
}

async function handleQRFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const img = new Image();
    img.onload = function () {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code) {
        processQRCode(code.data);
      } else {
        showToast('無法辨識 QR Code', 'error');
      }
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
  event.target.value = ''; // Reset input
}

// Initialize on page load
window.onload = function () {
  setTodayDate();
  refreshAttendance();
  loadStatistics();
  document.getElementById('name').focus();
};
