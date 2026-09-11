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
  initDirtyFormGuard();
  initSmartTableRowNavigation();
  initModalAutoHideManager();
  initUniversalFormValidation();
});

/* ==========================================================================
   🔒 COMPANY SWITCHER EDIT-PAGE GUARD
   Prevents changing company while editing or creating records to safeguard
   data integrity and tenant boundaries.
   Zero UI changes: Button remains 100% identical on all pages.
   ========================================================================== */
function isCompanySwitchingAllowed() {
  const path = window.location.pathname.toLowerCase();
  if (path.endsWith('/edit') || path.includes('/edit/') || path.endsWith('/new')) {
    return false;
  }

  const activeEditForm = document.querySelector('form#master-record-form, form#ar-record-form, form#cb-record-form, form.record-edit-form');
  if (activeEditForm && !activeEditForm.querySelector('fieldset[disabled]')) {
    const action = (activeEditForm.getAttribute('action') || '').toLowerCase();
    if (action.includes('/edit') || action.includes('/new')) {
      return false;
    }
  }

  return true;
}


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
  if (table.hasAttribute('data-no-smart-table') || table.classList.contains('no-smart-table') || table.getAttribute('data-no-smart-table') === 'true') {
    return;
  }
  const thead = table.querySelector('thead');
  const tbody = table.querySelector('tbody');
  if (!thead || !tbody) return;

  const headerRow = thead.querySelector('tr');
  if (!headerRow) return;

  const ths = Array.from(headerRow.querySelectorAll('th'));
  const rows = Array.from(tbody.querySelectorAll('tr'));
  // Store original order for resetting sorts
  rows.forEach((r, idx) => {
    if (r._originalIndex === undefined) r._originalIndex = idx;
  });

  // Active filters & sorting registry for this table
  table._activeFilters = {};
  table._sortState = { colIndex: -1, asc: null };

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
    menuBtn.className = 'btn-col-menu-trigger w-6 h-6 rounded-lg hover:bg-slate-200/70 dark:hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-blue-500 transition cursor-pointer';
    menuBtn.title = `Sort & Filter ${headerText}`;
    menuBtn.innerHTML = `<i data-lucide="filter" class="w-3 h-3"></i>`;

    // Create Unified Popover
    const popover = document.createElement('div');
    popover.className = 'table-filter-popover hidden text-xs w-72 select-none';
    
    // Check if we should show value checkboxes (if there are categorical values)
    const hasCategoryValues = distinctValues.size >= 2 && distinctValues.size <= 25;

    let optionsHtml = '';
    if (hasCategoryValues) {
      optionsHtml = `
        <div class="space-y-1.5 border-t border-slate-200 dark:border-white/10 pt-2 mb-2.5">
          <div class="flex items-center justify-between text-[11px] px-0.5">
            <span class="text-slate-500 dark:text-slate-400 font-medium">Values (${distinctValues.size})</span>
            <div class="flex items-center gap-1.5">
              <button type="button" class="btn-select-all-vals text-blue-600 dark:text-blue-400 hover:underline font-medium text-[10px] cursor-pointer">Select all</button>
              <span class="text-slate-400 dark:text-slate-600">&bull;</span>
              <button type="button" class="btn-clear-all-vals text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white font-medium text-[10px] cursor-pointer">Clear</button>
            </div>
          </div>
          <div class="space-y-0.5 max-h-36 overflow-y-auto custom-scrollbar pr-1 border border-slate-200 dark:border-white/5 rounded-xl p-1 bg-slate-50 dark:bg-slate-950/40 popover-options-list">
          </div>
        </div>
      `;
    }

    popover.innerHTML = `
      <!-- Header -->
      <div class="flex items-center justify-between pb-2 mb-2.5 border-b border-slate-200 dark:border-white/10">
        <div class="flex items-center gap-1.5 font-bold text-slate-900 dark:text-white text-xs tracking-tight">
          <i data-lucide="filter" class="w-3.5 h-3.5 text-blue-500"></i>
          <span class="truncate max-w-[190px]">${headerText}</span>
        </div>
        <button type="button" class="btn-popover-close w-6 h-6 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-white transition cursor-pointer" title="Close">
          <i data-lucide="x" class="w-3.5 h-3.5"></i>
        </button>
      </div>

      <!-- Segmented 3-Way Sort Control -->
      <div class="mb-2.5">
        <div class="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Sorting</div>
        <div class="grid grid-cols-3 gap-1 bg-slate-100 dark:bg-slate-950/60 p-1 rounded-xl border border-slate-200 dark:border-white/5 text-[11px] font-medium">
          <button type="button" class="btn-sort-asc py-1 px-1 rounded-lg flex items-center justify-center gap-1 transition text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white dark:hover:bg-white/10 cursor-pointer" title="Sort Ascending">
            <i data-lucide="arrow-down-a-z" class="w-3 h-3"></i>
            <span>A &rarr; Z</span>
          </button>
          <button type="button" class="btn-sort-desc py-1 px-1 rounded-lg flex items-center justify-center gap-1 transition text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white dark:hover:bg-white/10 cursor-pointer" title="Sort Descending">
            <i data-lucide="arrow-up-z-a" class="w-3 h-3"></i>
            <span>Z &rarr; A</span>
          </button>
          <button type="button" class="btn-sort-none py-1 px-1 rounded-lg flex items-center justify-center gap-1 transition bg-blue-600 text-white font-semibold shadow-sm cursor-pointer" title="Clear sort">
            <span>None</span>
          </button>
        </div>
      </div>

      <!-- Dynamic Search Input -->
      <div class="space-y-1 mb-2.5">
        <div class="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Search in ${headerText}</div>
        <div class="relative flex items-center">
          <i data-lucide="search" class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 pointer-events-none"></i>
          <input 
            type="text" 
            placeholder="Filter values..." 
            class="col-search-input w-full pl-8 pr-7 py-1.5 text-xs rounded-xl bg-slate-100 dark:bg-slate-950/60 border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition font-medium"
          >
          <button type="button" class="btn-clear-search-input hidden absolute right-2 text-slate-400 hover:text-slate-600 dark:hover:text-white cursor-pointer" title="Clear search">
            <i data-lucide="x" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>

      ${optionsHtml}

      <!-- Bottom Actions -->
      <div class="pt-2 border-t border-slate-200 dark:border-white/10 flex items-center justify-between text-xs">
        <button type="button" class="btn-clear-col text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white flex items-center gap-1 font-medium transition cursor-pointer" title="Reset this column's filters">
          <i data-lucide="rotate-ccw" class="w-3 h-3"></i>
          <span>Reset</span>
        </button>
        <button type="button" class="btn-popover-close px-3 py-1 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-sm transition cursor-pointer">
          Done
        </button>
      </div>
    `;

    // Populate distinct value checkboxes if applicable
    if (hasCategoryValues) {
      const optionsList = popover.querySelector('.popover-options-list');
      distinctValues.forEach((count, val) => {
        const item = document.createElement('label');
        item.className = 'table-filter-popover-item group';
        item.setAttribute('data-val', val);
        item.innerHTML = `
          <input type="checkbox" value="${val.replace(/"/g, '&quot;')}" class="filter-chk rounded text-blue-600 bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-white/20 focus:ring-0 cursor-pointer">
          <span class="truncate flex-1 text-[11px] text-slate-700 dark:text-slate-200 group-hover:text-slate-900 dark:group-hover:text-white">${val}</span>
          <span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-200/60 dark:bg-white/5 text-slate-500 dark:text-slate-400 font-semibold">${count}</span>
        `;
        optionsList.appendChild(item);
      });
    }

    // Sort Segment Handlers
    const btnSortAsc = popover.querySelector('.btn-sort-asc');
    const btnSortDesc = popover.querySelector('.btn-sort-desc');
    const btnSortNone = popover.querySelector('.btn-sort-none');

    function updateSortSegmentUi(mode) {
      const activeCls = ['bg-blue-600', 'text-white', 'font-semibold', 'shadow-sm'];
      const defaultCls = ['text-slate-600', 'dark:text-slate-400'];

      [btnSortAsc, btnSortDesc, btnSortNone].forEach(btn => {
        if (!btn) return;
        btn.classList.remove(...activeCls);
        btn.classList.add(...defaultCls);
      });

      if (mode === 'asc' && btnSortAsc) {
        btnSortAsc.classList.add(...activeCls);
        btnSortAsc.classList.remove(...defaultCls);
      } else if (mode === 'desc' && btnSortDesc) {
        btnSortDesc.classList.add(...activeCls);
        btnSortDesc.classList.remove(...defaultCls);
      } else if (btnSortNone) {
        btnSortNone.classList.add(...activeCls);
        btnSortNone.classList.remove(...defaultCls);
      }
      updateColHeaderIndicator(table, colIdx, menuBtn, popover);
    }

    btnSortAsc.addEventListener('click', (e) => {
      e.stopPropagation();
      sortSmartTableColumn(table, colIdx, true, totalTables);
      updateSortSegmentUi('asc');
    });

    btnSortDesc.addEventListener('click', (e) => {
      e.stopPropagation();
      sortSmartTableColumn(table, colIdx, false, totalTables);
      updateSortSegmentUi('desc');
    });

    btnSortNone.addEventListener('click', (e) => {
      e.stopPropagation();
      sortSmartTableColumn(table, colIdx, null, totalTables);
      updateSortSegmentUi('none');
    });

    // Search Input Keystroke & Option Filtering Handler
    const searchInput = popover.querySelector('.col-search-input');
    const clearSearchBtn = popover.querySelector('.btn-clear-search-input');

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase().trim();
        if (clearSearchBtn) {
          clearSearchBtn.classList.toggle('hidden', query === '');
        }
        // Live-filter checkboxes in popover
        popover.querySelectorAll('.table-filter-popover-item').forEach(item => {
          const val = (item.getAttribute('data-val') || '').toLowerCase();
          if (!query || val.includes(query)) {
            item.classList.remove('hidden');
          } else {
            item.classList.add('hidden');
          }
        });

        applySmartTableFilters(table, chipsContainer, totalTables);
        updateColHeaderIndicator(table, colIdx, menuBtn, popover);
      });

      if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          searchInput.value = '';
          clearSearchBtn.classList.add('hidden');
          popover.querySelectorAll('.table-filter-popover-item').forEach(item => item.classList.remove('hidden'));
          applySmartTableFilters(table, chipsContainer, totalTables);
          updateColHeaderIndicator(table, colIdx, menuBtn, popover);
          searchInput.focus();
        });
      }
    }

    // Batch Actions: Select All / Clear
    const btnSelectAll = popover.querySelector('.btn-select-all-vals');
    if (btnSelectAll) {
      btnSelectAll.addEventListener('click', (e) => {
        e.stopPropagation();
        popover.querySelectorAll('.table-filter-popover-item:not(.hidden) .filter-chk').forEach(chk => chk.checked = true);
        applySmartTableFilters(table, chipsContainer, totalTables);
        updateColHeaderIndicator(table, colIdx, menuBtn, popover);
      });
    }

    const btnClearAll = popover.querySelector('.btn-clear-all-vals');
    if (btnClearAll) {
      btnClearAll.addEventListener('click', (e) => {
        e.stopPropagation();
        popover.querySelectorAll('.filter-chk').forEach(chk => chk.checked = false);
        applySmartTableFilters(table, chipsContainer, totalTables);
        updateColHeaderIndicator(table, colIdx, menuBtn, popover);
      });
    }

    // Checkbox Handlers
    const checkboxes = popover.querySelectorAll('.filter-chk');
    checkboxes.forEach(chk => {
      chk.addEventListener('change', () => {
        applySmartTableFilters(table, chipsContainer, totalTables);
        updateColHeaderIndicator(table, colIdx, menuBtn, popover);
      });
    });

    // Reset / Clear Column Button Handler
    popover.querySelector('.btn-clear-col').addEventListener('click', () => {
      if (searchInput) {
        searchInput.value = '';
        if (clearSearchBtn) clearSearchBtn.classList.add('hidden');
        popover.querySelectorAll('.table-filter-popover-item').forEach(item => item.classList.remove('hidden'));
      }
      checkboxes.forEach(c => c.checked = false);
      if (table._sortState && table._sortState.colIndex === colIdx) {
        sortSmartTableColumn(table, colIdx, null, totalTables);
        updateSortSegmentUi('none');
      }
      applySmartTableFilters(table, chipsContainer, totalTables);
      updateColHeaderIndicator(table, colIdx, menuBtn, popover);
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
        popover.style.left = `${Math.min(Math.max(10, rect.left), window.innerWidth - 300)}px`;
        popover.style.zIndex = '99999';
        popover.classList.remove('hidden');
        initLucide();
        setTimeout(() => searchInput && searchInput.focus(), 50);
      }
    });

    wrapper.appendChild(menuBtn);
    th.appendChild(wrapper);
    document.body.appendChild(popover);
    table._colPopovers = table._colPopovers || [];
    table._colPopovers.push({ colIdx, popover, menuBtn, th, updateSortSegmentUi });
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
      activeFilters.push({
        colIdx,
        title: headerTitle,
        searchText: searchVal,
        checkedValues: checked,
        popover,
        menuBtn
      });
    }
    updateColHeaderIndicator(table, colIdx, menuBtn, popover);
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
  table._sortState = { colIndex: asc === null ? -1 : colIdx, asc: asc };

  if (asc === null) {
    allRows.sort((a, b) => (a._originalIndex ?? 0) - (b._originalIndex ?? 0));
  } else {
    allRows.sort((a, b) => {
      const textA = a.cells[colIdx]?.textContent.trim() || '';
      const textB = b.cells[colIdx]?.textContent.trim() || '';

      // Check if numeric or currency
      const numA = parseFloat(textA.replace(/[^0-9.-]/g, ''));
      const numB = parseFloat(textB.replace(/[^0-9.-]/g, ''));

      if (!isNaN(numA) && !isNaN(numB) && !textA.includes('-') && !textB.includes('-')) {
        return asc ? numA - numB : numB - numA;
      }
      return asc ? textA.localeCompare(textB, undefined, { numeric: true, sensitivity: 'base' }) : textB.localeCompare(textA, undefined, { numeric: true, sensitivity: 'base' });
    });
  }

  allRows.forEach(r => tbody.appendChild(r));
  
  if (table._pagination) {
    table._pagination.currentPage = 1;
    renderTablePage(table);
  }

  // Update indicators across all column popovers
  if (table._colPopovers) {
    table._colPopovers.forEach(cp => {
      if (cp.colIdx !== colIdx && cp.updateSortSegmentUi) {
        cp.updateSortSegmentUi('none');
      }
      updateColHeaderIndicator(table, cp.colIdx, cp.menuBtn, cp.popover);
    });
  }

  if (asc !== null) {
    showToast(`Sorted by column ${asc ? '(Ascending)' : '(Descending)'}`);
  } else {
    showToast('Reset column sort order');
  }
}

