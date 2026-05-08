/* ─────────────────────────────────────────────────────────
   ManifestPolicy — popup.js
   Wired to MP (window.MP) UI state machine
   ───────────────────────────────────────────────────────── */

// ═══════════════════════════════════════════════════════════
// UI STATE MACHINE
// ═══════════════════════════════════════════════════════════
window.MP = {
  showLoading() {
    document.getElementById('loadingState').style.display = 'flex';
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('summarySection').style.display = 'none';
    document.getElementById('redirectHint').style.display = 'none';
    document.getElementById('metricsRow').style.display = 'none';
    document.getElementById('statusDot').className = 'status-dot scanning';

    // Animate loader
    let w = 0;
    const fill = document.getElementById('loaderFill');
    fill.style.width = '0%';
    window._loaderInterval = setInterval(() => {
      w = Math.min(w + Math.random() * 4, 88);
      fill.style.width = w + '%';
    }, 120);
  },

  showResult(type, data) {
    clearInterval(window._loaderInterval);
    document.getElementById('loaderFill').style.width = '100%';
    setTimeout(() => {
      document.getElementById('loadingState').style.display = 'none';
      const rs = document.getElementById('resultSection');
      rs.style.display = 'block';
      rs.classList.add('fade-in');
    }, 300);

    const badge = document.getElementById('resultBadge');
    const icon  = document.getElementById('badgeIcon');
    const title = document.getElementById('badgeTitle');
    const meta  = document.getElementById('badgeMeta');
    const score = document.getElementById('badgeScore');
    const dot   = document.getElementById('statusDot');

    badge.className = 'result-badge';

    if (type === 'compliant') {
      badge.classList.add('badge-good');
      icon.textContent = '✓';
      title.textContent = 'Compliant';
      meta.textContent = 'Policy meets DPDP standards';
      score.textContent = '100';
      dot.className = 'status-dot good';
    } else if (type === 'partial') {
      badge.classList.add('badge-warn');
      icon.textContent = '△';
      title.textContent = 'Partial Compliance';
      meta.textContent = `${data.issues} issue${data.issues !== 1 ? 's' : ''} flagged`;
      score.textContent = Math.max(100 - data.issues * 12, 30);
      dot.className = 'status-dot warn';
    } else if (type === 'missing') {
      badge.classList.add('badge-bad');
      icon.textContent = '✕';
      title.textContent = 'Not a Privacy Policy';
      meta.textContent = data.sub || 'No policy detected';
      score.textContent = '—';
      dot.className = 'status-dot bad';
    } else if (type === 'error') {
      badge.classList.add('badge-neutral');
      icon.textContent = '!';
      title.textContent = 'Scan Failed';
      meta.textContent = data.msg || 'Backend unreachable';
      score.textContent = '—';
      dot.className = 'status-dot bad';
    }

    if (data && (data.shady !== undefined)) {
      document.getElementById('shadyVal').textContent = data.shady;
      document.getElementById('dpdpVal').textContent  = data.dpdp;
      const mr = document.getElementById('metricsRow');
      mr.style.display = 'flex';
      if (data.shady > 0) document.getElementById('metricShady').classList.add('metric-flagged');
      if (data.dpdp > 0)  document.getElementById('metricDpdp').classList.add('metric-flagged');
    }
  },

  showSummary(text) {
    const ss = document.getElementById('summarySection');
    const sb = document.getElementById('summaryBody');
    ss.style.display = 'block';
    sb.innerHTML = text;
  },

  showRedirect(msg, link) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('redirectHint').style.display = 'block';
    document.getElementById('statusDot').className = 'status-dot warn';
    document.getElementById('redirectText').textContent = msg;
    if (link) {
      const a = document.getElementById('openPrivacy');
      a.style.display = 'inline';
      a.href = link;
      a.onclick = (e) => {
        e.preventDefault();
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          chrome.tabs.update(tabs[0].id, { url: link });
        });
      };
    }
  }
};

// ═══════════════════════════════════════════════════════════
// INIT: Populate URL chip
// ═══════════════════════════════════════════════════════════
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (tabs[0]) {
    try {
      const url = new URL(tabs[0].url);
      document.getElementById('pageUrlText').textContent = url.hostname;
    } catch { 
      document.getElementById('pageUrlText').textContent = 'Current Tab';
    }
  }
});

// ═══════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════
function isLikelyPrivacyURL(url) {
  const patterns = [
    "/privacy",
    "/privacy-policy",
    "/privacy_policy",
    "/legal/privacy",
    "/policies/privacy",
    "/data-protection"
  ];
  return patterns.some(p => url.toLowerCase().includes(p));
}

function isPrivacyPolicyPage(text, url) {
  const lowerText = text.toLowerCase();
  const lowerUrl  = url.toLowerCase();

  const urlIndicators = ["privacy", "privacy-policy", "privacy_policy"];
  const urlMatch = urlIndicators.some(k => lowerUrl.includes(k));

  const titleIndicators = ["privacy policy", "privacy notice", "privacy statement"];
  const titleMatch = titleIndicators.some(k => lowerText.includes(k));

  const legalIndicators = [
    "personal data", "data controller", "data processor",
    "data retention", "data sharing", "third parties",
    "consent", "lawful basis", "rights of users"
  ];

  let legalCount = 0;
  legalIndicators.forEach(k => { if (lowerText.includes(k)) legalCount++; });

  return urlMatch && titleMatch && legalCount >= 2;
}

document.getElementById("scanBtn").addEventListener("click", () => {
  window.MP.showLoading();

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const pageUrl = tabs[0].url;

    chrome.tabs.sendMessage(tabs[0].id, { action: "GET_TEXT" }, async (response) => {

      if (!response || !response.text) {
        window.MP.showResult('error', { msg: 'Unable to read page content.' });
        return;
      }

      const pageText = response.text;
      const confirmedPolicy = isPrivacyPolicyPage(pageText, pageUrl);

      if (!confirmedPolicy) {
        if (response.privacyLink) {
          window.MP.showRedirect(
            "This page isn't a Privacy Policy. A link was found:",
            response.privacyLink
          );
        } else {
          window.MP.showRedirect(
            "No privacy policy detected on this website.",
            null
          );
        }
        return;
      }

      /* ── Confirmed → send to backend ── */
      try {
        const res = await fetch("http://127.0.0.1:5000/scan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: pageText })
        });

        const data = await res.json();

        if (data.error) {
          window.MP.showResult('error', { msg: data.error });
          return;
        }

        const shady = data.shady_clauses ? data.shady_clauses.length : 0;
        const dpdp  = data.dpdp_violations ? data.dpdp_violations.length : 0;
        const issues = shady + dpdp;

        if (issues === 0) {
          window.MP.showResult('compliant', { shady, dpdp });
        } else {
          window.MP.showResult('partial', { issues, shady, dpdp });
        }

        if (data.summary && data.summary.overview) {
          window.MP.showSummary(
            `<span style="opacity:.6;font-size:10px;text-transform:uppercase;letter-spacing:.08em;">Overview</span>
             <br>${data.summary.overview}`
          );
        }

      } catch (err) {
        window.MP.showResult('error', { msg: 'Backend not reachable. Start the server.' });
      }

    });
  });
});
