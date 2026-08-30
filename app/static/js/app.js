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
  initSmartTables();
  initDragToScroll();
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
   🗂️ RESPONSIVE SIDEBAR & OFF-CANVAS DRAWER CONTROLLER
   ========================================================================== */
function isSmallScreen() {
  return window.innerWidth < 1024;
}

function initSidebar() {
  const htmlEl = document.documentElement;
  
  if (isSmallScreen()) {
    htmlEl.classList.add('sidebar-collapsed');
    htmlEl.classList.remove('sidebar-open-mobile');
  } else {
    const isCollapsed = localStorage.getItem('pyrix_sidebar_collapsed') === 'true';
    if (isCollapsed) {
      htmlEl.classList.add('sidebar-collapsed');
    } else {
      htmlEl.classList.remove('sidebar-collapsed');
    }
  }

  updateSidebarIcon();

  // 1. Click/Touch outside backdrop listener
  const backdrop = document.getElementById('sidebar-backdrop');
  if (backdrop) {
    backdrop.addEventListener('click', closeSidebarMobile);
    backdrop.addEventListener('touchstart', closeSidebarMobile, { passive: true });
  }

  // 2. Escape key listener to close mobile drawer
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && document.documentElement.classList.contains('sidebar-open-mobile')) {
      closeSidebarMobile();
    }
  });

  // 3. Auto-close mobile drawer when user clicks any navigation link inside sidebar
  const sidebar = document.querySelector('.floating-sidebar');
  if (sidebar) {
    sidebar.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      if (link && isSmallScreen()) {
        closeSidebarMobile();
      }
    });
  }

  // 4. Smart window resize listener
  window.addEventListener('resize', handleSidebarResize);
}

function handleSidebarResize() {
  const htmlEl = document.documentElement;
  if (isSmallScreen()) {
    // If resized to mobile, make sure docked desktop open state doesn't cause overlap
    if (!htmlEl.classList.contains('sidebar-open-mobile')) {
      htmlEl.classList.add('sidebar-collapsed');
    }
  } else {
    // If resized to desktop, remove mobile drawer open state and restore desktop preference
    htmlEl.classList.remove('sidebar-open-mobile');
    const isCollapsed = localStorage.getItem('pyrix_sidebar_collapsed') === 'true';
    if (isCollapsed) {
      htmlEl.classList.add('sidebar-collapsed');
    } else {
      htmlEl.classList.remove('sidebar-collapsed');
    }
  }
  updateSidebarIcon();
}

function toggleSidebar() {
  const htmlEl = document.documentElement;

  if (isSmallScreen()) {
    const isCurrentlyOpen = htmlEl.classList.contains('sidebar-open-mobile');
    if (isCurrentlyOpen) {
      closeSidebarMobile();
    } else {
      openSidebarMobile();
    }
  } else {
    const isCurrentlyCollapsed = htmlEl.classList.contains('sidebar-collapsed');
    const newCollapsedState = !isCurrentlyCollapsed;

    if (newCollapsedState) {
      htmlEl.classList.add('sidebar-collapsed');
    } else {
      htmlEl.classList.remove('sidebar-collapsed');
    }

    localStorage.setItem('pyrix_sidebar_collapsed', String(newCollapsedState));
    updateSidebarIcon();
    showToast(newCollapsedState ? 'Sidebar collapsed (Full width view)' : 'Sidebar expanded');
  }
}

function openSidebarMobile() {
  document.documentElement.classList.add('sidebar-open-mobile');
  updateSidebarIcon();
}

function closeSidebarMobile() {
  document.documentElement.classList.remove('sidebar-open-mobile');
  updateSidebarIcon();
}