function updateColHeaderIndicator(table, colIdx, menuBtn, popover) {
  if (!menuBtn) return;
  const sortState = table._sortState || { colIndex: -1, asc: null };
  const searchVal = popover.querySelector('.col-search-input')?.value.trim() || '';
  const hasFilter = searchVal !== '' || popover.querySelectorAll('.filter-chk:checked').length > 0;
  const isSorted = sortState.colIndex === colIdx && sortState.asc !== null;

  if (isSorted) {
    menuBtn.classList.add('text-blue-500', 'bg-blue-500/15', 'font-bold');
    menuBtn.classList.remove('text-slate-400');
    if (sortState.asc) {
      menuBtn.innerHTML = `<i data-lucide="arrow-down-a-z" class="w-3.5 h-3.5 text-blue-500"></i>`;
    } else {
      menuBtn.innerHTML = `<i data-lucide="arrow-up-z-a" class="w-3.5 h-3.5 text-blue-500"></i>`;
    }
  } else if (hasFilter) {
    menuBtn.classList.add('text-blue-500', 'bg-blue-500/15');
    menuBtn.classList.remove('text-slate-400');
    menuBtn.innerHTML = `<span class="relative flex items-center justify-center"><i data-lucide="filter" class="w-3 h-3 text-blue-500"></i><span class="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-blue-500 ring-2 ring-white dark:ring-slate-900"></span></span>`;
  } else {
    menuBtn.classList.remove('text-blue-500', 'bg-blue-500/15', 'font-bold');
    menuBtn.classList.add('text-slate-400');
    menuBtn.innerHTML = `<i data-lucide="filter" class="w-3 h-3"></i>`;
  }
  initLucide();
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

/* ==========================================================================
   ⚡ UNIVERSAL MODAL / POP-UP AUTO-HIDE SIDEBAR ENGINE
   Automatically slides the side menu smoothly off-screen when ANY modal or
   popup opens in the application, and restores it when closed.
   ========================================================================== */
window.pyrixModalManager = {
  activeModals: new Set(),

  syncSidebarState() {
    const htmlEl = document.documentElement;
    const modalCandidates = document.querySelectorAll(
      '[id^="modal-"], [role="dialog"], [aria-modal="true"]'
    );
    let anyVisible = false;
    modalCandidates.forEach(el => {
      // Exclude small-screen sidebar backdrop
      if (el.id === 'sidebar-backdrop') return;

      const isVisible = !el.classList.contains('hidden') && 
                        window.getComputedStyle(el).display !== 'none' &&
                        window.getComputedStyle(el).visibility !== 'hidden' &&
                        (el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length > 0);
      if (isVisible) {
        anyVisible = true;
        this.activeModals.add(el.id || el);
      } else if (el.id) {
        this.activeModals.delete(el.id);
      }
    });

    if (anyVisible || this.activeModals.size > 0) {
      if (!htmlEl.classList.contains('modal-active-sidebar-hidden')) {
        htmlEl.classList.add('modal-active-sidebar-hidden');
      }
    } else {
      htmlEl.classList.remove('modal-active-sidebar-hidden');
    }
  },

  registerOpen(modalId) {
    if (modalId) this.activeModals.add(modalId);
    document.documentElement.classList.add('modal-active-sidebar-hidden');
  },

  registerClose(modalId) {
    if (modalId) this.activeModals.delete(modalId);
    setTimeout(() => this.syncSidebarState(), 40);
  },

  init() {
    if (typeof MutationObserver !== 'undefined') {
      const observer = new MutationObserver(() => {
        this.syncSidebarState();
      });

      observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['class', 'style'],
        subtree: true
      });
    }

    this.syncSidebarState();
  }
};

