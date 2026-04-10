// Shared helpers for all pages (no build step).
// Exposed via window.AppCommon.

(() => {
  const apiUrl = '/api';
  const adminTokenStorageKey = 'admin_token';

  function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = String(message ?? '');
    toast.className = `toast show ${type}`;
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  }

  function unwrapData(result) {
    return result && typeof result === 'object' && 'data' in result ? result.data : result;
  }

  function getAdminToken() {
    try {
      return localStorage.getItem(adminTokenStorageKey) || '';
    } catch {
      return '';
    }
  }

  function setAdminToken(token) {
    try {
      localStorage.setItem(adminTokenStorageKey, String(token ?? ''));
      return true;
    } catch {
      return false;
    }
  }

  function clearAdminToken() {
    try {
      localStorage.removeItem(adminTokenStorageKey);
      return true;
    } catch {
      return false;
    }
  }

  function isWriteMethod(method) {
    const m = String(method || 'GET').toUpperCase();
    return m === 'POST' || m === 'PUT' || m === 'PATCH' || m === 'DELETE';
  }

  async function apiFetch(path, options = {}) {
    const opts = { ...options };
    const method = (opts.method || 'GET').toUpperCase();
    const token = getAdminToken();

    if (token && isWriteMethod(method)) {
      const headers = new Headers(opts.headers || {});
      headers.set('X-Admin-Token', token);
      opts.headers = headers;
    }

    const res = await fetch(`${apiUrl}${path}`, opts);
    const contentType = res.headers.get('content-type') || '';
    let body;
    if (contentType.includes('application/json')) {
      body = await res.json();
    } else {
      body = await res.text();
    }
    return { res, body };
  }

  function initAdminTokenUI() {
    const openBtn = document.getElementById('adminTokenBtn');
    const modal = document.getElementById('adminTokenModal');
    const input = document.getElementById('adminTokenInput');
    const saveBtn = document.getElementById('adminTokenSaveBtn');
    const clearBtn = document.getElementById('adminTokenClearBtn');
    const closeBtn = document.getElementById('adminTokenCloseBtn');

    if (!openBtn || !modal || !input || !saveBtn || !clearBtn || !closeBtn) return;

    const open = () => {
      input.value = getAdminToken();
      modal.classList.add('show');
      input.focus();
      input.select();
    };
    const close = () => modal.classList.remove('show');

    openBtn.addEventListener('click', open);
    closeBtn.addEventListener('click', close);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) close();
    });

    saveBtn.addEventListener('click', () => {
      const ok = setAdminToken(input.value.trim());
      if (ok) {
        showToast('管理金鑰已儲存（僅存於本機瀏覽器）', 'success');
        close();
      } else {
        showToast('儲存失敗（瀏覽器可能禁止 localStorage）', 'error');
      }
    });

    clearBtn.addEventListener('click', () => {
      const ok = clearAdminToken();
      if (ok) {
        input.value = '';
        showToast('管理金鑰已清除', 'success');
        close();
      } else {
        showToast('清除失敗（瀏覽器可能禁止 localStorage）', 'error');
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        saveBtn.click();
      }
      if (e.key === 'Escape') {
        e.preventDefault();
        close();
      }
    });
  }

  window.AppCommon = {
    apiUrl,
    showToast,
    unwrapData,
    apiFetch,
    getAdminToken,
    setAdminToken,
    clearAdminToken,
    initAdminTokenUI
  };
})();