function updateSidebarIcon() {
  const icon = document.getElementById('sidebar-toggle-icon');
  const btn = document.getElementById('sidebar-toggle-btn');
  if (!icon || !btn) return;

  const htmlEl = document.documentElement;
  const isMobile = isSmallScreen();
  const isOpen = isMobile 
    ? htmlEl.classList.contains('sidebar-open-mobile') 
    : !htmlEl.classList.contains('sidebar-collapsed');

  if (isOpen) {
    icon.setAttribute('data-lucide', isMobile ? 'x' : 'panel-left');
    icon.className = 'w-4 h-4 text-blue-400';
    btn.setAttribute('title', 'Hide Side Navigation (Ctrl + B)');
  } else {
    icon.setAttribute('data-lucide', isMobile ? 'menu' : 'panel-left-open');
    icon.className = 'w-4 h-4 text-slate-400';
    btn.setAttribute('title', 'Unhide Side Navigation (Ctrl + B)');
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
   DYNAMIC TABLE RECORD ACTIONS (EDIT & DELETE)
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

/* ==========================================================================
   📊 UNIVERSAL UNIFIED COLUMN MENU & CONTENT-AWARE PAGINATION ENGINE
   ========================================================================== */
function initSmartTables() {
  const tables = document.querySelectorAll('table');
  const totalTables = tables.length;

  tables.forEach((table, tableIdx) => {
    setupSmartTable(table, tableIdx, totalTables);
  });

  // Global click outside to dismiss all column popovers
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.table-filter-popover') && !e.target.closest('.btn-col-menu-trigger')) {
      closeAllTablePopovers();
    }
  });

  // Global Escape key to dismiss popovers
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllTablePopovers();
    }
  });

  // Close on scroll to keep alignment clean
  window.addEventListener('scroll', closeAllTablePopovers, { passive: true });

  // On Window Resize: recalculate optimal page size for all auto-fitting tables
  let resizeTimeout;
  window.addEventListener('resize', () => {
    closeAllTablePopovers();
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      tables.forEach(table => {
        if (table._pagination && table._pagination.customMode === 'auto') {
          renderTablePage(table);
        }
      });
    }, 150);
  }, { passive: true });
}

function getVisibleTableCount() {
  const visible = Array.from(document.querySelectorAll('table')).filter(t => {
    return t.offsetParent !== null && window.getComputedStyle(t).display !== 'none';
  });
  return Math.max(1, visible.length);
}

function calculateOptimalPageSize(table) {
  const n = getVisibleTableCount();
  // Available height for table area after top navigation and card header
  const availHeight = Math.max(320, window.innerHeight - 220);
  const shareHeight = availHeight / n;
  const rawRows = Math.floor(shareHeight / 40);
  // Strictly enforce minimum 10 rows rule when space is divided among multiple tables!
  return Math.max(10, rawRows);
}

function closeAllTablePopovers() {
  document.querySelectorAll('.table-filter-popover').forEach(p => p.classList.add('hidden'));
}

