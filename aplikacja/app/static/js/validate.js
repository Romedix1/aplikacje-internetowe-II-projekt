function validateRequired(fieldId, errorId) {
    const el = document.getElementById(fieldId);
    const err = document.getElementById(errorId);
    if (!el || !el.value.trim()) {
        el?.classList.add('error');
        if (err) err.classList.add('show');
        return false;
    }
    el.classList.remove('error');
    if (err) err.classList.remove('show');
    return true;
}

function validateEmail(fieldId, errorId) {
    const el = document.getElementById(fieldId);
    const err = document.getElementById(errorId);
    if (!el) return false;
    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value);
    if (!valid) {
        el.classList.add('error');
        if (err) { err.textContent = 'Nieprawidłowy adres e-mail.'; err.classList.add('show'); }
        return false;
    }
    el.classList.remove('error');
    if (err) err.classList.remove('show');
    return true;
}

function validateIndexNumber(fieldId, errorId) {
    const el = document.getElementById(fieldId);
    const err = document.getElementById(errorId);
    if (!el) return false;
    const valid = /^\d{5}$/.test(el.value.trim());
    if (!valid) {
        el.classList.add('error');
        if (err) { err.textContent = 'Numer indeksu musi mieć dokładnie 5 cyfr.'; err.classList.add('show'); }
        return false;
    }
    el.classList.remove('error');
    if (err) err.classList.remove('show');
    return true;
}

function validateDateRange(startId, endId, errorId) {
    const start = document.getElementById(startId)?.value;
    const end   = document.getElementById(endId)?.value;
    const err   = document.getElementById(errorId);
    if (start && end && end <= start) {
        document.getElementById(endId)?.classList.add('error');
        if (err) { err.textContent = 'Data zakończenia musi być późniejsza niż rozpoczęcia.'; err.classList.add('show'); }
        return false;
    }
    document.getElementById(endId)?.classList.remove('error');
    if (err) err.classList.remove('show');
    return true;
}

function clearErrors(fieldIds) {
    fieldIds.forEach(id => {
        document.getElementById(id)?.classList.remove('error');
        const err = document.getElementById(id.replace('f-','e-'));
        err?.classList.remove('show');
    });
}
