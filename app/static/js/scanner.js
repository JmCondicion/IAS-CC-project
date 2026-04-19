// QR Attendance Scanner JavaScript
let html5QrCode = null;
let isScanning = false;
let currentPage = 1;
let currentFilters = {};

// DOM Elements
const startScanBtn = document.getElementById('start-scan-btn');
const stopScanBtn = document.getElementById('stop-scan-btn');
const readerDiv = document.getElementById('reader');
const scanStatusDiv = document.getElementById('scan-status');
const attendanceBody = document.getElementById('attendance-body');
const refreshBtn = document.getElementById('refresh-btn');
const dateFilter = document.getElementById('date-filter');
const studentIdFilter = document.getElementById('student-id-filter');
const applyFiltersBtn = document.getElementById('apply-filters-btn');
const paginationDiv = document.getElementById('pagination');
const toastContainer = document.getElementById('toast-container');

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAttendance();
    setupEventListeners();
    startAutoRefresh();
});

// Setup Event Listeners
function setupEventListeners() {
    startScanBtn.addEventListener('click', startScanner);
    stopScanBtn.addEventListener('click', stopScanner);
    refreshBtn.addEventListener('click', () => loadAttendance());
    applyFiltersBtn.addEventListener('click', applyFilters);
}

// Toast Notification Function
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Start QR Scanner
async function startScanner() {
    if (isScanning) return;
    
    try {
        html5QrCode = new Html5Qrcode("reader");
        
        const config = { 
            fps: 10, 
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0
        };
        
        await html5QrCode.start(
            { facingMode: "environment" }, 
            config, 
            onScanSuccess,
            onScanError
        );
        
        isScanning = true;
        startScanBtn.style.display = 'none';
        stopScanBtn.style.display = 'block';
        showToast('Scanner started - Point camera at QR code', 'info');
        
    } catch (error) {
        console.error('Failed to start scanner:', error);
        showToast('Failed to start scanner. Please allow camera access.', 'error');
    }
}

// Stop QR Scanner
function stopScanner() {
    if (!isScanning || !html5QrCode) return;
    
    html5QrCode.stop().then(() => {
        isScanning = false;
        startScanBtn.style.display = 'block';
        stopScanBtn.style.display = 'none';
        showToast('Scanner stopped', 'info');
    }).catch(error => {
        console.error('Failed to stop scanner:', error);
    });
}

// Handle Successful Scan
async function onScanSuccess(decodedText, decodedResult) {
    // Prevent multiple rapid scans
    if (window.isProcessing) return;
    window.isProcessing = true;
    
    try {
        showScanStatus('Scanning...', 'info');
        
        const response = await fetch('/api/scan_qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ qr_data: decodedText })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            showScanStatus(`✓ ${data.message}`, 'success');
            showToast(`${data.name} - ${data.message}`, 'success');
            loadAttendance(); // Refresh the table
        } else {
            showScanStatus(`✗ ${data.message}`, 'error');
            showToast(data.message, 'error');
        }
        
    } catch (error) {
        console.error('Scan error:', error);
        showScanStatus('Network error. Please try again.', 'error');
        showToast('Network error. Please try again.', 'error');
    } finally {
        // Cooldown before next scan
        setTimeout(() => {
            window.isProcessing = false;
        }, 2000);
    }
}

// Handle Scan Error
function onScanError(error) {
    // Ignore minor errors during scanning
    if (error.toString().includes('QR code not found')) return;
    console.warn('Scan error:', error);
}

// Show Scan Status
function showScanStatus(message, type) {
    scanStatusDiv.textContent = message;
    scanStatusDiv.className = `scan-status ${type}`;
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        scanStatusDiv.style.display = 'none';
    }, 3000);
}

// Load Attendance Records
async function loadAttendance(page = 1) {
    try {
        attendanceBody.innerHTML = '<tr><td colspan="4" class="loading">Loading...</td></tr>';
        
        let url = `/api/attendance?page=${page}&per_page=20`;
        
        if (currentFilters.date) {
            url += `&date=${currentFilters.date}`;
        }
        if (currentFilters.student_id) {
            url += `&student_id=${currentFilters.student_id}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.status === 'success') {
            renderAttendanceTable(data.records);
            renderPagination(data);
            currentPage = page;
        } else {
            attendanceBody.innerHTML = '<tr><td colspan="4" class="loading">Error loading data</td></tr>';
        }
        
    } catch (error) {
        console.error('Error loading attendance:', error);
        attendanceBody.innerHTML = '<tr><td colspan="4" class="loading">Network error</td></tr>';
    }
}

// Render Attendance Table
function renderAttendanceTable(records) {
    if (records.length === 0) {
        attendanceBody.innerHTML = '<tr><td colspan="4" class="loading">No records found</td></tr>';
        return;
    }
    
    attendanceBody.innerHTML = records.map(record => `
        <tr>
            <td>${escapeHtml(record.student_name || 'Unknown')}</td>
            <td>${record.student_id}</td>
            <td>${formatDateTime(record.timestamp)}</td>
            <td>
                <span class="status-badge ${record.status === 'IN' ? 'status-in' : 'status-out'}">
                    ${record.status}
                </span>
            </td>
        </tr>
    `).join('');
}

// Render Pagination
function renderPagination(data) {
    const { page, pages, total } = data;
    
    if (pages <= 1) {
        paginationDiv.innerHTML = '';
        return;
    }
    
    let html = `<button onclick="loadAttendance(1)" ${page === 1 ? 'disabled' : ''}>First</button>`;
    
    if (page > 1) {
        html += `<button onclick="loadAttendance(${page - 1})">Prev</button>`;
    }
    
    // Page numbers
    for (let i = Math.max(1, page - 2); i <= Math.min(pages, page + 2); i++) {
        html += `<button onclick="loadAttendance(${i})" class="${i === page ? 'active' : ''}">${i}</button>`;
    }
    
    if (page < pages) {
        html += `<button onclick="loadAttendance(${page + 1})">Next</button>`;
    }
    
    html += `<button onclick="loadAttendance(${pages})" ${page === pages ? 'disabled' : ''}>Last</button>`;
    
    paginationDiv.innerHTML = html;
}

// Apply Filters
function applyFilters() {
    currentFilters = {
        date: dateFilter.value,
        student_id: studentIdFilter.value
    };
    loadAttendance(1);
    showToast('Filters applied', 'info');
}

// Auto Refresh Every 3 Seconds
function startAutoRefresh() {
    setInterval(() => {
        if (!isScanning && !window.isProcessing) {
            loadAttendance(currentPage);
        }
    }, 3000);
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDateTime(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (isScanning && html5QrCode) {
        html5QrCode.stop();
    }
});
