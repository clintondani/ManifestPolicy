// ===================================
// CONFIGURATION
// ===================================

const backendUrl = "http://localhost:5000";

// ===================================
// INITIALIZATION
// ===================================

window.onload = () => {
  console.log("✅ ManifestPolicy initialized");
  
  // Check for logged-in user
  const username = localStorage.getItem("username");
  if (username) {
    document.getElementById("userName").textContent = username;
    // Only load reports if user is logged in
    loadReports();
  }
  
  // Setup file input handler
  const fileInput = document.getElementById("policyFile");
  fileInput.addEventListener("change", handleFileSelect);
};

// ===================================
// TAB SWITCHING
// ===================================

function switchTab(tabName) {
  // Remove active class from all tabs
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.remove("active");
  });
  
  // Remove active class from all tab contents
  document.querySelectorAll(".tab-content").forEach(content => {
    content.classList.remove("active");
  });
  
  // Add active class to clicked tab
  document.querySelector(`[data-tab="${tabName}"]`).classList.add("active");
  
  // Show corresponding content
  const contentId = tabName === "text" ? "textTab" : "fileTab";
  document.getElementById(contentId).classList.add("active");
}

// ===================================
// FILE HANDLING
// ===================================

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    document.getElementById("fileName").textContent = file.name;
    document.getElementById("selectedFile").style.display = "flex";
    document.querySelector(".file-upload-area").style.display = "none";
  }
}

function removeFile() {
  document.getElementById("policyFile").value = "";
  document.getElementById("selectedFile").style.display = "none";
  document.querySelector(".file-upload-area").style.display = "flex";
}

// ===================================
// SCAN TEXT / URL
// ===================================

