// Avoid scanning the scanner itself
if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
    console.log("PhishDetector: Skipping local/app check.");
} else {
    // Initial scan on load
    scanPage();
}

// Listen for messages from background script (for SPA navigation)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'start_scan') {
        console.log("PhishDetector: Received start_scan message");
        scanPage();
    }
});

async function scanPage() {
    console.log("PhishDetector: Scanning " + window.location.href);

    // Create loading indicator
    const alertBox = createAlertBox();
    alertBox.innerHTML = '<div class="pd-spinner"></div> Scanning...';

    try {
        const response = await fetch('http://127.0.0.1:5000/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: window.location.href })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (data.is_safe) {
            updateAlertBox(alertBox, 'SAFE', 'pd-safe');
            // Auto-hide safe message after 3 seconds
            setTimeout(() => {
                alertBox.style.opacity = '0';
                setTimeout(() => alertBox.remove(), 500);
            }, 3000);
        } else {
            updateAlertBox(alertBox, 'PHISHING DETECTED!', 'pd-phishing');
            // Keep phishing warning visible
        }

    } catch (error) {
        console.error('PhishDetector Error:', error);
        alertBox.innerHTML = '<span style="font-size:12px">PhishDetector: Server Off</span>';
        setTimeout(() => {
            alertBox.style.opacity = '0';
            setTimeout(() => alertBox.remove(), 500);
        }, 3000);
    }
}

function createAlertBox() {
    const existing = document.getElementById('phishdetector-alert');
    if (existing) {
        existing.remove();
    }
    const div = document.createElement('div');
    div.id = 'phishdetector-alert';
    document.body.appendChild(div);
    return div;
}

function updateAlertBox(div, text, className) {
    div.className = className;
    div.innerText = text;
}
