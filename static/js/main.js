/* =========================================================
   SplitMint — Main JavaScript
   ========================================================= */

'use strict';

// ── Auto-initialize Bootstrap Toasts ──────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Toast auto-show
  document.querySelectorAll('.toast').forEach(el => {
    const toast = new bootstrap.Toast(el, { delay: 4000 });
    toast.show();
  });

  // Active nav highlighting
  highlightActiveNav();

  // Date input defaults
  setDefaultDates();

  // Participant checkboxes toggle effect
  initParticipantUI();

  // Split type watcher (if on expense pages)
  initSplitTypeWatcher();

  // Percentage total watcher
  initPctWatcher();
});

// ── Active Nav ─────────────────────────────────────────────
function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && path.startsWith(href) && href !== '/') {
      link.classList.add('active');
    }
  });
}

// ── Default date = today ───────────────────────────────────
function setDefaultDates() {
  const dateInputs = document.querySelectorAll('input[type="date"]');
  const today = new Date().toISOString().split('T')[0];
  dateInputs.forEach(inp => {
    if (!inp.value) inp.value = today;
  });
}

// ── Participant checkbox card effect ──────────────────────
function initParticipantUI() {
  document.querySelectorAll('.participant-checkbox').forEach(cb => {
    const label = cb.closest('.sm-participant-item');
    if (!label) return;

    const updateStyle = () => {
      if (cb.checked) {
        label.style.borderColor = 'var(--mint)';
        label.style.background = 'rgba(0,229,160,0.07)';
        label.querySelector('.sm-pi-avatar').style.background = 'rgba(0,229,160,0.15)';
        label.querySelector('.sm-pi-avatar').style.color = 'var(--mint)';
      } else {
        label.style.borderColor = '';
        label.style.background = '';
        const av = label.querySelector('.sm-pi-avatar');
        if (av) { av.style.background = ''; av.style.color = ''; }
      }
    };

    updateStyle();
    cb.addEventListener('change', updateStyle);
  });
}

// ── Split type watcher ─────────────────────────────────────
function initSplitTypeWatcher() {
  const select = document.getElementById('id_split_type');
  if (!select) return;

  const customSection = document.getElementById('customSplitSection');
  const percentSection = document.getElementById('percentSplitSection');

  const toggle = () => {
    const val = select.value;
    if (customSection) customSection.style.display = val === 'custom' ? '' : 'none';
    if (percentSection) percentSection.style.display = val === 'percentage' ? '' : 'none';
    syncCustomRowVisibility();
  };

  select.addEventListener('change', toggle);
  toggle();

  // Also update when participants change
  document.querySelectorAll('.participant-checkbox').forEach(cb => {
    cb.addEventListener('change', syncCustomRowVisibility);
  });
}

// Show/hide custom & pct rows based on checked participants
function syncCustomRowVisibility() {
  const checked = new Set(
    [...document.querySelectorAll('.participant-checkbox:checked')].map(c => c.value)
  );
  document.querySelectorAll('.custom-row, .pct-row').forEach(row => {
    row.style.display = checked.has(row.dataset.userId) ? '' : 'none';
  });
  updatePctTotal();
}

// ── Percentage total updater ───────────────────────────────
function initPctWatcher() {
  document.querySelectorAll('[id^="pct_"]').forEach(inp => {
    inp.addEventListener('input', updatePctTotal);
  });
  updatePctTotal();
}

function updatePctTotal() {
  const el = document.getElementById('pctTotal');
  if (!el) return;

  let total = 0;
  document.querySelectorAll('.pct-row').forEach(row => {
    if (row.style.display === 'none') return;
    const inp = row.querySelector('input[type="number"]');
    if (inp) total += parseFloat(inp.value || 0);
  });

  el.textContent = `Total: ${total.toFixed(1)}%`;
  const ok = Math.abs(total - 100) < 0.11;
  el.className = 'small mt-1 fw-500 ' + (ok ? 'text-success' : 'text-danger');
}

// ── Confirm delete helper ──────────────────────────────────
function confirmDelete(msg) {
  return window.confirm(msg || 'Are you sure you want to delete this?');
}

