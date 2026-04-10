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

  function initAdminTokenFromUrl() {
    // Allow one-time provisioning without UI:
    // - http://localhost/?admin_token=...  (query)
    // - http://localhost/#admin_token=...  (hash)
    try {
      const url = new URL(window.location.href);

      const qToken = url.searchParams.get('admin_token');
      if (qToken) {
        setAdminToken(qToken);
        url.searchParams.delete('admin_token');
        window.history.replaceState({}, '', url.toString());
        showToast('管理金鑰已設定（從網址參數）', 'success');
        return;
      }

      const hash = (url.hash || '').replace(/^#/, '');
      if (hash.startsWith('admin_token=')) {
        const hToken = decodeURIComponent(hash.slice('admin_token='.length));
        if (hToken) setAdminToken(hToken);
        url.hash = '';
        window.history.replaceState({}, '', url.toString());
        showToast('管理金鑰已設定（從網址片段）', 'success');
      }
    } catch {
      // ignore
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

  window.AppCommon = {
    apiUrl,
    showToast,
    unwrapData,
    apiFetch,
    getAdminToken,
    setAdminToken,
    clearAdminToken,
    initAdminTokenFromUrl
  };

  // Auto-run: provision token from URL (no UI)
  initAdminTokenFromUrl();
})();

