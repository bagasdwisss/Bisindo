/**
 * BISINDO Translator - Client-side AI Web Application
 * Powered by TensorFlow.js, MediaPipe Hands, and Web Speech API
 */

// --- Global Application State ---
const state = {
  // Models and Labels
  modelAbjad: null,
  modelKosakata: null,
  labelsAbjad: [],
  labelsKosakata: [],
  modelsReady: false,

  // Camera & MediaPipe
  camera: null,
  hands: null,
  isCameraRunning: false,
  facingMode: 'user', // 'user' or 'environment'

  // Recognition Mode & Settings
  isModeAbjad: false, // false = Mode Kata, true = Mode Abjad
  autoSpeak: false,

  // Prediction State (faithful to app.py logic)
  historyItems: [], // Array of [word, modeType]
  history: [],      // Rolling window of last predictions
  lastIndex: null,
  pendingWord: '',
  pendingTime: 0,
  lastAddTime: 0,

  // Performance / Stats
  lastFrameTime: performance.now(),
  fps: 0,
  frameCount: 0,
  fpsTimer: performance.now(),
};

// --- DOM Element References ---
const elements = {
  // Video & Canvas
  webcam: document.getElementById('webcam'),
  canvas: document.getElementById('output-canvas'),
  cameraPlaceholder: document.getElementById('camera-placeholder'),
  videoHud: document.getElementById('video-hud'),
  predictionHoldBar: document.getElementById('prediction-hold-bar'),

  // Status & Badges
  systemStatusPill: document.getElementById('system-status-pill'),
  systemStatusDot: document.getElementById('system-status-dot'),
  systemStatusText: document.getElementById('system-status-text'),
  badgeActiveMode: document.getElementById('badge-active-mode'),
  badgeHandsCount: document.getElementById('badge-hands-count'),
  handsCountText: document.getElementById('hands-count-text'),
  badgeFps: document.getElementById('badge-fps'),
  currentDetectionLabel: document.getElementById('current-detection-label'),
  currentConfidenceLabel: document.getElementById('current-confidence-label'),

  // Buttons & Controls
  btnStartCamera: document.getElementById('btn-start-camera'),
  btnToggleCam: document.getElementById('btn-toggle-cam'),
  btnToggleCamText: document.getElementById('btn-toggle-cam-text'),
  btnSwitchCamera: document.getElementById('btn-switch-camera'),
  translationOutput: document.getElementById('translation-output'),
  btnDeleteLast: document.getElementById('btn-delete-last'),
  btnResetSentence: document.getElementById('btn-reset-sentence'),
  btnCopyText: document.getElementById('btn-copy-text'),
  copyTextFeedback: document.getElementById('copy-text-feedback'),

  // Mode Selection
  labelModeKata: document.getElementById('label-mode-kata'),
  labelModeAbjad: document.getElementById('label-mode-abjad'),
  radioModeKata: document.querySelector('input[name="translation-mode"][value="kata"]'),
  radioModeAbjad: document.querySelector('input[name="translation-mode"][value="abjad"]'),

  // TTS
  btnSpeakSentence: document.getElementById('btn-speak-sentence'),
  toggleAutoSpeak: document.getElementById('toggle-auto-speak'),
};

const canvasCtx = elements.canvas.getContext('2d');