function initModalAutoHideManager() {
  if (window.pyrixModalManager && typeof window.pyrixModalManager.init === 'function') {
    window.pyrixModalManager.init();
  }
}

/* ==========================================================================
   ⚡ UNIVERSAL DYNAMIC CRUD MODAL CONTROLLER (Edit & Delete)
   ========================================================================== */
let currentDeleteTarget = { entity: null, id: null, rowElement: null };

function showDynamicToast(message, type = 'success') {
  const container = document.getElementById('dynamic-toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const isSuccess = type === 'success';
  toast.className = `px-4 py-3 rounded-2xl shadow-xl border text-xs font-semibold flex items-center gap-2.5 transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-auto ${
    isSuccess 
      ? 'bg-emerald-950/90 border-emerald-500/30 text-emerald-300' 
      : 'bg-rose-950/90 border-rose-500/30 text-rose-300'
  }`;
  toast.innerHTML = `
    <i data-lucide="${isSuccess ? 'check-circle' : 'alert-triangle'}" class="w-4 h-4 ${isSuccess ? 'text-emerald-400' : 'text-rose-400'}"></i>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  if (window.lucide) window.lucide.createIcons();

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-4', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

async function openDynamicEditModal(entity, id) {
  const modal = document.getElementById('modal-dynamic-edit');
  const loading = document.getElementById('dynamic-edit-loading');
  const fieldsContainer = document.getElementById('dynamic-fields-container');
  const titleEl = document.getElementById('dynamic-edit-title');
  const entityInput = document.getElementById('dynamic-edit-entity');
  const idInput = document.getElementById('dynamic-edit-id');

  if (!modal) return;

  entityInput.value = entity;
  idInput.value = id;

  modal.classList.remove('hidden');
  loading.classList.remove('hidden');
  fieldsContainer.classList.add('hidden');
  fieldsContainer.innerHTML = '';

  try {
    const res = await fetch(`/api/crud/${entity}/${id}`);
    const json = await res.json();
    if (!json.success || !json.payload) throw new Error(json.error || 'Failed to load record');

    const { title, fields, data } = json.payload;
    titleEl.textContent = `Edit ${title}`;

    fields.forEach(f => {
      const fieldWrapper = document.createElement('div');
      fieldWrapper.className = 'space-y-1.5';

      const label = document.createElement('label');
      label.className = 'text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center justify-between';
      label.innerHTML = `<span>${f.label}</span> ${f.required ? '<span class="text-rose-500 text-[10px]">*</span>' : ''}`;
      fieldWrapper.appendChild(label);

      const val = data[f.field] !== undefined && data[f.field] !== null ? data[f.field] : '';

      if (f.type === 'select') {
        const select = document.createElement('select');
        select.name = f.field;
        select.required = !!f.required;
        select.className = 'mac-input w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-800 dark:text-white font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none';
        f.options.forEach(opt => {
          const optEl = document.createElement('option');
          optEl.value = opt;
          optEl.textContent = opt;
          if (String(opt).toUpperCase() === String(val).toUpperCase()) optEl.selected = true;
          select.appendChild(optEl);
        });
        fieldWrapper.appendChild(select);
      } else if (f.type === 'checkbox') {
        const checkWrap = document.createElement('label');
        checkWrap.className = 'flex items-center gap-2.5 p-2 rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 cursor-pointer';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = f.field;
        checkbox.checked = !!val && val !== 0 && val !== '0';
        checkbox.className = 'w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300';
        const span = document.createElement('span');
        span.className = 'text-xs font-semibold text-slate-700 dark:text-slate-200';
        span.textContent = f.label;
        checkWrap.appendChild(checkbox);
        checkWrap.appendChild(span);
        fieldWrapper.appendChild(checkWrap);
      } else {
        const input = document.createElement('input');
        input.type = f.type || 'text';
        input.name = f.field;
        input.value = val;
        if (f.step) input.step = f.step;
        input.required = !!f.required;
        input.className = 'mac-input w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-800 dark:text-white font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none';
        fieldWrapper.appendChild(input);
      }

      fieldsContainer.appendChild(fieldWrapper);
    });

    loading.classList.add('hidden');
    fieldsContainer.classList.remove('hidden');
    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    showDynamicToast(err.message || 'Error loading record', 'error');
    closeDynamicEditModal();
  }
}

function closeDynamicEditModal() {
  const modal = document.getElementById('modal-dynamic-edit');
  if (modal) modal.classList.add('hidden');
}

async function submitDynamicEditForm(e) {
  e.preventDefault();
  const form = e.target;
  const entity = document.getElementById('dynamic-edit-entity').value;
  const id = document.getElementById('dynamic-edit-id').value;
  const btn = document.getElementById('btn-save-dynamic-edit');

  const formData = {};
  new FormData(form).forEach((val, key) => {
    formData[key] = val;
  });

  form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
    formData[cb.name] = cb.checked;
  });

  const originalBtnText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Saving...</span>`;

  try {
    const res = await fetch(`/api/crud/${entity}/${id}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    const json = await res.json();
    if (!res.ok || !json.success) throw new Error(json.detail || json.error || 'Update failed');

    showDynamicToast(json.message || 'Record updated successfully!', 'success');
    closeDynamicEditModal();

    // Dynamically update corresponding row in DOM if present
    const row = document.querySelector(`tr[data-id="${id}"], tr[data-record-id="${id}"]`);
    if (row) {
      Object.keys(formData).forEach(k => {
        const cell = row.querySelector(`[data-field="${k}"]`);
        if (cell) cell.textContent = formData[k];
      });
    } else {
      setTimeout(() => window.location.reload(), 600);
    }
  } catch (err) {
    showDynamicToast(err.message || 'Failed to update record', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalBtnText;
    if (window.lucide) window.lucide.createIcons();
  }
}

async function confirmDynamicDelete(entity, id, title = 'Record', clickedButton = null) {
  const modal = document.getElementById('modal-dynamic-delete');
  const titleEl = document.getElementById('dynamic-delete-title');
  const blockedBox = document.getElementById('dynamic-delete-blocked');
  const blockedMsg = document.getElementById('dynamic-delete-blocked-msg');
  const deleteBtn = document.getElementById('btn-execute-delete');

  if (!modal) return;

  currentDeleteTarget = {
    entity,
    id,
    rowElement: clickedButton ? clickedButton.closest('tr') : (document.querySelector(`tr[data-id="${id}"], tr[data-record-id="${id}"]`))
  };

  titleEl.textContent = `"${title}"`;
  blockedBox.classList.add('hidden');
  deleteBtn.disabled = false;
  deleteBtn.classList.remove('opacity-50', 'pointer-events-none');
  modal.classList.remove('hidden');

  try {
    const res = await fetch(`/api/crud/${entity}/${id}/precheck-delete`);
    const json = await res.json();
    if (!json.can_delete) {
      blockedMsg.textContent = json.reason;
      blockedBox.classList.remove('hidden');
      deleteBtn.disabled = true;
      deleteBtn.classList.add('opacity-50', 'pointer-events-none');
    }
  } catch (err) {
    console.warn('Dependency pre-check warning:', err);
  }
}

function closeDynamicDeleteModal() {
  const modal = document.getElementById('modal-dynamic-delete');
  if (modal) modal.classList.add('hidden');
  currentDeleteTarget = { entity: null, id: null, rowElement: null };
}

async function executeDynamicDelete() {
  if (!currentDeleteTarget.entity || !currentDeleteTarget.id) return;

  const { entity, id, rowElement } = currentDeleteTarget;
  const deleteBtn = document.getElementById('btn-execute-delete');
  const origHtml = deleteBtn.innerHTML;

  deleteBtn.disabled = true;
  deleteBtn.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Deleting...</span>`;

  try {
    const res = await fetch(`/api/crud/${entity}/${id}/delete`, {
      method: 'POST'
    });
    const json = await res.json();
    if (!res.ok || !json.success) throw new Error(json.detail || json.error || 'Deletion failed');

    showDynamicToast(json.message || 'Record successfully deleted.', 'success');
    closeDynamicDeleteModal();

    // Smooth row fade-out and collapse animation
    if (rowElement) {
      rowElement.style.transition = 'all 0.35s ease';
      rowElement.style.opacity = '0';
      rowElement.style.transform = 'scale(0.95)';
      setTimeout(() => rowElement.remove(), 350);
    } else {
      setTimeout(() => window.location.reload(), 600);
    }
  } catch (err) {
    showDynamicToast(err.message || 'Failed to delete record', 'error');
  } finally {
    deleteBtn.disabled = false;
    deleteBtn.innerHTML = origHtml;
    if (window.lucide) window.lucide.createIcons();
  }
}

/* ==========================================================================
   ⚡ UNIVERSAL FLOATING ROW ACTION POPOVER & DYNAMIC VIEW ENGINE
   ========================================================================== */
let currentActionTarget = {
  entity: null,
  id: null,
  title: null,
  editUrl: null,
  deleteFnStr: null,
  triggerBtn: null,
  rowElement: null
};

function openRowActionMenu(btn, e, entity, id, title, editUrl, deleteFnStr) {
  if (e) {
    e.stopPropagation();
    e.preventDefault();
  }

  const menu = document.getElementById('floating-row-action-menu');
  if (!menu) return;

  // Toggle close if clicking the same trigger button while open
  if (!menu.classList.contains('hidden') && currentActionTarget.triggerBtn === btn) {
    closeRowActionMenu();
    return;
  }

  currentActionTarget = {
    entity: entity,
    id: id,
    title: title || 'Record',
    editUrl: editUrl || null,
    deleteFnStr: deleteFnStr || null,
    triggerBtn: btn,
    rowElement: btn ? btn.closest('tr') : null
  };

  // Display menu to measure dimensions
  menu.style.visibility = 'hidden';
  menu.classList.remove('hidden');

  const rect = btn.getBoundingClientRect();
  const menuWidth = menu.offsetWidth || 176;
  const menuHeight = menu.offsetHeight || 150;

  // Horizontal position (align right edge of menu to right edge of button)
  let left = rect.right - menuWidth;
  if (left < 8) left = 8;
  if (left + menuWidth > window.innerWidth - 8) {
    left = window.innerWidth - menuWidth - 8;
  }

  // Vertical position (check if opening downwards overflows viewport)
  let top = rect.bottom + 4;
  if (top + menuHeight > window.innerHeight - 8) {
    // Open upwards
    top = rect.top - menuHeight - 4;
  }

  menu.style.top = `${Math.round(top)}px`;
  menu.style.left = `${Math.round(left)}px`;
  menu.style.visibility = 'visible';

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function closeRowActionMenu() {
  const menu = document.getElementById('floating-row-action-menu');
  if (menu && !menu.classList.contains('hidden')) {
    menu.classList.add('hidden');
  }
}

function handleActionMenuClick(action) {
  const { entity, id, title, editUrl, deleteFnStr, triggerBtn } = currentActionTarget;
  closeRowActionMenu();

  if (action === 'view') {
    if (editUrl) {
      const viewUrl = editUrl.endsWith('/edit')
        ? editUrl.replace(/\/edit$/, '/view')
        : `${editUrl}?mode=view`;
      window.location.href = viewUrl;
    } else if (entity && id) {
      openDynamicViewModal(entity, id, title);
    }
  } else if (action === 'edit') {
    if (editUrl) {
      window.location.href = editUrl;
    } else if (entity && id) {
      openDynamicEditModal(entity, id);
    }
  } else if (action === 'delete') {
    if (deleteFnStr) {
      try {
        const fn = new Function(deleteFnStr);
        fn();
      } catch (err) {
        console.error('Delete action failed', err);
      }
    } else if (entity && id) {
      confirmDynamicDelete(entity, id, title, triggerBtn);
    }
  }
}

async function openDynamicViewModal(entity, id, title) {
  const modal = document.getElementById('modal-dynamic-view');
  const loading = document.getElementById('dynamic-view-loading');
  const fieldsContainer = document.getElementById('dynamic-view-fields');
  const titleEl = document.getElementById('dynamic-view-title');
  const subtitleEl = document.getElementById('dynamic-view-subtitle');

  if (!modal) return;

  modal.classList.remove('hidden');
  loading.classList.remove('hidden');
  fieldsContainer.classList.add('hidden');
  fieldsContainer.innerHTML = '';

  titleEl.textContent = title ? `${title}` : 'Record Details';
  subtitleEl.textContent = `Entity: ${entity} • Record ID: ${id}`;

  try {
    const res = await fetch(`/api/crud/${entity}/${id}`);
    const json = await res.json();
    if (!json.success || !json.payload) throw new Error(json.error || 'Failed to load record');

    const { title: entityTitle, fields, data } = json.payload;
    titleEl.textContent = entityTitle ? `${entityTitle}: ${title || id}` : (title || 'Record Details');

    fields.forEach(f => {
      const fieldCard = document.createElement('div');
      fieldCard.className = 'p-3 rounded-2xl border border-slate-100 dark:border-white/5 bg-slate-50/60 dark:bg-white/[0.02] space-y-1';

      const val = data[f.field] !== undefined && data[f.field] !== null ? data[f.field] : '—';
      let formattedVal = val;

      if (f.type === 'checkbox') {
        formattedVal = val 
          ? '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">YES</span>' 
          : '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 dark:bg-white/10 text-slate-500">NO</span>';
      } else if (typeof val === 'boolean') {
        formattedVal = val 
          ? '<span class="text-emerald-600 font-bold">Yes</span>' 
          : '<span class="text-slate-400">No</span>';
      }

      fieldCard.innerHTML = `
        <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">${f.label}</div>
        <div class="text-xs font-semibold text-slate-800 dark:text-slate-200 break-words">${formattedVal}</div>
      `;
      fieldsContainer.appendChild(fieldCard);
    });

    loading.classList.add('hidden');
    fieldsContainer.classList.remove('hidden');
    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    loading.innerHTML = `<div class="text-rose-500 text-xs font-semibold">${err.message || 'Error loading details'}</div>`;
  }
}

function closeDynamicViewModal() {
  const modal = document.getElementById('modal-dynamic-view');
  if (modal) modal.classList.add('hidden');
}

function switchToEditFromView() {
  const { entity, id } = currentActionTarget;
  closeDynamicViewModal();
  if (entity && id) {
    openDynamicEditModal(entity, id);
  }
}

// Global dismiss listeners for floating action menu
document.addEventListener('click', (e) => {
  const menu = document.getElementById('floating-row-action-menu');
  if (menu && !menu.classList.contains('hidden')) {
    if (!menu.contains(e.target) && (!currentActionTarget.triggerBtn || !currentActionTarget.triggerBtn.contains(e.target))) {
      closeRowActionMenu();
    }
  }
});

window.addEventListener('scroll', () => {
  closeRowActionMenu();
}, { passive: true });

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeRowActionMenu();
    closeDynamicViewModal();
    dismissUnsavedModal();
  }
});

/* ==========================================================================
   🛡️ UNSAVED CHANGES GUARD & DIRTY FORM CONTROLLER
   ========================================================================== */
let isFormDirty = false;
let pendingNavigationUrl = null;

function initDirtyFormGuard() {
  // Find any active record forms
  const forms = document.querySelectorAll('form:not([data-no-dirty-guard])');
  forms.forEach(form => {
    if (form.querySelector('input:not([type="hidden"]), select, textarea')) {
      form.addEventListener('input', (e) => {
        if (!e.target.closest('#header-search-container')) {
          isFormDirty = true;
        }
      });
      form.addEventListener('change', (e) => {
        if (!e.target.closest('#header-search-container')) {
          isFormDirty = true;
        }
      });
      form.addEventListener('submit', () => {
        isFormDirty = false;
      });
    }
  });

  // Intercept all Back buttons (.btn-action-back)
  document.addEventListener('click', (e) => {
    const backBtn = e.target.closest('.btn-action-back');
    if (backBtn && isFormDirty) {
      e.preventDefault();
      e.stopPropagation();
      pendingNavigationUrl = backBtn.getAttribute('href');
      showUnsavedModal();
    }
  });

  // Native browser navigation protection
  window.addEventListener('beforeunload', (e) => {
    if (isFormDirty) {
      e.preventDefault();
      e.returnValue = '';
      return '';
    }
  });
}

function showUnsavedModal() {
  const modal = document.getElementById('modal-unsaved-changes');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (window.lucide) window.lucide.createIcons();
  }
}

