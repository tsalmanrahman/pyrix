// Pyrix Client Application Controller
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
  initLucide();
  initSearch();
  initSortable();
  initDynamicInputs();
  initShortcuts();
  initUserMenu();
});

function initLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

/* ==========================================================================
   👤 USER PROFILE DROPDOWN MENU CONTROLLER
   ========================================================================== */
function initUserMenu() {
  const btn = document.getElementById('user-profile-btn');
  const dropdown = document.getElementById('user-profile-dropdown');
  const container = document.getElementById('user-profile-menu-container');

  if (btn && dropdown) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleUserMenu();
    });

    dropdown.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  document.addEventListener('click', (e) => {
    if (container && dropdown && !container.contains(e.target)) {
      closeUserMenu();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && dropdown && !dropdown.classList.contains('hidden')) {
      closeUserMenu();
    }
  });
}

function toggleUserMenu() {
  const dropdown = document.getElementById('user-profile-dropdown');
  const chevron = document.getElementById('user-profile-chevron');
  if (!dropdown) return;

  const isHidden = dropdown.classList.contains('hidden');
  if (isHidden) {
    dropdown.classList.remove('hidden');
    if (chevron) chevron.classList.add('open');
  } else {
    dropdown.classList.add('hidden');
    if (chevron) chevron.classList.remove('open');
  }
  initLucide();
}

function closeUserMenu() {
  const dropdown = document.getElementById('user-profile-dropdown');
  const chevron = document.getElementById('user-profile-chevron');
  if (dropdown) {
    dropdown.classList.add('hidden');
  }
  if (chevron) {
    chevron.classList.remove('open');
  }
}

/* ==========================================================================
   🌙 / ☀️ ROBUST DARK & LIGHT MODE THEME CONTROLLER
   ========================================================================== */
function initTheme() {
  const serverTheme = document.documentElement.getAttribute('data-theme');
  const currentTheme = serverTheme || localStorage.getItem('pyrix_theme') || 'light';
  applyTheme(currentTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  applyTheme(newTheme);
  localStorage.setItem('pyrix_theme', newTheme);
  document.cookie = `pyrix_theme=${newTheme};path=/;max-age=31536000;SameSite=Lax`;
  
  // Asynchronously persist to SQL Server for the logged-in user
  fetch('/api/user/theme-pref', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme_pref: newTheme })
  }).catch(() => {});

  showToast(`Switched to ${newTheme === 'dark' ? 'Dark Mode' : 'Light Mode'}`);
}

function applyTheme(theme) {
  const activeTheme = (theme === 'dark') ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', activeTheme);
  if (activeTheme === 'light') {
    document.documentElement.classList.add('light');
    document.documentElement.classList.remove('dark');
  } else {
    document.documentElement.classList.add('dark');
    document.documentElement.classList.remove('light');
  }

  const icon = document.getElementById('theme-toggle-icon');
  const btn = document.getElementById('theme-toggle-btn');
  if (icon && btn) {
    if (activeTheme === 'dark') {
      icon.setAttribute('data-lucide', 'sun');
      icon.className = 'w-4 h-4 text-amber-400';
      btn.setAttribute('title', 'Switch to Light Mode');
    } else {
      icon.setAttribute('data-lucide', 'moon');
      icon.className = 'w-4 h-4 text-indigo-600';
      btn.setAttribute('title', 'Switch to Dark Mode');
    }
  }
  initLucide();
}

/* ==========================================================================
   🗂️ SIDEBAR HIDE / UNHIDE (COLLAPSE / EXPAND) CONTROLLER
   ========================================================================== */
function initSidebar() {
  const isCollapsed = localStorage.getItem('pyrix_sidebar_collapsed') === 'true';
  if (isCollapsed) {
    document.documentElement.classList.add('sidebar-collapsed');
  } else {
    document.documentElement.classList.remove('sidebar-collapsed');
  }
  updateSidebarIcon(isCollapsed);
}