// --- 1. Model Loading ---
async function loadModels() {
  try {
    updateSystemStatus('loading', 'Memuat Model AI...');

    // Load labels JSON
    const [resAbjad, resKosa] = await Promise.all([
      fetch('./models/web/labels_abjad.json'),
      fetch('./models/web/labels_kosakata.json')
    ]);

    if (!resAbjad.ok || !resKosa.ok) {
      throw new Error('Gagal mengambil file label model.');
    }

    state.labelsAbjad = await resAbjad.json();
    state.labelsKosakata = await resKosa.json();

    // Set TensorFlow.js backend
    await tf.ready();
    console.log(`TensorFlow.js backend aktif: ${tf.getBackend()}`);

    // Load TF.js Layers Models
    const [modelAbjad, modelKosa] = await Promise.all([
      tf.loadLayersModel('./models/web/abjad/model.json'),
      tf.loadLayersModel('./models/web/kosakata/model.json')
    ]);

    state.modelAbjad = modelAbjad;
    state.modelKosakata = modelKosa;
    state.modelsReady = true;

    // Warm up models with dummy tensor
    tf.tidy(() => {
      const dummy = tf.zeros([1, 126]);
      state.modelAbjad.predict(dummy);
      state.modelKosakata.predict(dummy);
    });

    console.log('Semua model AI dan label berhasil dimuat!');
    updateSystemStatus('ready', 'Model AI Siap Digunakan');

  } catch (err) {
    console.error('Error saat memuat model AI:', err);
    updateSystemStatus('error', 'Gagal Memuat Model AI');
    alert('Terjadi kesalahan saat memuat model AI. Pastikan file model tersedia di folder models/web/.');
  }
}

function updateSystemStatus(type, message) {
  elements.systemStatusText.innerText = message;
  elements.systemStatusDot.className = 'w-2.5 h-2.5 rounded-full';

  if (type === 'loading') {
    elements.systemStatusDot.classList.add('bg-yellow-400', 'animate-pulse');
  } else if (type === 'ready') {
    elements.systemStatusDot.classList.add('bg-emerald-400');
  } else if (type === 'error') {
    elements.systemStatusDot.classList.add('bg-red-500');
  }
}

// --- 2. Landmark Processing (Exact equivalent of utils.py) ---
function processLandmarks(multiHandLandmarks) {
  // keypoints shape: 126 floats (2 hands * 21 points * 3 coordinates)
  const keypoints = new Float32Array(126);

  if (multiHandLandmarks && multiHandLandmarks.length > 0) {
    const numHands = Math.min(2, multiHandLandmarks.length);

    for (let i = 0; i < numHands; i++) {
      const handLandmarks = multiHandLandmarks[i];
      const wrist = handLandmarks[0]; // Landmark 0 is the wrist
      const startIdx = i * 63;

      for (let j = 0; j < 21; j++) {
        const lm = handLandmarks[j];
        // Normalized relative to wrist: lm - wrist
        keypoints[startIdx + j * 3]     = lm.x - wrist.x;
        keypoints[startIdx + j * 3 + 1] = lm.y - wrist.y;
        keypoints[startIdx + j * 3 + 2] = lm.z - wrist.z;
      }
    }
  }

  return keypoints;
}

// --- 3. MediaPipe Hands Setup ---
function setupMediaPipe() {
  state.hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  state.hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  });

  state.hands.onResults(onHandResults);
}