function dismissUnsavedModal() {
  const modal = document.getElementById('modal-unsaved-changes');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
  pendingNavigationUrl = null;
}

function confirmDiscardNavigation() {
  isFormDirty = false;
  dismissUnsavedModal();
  if (pendingNavigationUrl) {
    window.location.href = pendingNavigationUrl;
  } else {
    window.history.back();
  }
}

/* ==========================================================================
   🖱️ SMART TABLE ROW NAVIGATION (SINGLE-CLICK ID & DOUBLE-CLICK ROW)
   ========================================================================== */
function initSmartTableRowNavigation() {
  // 1. Delegated Double-Click on table row with [data-view-url], [data-edit-url], or [data-entity]
  document.addEventListener('dblclick', (e) => {
    // Shield interactive elements (buttons, links, inputs, selects, action menus)
    if (e.target.closest('button, a, input, select, textarea, .table-action-menu, #floating-row-action-menu, .table-filter-popover, .smart-table-col-menu, .view-size-popover')) {
      return;
    }

    // Shield accidental double-click during text selection (e.g. copying text from a cell)
    const selectedText = window.getSelection() ? window.getSelection().toString().trim() : '';
    if (selectedText.length > 0) {
      return;
    }

    // Locate enclosing row with data-view-url, data-edit-url, or data-entity
    const row = e.target.closest('tr[data-view-url], tr[data-edit-url], tr[data-entity]');
    if (!row) return;

    let targetUrl = row.getAttribute('data-view-url');
    if (!targetUrl || targetUrl === '#' || targetUrl === 'null') {
      const editUrl = row.getAttribute('data-edit-url');
      if (editUrl) {
        targetUrl = editUrl.endsWith('/edit') ? editUrl.replace(/\/edit$/, '/view') : `${editUrl}?mode=view`;
      }
    }

    if (targetUrl && targetUrl !== '#' && targetUrl !== 'null') {
      window.location.href = targetUrl;
    } else {
      const entity = row.getAttribute('data-entity');
      const id = row.getAttribute('data-id');
      const title = row.getAttribute('data-title') || '';
      if (entity && id && typeof openDynamicViewModal === 'function') {
        openDynamicViewModal(entity, id, title);
      }
    }
  });

  // 2. Delegated Enter Key on table row when focused
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const activeEl = document.activeElement;
      if (activeEl && (activeEl.matches('tr[data-view-url]') || activeEl.matches('tr[data-edit-url]') || activeEl.matches('tr[data-entity]'))) {
        // If an inner element has focus (like a button, input, or link), let it handle its own Enter
        if (e.target.closest('button, a, input, select, textarea')) return;
        let targetUrl = activeEl.getAttribute('data-view-url');
        if (!targetUrl || targetUrl === '#' || targetUrl === 'null') {
          const editUrl = activeEl.getAttribute('data-edit-url');
          if (editUrl) {
            targetUrl = editUrl.endsWith('/edit') ? editUrl.replace(/\/edit$/, '/view') : `${editUrl}?mode=view`;
          }
        }
        if (targetUrl && targetUrl !== '#' && targetUrl !== 'null') {
          window.location.href = targetUrl;
        } else {
          const entity = activeEl.getAttribute('data-entity');
          const id = activeEl.getAttribute('data-id');
          const title = activeEl.getAttribute('data-title') || '';
          if (entity && id && typeof openDynamicViewModal === 'function') {
            openDynamicViewModal(entity, id, title);
          }
        }
      }
    }
  });
}

