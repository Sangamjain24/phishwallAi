chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
        console.log(`PhishDetector: Tab ${tabId} updated to ${tab.url}`);

        // Send message to content script to start scan
        chrome.tabs.sendMessage(tabId, {
            action: 'start_scan',
            url: tab.url
        }).catch((error) => {
            // Content script might not be ready or injected yet on some pages
            console.log('PhishDetector: Could not send message to content script (it might not be loaded yet)', error);
        });
    }
});