// --- 4. Frame Inference & Debounce Engine ---
async function onHandResults(results) {
  // Calculate FPS
  state.frameCount++;
  const now = performance.now();
  if (now - state.fpsTimer >= 1000) {
    state.fps = Math.round((state.frameCount * 1000) / (now - state.fpsTimer));
    elements.badgeFps.innerText = `${state.fps} FPS`;
    state.frameCount = 0;
    state.fpsTimer = now;
  }

  // Set canvas dimension matching video
  if (elements.canvas.width !== elements.webcam.videoWidth && elements.webcam.videoWidth > 0) {
    elements.canvas.width = elements.webcam.videoWidth;
    elements.canvas.height = elements.webcam.videoHeight;
  }

  // Draw current frame to canvas
  canvasCtx.save();
  canvasCtx.clearRect(0, 0, elements.canvas.width, elements.canvas.height);
  canvasCtx.drawImage(results.image, 0, 0, elements.canvas.width, elements.canvas.height);

  const numHands = results.multiHandLandmarks ? results.multiHandLandmarks.length : 0;
  elements.handsCountText.innerText = `${numHands} Tangan`;

  let detectedWord = null;
  let detectedConfidence = 0;

  if (numHands > 0 && state.modelsReady) {
    // Draw landmarks and connectors
    for (const landmarks of results.multiHandLandmarks) {
      drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
        color: '#10b981',
        lineWidth: 3
      });
      drawLandmarks(canvasCtx, landmarks, {
        color: '#34d399',
        lineWidth: 1,
        radius: 4
      });
    }

    // Extract normalized keypoints vector (126 floats)
    const keypoints = processLandmarks(results.multiHandLandmarks);

    // Run active model prediction
    const activeModel = state.isModeAbjad ? state.modelAbjad : state.modelKosakata;
    const activeLabels = state.isModeAbjad ? state.labelsAbjad : state.labelsKosakata;
    const threshold = state.isModeAbjad ? 0.85 : 0.75;
    const currentType = state.isModeAbjad ? 'abjad' : 'kata';

    const inputTensor = tf.tensor2d(keypoints, [1, 126]);
    const predictionTensor = activeModel.predict(inputTensor);
    const probabilities = await predictionTensor.data();

    inputTensor.dispose();
    predictionTensor.dispose();

    // Find argmax and max confidence
    let maxIndex = 0;
    let maxConf = 0;
    for (let i = 0; i < probabilities.length; i++) {
      if (probabilities[i] > maxConf) {
        maxConf = probabilities[i];
        maxIndex = i;
      }
    }

    detectedWord = activeLabels[maxIndex];
    detectedConfidence = maxConf;

    // --- Smoothing & Decision Logic (faithful to app.py) ---
    let finalWord = null;

    if (maxConf > threshold) {
      finalWord = activeLabels[maxIndex];
      state.history = [];
      state.lastIndex = maxIndex;
    } else {
      if (state.lastIndex !== null && maxIndex !== state.lastIndex) {
        state.history = [];
      }

      state.history.push(maxIndex);
      if (state.history.length > 5) {
        state.history.shift();
      }

      // Count occurrences
      const counts = {};
      let finalIndex = state.history[0];
      let maxCount = 0;

      for (const idx of state.history) {
        counts[idx] = (counts[idx] || 0) + 1;
        if (counts[idx] > maxCount) {
          maxCount = counts[idx];
          finalIndex = idx;
        }
      }

      if (maxConf > 0.60 && maxCount >= 4) {
        finalWord = activeLabels[finalIndex];
      }
    }

    // --- Debouncing & Sentence Appending (from app.py) ---
    if (finalWord) {
      const currentTime = Date.now();

      if (finalWord !== state.pendingWord) {
        state.pendingWord = finalWord;
        state.pendingTime = currentTime;
        elements.predictionHoldBar.style.width = '0%';
      } else {
        const holdElapsed = currentTime - state.pendingTime;
        const holdPercent = Math.min(100, (holdElapsed / 600) * 100);
        elements.predictionHoldBar.style.width = `${holdPercent}%`;

        if (holdElapsed > 600) {
          const lastItem = state.historyItems.length > 0 ? state.historyItems[state.historyItems.length - 1] : null;
          const lastWord = lastItem ? lastItem[0] : '';

          if (finalWord !== lastWord || (currentTime - state.lastAddTime > 1500)) {
            state.historyItems.push([finalWord, currentType]);
            state.lastAddTime = currentTime;
            state.pendingWord = '';
            elements.predictionHoldBar.style.width = '0%';

            renderTranslation();

            if (state.autoSpeak) {
              speakText(finalWord);
            }
          }
        }
      }
    } else {
      state.pendingWord = '';
      elements.predictionHoldBar.style.width = '0%';
    }

  } else {
    state.pendingWord = '';
    elements.predictionHoldBar.style.width = '0%';
  }

  canvasCtx.restore();

  // Update current detection labels on UI
  if (detectedWord && detectedConfidence > 0.3) {
    elements.currentDetectionLabel.innerText = detectedWord;
    elements.currentConfidenceLabel.innerText = `(${Math.round(detectedConfidence * 100)}%)`;
  } else {
    elements.currentDetectionLabel.innerText = '-';
    elements.currentConfidenceLabel.innerText = '(0%)';
  }
}