/* ==========================================================================
   🚨 UNIVERSAL FORM FIELD VALIDATION & REAL-TIME DUPLICATE DETECTION ENGINE
   ========================================================================== */
function initUniversalFormValidation() {
  // 1. Locate all active data forms across the application
  const forms = document.querySelectorAll('form:not([data-no-validate]):not(#header-search-container form)');
  
  forms.forEach(form => {
    // Disable native browser validation popups so our smooth shake alerts take precedence
    form.setAttribute('novalidate', 'true');

    // Intercept form submit event
    form.addEventListener('submit', (e) => {
      const isValid = validatePyrixForm(form);
      if (!isValid) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        return false;
      }
    });

    // Wire real-time duplicate checks on eligible inputs
    setupDuplicateCheckers(form);
  });

  // 2. Intercept external submit buttons (e.g. <button type="submit" form="master-record-form">)
  document.addEventListener('click', (e) => {
    const submitBtn = e.target.closest('button[type="submit"][form]');
    if (!submitBtn) return;

    const targetFormId = submitBtn.getAttribute('form');
    if (!targetFormId) return;

    const targetForm = document.getElementById(targetFormId);
    if (!targetForm) return;

    const isValid = validatePyrixForm(targetForm);
    if (!isValid) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      return false;
    }
  });
}