function toggleSidebar() {
  const isCurrentlyCollapsed = document.documentElement.classList.contains('sidebar-collapsed');
  const newCollapsedState = !isCurrentlyCollapsed;

  if (newCollapsedState) {
    document.documentElement.classList.add('sidebar-collapsed');
  } else {
    document.documentElement.classList.remove('sidebar-collapsed');
  }

  localStorage.setItem('pyrix_sidebar_collapsed', String(newCollapsedState));
  updateSidebarIcon(newCollapsedState);
  showToast(newCollapsedState ? 'Sidebar collapsed (Full width view)' : 'Sidebar expanded');
}

function updateSidebarIcon(isCollapsed) {
  const icon = document.getElementById('sidebar-toggle-icon');
  const btn = document.getElementById('sidebar-toggle-btn');
  if (!icon || !btn) return;

  if (isCollapsed) {
    icon.setAttribute('data-lucide', 'panel-left-open');
    icon.className = 'w-4 h-4 text-slate-400';
    btn.setAttribute('title', 'Unhide Side Navigation (Ctrl + B)');
  } else {
    icon.setAttribute('data-lucide', 'panel-left');
    icon.className = 'w-4 h-4 text-blue-400';
    btn.setAttribute('title', 'Hide Side Navigation (Ctrl + B)');
  }
  initLucide();
}

// Toast notification helper
function showToast(message, type = 'success') {
  const existing = document.querySelector('.pyrix-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'pyrix-toast';
  const icon = type === 'success' ? 'check-circle-2' : 'alert-circle';
  toast.innerHTML = `<i data-lucide="${icon}" class="w-4 h-4 text-blue-400"></i> <span>${message}</span>`;
  document.body.appendChild(toast);
  initLucide();

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2200);
}

/* ==========================================================================
   🔍 CONTEXT-AWARE HIERARCHICAL SEARCH CONTROLLER
   ========================================================================== */
function initSearch() {
  const searchInput = document.getElementById('global-search');
  const searchContainer = document.getElementById('header-search-container');
  const sliderBox = document.getElementById('search-slider-box');
  const toggleBtn = document.getElementById('search-toggle-btn');
  const clearBtn = document.getElementById('search-clear-btn');

  if (!searchInput || !sliderBox) return;

  // Set intelligent context-aware placeholder based on active screen
  updateSearchContextPlaceholder();

  // Toggle button click with stopPropagation
  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleSearchSlider();
    });
  }

  // Prevent clicks inside search container from triggering document click-outside
  if (searchContainer) {
    searchContainer.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  // Filter page resources on user input
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (clearBtn) {
      if (query.length > 0) {
        clearBtn.classList.remove('hidden');
      } else {
        clearBtn.classList.add('hidden');
      }
    }
    filterUniversal(query);
  });

  // Smooth collapse when clicking outside anywhere on document
  document.addEventListener('click', (e) => {
    if (sliderBox.classList.contains('expanded')) {
      closeSearchSlider();
    }
  });

  // Escape key collapses and resets
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sliderBox.classList.contains('expanded')) {
      clearHeaderSearch();
      closeSearchSlider();
    }
  });
}

function updateSearchContextPlaceholder() {
  const searchInput = document.getElementById('global-search');
  if (!searchInput) return;

  const pathname = window.location.pathname;
  const moduleHeading = document.querySelector('h2.text-lg.font-bold');
  if (moduleHeading && pathname.startsWith('/modules/')) {
    searchInput.setAttribute('placeholder', `Search in ${moduleHeading.innerText.trim()}...`);
  } else if (pathname.startsWith('/settings/')) {
    const pageHeading = document.querySelector('h2, h1');
    const title = pageHeading ? pageHeading.innerText.trim() : 'Settings';
    searchInput.setAttribute('placeholder', `Search in ${title}...`);
  } else {
    searchInput.setAttribute('placeholder', 'Search modules & records...');
  }
}