// ── Format currency ────────────────────────────────────────
function formatINR(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', maximumFractionDigits: 2
  }).format(amount);
}

// ── AI MintSense inline parser (add_expense page) ─────────
async function quickParse() {
  const inputEl = document.getElementById('aiParseInput');
  const statusEl = document.getElementById('aiParseStatus');
  const btnEl = document.getElementById('aiParseBtn');
  if (!inputEl) return;

  const text = inputEl.value.trim();
  if (!text) { inputEl.focus(); return; }

  btnEl.disabled = true;
  btnEl.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Parsing…';
  if (statusEl) { statusEl.classList.remove('d-none'); statusEl.textContent = 'Sending to MintSense AI…'; }

  const formData = new FormData();
  formData.append('user_input', text);
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
  if (csrf) formData.append('csrfmiddlewaretoken', csrf.value);

  try {
    const resp = await fetch('/ai/parse/', { method: 'POST', body: formData });
    const html = await resp.text();

    // Extract parsed values from response HTML using a hidden parser trick
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    const rfValues = doc.querySelectorAll('.sm-rf-value');
    let title = '', amount = '', category = '';
    if (rfValues.length >= 2) {
      title = rfValues[0]?.textContent?.trim() || '';
      amount = rfValues[1]?.textContent?.replace('₹', '').trim() || '';
    }
    if (rfValues.length >= 3) {
      category = rfValues[2]?.textContent?.trim().toLowerCase() || 'other';
    }

    // Fallback: regex parse from text if AI result not extractable
    if (!title) {
      const words = text.split(' ').slice(0, 5).join(' ');
      title = words.charAt(0).toUpperCase() + words.slice(1);
    }
    if (!amount) {
      const m = text.match(/[\d,]+\.?\d*/);
      if (m) amount = m[0].replace(',', '');
    }

    const titleEl = document.getElementById('id_title');
    const amountEl = document.getElementById('id_amount');
    const categoryEl = document.getElementById('id_category');

    if (titleEl && title) titleEl.value = title;
    if (amountEl && amount) amountEl.value = amount;
    if (categoryEl && category) {
      [...categoryEl.options].forEach(opt => {
        if (opt.value === category) opt.selected = true;
      });
    }

    if (statusEl) statusEl.textContent = '✓ Form filled from your description.';
    btnEl.innerHTML = '<i class="bi bi-magic me-1"></i>Re-Parse';
  } catch (err) {
    // Graceful fallback
    const words = text.split(' ').slice(0, 5).join(' ');
    const titleEl = document.getElementById('id_title');
    const amountEl = document.getElementById('id_amount');
    const m = text.match(/[\d,]+\.?\d*/);

    if (titleEl) titleEl.value = words.charAt(0).toUpperCase() + words.slice(1);
    if (amountEl && m) amountEl.value = m[0].replace(',', '');

    if (statusEl) statusEl.textContent = 'AI unavailable — applied basic fill.';
    btnEl.innerHTML = '<i class="bi bi-magic me-1"></i>Parse';
  } finally {
    btnEl.disabled = false;
  }
}

// ── Group AI Summary loader ────────────────────────────────
async function loadAISummary(groupPk) {
  const btn = document.getElementById('aiSummaryBtn');
  const result = document.getElementById('aiSummaryText');
  if (!btn || !result) return;

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Thinking…';

  try {
    const resp = await fetch(`/ai/group/${groupPk}/summary/`);
    const data = await resp.json();
    result.textContent = data.summary || 'No summary available.';
    result.classList.remove('d-none');
    btn.innerHTML = '<i class="bi bi-magic me-1"></i>Regenerate';
  } catch {
    result.textContent = 'Could not load AI summary. Please check your Anthropic API key in .env';
    result.classList.remove('d-none');
    btn.innerHTML = '<i class="bi bi-magic me-1"></i>Retry';
  } finally {
    btn.disabled = false;
  }
}

// ── Expose globals ─────────────────────────────────────────
window.quickParse = quickParse;
window.loadAISummary = loadAISummary;
window.confirmDelete = confirmDelete;
window.updatePctTotal = updatePctTotal;