// --- 5. Sentence Builder (Equivalent of get_display_text in app.py) ---
function getDisplayText() {
  let displayText = '';

  for (let i = 0; i < state.historyItems.length; i++) {
    const [word, modeType] = state.historyItems[i];

    if (i === 0) {
      displayText += word;
    } else {
      const [, prevType] = state.historyItems[i - 1];

      if (modeType === 'kata') {
        displayText += ' ' + word;
      } else if (modeType === 'abjad') {
        if (prevType === 'kata') {
          displayText += ' ' + word;
        } else {
          displayText += word; // Abjad letters concatenate without space (spelling)
        }
      }
    }
  }

  return displayText;
}

function renderTranslation() {
  const text = getDisplayText();

  if (!text.trim()) {
    elements.translationOutput.innerHTML = `<span class="text-gray-600 font-normal text-base italic">Belum ada kata terdeteksi...</span>`;
  } else {
    elements.translationOutput.innerText = text;
  }
}

// --- 6. Text-to-Speech (Web Speech API) ---
function speakText(text) {
  if (!text || !text.trim()) return;

  if (!('speechSynthesis' in window)) {
    console.warn('Browser tidak mendukung Web Speech API.');
    return;
  }

  window.speechSynthesis.cancel(); // Stop current speech
  const utterance = new SpeechSynthesisUtterance(text.trim());
  utterance.lang = 'id-ID';

  // Find Indonesian voice if available
  const voices = window.speechSynthesis.getVoices();
  const idVoice = voices.find(v => v.lang.startsWith('id') || v.lang.includes('ID'));
  if (idVoice) {
    utterance.voice = idVoice;
  }

  utterance.rate = 1.0;
  window.speechSynthesis.speak(utterance);
}

// Ensure voices are loaded (Chrome loads them asynchronously)
if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
  };
}

