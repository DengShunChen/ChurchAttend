// Shared helpers for all pages (no build step).
// Exposed via window.AppCommon.

(() => {
  const apiUrl = '/api';

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

  async function apiFetch(path, options = {}) {
    const res = await fetch(`${apiUrl}${path}`, options);
    const contentType = res.headers.get('content-type') || '';
    let body;
    if (contentType.includes('application/json')) {
      body = await res.json();
    } else {
      body = await res.text();
    }
    return { res, body };
  }

  window.AppCommon = { apiUrl, showToast, unwrapData, apiFetch };
})();

