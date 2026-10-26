/**
 * BISINDO Translator - Client-side AI Web Application
 * Powered by TensorFlow.js, MediaPipe Hands, Web Speech API, and PWA
 */

// Register custom regularizer to handle Keras L2 serialization seamlessly
try {
  if (window.tf && tf.serialization) {
    class L2Regularizer extends tf.regularizers.l1l2 {
      constructor(config) {
        super({ l2: config ? (config.l2 || 0) : 0 });
      }
      static get className() {
        return 'L2';
      }
    }
    tf.serialization.registerClass(L2Regularizer);
  }
} catch (e) {
  console.warn('L2 regularizer registration notice:', e);
}

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

  // Dynamic Sensitivity & Timing Settings
  thresholdKata: 0.75,
  thresholdAbjad: 0.85,
  holdDuration: 600, // ms
  cooldownRepeat: 1500, // ms

  // Prediction State (faithful to app.py logic)
  historyItems: [], // Array of [word, modeType]
  history: [],      // Rolling window of last predictions
  lastIndex: null,
  pendingWord: '',
  pendingTime: 0,
  lastAddTime: 0,

  // Speech Recognition (Two-Way Communication)
  recognition: null,
  isListening: false,

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
  btnNlpSmooth: document.getElementById('btn-nlp-smooth'),
  btnDownloadTxt: document.getElementById('btn-download-txt'),

  // Mode Selection
  labelModeKata: document.getElementById('label-mode-kata'),
  labelModeAbjad: document.getElementById('label-mode-abjad'),
  radioModeKata: document.querySelector('input[name="translation-mode"][value="kata"]'),
  radioModeAbjad: document.querySelector('input[name="translation-mode"][value="abjad"]'),

  // TTS
  btnSpeakSentence: document.getElementById('btn-speak-sentence'),
  toggleAutoSpeak: document.getElementById('toggle-auto-speak'),

  // Modal 1: Dictionary
  btnOpenDictionary: document.getElementById('btn-open-dictionary'),
  modalDictionary: document.getElementById('modal-dictionary'),
  btnCloseDictionary: document.getElementById('btn-close-dictionary'),
  tabDictKata: document.getElementById('tab-dict-kata'),
  tabDictAbjad: document.getElementById('tab-dict-abjad'),
  dictSearchInput: document.getElementById('dict-search-input'),
  dictKataGrid: document.getElementById('dict-kata-grid'),
  dictAbjadGrid: document.getElementById('dict-abjad-grid'),

  // Modal 2: Hearing 2-Way Speech
  btnOpenHearingModal: document.getElementById('btn-open-hearing-modal'),
  modalHearing: document.getElementById('modal-hearing'),
  btnCloseHearing: document.getElementById('btn-close-hearing'),
  btnToggleSpeechRec: document.getElementById('btn-toggle-speech-rec'),
  speechRecBtnText: document.getElementById('speech-rec-btn-text'),
  speechTranscriptOutput: document.getElementById('speech-transcript-output'),
  speechDetectedTags: document.getElementById('speech-detected-tags'),

  // Modal 3: Settings
  btnOpenSettings: document.getElementById('btn-open-settings'),
  modalSettings: document.getElementById('modal-settings'),
  btnCloseSettings: document.getElementById('btn-close-settings'),
  sliderThresholdKata: document.getElementById('slider-threshold-kata'),
  sliderThresholdKataVal: document.getElementById('slider-threshold-kata-val'),
  sliderThresholdAbjad: document.getElementById('slider-threshold-abjad'),
  sliderThresholdAbjadVal: document.getElementById('slider-threshold-abjad-val'),
  sliderHoldTime: document.getElementById('slider-hold-time'),
  sliderHoldTimeVal: document.getElementById('slider-hold-time-val'),
  btnResetSettings: document.getElementById('btn-reset-settings'),
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

    // Populate Dictionary Modal content
    populateDictionary();

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
    // Draw landmarks and connectors with vivid colors
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
    const threshold = state.isModeAbjad ? state.thresholdAbjad : state.thresholdKata;
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
        const holdPercent = Math.min(100, (holdElapsed / state.holdDuration) * 100);
        elements.predictionHoldBar.style.width = `${holdPercent}%`;

        if (holdElapsed >= state.holdDuration) {
          const lastItem = state.historyItems.length > 0 ? state.historyItems[state.historyItems.length - 1] : null;
          const lastWord = lastItem ? lastItem[0] : '';

          if (finalWord !== lastWord || (currentTime - state.lastAddTime > state.cooldownRepeat)) {
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

// --- 5. Sentence Builder & NLP Grammar Smoothing ---
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

// NLP Grammar Smoothing Function
function smoothSentenceNLP(rawText) {
  if (!rawText || !rawText.trim()) return '';

  let text = rawText.trim();

  // Normalize duplicate spaces
  text = text.replace(/\s+/g, ' ');

  // Capitalize first letter of every sentence
  text = text.replace(/(^\w|\.\s+\w)/g, (c) => c.toUpperCase());

  // Add terminal period if missing
  if (!/[.!?]$/.test(text)) {
    text += '.';
  }

  return text;
}

// --- 6. Text-to-Speech (Web Speech API) ---
function speakText(text) {
  if (!text || !text.trim()) return;

  if (!('speechSynthesis' in window)) {
    console.warn('Browser tidak mendukung Web Speech API.');
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text.trim());
  utterance.lang = 'id-ID';

  const voices = window.speechSynthesis.getVoices();
  const idVoice = voices.find(v => v.lang.startsWith('id') || v.lang.includes('ID'));
  if (idVoice) {
    utterance.voice = idVoice;
  }

  utterance.rate = 1.0;
  window.speechSynthesis.speak(utterance);
}

if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
  };
}

