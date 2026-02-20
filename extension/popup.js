document.getElementById('scanBtn').addEventListener('click', async () => {
  const statusDiv = document.getElementById('status');
  const resultDiv = document.getElementById('result');
  const predictionP = document.getElementById('prediction');
  
  statusDiv.innerHTML = '<p>Scanning...</p>';
  resultDiv.classList.add('hidden');

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.url) {
      statusDiv.innerHTML = '<p>Cannot scan this tab.</p>';
      return;
    }

    const response = await fetch('http://127.0.0.1:5000/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: tab.url })
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    const data = await response.json();
    
    statusDiv.innerHTML = '';
    resultDiv.classList.remove('hidden');
    
    if (data.is_safe) {
      predictionP.textContent = 'Safe';
      predictionP.className = 'safe';
      document.body.className = 'safe-bg';
    } else {
      predictionP.textContent = 'PHISHING DETECTED!';
      predictionP.className = 'phishing';
      document.body.className = 'phishing-bg';
    }

  } catch (error) {
    console.error('Error:', error);
    statusDiv.innerHTML = '<p style="color:red;">Error connecting to server. Is app.py running?</p>';
  }
});