/**
 * Validates all required fields and duplicate flags in the target form.
 * Returns true if valid, false if any field fails.
 */
function validatePyrixForm(form) {
  if (!form) return true;

  // Find all visible and enabled required fields
  const requiredFields = form.querySelectorAll(
    'input[required]:not([type="hidden"]):not([disabled]), ' +
    'select[required]:not([disabled]), ' +
    'textarea[required]:not([disabled]), ' +
    '[data-required="true"]:not([disabled])'
  );

  let hasError = false;
  let firstInvalidField = null;

  requiredFields.forEach(field => {
    // Skip fields that are explicitly hidden or inside hidden containers
    if (field.offsetParent === null && !field.classList.contains('always-validate')) {
      return;
    }

    const val = field.value ? field.value.trim() : '';
    const isBlank = (field.tagName === 'SELECT') ? (!val || val === '' || val === '__none__') : (val === '');

    if (isBlank) {
      hasError = true;
      const labelText = getFieldLabel(field);
      triggerFieldShake(field, `${labelText} is required and cannot be blank.`);
      if (!firstInvalidField) firstInvalidField = field;
    } else if (field.dataset.duplicateConflict === 'true') {
      hasError = true;
      const dupMsg = field.dataset.duplicateMessage || 'This value already exists in the database. Please provide a unique value.';
      triggerFieldShake(field, dupMsg);
      if (!firstInvalidField) firstInvalidField = field;
    }
  });

  // Also check any non-required fields that have duplicate conflicts
  const nonRequiredDuplicates = form.querySelectorAll('[data-duplicate-conflict="true"]');
  nonRequiredDuplicates.forEach(field => {
    hasError = true;
    const dupMsg = field.dataset.duplicateMessage || 'This value already exists in the database.';
    triggerFieldShake(field, dupMsg);
    if (!firstInvalidField) firstInvalidField = field;
  });

  if (hasError && firstInvalidField) {
    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    firstInvalidField.focus({ preventScroll: true });
    return false;
  }

  return true;
}