function setupSmartTable(table, tableIdx, totalTables) {
  const thead = table.querySelector('thead');
  const tbody = table.querySelector('tbody');
  if (!thead || !tbody) return;

  const headerRow = thead.querySelector('tr');
  if (!headerRow) return;

  const ths = Array.from(headerRow.querySelectorAll('th'));
  const rows = Array.from(tbody.querySelectorAll('tr'));
  if (rows.length === 0) return;

  // Active filters & sorting registry for this table
  table._activeFilters = {};
  table._sortState = { colIndex: -1, asc: true };

  // Setup Pagination state on table
  table._pagination = {
    currentPage: 1,
    customMode: 'auto',
    allRows: rows,
    matchingRows: rows
  };

  // Create or identify Active Filter Chips Container above table container
  let tableCard = table.closest('.glass-card') || table.parentElement;
  let chipsContainer = tableCard ? tableCard.querySelector('.table-active-chips-bar') : null;
  if (!chipsContainer && tableCard) {
    chipsContainer = document.createElement('div');
    chipsContainer.className = 'table-active-chips-bar flex items-center gap-2 flex-wrap min-h-[24px] mb-2 hidden text-xs';
    table.parentElement.insertBefore(chipsContainer, table);
  }

  // Create Modern Dynamic Pagination Toolbar below table if records exist
  let paginationToolbar = tableCard ? tableCard.querySelector('.table-pagination-toolbar') : null;
  if (!paginationToolbar && tableCard) {
    paginationToolbar = document.createElement('div');
    paginationToolbar.className = 'table-pagination-toolbar pt-3 border-t border-slate-200 dark:border-white/10 flex items-center justify-between flex-wrap gap-3 text-xs text-slate-500 dark:text-slate-400 select-none';
    paginationToolbar.innerHTML = `
      <!-- Left: Record Counter & Page info -->
      <div class="flex items-center gap-2">
        <span class="page-summary-text text-xs text-slate-600 dark:text-slate-400"></span>
        <span class="h-3 w-[1px] bg-slate-300 dark:bg-white/10"></span>
        <span class="page-current-badge text-[11px] font-mono text-slate-400 dark:text-slate-500"></span>
      </div>

      <!-- Center: Unified Segmented Capsule -->
      <div class="table-segmented-pager inline-flex items-center p-0.5 rounded-xl bg-slate-100 dark:bg-slate-900/90 border border-slate-300 dark:border-white/10 shadow-sm">
        <button type="button" class="btn-prev-page px-2.5 py-1 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white/80 dark:hover:bg-white/5 transition flex items-center gap-1 text-xs font-medium cursor-pointer disabled:opacity-30 disabled:pointer-events-none">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          <span>Prev</span>
        </button>

        <div class="h-3 w-[1px] bg-slate-300 dark:bg-white/10 mx-0.5"></div>

        <div class="page-pills-container flex items-center gap-0.5"></div>

        <div class="h-3 w-[1px] bg-slate-300 dark:bg-white/10 mx-0.5"></div>

        <button type="button" class="btn-next-page px-2.5 py-1 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white/80 dark:hover:bg-white/5 transition flex items-center gap-1 text-xs font-medium cursor-pointer disabled:opacity-30 disabled:pointer-events-none">
          <span>Next</span>
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
      </div>

      <!-- Right: Custom View Popover Trigger -->
      <div class="relative">
        <button type="button" class="btn-view-size-trigger px-2.5 py-1 rounded-xl bg-slate-100 dark:bg-slate-900/90 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-300 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white text-xs font-medium transition flex items-center gap-1.5 shadow-sm cursor-pointer">
          <span class="text-slate-400">View:</span>
          <span class="current-view-label font-semibold text-slate-800 dark:text-white">Auto</span>
          <svg class="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </button>

        <!-- View Popover Menu -->
        <div class="view-size-popover absolute right-0 bottom-9 w-44 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/15 p-1 shadow-2xl z-50 hidden space-y-0.5 text-xs backdrop-blur-xl">
          <button type="button" data-val="auto" class="size-opt-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 transition cursor-pointer">
            <span>Auto (Screen Fit)</span>
            <span class="check-mark font-bold text-blue-500">✓</span>
          </button>
          <button type="button" data-val="10" class="size-opt-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 transition cursor-pointer">
            <span>10 per page</span>
            <span class="check-mark font-bold text-blue-500 hidden">✓</span>
          </button>
          <button type="button" data-val="25" class="size-opt-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 transition cursor-pointer">
            <span>25 per page</span>
            <span class="check-mark font-bold text-blue-500 hidden">✓</span>
          </button>
          <button type="button" data-val="50" class="size-opt-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 transition cursor-pointer">
            <span>50 per page</span>
            <span class="check-mark font-bold text-blue-500 hidden">✓</span>
          </button>
          <button type="button" data-val="all" class="size-opt-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 transition cursor-pointer">
            <span>All records</span>
            <span class="check-mark font-bold text-blue-500 hidden">✓</span>
          </button>
        </div>
      </div>
    `;

    table.parentElement.appendChild(paginationToolbar);

    const btnPrev = paginationToolbar.querySelector('.btn-prev-page');
    const btnNext = paginationToolbar.querySelector('.btn-next-page');
    const viewTrigger = paginationToolbar.querySelector('.btn-view-size-trigger');
    const viewPopover = paginationToolbar.querySelector('.view-size-popover');
    const optButtons = paginationToolbar.querySelectorAll('.size-opt-btn');

    btnPrev.addEventListener('click', () => {
      if (table._pagination.currentPage > 1) {
        table._pagination.currentPage--;
        renderTablePage(table);
      }
    });

    btnNext.addEventListener('click', () => {
      table._pagination.currentPage++;
      renderTablePage(table);
    });

    viewTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      closeAllTablePopovers();
      viewPopover.classList.toggle('hidden');
    });

    optButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const val = btn.getAttribute('data-val');
        table._pagination.customMode = val;
        table._pagination.currentPage = 1;
        viewPopover.classList.add('hidden');
        renderTablePage(table);
      });
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.view-size-popover') && !e.target.closest('.btn-view-size-trigger')) {
        viewPopover.classList.add('hidden');
      }
    });

    table._paginationToolbar = paginationToolbar;
  }

  ths.forEach((th, colIdx) => {
    const headerText = th.textContent.trim();
    if (headerText.toLowerCase() === 'actions') return;

    // Collect distinct values for this column
    const distinctValues = new Map();
    rows.forEach(r => {
      const cell = r.cells[colIdx];
      if (cell) {
        const val = cell.textContent.trim();
        if (val) {
          distinctValues.set(val, (distinctValues.get(val) || 0) + 1);
        }
      }
    });

    th.classList.add('relative');
    
    // Wrap header content
    const originalHtml = th.innerHTML;
    th.innerHTML = '';
    
    const wrapper = document.createElement('div');
    wrapper.className = 'flex items-center justify-between gap-1.5 select-none';
    
    const labelSpan = document.createElement('span');
    labelSpan.className = 'font-semibold text-slate-300';
    labelSpan.innerHTML = originalHtml;
    wrapper.appendChild(labelSpan);

    // Create Unified Menu Button
    const menuBtn = document.createElement('button');
    menuBtn.type = 'button';
    menuBtn.className = 'btn-col-menu-trigger w-5 h-5 rounded hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-blue-400 transition cursor-pointer';
    menuBtn.title = `Sort & Filter ${headerText}`;
    menuBtn.innerHTML = `<i data-lucide="filter" class="w-3 h-3"></i>`;

    // Create Unified Popover
    const popover = document.createElement('div');
    popover.className = 'table-filter-popover hidden text-xs w-60';
    
    // Check if we should show value checkboxes (if there are categorical values)
    const hasCategoryValues = distinctValues.size >= 2 && distinctValues.size <= 20;

    let optionsHtml = '';
    if (hasCategoryValues) {
      optionsHtml = `
        <div class="space-y-1 max-h-36 overflow-y-auto text-slate-700 dark:text-slate-300 border-t border-slate-200 dark:border-white/10 pt-1.5 mt-1.5 popover-options-list">
          <div class="text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1">Filter by value:</div>
        </div>
      `;
    }

    popover.innerHTML = `
      <div class="font-bold text-slate-900 dark:text-white text-[11px] border-b border-slate-200 dark:border-white/10 pb-1.5 mb-1.5 flex justify-between items-center">
        <span>${headerText}</span>
        <button type="button" class="text-slate-400 hover:text-slate-600 dark:hover:text-white btn-popover-close text-sm leading-none">&times;</button>
      </div>

      <!-- Sort Controls -->
      <div class="space-y-0.5 border-b border-slate-200 dark:border-white/10 pb-1.5 mb-1.5">
        <button type="button" class="btn-sort-asc w-full flex items-center gap-2 px-2 py-1 rounded hover:bg-slate-100 dark:hover:bg-white/10 text-left text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition cursor-pointer">
          <svg class="w-3.5 h-3.5 text-blue-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/></svg>
          <span>Sort A &rarr; Z (Lowest first)</span>
        </button>
        <button type="button" class="btn-sort-desc w-full flex items-center gap-2 px-2 py-1 rounded hover:bg-slate-100 dark:hover:bg-white/10 text-left text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition cursor-pointer">
          <svg class="w-3.5 h-3.5 text-blue-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"/></svg>
          <span>Sort Z &rarr; A (Highest first)</span>
        </button>
      </div>

      <!-- Quick Search Filter -->
      <div class="space-y-1">
        <div class="text-[11px] font-semibold text-slate-600 dark:text-slate-400">Search in ${headerText}:</div>
        <input 
          type="text" 
          placeholder="Type to filter..." 
          class="col-search-input w-full px-2.5 py-1 text-xs rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition"
        >
      </div>

      ${optionsHtml}

      <!-- Bottom Actions -->
      <div class="pt-2 mt-1.5 border-t border-slate-200 dark:border-white/10 flex justify-between text-[10px]">
        <button type="button" class="btn-clear-col text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white">Clear</button>
        <button type="button" class="btn-popover-close text-blue-600 dark:text-blue-400 hover:underline font-semibold">Done</button>
      </div>
    `;

    // Populate distinct value checkboxes if applicable
    if (hasCategoryValues) {
      const optionsList = popover.querySelector('.popover-options-list');
      distinctValues.forEach((count, val) => {
        const item = document.createElement('label');
        item.className = 'table-filter-popover-item';
        item.innerHTML = `
          <input type="checkbox" value="${val}" class="filter-chk rounded text-blue-600 bg-slate-800 border-white/10">
          <span class="truncate flex-1">${val}</span>
          <span class="text-[9px] font-mono text-slate-400">(${count})</span>
        `;
        optionsList.appendChild(item);
      });
    }

    // Sort Handlers
    popover.querySelector('.btn-sort-asc').addEventListener('click', (e) => {
      e.stopPropagation();
      sortSmartTableColumn(table, colIdx, true, totalTables);
      closeAllTablePopovers();
    });

    popover.querySelector('.btn-sort-desc').addEventListener('click', (e) => {
      e.stopPropagation();
      sortSmartTableColumn(table, colIdx, false, totalTables);
      closeAllTablePopovers();
    });

    // Search Input Keystroke Handler
    const searchInput = popover.querySelector('.col-search-input');
    searchInput.addEventListener('input', () => {
      applySmartTableFilters(table, chipsContainer, totalTables);
    });

    // Checkbox Handlers
    const checkboxes = popover.querySelectorAll('.filter-chk');
    checkboxes.forEach(chk => {
      chk.addEventListener('change', () => {
        applySmartTableFilters(table, chipsContainer, totalTables);
      });
    });

    // Clear Button Handler
    popover.querySelector('.btn-clear-col').addEventListener('click', () => {
      searchInput.value = '';
      checkboxes.forEach(c => c.checked = false);
      applySmartTableFilters(table, chipsContainer, totalTables);
    });

    // Close Button Handlers
    popover.querySelectorAll('.btn-popover-close').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        popover.classList.add('hidden');
      });
    });

    // Toggle Popover Trigger
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = popover.classList.contains('hidden');
      closeAllTablePopovers();
      if (isHidden) {
        const rect = menuBtn.getBoundingClientRect();
        popover.style.position = 'fixed';
        popover.style.top = `${rect.bottom + 6}px`;
        popover.style.left = `${Math.min(Math.max(10, rect.left), window.innerWidth - 260)}px`;
        popover.style.zIndex = '99999';
        popover.classList.remove('hidden');
        setTimeout(() => searchInput.focus(), 50);
      }
    });

    wrapper.appendChild(menuBtn);
    th.appendChild(wrapper);
    document.body.appendChild(popover);
    table._colPopovers = table._colPopovers || [];
    table._colPopovers.push({ colIdx, popover, menuBtn, th });
  });

  // Initial page render
  renderTablePage(table);
  initLucide();
}