async function scanText() {
  const text = document.getElementById("policyText").value.trim();
  const username = localStorage.getItem("username");

  if (!text) {
    showNotification("Please enter or paste a privacy policy text or URL", "warning");
    return;
  }

  showLoading();
  hideResults();

  try {
    const response = await fetch(`${backendUrl}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        text, 
        username: username && username !== "null" ? username : null 
      })
    });

    const result = await response.json();
    hideLoading();
    
    if (response.ok) {
      displayResults(result);
      // Only refresh history if user is logged in
      const username = localStorage.getItem("username");
      if (username && username !== "null" && username !== "") {
        loadReports(); // Refresh history for logged-in users
      }
    } else {
      showNotification(result.error || "Scan failed", "danger");
    }
  } catch (error) {
    hideLoading();
    console.error("❌ Scan failed:", error);
    showNotification("Failed to scan. Please check your connection.", "danger");
  }
}

// ===================================
// UPLOAD FILE
// ===================================

async function uploadFile() {
  const fileInput = document.getElementById("policyFile");
  if (!fileInput.files.length) {
    showNotification("Please select a file to scan", "warning");
    return;
  }

  const username = localStorage.getItem("username");
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("username", username && username !== "null" ? username : "");

  showLoading();
  hideResults();

  try {
    const response = await fetch(`${backendUrl}/upload`, {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    hideLoading();
    
    if (response.ok) {
      displayResults(result);
      removeFile();
      // Only refresh history if user is logged in
      const username = localStorage.getItem("username");
      if (username && username !== "null" && username !== "") {
        loadReports(); // Refresh history for logged-in users
      }
    } else {
      showNotification(result.error || "File upload failed", "danger");
    }
  } catch (error) {
    hideLoading();
    console.error("❌ File upload failed:", error);
    showNotification("Failed to upload file. Please check your connection.", "danger");
  }
}

// ===================================
// DISPLAY RESULTS
// ===================================

function displayResults(result) {
  if (result.error) {
    showNotification(result.error, "danger");
    return;
  }

  console.log("📊 Displaying results:", result);
  
  const resultsSection = document.getElementById("resultsSection");
  resultsSection.style.display = "block";
  
  // Scroll to results
  setTimeout(() => {
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 100);
  
  // Update status badge
  const statusBadge = document.getElementById("resultStatus");
  const hasIssues = result.shady_clauses?.length > 0 || result.dpdp_violations?.length > 0;
  
  if (!hasIssues) {
    statusBadge.className = "status-badge status-success";
    statusBadge.innerHTML = '<span class="status-dot"></span>All Clear';
  } else if (result.dpdp_violations?.length > 0) {
    statusBadge.className = "status-badge status-danger";
    statusBadge.innerHTML = '<span class="status-dot"></span>Critical Issues';
  } else {
    statusBadge.className = "status-badge status-warning";
    statusBadge.innerHTML = '<span class="status-dot"></span>Issues Found';
  }
  
  // Display summary
  displaySummary(result.summary);
  
  // Display shady clauses
  displayShadyClauses(result.shady_clauses || []);
  
  // Display DPDP violations
  displayDPDPViolations(result.dpdp_violations || []);
  
  console.log("✅ Results displayed successfully");
}

function displaySummary(summary) {
  const summaryContent = document.getElementById("summaryContent");
  
  if (!summary || typeof summary !== 'object') {
    summaryContent.innerHTML = '<p class="no-issues">Summary not available</p>';
    return;
  }
  
  const summaryItems = [
    { title: "Overview", key: "overview" },
    { title: "Data Collected", key: "data_collected" },
    { title: "Data Sharing", key: "data_sharing" },
    { title: "User Rights", key: "user_rights" },
    { title: "Data Retention", key: "data_retention" }
  ];
  
  let html = '';
  summaryItems.forEach(item => {
    const value = summary[item.key] || "Not clearly stated";
    html += `
      <div class="summary-item">
        <div class="summary-item-title">${item.title}</div>
        <div class="summary-item-text">${value}</div>
      </div>
    `;
  });
  
  summaryContent.innerHTML = html;
}

function displayShadyClauses(clauses) {
  const list = document.getElementById("shadyClausesList");
  const count = document.getElementById("shadyCount");
  
  count.textContent = clauses.length;
  
  if (clauses.length === 0) {
    list.innerHTML = '<div class="no-issues">✅ No shady clauses detected</div>';
    return;
  }
  
  let html = '';
  clauses.forEach(item => {
    const clause = item.clause || item;
    const reason = item.reason || '';
    
    html += `
      <div class="issue-item">
        <div class="issue-title">${clause}</div>
        ${reason ? `<div class="issue-description">${reason}</div>` : ''}
      </div>
    `;
  });
  
  list.innerHTML = html;
}

function displayDPDPViolations(violations) {
  const list = document.getElementById("dpdpViolationsList");
  const count = document.getElementById("dpdpCount");
  
  count.textContent = violations.length;
  
  if (violations.length === 0) {
    list.innerHTML = '<div class="no-issues">✅ No DPDP violations detected</div>';
    return;
  }
  
  let html = '';
  violations.forEach(item => {
    const violation = item.violation || item;
    const description = item.description || '';
    const section = item.section || '';
    
    html += `
      <div class="issue-item danger">
        <div class="issue-title">${violation}</div>
        ${description ? `<div class="issue-description">${description}</div>` : ''}
        ${section ? `<div class="issue-section">${section}</div>` : ''}
      </div>
    `;
  });
  
  list.innerHTML = html;
}

// ===================================
// LOAD REPORTS (HISTORY)
// ===================================

async function loadReports() {
  try {
    const username = localStorage.getItem("username");
    
    // Show message for guest users
    if (!username || username === "null" || username === "") {
      document.getElementById("reportsList").innerHTML = `
        <div class="guest-message-card glass-card" style="text-align: center; padding: 3rem; max-width: 500px; margin: 0 auto;">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="color: var(--color-tertiary); margin: 0 auto 1.5rem;">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke-width="2"/>
            <circle cx="8.5" cy="7" r="4" stroke-width="2"/>
            <line x1="20" y1="8" x2="20" y2="14" stroke-width="2"/>
            <line x1="23" y1="11" x2="17" y2="11" stroke-width="2"/>
          </svg>
          <h3 style="color: var(--color-light); margin-bottom: 0.75rem; font-size: 1.25rem; font-weight: 600;">History Not Available for Guests</h3>
          <p style="color: var(--color-tertiary); margin-bottom: 1.5rem; line-height: 1.6; font-size: 0.9375rem;">
            To save and view your scan history, please log in or create an account. Your scans will be stored securely and accessible anytime.
          </p>
          <button class="btn-primary" onclick="window.location.href='login_new.html'" style="display: inline-flex;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" stroke-width="2"/>
              <polyline points="10 17 15 12 10 7" stroke-width="2"/>
              <line x1="15" y1="12" x2="3" y2="12" stroke-width="2"/>
            </svg>
            Login / Sign Up
          </button>
        </div>
      `;
      return;
    }

    const url = `${backendUrl}/history?username=${encodeURIComponent(username)}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch reports");

    const reports = await response.json();
    displayReports(reports);
  } catch (err) {
    console.error("❌ Error loading reports:", err);
    document.getElementById("reportsList").innerHTML = 
      '<div class="empty-state"><p class="empty-state-text">Failed to load reports</p></div>';
  }
}

function displayReports(reports) {
  const reportsList = document.getElementById("reportsList");
  
  if (!reports || reports.length === 0) {
    reportsList.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-width="2"/>
        </svg>
        <p class="empty-state-text">No scan reports yet</p>
      </div>
    `;
    return;
  }

  let html = '';
  reports.forEach(report => {
    const timestamp = new Date(report.timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    const shadyCount = report.shady_clauses?.length || 0;
    const dpdpCount = report.dpdp_violations?.length || 0;
    
    html += `
      <div class="report-card" onclick="openReport(${report.id})">
        <div class="report-header">
          <span class="report-timestamp">${timestamp}</span>
          <span class="report-type">${report.input_type}</span>
        </div>
        
        <div class="report-details">
          ${report.username ? `
            <div class="report-detail">
              <span class="report-detail-label">User</span>
              <span class="report-detail-value">${report.username}</span>
            </div>
          ` : ''}
          
          ${report.filename ? `
            <div class="report-detail">
              <span class="report-detail-label">File</span>
              <span class="report-detail-value">${truncateFilename(report.filename)}</span>
            </div>
          ` : ''}
        </div>
        
        <div class="report-stats">
          <div class="report-stat">
            <span class="report-stat-value">${shadyCount}</span>
            <span class="report-stat-label">Shady Clauses</span>
          </div>
          <div class="report-stat">
            <span class="report-stat-value">${dpdpCount}</span>
            <span class="report-stat-label">DPDP Violations</span>
          </div>
        </div>
      </div>
    `;
  });
  
  reportsList.innerHTML = html;
}

function truncateFilename(filename, maxLength = 30) {
  if (filename.length <= maxLength) return filename;
  const ext = filename.split('.').pop();
  const name = filename.substring(0, maxLength - ext.length - 4);
  return `${name}...${ext}`;
}

function openReport(id) {
  window.open(`report_new.html?id=${id}`, "_blank");
}

// ===================================
// UI HELPERS
// ===================================

function showLoading() {
  document.getElementById("loadingState").style.display = "flex";
}

function hideLoading() {
  document.getElementById("loadingState").style.display = "none";
}

function hideResults() {
  document.getElementById("resultsSection").style.display = "none";
}

function showNotification(message, type = "info") {
  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? 'rgba(76, 175, 80, 0.9)' : 
                 type === 'warning' ? 'rgba(255, 152, 0, 0.9)' : 
                 type === 'danger' ? 'rgba(244, 67, 54, 0.9)' : 
                 'rgba(33, 150, 243, 0.9)'};
    color: white;
    padding: 16px 24px;
    border-radius: 10px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    z-index: 10000;
    font-weight: 500;
    animation: slideIn 0.3s ease;
  `;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Auto remove after 4 seconds
  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease";
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}

// ===================================
// AUTH
// ===================================

function logout() {
  if (confirm("Are you sure you want to logout?")) {
    localStorage.removeItem("username");
    window.location.href = "login_new.html";
  }
}

// ===================================
// ANIMATIONS CSS (injected)
// ===================================

const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
