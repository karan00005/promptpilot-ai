// ==========================================
// PROMPTPILOT AI — POPUP CONTROLLER LOGIC
// ==========================================

const LEVEL_DESCRIPTIONS = {
  1: "Level 1: Rule-based. Trims whitespace and removes politeness fillers like 'please' and 'kindly'. Instant.",
  2: "Level 2: Heuristics. Adds sentence-level TF-IDF importance pruning. Safe for code and explicit metrics.",
  3: "Level 3: Deep Summarization. Activates local HuggingFace BART CNN context summarization for prompts > 500 tokens."
};

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const toggleBtn = document.getElementById("extension-toggle");
  const modelSelect = document.getElementById("select-model");
  const levelSlider = document.getElementById("range-level");
  const levelDisplay = document.getElementById("level-display");
  const levelDesc = document.getElementById("level-desc");
  const tokenInput = document.getElementById("input-token");
  const serverUrlInput = document.getElementById("input-server-url");
  const dashboardLink = document.getElementById("dashboard-link");
  
  const moneySavedText = document.getElementById("stat-money");
  const tokensSavedText = document.getElementById("stat-tokens");

  // 1. Load current settings from Chrome Storage
  chrome.storage.local.get([
    "isEnabled",
    "compressionLevel",
    "targetModel",
    "authToken",
    "serverUrl",
    "totalTokensSaved",
    "totalCostSavedUsd"
  ], (settings) => {
    // Enable/Disable toggle
    toggleBtn.checked = settings.isEnabled !== false;
    
    // Model select
    if (settings.targetModel) {
      modelSelect.value = settings.targetModel;
    }
    
    // Level slider
    const lvl = settings.compressionLevel !== undefined ? settings.compressionLevel : 2;
    levelSlider.value = lvl;
    levelDisplay.innerText = lvl;
    levelDesc.innerText = LEVEL_DESCRIPTIONS[lvl];
    
    // Auth token
    if (settings.authToken) {
      tokenInput.value = settings.authToken;
    }

    // Server URL
    const savedUrl = settings.serverUrl || "http://127.0.0.1:8000/api/v1";
    serverUrlInput.value = savedUrl;

    // Set dashboard link dynamically based on server URL
    try {
      const base = new URL(savedUrl);
      dashboardLink.href = `${base.protocol}//${base.host}`;
    } catch (_) {
      dashboardLink.href = "http://localhost:3001";
    }

    // Telemetry Statistics
    const tokens = settings.totalTokensSaved || 0;
    const cost = settings.totalCostSavedUsd || 0.0;
    
    tokensSavedText.innerText = formatNumber(tokens);
    moneySavedText.innerText = `$${cost.toFixed(2)}`;
  });

  // 2. Bind Event Listeners to save preferences on-change
  
  // ON/OFF toggle
  toggleBtn.addEventListener("change", () => {
    chrome.storage.local.set({ isEnabled: toggleBtn.checked });
  });

  // Model selection
  modelSelect.addEventListener("change", () => {
    chrome.storage.local.set({ targetModel: modelSelect.value });
  });

  // Compression Level Slider
  levelSlider.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    levelDisplay.innerText = val;
    levelDesc.innerText = LEVEL_DESCRIPTIONS[val];
    chrome.storage.local.set({ compressionLevel: val });
  });

  // Auth Token credentials
  tokenInput.addEventListener("input", (e) => {
    chrome.storage.local.set({ authToken: e.target.value.trim() });
  });

  // Custom Server URL
  serverUrlInput.addEventListener("input", (e) => {
    const url = e.target.value.trim();
    chrome.storage.local.set({ serverUrl: url });
    // Update dashboard link live
    try {
      const base = new URL(url);
      dashboardLink.href = `${base.protocol}//${base.host}`;
    } catch (_) {}
  });
});

// Helper to format large numbers (e.g. 1500 -> 1.5k)
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "k";
  }
  return num.toString();
}