function renderTablePage(table) {
  if (!table._pagination) return;

  const { customMode, allRows, matchingRows } = table._pagination;
  const optimalSize = calculateOptimalPageSize(table);
  const pageSize = customMode === 'auto' ? optimalSize : (customMode === 'all' ? (matchingRows.length || 1) : parseInt(customMode) || 10);

  const totalRecords = matchingRows.length;
  const totalPages = Math.max(1, Math.ceil(totalRecords / pageSize));

  if (table._pagination.currentPage > totalPages) table._pagination.currentPage = totalPages;
  if (table._pagination.currentPage < 1) table._pagination.currentPage = 1;
  const currentPage = table._pagination.currentPage;

  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalRecords);
  const visibleSlice = matchingRows.slice(startIndex, endIndex);

  // Hide all rows, display slice rows
  allRows.forEach(r => r.style.display = 'none');
  visibleSlice.forEach(r => r.style.display = '');

  // Update Toolbar UI
  const toolbar = table._paginationToolbar;
  if (toolbar) {
    const summaryEl = toolbar.querySelector('.page-summary-text');
    const badgeEl = toolbar.querySelector('.page-current-badge');
    const viewLabel = toolbar.querySelector('.current-view-label');
    const viewPopover = toolbar.querySelector('.view-size-popover');

    if (summaryEl) {
      if (totalRecords === 0) {
        summaryEl.innerHTML = 'Showing <span class="font-semibold text-slate-700 dark:text-slate-300">0</span> records';
      } else {
        summaryEl.innerHTML = `<span class="font-semibold text-slate-800 dark:text-slate-200">${startIndex + 1}–${endIndex}</span> of <span class="font-semibold text-slate-800 dark:text-slate-200">${totalRecords}</span> records`;
      }
    }

    if (badgeEl) {
      badgeEl.textContent = `Page ${currentPage} / ${totalPages}`;
    }

    if (viewLabel) {
      const labelMap = {
        'auto': 'Auto (Adaptive)',
        '10': '10 / page',
        '25': '25 / page',
        '50': '50 / page',
        'all': 'All records'
      };
      viewLabel.textContent = labelMap[customMode] || customMode;
    }

    if (viewPopover) {
      viewPopover.querySelectorAll('.size-opt-btn').forEach(btn => {
        const val = btn.getAttribute('data-val');
        const check = btn.querySelector('.check-mark');
        if (val === customMode) {
          btn.classList.add('bg-blue-500/10', 'text-blue-500', 'font-semibold');
          if (check) check.classList.remove('hidden');
        } else {
          btn.classList.remove('bg-blue-500/10', 'text-blue-500', 'font-semibold');
          if (check) check.classList.add('hidden');
        }
      });
    }

    const btnPrev = toolbar.querySelector('.btn-prev-page');
    const btnNext = toolbar.querySelector('.btn-next-page');
    if (btnPrev) btnPrev.disabled = (currentPage === 1);
    if (btnNext) btnNext.disabled = (currentPage === totalPages || totalRecords === 0);

    const pillsContainer = toolbar.querySelector('.page-pills-container');
    if (pillsContainer) {
      pillsContainer.innerHTML = '';
      for (let p = 1; p <= totalPages; p++) {
        if (p === 1 || p === totalPages || (p >= currentPage - 1 && p <= currentPage + 1)) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = `w-7 h-7 rounded-lg text-xs font-semibold transition cursor-pointer ${p === currentPage ? 'bg-blue-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white/80 dark:hover:bg-white/5'}`;
          btn.textContent = p;
          btn.onclick = () => {
            table._pagination.currentPage = p;
            renderTablePage(table);
          };
          pillsContainer.appendChild(btn);
        } else if (p === currentPage - 2 || p === currentPage + 2) {
          const span = document.createElement('span');
          span.className = 'text-slate-400 px-1 text-xs select-none';
          span.textContent = '…';
          pillsContainer.appendChild(span);
        }
      }
    }
  }
}

