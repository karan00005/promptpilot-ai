// ==========================================
// PROMPTPILOT AI — CONTENT INJECTION SCRIPT
// ==========================================

let activeTextarea = null;
let injectionInterval = null;

// Selectors for prompt textareas/contenteditables across supported AI platforms
const PLATFORM_SELECTORS = [
  "#prompt-textarea",                 // ChatGPT
  "div[contenteditable=\"true\"]",    // Claude & Gemini & standard editors
  "textarea[placeholder*=\"prompt\"]", // Generic fallbacks
  "textarea[placeholder*=\"ask\"]",
  "#input-area textarea"
];

// Initialize extension content script
function init() {
  // Check if extension is enabled, then start injecting
  chrome.storage.local.get("isEnabled", (data) => {
    if (data.isEnabled !== false) {
      startInjections();
    }
  });

  // Listen for setting changes (ON/OFF toggle)
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.isEnabled) {
      if (changes.isEnabled.newValue) {
        startInjections();
      } else {
        stopInjections();
      }
    }
  });
}

function startInjections() {
  if (injectionInterval) clearInterval(injectionInterval);
  
  // Periodic check handles dynamic single-page app DOM shifts
  injectionInterval = setInterval(checkForTextarea, 1000);
}

function stopInjections() {
  if (injectionInterval) {
    clearInterval(injectionInterval);
    injectionInterval = null;
  }
  removeInjectedUI();
}

function checkForTextarea() {
  let textarea = null;
  
  for (const selector of PLATFORM_SELECTORS) {
    textarea = document.querySelector(selector);
    if (textarea) break;
  }

  if (textarea && textarea !== activeTextarea) {
    activeTextarea = textarea;
    injectPromptPilotUI(textarea);
  }
}

function injectPromptPilotUI(target) {
  // Prevent duplicate injections
  if (target.parentElement.querySelector(".promptpilot-ui-container")) {
    return;
  }

  // Create container wrapper
  const container = document.createElement("div");
  container.className = "promptpilot-ui-container";
  
  // Create beautiful optimize button
  const button = document.createElement("button");
  button.type = "button";
  button.className = "promptpilot-btn-optimize";
  button.innerHTML = "✨ Optimize";
  
  // Create token badge
  const badge = document.createElement("span");
  badge.className = "promptpilot-token-badge badge-green";
  badge.innerText = "0 tokens";
  
  container.appendChild(badge);
  container.appendChild(button);
  
  // Inject container relative to target
  // Place inside parent layout right next to text field
  if (target.nextSibling) {
    target.parentNode.insertBefore(container, target.nextSibling);
  } else {
    target.parentNode.appendChild(container);
  }

  // Update token count dynamically on type
  const updateBadge = () => {
    const text = getElementText(target);
    const estTokens = estimateTokensLocal(text);
    badge.innerText = `${estTokens} tokens`;
    
    // Dynamic color badge based on length
    badge.className = "promptpilot-token-badge";
    if (estTokens < 1000) {
      badge.classList.add("badge-green");
    } else if (estTokens < 3000) {
      badge.classList.add("badge-yellow");
    } else {
      badge.classList.add("badge-red");
    }
  };

  // Robust event listeners to capture all typing, pasting, and state changes
  target.addEventListener("input", updateBadge);
  target.addEventListener("keyup", updateBadge);
  target.addEventListener("change", updateBadge);
  target.addEventListener("paste", updateBadge);
  target.addEventListener("focus", updateBadge);
  
  // Background polling to capture pre-filled, drag-dropped, or React-rendered template content
  const badgePoller = setInterval(() => {
    if (document.body.contains(target)) {
      updateBadge();
    } else {
      clearInterval(badgePoller);
    }
  }, 500);

  updateBadge(); // run once initially

  // Button click trigger
  button.addEventListener("click", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const text = getElementText(target).trim();
    if (!text) {
      showToast("Please enter a prompt first!", "warn");
      return;
    }

    button.innerText = "⚡ Optimizing...";
    button.disabled = true;
    badge.innerText = "Calculating...";

    chrome.runtime.sendMessage(
      { type: "COMPRESS_PROMPT", prompt: text },
      (response) => {
        button.innerText = "✨ Optimize";
        button.disabled = false;

        if (response && response.success) {
          const res = response.data;
          
          // Replace prompt in input field
          setElementText(target, res.compressed_prompt);
          updateBadge();
          
          const savings = res.savings_percent;
          const tokensSaved = res.original_tokens - res.compressed_tokens;
          showToast(`Saved ${tokensSaved} tokens (${savings}%)! 💰`, "success");
        } else {
          const errorMsg = response ? response.error : "Connection to backend failed";
          showToast(`Error: ${errorMsg}`, "error");
          updateBadge();
        }
      }
    );
  });
}

function removeInjectedUI() {
  const containers = document.querySelectorAll(".promptpilot-ui-container");
  containers.forEach(c => c.remove());
  activeTextarea = null;
}

// Helpers to handle textarea vs contenteditable divs
function getElementText(el) {
  if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
    return el.value;
  }
  return el.innerText || el.textContent || "";
}

function setElementText(el, val) {
  if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
    el.value = val;
  } else {
    el.innerText = val;
  }
  
  // CRITICAL: Dispatch events so React/Vue frameworks update their state
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.dispatchEvent(new Event("change", { bubbles: true }));
}

// Lightweight token approximation (4 characters per token average)
function estimateTokensLocal(text) {
  if (!text) return 0;
  return Math.max(1, Math.round(text.length / 4));
}

// Custom Toast notification UI injector
function showToast(message, type = "success") {
  // Remove existing toast if present
  const existing = document.querySelector(".promptpilot-toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = `promptpilot-toast toast-${type}`;
  toast.innerText = message;
  
  document.body.appendChild(toast);
  
  // Trigger fade out after 2.5s
  setTimeout(() => {
    toast.classList.add("fade-out");
    setTimeout(() => toast.remove(), 500);
  }, 2500);
}

// Run initial execution
init();