/**
 * Triggers the animated shake alert, glowing red border, and inline error message.
 */
function triggerFieldShake(field, errorMsg) {
  if (!field) return;

  // Resolve enclosing wrapper for the shake animation
  let wrapper = field.closest('.form-group, .space-y-1, .space-y-1\\.5, .space-y-2');
  if (!wrapper) {
    const relContainer = field.closest('.relative');
    wrapper = relContainer ? relContainer.parentElement : field.parentElement;
  }
  if (!wrapper) wrapper = field;

  // Apply red error glow
  field.classList.remove('field-success-border');
  field.classList.add('field-error-border');

  // Trigger CSS shake animation with forced reflow
  wrapper.classList.remove('animate-shake');
  void wrapper.offsetWidth; // Force reflow
  wrapper.classList.add('animate-shake');

  // Insert or update inline error message element
  let errEl = wrapper.querySelector('.field-error-msg');
  if (!errEl) {
    errEl = document.createElement('div');
    errEl.className = 'field-error-msg';
    errEl.innerHTML = `
      <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <span class="field-error-text"></span>
    `;
    // Insert after input or after relative wrapper
    const insertAfterEl = field.closest('.relative') || field;
    if (insertAfterEl.nextSibling) {
      insertAfterEl.parentNode.insertBefore(errEl, insertAfterEl.nextSibling);
    } else {
      insertAfterEl.parentNode.appendChild(errEl);
    }
  }

  const textSpan = errEl.querySelector('.field-error-text') || errEl.querySelector('span');
  if (textSpan && errorMsg) {
    textSpan.textContent = errorMsg;
  }
  errEl.classList.remove('hidden');

  // Clean up animation class after completion
  setTimeout(() => {
    wrapper.classList.remove('animate-shake');
  }, 500);

  // Real-time listener: clear error as soon as user enters valid data
  function clearOnInput() {
    const currentVal = field.value ? field.value.trim() : '';
    if (currentVal !== '' && field.dataset.duplicateConflict !== 'true') {
      field.classList.remove('field-error-border');
      if (errEl) errEl.classList.add('hidden');
      field.removeEventListener('input', clearOnInput);
      field.removeEventListener('change', clearOnInput);
    }
  }

  field.addEventListener('input', clearOnInput);
  field.addEventListener('change', clearOnInput);
}