function applySmartTableFilters(table, chipsContainer, totalTables) {
  const allRows = table._pagination ? table._pagination.allRows : Array.from(table.querySelectorAll('tbody tr'));
  const colPopovers = table._colPopovers || [];

  const activeFilters = [];

  colPopovers.forEach(({ colIdx, popover, menuBtn, th }) => {
    const searchVal = popover.querySelector('.col-search-input')?.value.toLowerCase().trim() || '';
    const checked = Array.from(popover.querySelectorAll('.filter-chk:checked')).map(c => c.value);
    const headerTitle = th.querySelector('span')?.textContent.trim() || `Col ${colIdx}`;

    if (searchVal || checked.length > 0) {
      if (menuBtn) {
        menuBtn.classList.add('text-blue-400', 'bg-blue-500/20');
        menuBtn.classList.remove('text-slate-400');
      }
      activeFilters.push({
        colIdx,
        title: headerTitle,
        searchText: searchVal,
        checkedValues: checked,
        popover,
        menuBtn
      });
    } else {
      if (menuBtn) {
        menuBtn.classList.remove('text-blue-400', 'bg-blue-500/20');
        menuBtn.classList.add('text-slate-400');
      }
    }
  });

  // Filter rows into matchingRows array
  const matchingRows = allRows.filter(r => {
    for (const f of activeFilters) {
      const cellText = r.cells[f.colIdx]?.textContent.trim() || '';
      
      // Search query match
      if (f.searchText && !cellText.toLowerCase().includes(f.searchText)) {
        return false;
      }

      // Checkbox match
      if (f.checkedValues.length > 0 && !f.checkedValues.some(v => cellText.includes(v))) {
        return false;
      }
    }
    return true;
  });

  // Update pagination state with filtered subset
  if (table._pagination) {
    table._pagination.matchingRows = matchingRows;
    table._pagination.currentPage = 1;
    renderTablePage(table);
  }

  // Render active filter chips toolbar
  if (chipsContainer) {
    chipsContainer.innerHTML = '';
    if (activeFilters.length > 0) {
      chipsContainer.classList.remove('hidden');

      const label = document.createElement('span');
      label.className = 'text-xs text-slate-400 font-medium flex items-center gap-1.5';
      label.innerHTML = `<i data-lucide="filter" class="w-3.5 h-3.5 text-blue-400"></i> Active Filters:`;
      chipsContainer.appendChild(label);

      activeFilters.forEach(f => {
        const chipEl = document.createElement('span');
        chipEl.className = 'filter-chip';
        
        let desc = f.searchText ? `"${f.searchText}"` : f.checkedValues.join(', ');
        chipEl.innerHTML = `<span>${f.title}: <strong>${desc}</strong></span><button type="button" title="Clear filter">&times;</button>`;
        chipEl.querySelector('button').addEventListener('click', () => {
          const input = f.popover.querySelector('.col-search-input');
          if (input) input.value = '';
          f.popover.querySelectorAll('.filter-chk').forEach(c => c.checked = false);
          applySmartTableFilters(table, chipsContainer, totalTables);
        });
        chipsContainer.appendChild(chipEl);
      });

      const clearAllBtn = document.createElement('button');
      clearAllBtn.type = 'button';
      clearAllBtn.className = 'text-[11px] text-slate-400 hover:text-white underline ml-auto';
      clearAllBtn.textContent = 'Clear all filters';
      clearAllBtn.addEventListener('click', () => {
        colPopovers.forEach(({ popover }) => {
          const input = popover.querySelector('.col-search-input');
          if (input) input.value = '';
          popover.querySelectorAll('.filter-chk').forEach(c => c.checked = false);
        });
        applySmartTableFilters(table, chipsContainer, totalTables);
      });
      chipsContainer.appendChild(clearAllBtn);
    } else {
      chipsContainer.classList.add('hidden');
    }
    initLucide();
  }
}