// --- 7. Two-Way Speech Recognition (Teman Dengar Bicara) ---
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.warn('Browser tidak mendukung Web Speech Recognition.');
    return;
  }

  state.recognition = new SpeechRecognition();
  state.recognition.lang = 'id-ID';
  state.recognition.continuous = true;
  state.recognition.interimResults = true;

  state.recognition.onstart = () => {
    state.isListening = true;
    elements.speechRecBtnText.innerText = 'Mendengarkan... (Klik untuk Berhenti)';
    elements.btnToggleSpeechRec.classList.replace('bg-blue-600', 'bg-red-600');
    elements.btnToggleSpeechRec.classList.replace('hover:bg-blue-500', 'hover:bg-red-500');
  };

  state.recognition.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }

    elements.speechTranscriptOutput.innerText = transcript || 'Sedang mendengarkan...';

    // Highlight recognized BISINDO vocabulary tags
    const words = transcript.toLowerCase().split(/\s+/);
    elements.speechDetectedTags.innerHTML = '';

    const recognizedInDict = new Set();
    words.forEach((w) => {
      const cleanWord = w.replace(/[^\w\s]/gi, '');
      if (state.labelsKosakata.includes(cleanWord)) {
        recognizedInDict.add(cleanWord);
      }
    });

    if (recognizedInDict.size > 0) {
      recognizedInDict.forEach((item) => {
        const tag = document.createElement('span');
        tag.className = 'px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        tag.innerText = `🤟 Isyarat: ${item}`;
        elements.speechDetectedTags.appendChild(tag);
      });
    }
  };

  state.recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    stopSpeechRecognition();
  };

  state.recognition.onend = () => {
    state.isListening = false;
    elements.speechRecBtnText.innerText = 'Mulai Mendengarkan';
    elements.btnToggleSpeechRec.classList.replace('bg-red-600', 'bg-blue-600');
    elements.btnToggleSpeechRec.classList.replace('hover:bg-red-500', 'hover:bg-blue-500');
  };
}

function startSpeechRecognition() {
  if (state.recognition && !state.isListening) {
    try {
      state.recognition.start();
    } catch (e) {
      console.warn(e);
    }
  }
}

function stopSpeechRecognition() {
  if (state.recognition && state.isListening) {
    state.recognition.stop();
  }
}