function filterUniversal(query) {
  // 1. Filter Cards (.module-card-item, .setting-card-item, .sub-area-card)
  const cards = document.querySelectorAll('.setting-card-item, .module-card-item, .sub-area-card');
  cards.forEach(card => {
    const label = card.getAttribute('data-label')?.toLowerCase() || '';
    const desc = card.getAttribute('data-desc')?.toLowerCase() || '';
    const key = card.getAttribute('data-key')?.toLowerCase() || '';
    const code = card.getAttribute('data-code')?.toLowerCase() || '';
    const text = card.innerText.toLowerCase();

    if (!query || label.includes(query) || desc.includes(query) || key.includes(query) || code.includes(query) || text.includes(query)) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });

  // 2. Filter Table Rows (table tbody tr) across all active tables
  const tbodies = document.querySelectorAll('table tbody');
  tbodies.forEach(tbody => {
    const rows = Array.from(tbody.querySelectorAll('tr:not(.pyrix-empty-search-row)'));
    if (rows.length === 0) return;

    let visibleCount = 0;
    rows.forEach(row => {
      const rowText = row.innerText.toLowerCase();
      if (!query || rowText.includes(query)) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    // Handle empty state row inside the table
    const existingEmptyRow = tbody.querySelector('.pyrix-empty-search-row');
    if (visibleCount === 0 && query) {
      if (!existingEmptyRow) {
        const colCount = tbody.closest('table')?.querySelectorAll('thead th').length || 8;
        const emptyTr = document.createElement('tr');
        emptyTr.className = 'pyrix-empty-search-row';
        emptyTr.innerHTML = `
          <td colspan="${colCount}" class="py-8 text-center text-xs text-slate-500 font-medium">
            <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/5 text-slate-400">
              No records matching "<strong>${escapeHtml(query)}</strong>" in this view
            </span>
          </td>
        `;
        tbody.appendChild(emptyTr);
      }
    } else {
      if (existingEmptyRow) {
        existingEmptyRow.remove();
      }
    }
  });
}

function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

function toggleSearchSlider(e) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  const sliderBox = document.getElementById('search-slider-box');
  if (!sliderBox) return;
  
  if (sliderBox.classList.contains('expanded')) {
    closeSearchSlider();
  } else {
    openSearchSlider();
  }
}

function openSearchSlider() {
  const sliderBox = document.getElementById('search-slider-box');
  const toggleBtn = document.getElementById('search-toggle-btn');
  const searchInput = document.getElementById('global-search');

  if (sliderBox) {
    sliderBox.classList.add('expanded');
  }
  if (toggleBtn) {
    toggleBtn.classList.add('active');
  }
  if (searchInput) {
    setTimeout(() => {
      searchInput.focus();
      searchInput.select();
    }, 50);
  }
}

function closeSearchSlider() {
  const sliderBox = document.getElementById('search-slider-box');
  const toggleBtn = document.getElementById('search-toggle-btn');
  const searchInput = document.getElementById('global-search');

  if (sliderBox) {
    sliderBox.classList.remove('expanded');
  }
  if (toggleBtn) {
    toggleBtn.classList.remove('active');
  }
  if (searchInput) {
    searchInput.blur();
  }
}

function clearHeaderSearch() {
  const searchInput = document.getElementById('global-search');
  const clearBtn = document.getElementById('search-clear-btn');
  if (searchInput) {
    searchInput.value = '';
    filterUniversal('');
    searchInput.focus();
  }
  if (clearBtn) {
    clearBtn.classList.add('hidden');
  }
}

// Keyboard shortcuts (Ctrl+K to search, Ctrl+B to toggle sidebar, Ctrl+Shift+C to switch company)
function initShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl + K -> Open and focus search slider
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openSearchSlider();
    }

    // Ctrl + B -> Toggle Sidebar
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && (e.key === 'b' || e.key === 'B')) {
      e.preventDefault();
      toggleSidebar();
    }
  });
}

// Drag and Drop card reordering via SortableJS
function initSortable() {
  const container = document.getElementById('sortable-settings-container');
  if (!container || !window.Sortable) return;

  new Sortable(container, {
    animation: 200,
    handle: '.drag-handle',
    ghostClass: 'sortable-ghost',
    onEnd: async function () {
      const cards = container.querySelectorAll('.setting-card-item');
      const order = Array.from(cards).map(c => parseInt(c.getAttribute('data-option-id')));
      
      try {
        const res = await fetch('/api/dynamic-options/reorder', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ order: order })
        });
        const data = await res.json();
        if (data.success) {
          showToast('Layout arrangement saved to SQL Server.');
        }
      } catch (err) {
        console.error('Reorder error:', err);
        showToast('Failed to save layout order.', 'error');
      }
    }
  });
}