/**
 * Extracts a human-friendly label for an input field.
 */
function getFieldLabel(field) {
  // 1. Check data-label
  if (field.dataset.label) return field.dataset.label;

  // 2. Check label with for="field.id"
  if (field.id) {
    const forLabel = document.querySelector(`label[for="${field.id}"]`);
    if (forLabel) {
      const clone = forLabel.cloneNode(true);
      clone.querySelectorAll('span').forEach(s => s.remove());
      const txt = clone.textContent.trim();
      if (txt) return txt;
    }
  }

  // 3. Check enclosing wrapper (look upwards past .relative)
  let parent = field.parentElement;
  while (parent && (parent.classList.contains('relative') || parent.tagName === 'FIELDSET')) {
    parent = parent.parentElement;
  }
  if (parent) {
    const labelEl = parent.querySelector('label');
    if (labelEl) {
      const clone = labelEl.cloneNode(true);
      clone.querySelectorAll('span').forEach(s => s.remove());
      const txt = clone.textContent.trim();
      if (txt) return txt;
    }
  }

  // 4. Fallback to placeholder or name
  if (field.placeholder && !field.placeholder.startsWith('e.g.') && !field.placeholder.startsWith('••••')) {
    return field.placeholder.replace('...', '').trim();
  }
  if (field.name) {
    if (field.name === 'email') return 'Username';
    if (field.name === 'password') return 'Password';
    return field.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  return 'This field';
}


/**
 * Attaches real-time duplicate checking to identifier fields in a form.
 */
function setupDuplicateCheckers(form) {
  // Auto-detect entity from form action or data attribute
  let entity = form.dataset.uniqueEntity;
  if (!entity && form.action) {
    if (form.action.includes('/master/gl-accounts')) entity = 'gl-accounts';
    else if (form.action.includes('/categories')) entity = 'gl-categories';
    else if (form.action.includes('/segments')) entity = 'gl-segments';
    else if (form.action.includes('/master/departments')) entity = 'departments';
    else if (form.action.includes('/master/cost-centres')) entity = 'cost-centres';
    else if (form.action.includes('/master/cb-bank-accounts')) entity = 'cb-bank-accounts';
    else if (form.action.includes('/master/customers')) entity = 'customers';
    else if (form.action.includes('/master/vendors')) entity = 'vendors';
  }

  // Find candidate fields for duplicate validation
  const candidateInputs = form.querySelectorAll(
    '[data-unique-entity], ' +
    'input[name="account_name"], input[name="category_code"], input[name="category_name"], ' +
    'input[name="segment_code"], input[name="segment_name"], input[name="dept_name"], input[name="dept_code"], ' +
    'input[name="cost_centre_name"], input[name="cost_centre_code"], input[name="customer_name"], input[name="vendor_name"]'
  );

  candidateInputs.forEach(input => {
    const targetEntity = input.dataset.uniqueEntity || entity;
    const targetField = input.dataset.uniqueField || input.name;
    if (!targetEntity || !targetField) return;

    // Extract exclude_id if editing existing record
    let excludeId = form.dataset.recordId || null;
    if (!excludeId && form.action) {
      const match = form.action.match(/\/(?:master\/[^\/]+|categories|segments)\/([^\/]+)\/edit/);
      if (match) excludeId = match[1];
    }

    let debounceTimer = null;

    function executeCheck() {
      const val = input.value ? input.value.trim() : '';
      if (!val) {
        delete input.dataset.duplicateConflict;
        delete input.dataset.duplicateMessage;
        input.classList.remove('field-error-border');
        input.classList.remove('field-success-border');
        const err = input.closest('div')?.querySelector('.field-error-msg');
        if (err) err.classList.add('hidden');
        return;
      }

      let url = `/api/validation/check-unique?entity=${encodeURIComponent(targetEntity)}&field=${encodeURIComponent(targetField)}&value=${encodeURIComponent(val)}`;
      if (excludeId) {
        url += `&exclude_id=${encodeURIComponent(excludeId)}`;
      }

      fetch(url)
        .then(res => res.json())
        .then(data => {
          if (!data) return;
          if (data.is_unique === false) {
            input.dataset.duplicateConflict = 'true';
            input.dataset.duplicateMessage = data.message;
            triggerFieldShake(input, data.message);
          } else {
            delete input.dataset.duplicateConflict;
            delete input.dataset.duplicateMessage;
            input.classList.remove('field-error-border');
            input.classList.add('field-success-border');
            const err = input.closest('div')?.querySelector('.field-error-msg');
            if (err) err.classList.add('hidden');
          }
        })
        .catch(() => {});
    }

    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(executeCheck, 400);
    });

    input.addEventListener('blur', () => {
      clearTimeout(debounceTimer);
      executeCheck();
    });
  });
}



