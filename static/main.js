const input = document.getElementById('email-input');
const charCount = document.getElementById('char-count');
const resultPanel = document.getElementById('result-panel');
const resultInner = document.getElementById('result-inner');
const resultIcon = document.getElementById('result-icon');
const resultLabel = document.getElementById('result-label');
const resultConf = document.getElementById('result-confidence');
const confBar = document.getElementById('confidence-bar');
const historyList = document.getElementById('history-list');
const historyCount = document.getElementById('history-count');
const loadingOverlay = document.getElementById('loading-overlay');

input.addEventListener('input', () => {
  charCount.textContent = input.value.length;
});

function clearInput() {
  input.value = '';
  charCount.textContent = '0';
  resultPanel.classList.remove('visible');
}

async function analyzeEmail() {
  const text = input.value.trim();

  if (!text) {
    input.focus();
    input.style.borderColor = '#ff4d6d';
    setTimeout(() => input.style.borderColor = '', 1200);
    return;
  }

  loadingOverlay.classList.add('active');

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    // ✅ FIX: handle server + API errors properly
    if (!res.ok || data.error) {
      alert(data.error || "Server error");
      return;
    }

    // ✅ FIX: ensure number format
    const confidence = Math.round(data.confidence);

    showResult(data.result, confidence);
    updateStats(data.result);
    addHistoryItem(text, data.result, confidence);

  } catch (e) {
    alert('Something went wrong. Is the server running?');
  } finally {
    loadingOverlay.classList.remove('active');
  }
}

function showResult(result, confidence) {
  const isSpam = result === 'spam';

  resultInner.className = 'result-inner glass ' + (isSpam ? 'spam' : 'safe');
  resultIcon.textContent = isSpam ? '🚨' : '✅';
  resultLabel.textContent = isSpam ? 'SPAM DETECTED' : 'SAFE EMAIL';
  resultConf.textContent = `Confidence: ${confidence}%`;

  confBar.style.width = '0%';
  resultPanel.classList.add('visible');

  setTimeout(() => {
    confBar.style.width = confidence + '%';
  }, 100);
}

function updateStats(result) {
  const totalEl = document.getElementById('stat-total');
  const spamEl = document.getElementById('stat-spam');
  const safeEl = document.getElementById('stat-safe');

  totalEl.textContent = parseInt(totalEl.textContent) + 1;

  if (result === 'spam') {
    spamEl.textContent = parseInt(spamEl.textContent) + 1;
  } else {
    safeEl.textContent = parseInt(safeEl.textContent) + 1;
  }
}

function addHistoryItem(text, result, confidence) {
  const now = new Date();
  const ts = now.toISOString().replace('T', ' ').substring(0, 19);

  const preview = text.length > 80 ? text.substring(0, 80) + '...' : text;

  const badgeClass = result === 'spam' ? 'spam' : 'ham';
  const borderClass = badgeClass;
  const badgeText = result.toUpperCase();

  const empty = historyList.querySelector('.empty-state');
  if (empty) empty.remove();

  const item = document.createElement('div');
  item.className = `history-item ${borderClass}`;
  item.style.animation = 'slideUp 0.3s cubic-bezier(0.22,1,0.36,1)';

  item.innerHTML = `
    <div class="history-left">
      <span class="history-badge ${badgeClass}">${badgeText}</span>
      <span class="history-text">${escapeHtml(preview)}</span>
    </div>
    <div class="history-right">
      <span class="history-conf">${confidence}%</span>
      <span class="history-time">${ts}</span>
    </div>
  `;

  historyList.insertBefore(item, historyList.firstChild);

  const items = historyList.querySelectorAll('.history-item');
  if (items.length > 20) items[items.length - 1].remove();

  const count = historyList.querySelectorAll('.history-item').length;
  historyCount.textContent = count + ' ' + (count === 1 ? 'entry' : 'entries');
}

function escapeHtml(str) {
  return str
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

// shortcut: Ctrl + Enter
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    analyzeEmail();
  }
});