// --- 7. Camera Controls ---
async function startCamera() {
  if (state.isCameraRunning) return;

  try {
    elements.btnToggleCamText.innerText = 'Menyalakan...';

    const constraints = {
      video: {
        facingMode: state.facingMode,
        width: { ideal: 640 },
        height: { ideal: 480 }
      },
      audio: false
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    elements.webcam.srcObject = stream;

    await new Promise((resolve) => {
      elements.webcam.onloadedmetadata = () => {
        elements.webcam.play();
        resolve();
      };
    });

    state.camera = new Camera(elements.webcam, {
      onFrame: async () => {
        if (state.isCameraRunning && state.hands) {
          await state.hands.send({ image: elements.webcam });
        }
      },
      width: 640,
      height: 480
    });

    await state.camera.start();

    state.isCameraRunning = true;
    elements.cameraPlaceholder.classList.add('hidden');
    elements.videoHud.classList.remove('opacity-0');
    elements.btnToggleCamText.innerText = 'Matikan Kamera';

  } catch (err) {
    console.error('Gagal mengakses kamera:', err);
    alert('Tidak dapat mengakses kamera. Pastikan Anda telah memberikan izin kamera pada browser.');
    elements.btnToggleCamText.innerText = 'Nyalakan Kamera';
  }
}

function stopCamera() {
  if (!state.isCameraRunning) return;

  if (state.camera) {
    state.camera.stop();
    state.camera = null;
  }

  if (elements.webcam.srcObject) {
    const stream = elements.webcam.srcObject;
    stream.getTracks().forEach(track => track.stop());
    elements.webcam.srcObject = null;
  }

  state.isCameraRunning = false;
  elements.cameraPlaceholder.classList.remove('hidden');
  elements.videoHud.classList.add('opacity-0');
  elements.btnToggleCamText.innerText = 'Nyalakan Kamera';
  elements.handsCountText.innerText = '0 Tangan';
  elements.badgeFps.innerText = '0 FPS';
  elements.currentDetectionLabel.innerText = '-';
  elements.currentConfidenceLabel.innerText = '(0%)';

  // Clear canvas
  canvasCtx.clearRect(0, 0, elements.canvas.width, elements.canvas.height);
}

function toggleCamera() {
  if (state.isCameraRunning) {
    stopCamera();
  } else {
    startCamera();
  }
}

function switchCamera() {
  state.facingMode = state.facingMode === 'user' ? 'environment' : 'user';
  if (state.isCameraRunning) {
    stopCamera();
    startCamera();
  }
}

// --- 8. UI Mode Switcher ---
function setMode(mode) {
  state.isModeAbjad = (mode === 'abjad');

  // Update visual styles
  if (state.isModeAbjad) {
    elements.labelModeAbjad.classList.replace('border-gray-800', 'border-brand-500');
    elements.labelModeAbjad.classList.replace('bg-gray-800/40', 'bg-brand-500/10');
    elements.labelModeKata.classList.replace('border-brand-500', 'border-gray-800');
    elements.labelModeKata.classList.replace('bg-brand-500/10', 'bg-gray-800/40');
    elements.badgeActiveMode.innerText = 'Mode Abjad';
  } else {
    elements.labelModeKata.classList.replace('border-gray-800', 'border-brand-500');
    elements.labelModeKata.classList.replace('bg-gray-800/40', 'bg-brand-500/10');
    elements.labelModeAbjad.classList.replace('border-brand-500', 'border-gray-800');
    elements.labelModeAbjad.classList.replace('bg-brand-500/10', 'bg-gray-800/40');
    elements.badgeActiveMode.innerText = 'Mode Kata';
  }

  // Clear pending states
  state.history = [];
  state.lastIndex = null;
  state.pendingWord = '';
  elements.predictionHoldBar.style.width = '0%';
}

// --- 9. Event Listeners ---
function setupEventListeners() {
  // Camera buttons
  elements.btnStartCamera.addEventListener('click', startCamera);
  elements.btnToggleCam.addEventListener('click', toggleCamera);
  elements.btnSwitchCamera.addEventListener('click', switchCamera);

  // Mode radio buttons
  elements.radioModeKata.addEventListener('change', () => setMode('kata'));
  elements.radioModeAbjad.addEventListener('change', () => setMode('abjad'));
  elements.labelModeKata.addEventListener('click', () => {
    elements.radioModeKata.checked = true;
    setMode('kata');
  });
  elements.labelModeAbjad.addEventListener('click', () => {
    elements.radioModeAbjad.checked = true;
    setMode('abjad');
  });

  // Action buttons
  elements.btnDeleteLast.addEventListener('click', () => {
    if (state.historyItems.length > 0) {
      state.historyItems.pop();
      renderTranslation();
    }
  });

  elements.btnResetSentence.addEventListener('click', () => {
    state.historyItems = [];
    renderTranslation();
  });

  elements.btnCopyText.addEventListener('click', async () => {
    const text = getDisplayText();
    if (!text.trim()) return;

    try {
      await navigator.clipboard.writeText(text);
      elements.copyTextFeedback.innerText = 'Tersalin!';
      setTimeout(() => {
        elements.copyTextFeedback.innerText = 'Salin';
      }, 1500);
    } catch (err) {
      console.warn('Gagal menyalin:', err);
    }
  });

  // TTS buttons
  elements.btnSpeakSentence.addEventListener('click', () => {
    speakText(getDisplayText());
  });

  elements.toggleAutoSpeak.addEventListener('change', (e) => {
    state.autoSpeak = e.target.checked;
  });
}

// --- Initialization ---
window.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }

  setupEventListeners();
  setupMediaPipe();
  await loadModels();
});