// --- 8. Dictionary Population & Search ---
function populateDictionary() {
  // 38 Kosakata
  elements.dictKataGrid.innerHTML = '';
  state.labelsKosakata.forEach((kata) => {
    const card = document.createElement('div');
    card.className = 'dict-card-kata p-3 rounded-xl bg-gray-950 border border-gray-800 hover:border-brand-500/50 transition-all flex flex-col justify-between';
    card.setAttribute('data-name', kata.toLowerCase());
    card.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <span class="font-bold text-sm text-brand-400">${kata}</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-400">Kata</span>
      </div>
      <p class="text-[11px] text-gray-500">2 Tangan / Gestur BISINDO</p>
    `;
    elements.dictKataGrid.appendChild(card);
  });

  // 26 Abjad
  elements.dictAbjadGrid.innerHTML = '';
  state.labelsAbjad.forEach((huruf) => {
    const card = document.createElement('div');
    card.className = 'dict-card-abjad p-3 rounded-xl bg-gray-950 border border-gray-800 hover:border-purple-500/50 transition-all flex flex-col items-center justify-center text-center';
    card.setAttribute('data-name', huruf.toLowerCase());
    card.innerHTML = `
      <span class="text-xl font-black text-purple-400 mb-0.5">${huruf}</span>
      <span class="text-[10px] text-gray-500">Huruf</span>
    `;
    elements.dictAbjadGrid.appendChild(card);
  });
}

function filterDictionary(query) {
  const q = query.toLowerCase().trim();

  // Filter Kata
  const kataCards = document.querySelectorAll('.dict-card-kata');
  kataCards.forEach((c) => {
    const name = c.getAttribute('data-name');
    c.classList.toggle('hidden', !name.includes(q));
  });

  // Filter Abjad
  const abjadCards = document.querySelectorAll('.dict-card-abjad');
  abjadCards.forEach((c) => {
    const name = c.getAttribute('data-name');
    c.classList.toggle('hidden', !name.includes(q));
  });
}

// --- 9. Camera Controls ---
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

// --- 10. UI Mode Switcher ---
function setMode(mode) {
  state.isModeAbjad = (mode === 'abjad');

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

  state.history = [];
  state.lastIndex = null;
  state.pendingWord = '';
  elements.predictionHoldBar.style.width = '0%';
}

// --- 11. Event Listeners ---
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

  // NLP Grammar Smoothing Button
  elements.btnNlpSmooth.addEventListener('click', () => {
    const rawText = getDisplayText();
    if (!rawText.trim()) return;

    const polished = smoothSentenceNLP(rawText);
    elements.translationOutput.innerText = polished;
    elements.btnNlpSmooth.classList.add('bg-brand-500/30');
    setTimeout(() => {
      elements.btnNlpSmooth.classList.remove('bg-brand-500/30');
    }, 1000);
  });

  // Download TXT Button
  elements.btnDownloadTxt.addEventListener('click', () => {
    const text = getDisplayText();
    if (!text.trim()) return;

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `terjemahan-bisindo-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // TTS buttons
  elements.btnSpeakSentence.addEventListener('click', () => {
    speakText(getDisplayText());
  });

  elements.toggleAutoSpeak.addEventListener('change', (e) => {
    state.autoSpeak = e.target.checked;
  });

  // --- Modal 1: Dictionary Event Listeners ---
  elements.btnOpenDictionary.addEventListener('click', () => {
    elements.modalDictionary.classList.remove('hidden');
  });
  elements.btnCloseDictionary.addEventListener('click', () => {
    elements.modalDictionary.classList.add('hidden');
  });
  elements.tabDictKata.addEventListener('click', () => {
    elements.dictKataGrid.classList.remove('hidden');
    elements.dictAbjadGrid.classList.add('hidden');
    elements.tabDictKata.className = 'px-3 py-1.5 rounded-md text-xs font-semibold bg-brand-600 text-white transition-all';
    elements.tabDictAbjad.className = 'px-3 py-1.5 rounded-md text-xs font-semibold text-gray-400 hover:text-white transition-all';
  });
  elements.tabDictAbjad.addEventListener('click', () => {
    elements.dictKataGrid.classList.add('hidden');
    elements.dictAbjadGrid.classList.remove('hidden');
    elements.tabDictAbjad.className = 'px-3 py-1.5 rounded-md text-xs font-semibold bg-purple-600 text-white transition-all';
    elements.tabDictKata.className = 'px-3 py-1.5 rounded-md text-xs font-semibold text-gray-400 hover:text-white transition-all';
  });
  elements.dictSearchInput.addEventListener('input', (e) => {
    filterDictionary(e.target.value);
  });

  // --- Modal 2: Hearing Event Listeners ---
  elements.btnOpenHearingModal.addEventListener('click', () => {
    elements.modalHearing.classList.remove('hidden');
  });
  elements.btnCloseHearing.addEventListener('click', () => {
    elements.modalHearing.classList.add('hidden');
    stopSpeechRecognition();
  });
  elements.btnToggleSpeechRec.addEventListener('click', () => {
    if (state.isListening) {
      stopSpeechRecognition();
    } else {
      startSpeechRecognition();
    }
  });

  // --- Modal 3: Settings Event Listeners ---
  elements.btnOpenSettings.addEventListener('click', () => {
    elements.modalSettings.classList.remove('hidden');
  });
  elements.btnCloseSettings.addEventListener('click', () => {
    elements.modalSettings.classList.add('hidden');
  });
  elements.sliderThresholdKata.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    state.thresholdKata = val / 100;
    elements.sliderThresholdKataVal.innerText = `${val}%`;
  });
  elements.sliderThresholdAbjad.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    state.thresholdAbjad = val / 100;
    elements.sliderThresholdAbjadVal.innerText = `${val}%`;
  });
  elements.sliderHoldTime.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    state.holdDuration = val;
    elements.sliderHoldTimeVal.innerText = `${(val / 1000).toFixed(1)} detik`;
  });
  elements.btnResetSettings.addEventListener('click', () => {
    state.thresholdKata = 0.75;
    state.thresholdAbjad = 0.85;
    state.holdDuration = 600;
    elements.sliderThresholdKata.value = 75;
    elements.sliderThresholdKataVal.innerText = '75%';
    elements.sliderThresholdAbjad.value = 85;
    elements.sliderThresholdAbjadVal.innerText = '85%';
    elements.sliderHoldTime.value = 600;
    elements.sliderHoldTimeVal.innerText = '0.6 detik';
  });
}

// --- PWA Service Worker Registration ---
function setupPWA() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').then((reg) => {
        console.log('[PWA] Service Worker registered:', reg.scope);
      }).catch((err) => {
        console.warn('[PWA] Service Worker notice:', err);
      });
    });
  }
}

// --- Initialization ---
window.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }

  setupEventListeners();
  setupSpeechRecognition();
  setupMediaPipe();
  setupPWA();
  await loadModels();
});