// Live Dynamic Option Inputs auto-save
function initDynamicInputs() {
  document.querySelectorAll('.dynamic-toggle-input').forEach(toggle => {
    toggle.addEventListener('change', async (e) => {
      const key = e.target.getAttribute('data-key');
      const val = e.target.checked ? 'true' : 'false';
      await saveOptionValue(key, val);
    });
  });

  document.querySelectorAll('.dynamic-slider-input').forEach(slider => {
    slider.addEventListener('input', (e) => {
      const bubble = document.getElementById(`val-${e.target.getAttribute('data-key')}`);
      if (bubble) bubble.textContent = e.target.value;
    });

    slider.addEventListener('change', async (e) => {
      const key = e.target.getAttribute('data-key');
      await saveOptionValue(key, e.target.value);
    });
  });

  document.querySelectorAll('.dynamic-select-input').forEach(select => {
    select.addEventListener('change', async (e) => {
      const key = e.target.getAttribute('data-key');
      await saveOptionValue(key, e.target.value);
    });
  });

  document.querySelectorAll('.dynamic-color-input').forEach(picker => {
    picker.addEventListener('change', async (e) => {
      const key = e.target.getAttribute('data-key');
      await saveOptionValue(key, e.target.value);
      if (key === 'app_ui_accent_color') {
        document.documentElement.style.setProperty('--accent-color', e.target.value);
      }
    });
  });

  document.querySelectorAll('.dynamic-text-input').forEach(input => {
    let timeout = null;
    input.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(async () => {
        const key = e.target.getAttribute('data-key');
        await saveOptionValue(key, e.target.value);
      }, 600);
    });
  });
}

async function saveOptionValue(key, value) {
  const formData = new FormData();
  formData.append('option_key', key);
  formData.append('value', value);

  try {
    const res = await fetch('/api/dynamic-options/update-value', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Updated '${key}' successfully.`);
    } else {
      showToast(`Error updating '${key}'.`, 'error');
    }
  } catch (err) {
    console.error('Save error:', err);
    showToast('Failed to save to SQL Server.', 'error');
  }
}

/* ==========================================================================
   ⚡ DYNAMIC TABLE RECORD ACTIONS (EDIT & DELETE)
   ========================================================================== */
async function deleteMasterRecord(entity, recordId, label, rowId) {
  if (!confirm(`Are you sure you want to delete "${label}"? This action will permanently remove it from SQL Server.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/modules/master/${entity}/${recordId}/delete`, {
      method: 'POST'
    });
    const data = await res.json();
    if (data.success) {
      const row = document.getElementById(rowId);
      if (row) {
        row.style.transition = 'all 0.3s ease';
        row.style.opacity = '0';
        row.style.transform = 'scale(0.96)';
        setTimeout(() => row.remove(), 300);
      }
      showToast(`Deleted ${label} successfully.`);
    } else {
      showToast(data.detail || 'Failed to delete record.', 'error');
    }
  } catch (err) {
    console.error('Delete error:', err);
    showToast('Failed to connect to server.', 'error');
  }
}

async function deleteModuleRecord(recordId, refNumber, rowId) {
  if (!confirm(`Are you sure you want to delete transaction "${refNumber}"?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/modules/records/${recordId}/delete`, {
      method: 'POST'
    });
    const data = await res.json();
    if (data.success) {
      const row = document.getElementById(rowId);
      if (row) {
        row.style.transition = 'all 0.3s ease';
        row.style.opacity = '0';
        row.style.transform = 'scale(0.96)';
        setTimeout(() => row.remove(), 300);
      }
      showToast(`Deleted transaction ${refNumber} successfully.`);
    } else {
      showToast('Failed to delete transaction.', 'error');
    }
  } catch (err) {
    console.error('Delete error:', err);
    showToast('Failed to connect to server.', 'error');
  }
}

function editMasterRecord(entity, recordId, label) {
  showToast(`Editing ${label} (Master Setup)...`);
}

function editModuleRecord(recordId, refNumber) {
  showToast(`Editing transaction ${refNumber}...`);
}

// 1. Delete Journal Voucher
async function deleteVoucherRecord(voucherId, voucherNumber, rowId) {
  if (!confirm(`Are you sure you want to delete Journal Voucher "${voucherNumber}"?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/modules/general-ledger/vouchers/${voucherId}/delete`, {
      method: 'POST'
    });
    const data = await res.json();
    if (data.success) {
      const row = document.getElementById(rowId);
      if (row) {
        row.style.transition = 'all 0.3s ease';
        row.style.opacity = '0';
        row.style.transform = 'scale(0.96)';
        setTimeout(() => row.remove(), 300);
      }
      showToast(`Soft-deleted Journal Voucher ${voucherNumber}.`);
    } else {
      showToast('Failed to delete voucher.', 'error');
    }
  } catch (err) {
    console.error('Delete voucher error:', err);
    showToast('Failed to connect to server.', 'error');
  }
}

// 2. Post Journal Batch
async function postBatchRecord(batchId, batchNumber) {
  if (!confirm(`Post Batch "${batchNumber}" to General Ledger? All vouchers in this batch will be posted.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/modules/general-ledger/batches/${batchId}/post`, {
      method: 'POST'
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Batch ${batchNumber} posted to General Ledger!`);
      setTimeout(() => location.reload(), 600);
    } else {
      showToast('Failed to post batch.', 'error');
    }
  } catch (err) {
    console.error('Post batch error:', err);
    showToast('Failed to connect to server.', 'error');
  }
}

