let lastError = null;

async function apiFetch(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            lastError = data.error || `HTTP ${res.status}`;
            showGlobalError(lastError);
            return null;
        }
        return await res.json();
    } catch (e) {
        lastError = 'Brak połączenia z serwerem.';
        showGlobalError(lastError);
        return null;
    }
}

async function apiPost(url, body) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            lastError = data.error || `HTTP ${res.status}`;
            return null;
        }
        return data;
    } catch (e) {
        lastError = 'Brak połączenia z serwerem.';
        return null;
    }
}

async function apiPut(url, body) {
    try {
        const res = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            lastError = data.error || `HTTP ${res.status}`;
            showGlobalError(lastError);
            return null;
        }
        return data;
    } catch (e) {
        lastError = 'Brak połączenia z serwerem.';
        return null;
    }
}

async function apiDelete(url) {
    try {
        const res = await fetch(url, { method: 'DELETE' });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            lastError = data.error || `HTTP ${res.status}`;
            showGlobalError(lastError);
            return false;
        }
        return true;
    } catch (e) {
        lastError = 'Brak połączenia z serwerem.';
        showGlobalError(lastError);
        return false;
    }
}

function showGlobalError(message) {
    let el = document.getElementById('global-error');
    if (!el) {
        el = document.createElement('div');
        el.id = 'global-error';
        el.className = 'alert alert-error';
        el.style.cssText = 'position:fixed;top:16px;right:16px;z-index:9999;max-width:360px;box-shadow:0 4px 12px rgba(0,0,0,0.15)';
        document.body.appendChild(el);
    }
    el.textContent = message;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 5000);
}
