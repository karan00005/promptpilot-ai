// ==========================================
// PROMPTPILOT AI — SERVICE WORKER BACKGROUND
// ==========================================

// Default API URL (can be overridden by user in popup settings)
const DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1";


// Set initial storage defaults on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    isEnabled: true,
    compressionLevel: 2,
    targetModel: "gpt-4o",
    authToken: "mock-dev-token", // Fallback dev token
    serverUrl: DEFAULT_API_URL,  // Default to localhost; user can change in popup
    totalCompressions: 0,
    totalTokensSaved: 0,
    totalCostSavedUsd: 0.0
  });
  console.log("PromptPilot AI extension successfully initialized!");
});

// Listener for content scripts and popup requests
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "COMPRESS_PROMPT") {
    // We execute async API fetch
    handleCompression(message.prompt)
      .then(response => sendResponse({ success: true, data: response }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true; // Keep message channel open for async response
  }
});

async function handleCompression(promptText) {
  // 1. Get settings from storage (including dynamic server URL)
  const settings = await new Promise(resolve => {
    chrome.storage.local.get([
      "compressionLevel",
      "targetModel",
      "authToken",
      "serverUrl"
    ], resolve);
  });

  const level = settings.compressionLevel || 2;
  const model = settings.targetModel || "gpt-4o";
  const token = settings.authToken || "mock-dev-token";
  const apiBaseUrl = settings.serverUrl || DEFAULT_API_URL;  // 🌐 Dynamic URL!

  // 2. Call the configured FastAPI endpoint (local or cloud)
  const response = await fetch(`${apiBaseUrl}/compress`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      prompt: promptText,
      model: model,
      level: parseInt(level)
    })
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || `Server returned error status ${response.status}`);
  }

  const result = await response.json();

  // 3. Update saved statistics asynchronously
  updateStats(
    result.original_tokens,
    result.compressed_tokens,
    model
  );

  return result;
}

function updateStats(origTokens, compTokens, model) {
  const tokensSaved = Math.max(0, origTokens - compTokens);
  
  // Calculate average cost saved: ~$15 per 1M input tokens fallback
  let rate = 0.000015; 
  const modelLower = model.toLowerCase();
  
  if (modelLower.includes("gpt-4o-mini")) {
    rate = 0.00000015;
  } else if (modelLower.includes("gpt-4o")) {
    rate = 0.000005;
  } else if (modelLower.includes("claude-3-5")) {
    rate = 0.000003;
  } else if (modelLower.includes("gemini")) {
    rate = 0.0000035;
  }

  const costSaved = tokensSaved * rate;

  chrome.storage.local.get([
    "totalCompressions",
    "totalTokensSaved",
    "totalCostSavedUsd"
  ], (stats) => {
    chrome.storage.local.set({
      totalCompressions: (stats.totalCompressions || 0) + 1,
      totalTokensSaved: (stats.totalTokensSaved || 0) + tokensSaved,
      totalCostSavedUsd: parseFloat(((stats.totalCostSavedUsd || 0.0) + costSaved).toFixed(5))
    });
  });
}