// 3. Delete Journal Batch
async function deleteBatchRecord(batchId, batchNumber, rowId) {
  if (!confirm(`Are you sure you want to delete Batch "${batchNumber}"?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/modules/general-ledger/batches/${batchId}/delete`, {
      method: 'POST'
    });
    const data = await res.json();
    if (data.success) {
      const row = document.getElementById(rowId);
      if (row) {
        row.style.transition = 'all 0.3s ease';
        row.style.opacity = '0';
        row.style.transform = 'scale(0.96)';
        setTimeout(() => row.remove(), 300);
      }
      showToast(`Deleted batch ${batchNumber}.`);
    } else {
      showToast('Failed to delete batch.', 'error');
    }
  } catch (err) {
    console.error('Delete batch error:', err);
    showToast('Failed to connect to server.', 'error');
  }
}

// 4. Auto Batch Generator
async function triggerAutoBatchGeneration() {
  showToast('Generating automated journal batch from recurring rules...');
  try {
    const res = await fetch('/api/modules/general-ledger/batches/generate-auto', {
      method: 'POST'
    });
    const data = await res.json();
    if (data.success) {
      showToast('Automated Journal Batch generated!');
      setTimeout(() => location.reload(), 700);
    } else {
      showToast(data.message || 'Failed to generate auto batch.', 'error');
    }
  } catch (err) {
    console.error('Auto batch error:', err);
    showToast('Failed to connect to server.', 'error');
  }
}

// 5. Generate Batch from Template
async function generateFromTemplate(templateId, templateName) {
  const amountStr = prompt(`Generate Journal Batch from template "${templateName}". Enter batch amount:`, "50000.00");
  if (!amountStr) return;

  const amount = parseFloat(amountStr) || 50000.0;
  showToast(`Instantiating batch from "${templateName}"...`);

  try {
    const formData = new FormData();
    formData.append('template_id', templateId);
    formData.append('amount', amount.toString());

    const res = await fetch('/api/modules/general-ledger/batches/generate-from-template', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Batch successfully generated from template!`);
      setTimeout(() => window.location.href = '/modules/general-ledger?tab=batches', 800);
    } else {
      showToast(data.message || 'Failed to generate batch.', 'error');
    }
  } catch (err) {
    console.error('Template batch error:', err);
    showToast('Failed to connect to server.', 'error');
  }
}