function sortSmartTableColumn(table, colIdx, asc, totalTables) {
  const tbody = table.querySelector('tbody');
  const allRows = table._pagination ? table._pagination.allRows : Array.from(tbody.querySelectorAll('tr'));
  table._sortState = { colIndex: colIdx, asc: asc };

  allRows.sort((a, b) => {
    const textA = a.cells[colIdx]?.textContent.trim() || '';
    const textB = b.cells[colIdx]?.textContent.trim() || '';

    // Check if numeric or currency
    const numA = parseFloat(textA.replace(/[^0-9.-]/g, ''));
    const numB = parseFloat(textB.replace(/[^0-9.-]/g, ''));

    if (!isNaN(numA) && !isNaN(numB) && !textA.includes('-') && !textB.includes('-')) {
      return asc ? numA - numB : numB - numA;
    }
    return asc ? textA.localeCompare(textB) : textB.localeCompare(textA);
  });

  allRows.forEach(r => tbody.appendChild(r));
  
  if (table._pagination) {
    table._pagination.currentPage = 1;
    renderTablePage(table);
  }

  showToast(`Sorted by column ${asc ? '(Ascending)' : '(Descending)'}`);
}

/* ==========================================================================
   🖱️ UNIVERSAL CLICK-AND-DRAG (GRAB & PAN) + CHEVRON SCROLL ENGINE
   ========================================================================== */
function initDragToScroll() {
  const scrollContainers = document.querySelectorAll('.overflow-x-auto, .table-responsive');

  scrollContainers.forEach(container => {
    // Hide ugly native scrollbar
    container.classList.add('no-scrollbar');

    let isDown = false;
    let startX, scrollLeft;
    let hasMoved = false;

    container.addEventListener('mousedown', (e) => {
      // Don't drag if clicking interactive controls
      if (e.target.closest('button, a, input, select, textarea, .btn-col-menu-trigger, .table-filter-popover')) return;
      isDown = true;
      hasMoved = false;
      container.classList.add('grab-scroll-active');
      startX = e.pageX - container.offsetLeft;
      scrollLeft = container.scrollLeft;
    });

    container.addEventListener('mouseleave', () => {
      isDown = false;
      container.classList.remove('grab-scroll-active');
    });

    container.addEventListener('mouseup', () => {
      isDown = false;
      container.classList.remove('grab-scroll-active');
    });

    container.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - container.offsetLeft;
      const walk = (x - startX) * 1.5;
      if (Math.abs(walk) > 3) hasMoved = true;
      container.scrollLeft = scrollLeft - walk;
    });

    // Add floating chevrons if not already present
    const parentWrapper = container.parentElement;
    if (parentWrapper && !parentWrapper.querySelector('.btn-table-scroll-left')) {
      parentWrapper.classList.add('relative', 'group');

      const btnLeft = document.createElement('button');
      btnLeft.type = 'button';
      btnLeft.className = 'btn-table-scroll-left absolute left-1 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-slate-900/90 hover:bg-blue-600 border border-white/15 text-white shadow-xl flex items-center justify-center transition-all opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto hover:scale-110 cursor-pointer';
      btnLeft.title = 'Scroll Left';
      btnLeft.innerHTML = `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>`;

      const btnRight = document.createElement('button');
      btnRight.type = 'button';
      btnRight.className = 'btn-table-scroll-right absolute right-1 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-slate-900/90 hover:bg-blue-600 border border-white/15 text-white shadow-xl flex items-center justify-center transition-all opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto hover:scale-110 cursor-pointer';
      btnRight.title = 'Scroll Right';
      btnRight.innerHTML = `<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>`;

      btnLeft.addEventListener('click', (e) => {
        e.stopPropagation();
        container.scrollBy({ left: -260, behavior: 'smooth' });
      });

      btnRight.addEventListener('click', (e) => {
        e.stopPropagation();
        container.scrollBy({ left: 260, behavior: 'smooth' });
      });

      const updateChevronVisibility = () => {
        const canScrollLeft = container.scrollLeft > 5;
        const canScrollRight = container.scrollLeft < (container.scrollWidth - container.clientWidth - 5);
        btnLeft.style.display = canScrollLeft ? 'flex' : 'none';
        btnRight.style.display = canScrollRight ? 'flex' : 'none';
      };

      container.addEventListener('scroll', updateChevronVisibility, { passive: true });
      window.addEventListener('resize', updateChevronVisibility, { passive: true });
      setTimeout(updateChevronVisibility, 100);

      parentWrapper.insertBefore(btnLeft, container);
      parentWrapper.appendChild(btnRight);
    }
  });
}


