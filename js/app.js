/**
 * BISINDO Translator - Client-side AI Web Application
 * Optimized for High FPS (60 FPS), 3D Animated Hand Skeleton Dictionary,
 * Two-Way Speech Recognition, and PWA
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

// MediaPipe standard 21-hand landmark connections
const HAND_CONNECTIONS_MAP = [
  // Thumb
  [0, 1], [1, 2], [2, 3], [3, 4],
  // Index
  [0, 5], [5, 6], [6, 7], [7, 8],
  // Middle
  [5, 9], [9, 10], [10, 11], [11, 12],
  // Ring
  [9, 13], [13, 14], [14, 15], [15, 16],
  // Pinky
  [13, 17], [17, 18], [18, 19], [19, 20],
  // Palm Base
  [0, 17]
];

// --- Global Application State ---
const state = {
  // Models and Labels
  modelAbjad: null,
  modelKosakata: null,
  labelsAbjad: [],
  labelsKosakata: [],
  landmarksDictionary: null,
  modelsReady: false,

  // Camera & MediaPipe
  camera: null,
  hands: null,
  isCameraRunning: false,
  facingMode: 'user',

  // High FPS & Non-blocking Inference Loop
  isPredicting: false,
  lastPredictionTime: 0,
  predictionInterval: 75, // ms (at most 13 predictions/sec; leaves 60 FPS for camera render)

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
  fps: 0,
  frameCount: 0,
  fpsTimer: performance.now(),

  // Active Detail Gesture Modal Animation
  activeDetailGesture: null,
  detailAnimFrameId: null,
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

  // Modal 1B: Detail Gesture 3D Viewer
  modalGestureDetail: document.getElementById('modal-gesture-detail'),
  btnCloseGestureDetail: document.getElementById('btn-close-gesture-detail'),
  detailGestureCanvas: document.getElementById('detail-gesture-canvas'),
  detailGestureTitle: document.getElementById('detail-gesture-title'),
  detailGestureDesc: document.getElementById('detail-gesture-desc'),
  detailGestureTypeBadge: document.getElementById('detail-gesture-type-badge'),
  detailGestureHandsBadge: document.getElementById('detail-gesture-hands-badge'),
  btnPracticeInCamera: document.getElementById('btn-practice-in-camera'),

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

const canvasCtx = elements.canvas.getContext('2d', { alpha: false, desynchronized: true });
const detailCanvasCtx = elements.detailGestureCanvas.getContext('2d');

// --- 1. Model & Landmarks Loading ---
async function loadModels() {
  try {
    updateSystemStatus('loading', 'Memuat Model AI & Visual...');

    // Optimize TensorFlow.js GPU settings for speed
    await tf.ready();
    if (tf.getBackend() === 'webgl') {
      tf.env().set('WEBGL_PACK', true);
      tf.env().set('WEBGL_PACK_BINARY_OPERATIONS', true);
    }
    console.log(`TensorFlow.js backend aktif: ${tf.getBackend()}`);

    // Load labels and landmark dictionary in parallel
    const [resAbjad, resKosa, resDict] = await Promise.all([
      fetch('./models/web/labels_abjad.json'),
      fetch('./models/web/labels_kosakata.json'),
      fetch('./models/web/landmarks_dictionary.json')
    ]);

    if (!resAbjad.ok || !resKosa.ok || !resDict.ok) {
      throw new Error('Gagal mengambil file model atau kamus visual.');
    }

    state.labelsAbjad = await resAbjad.json();
    state.labelsKosakata = await resKosa.json();
    state.landmarksDictionary = await resDict.json();

    // Populate Visual Dictionary
    populateVisualDictionary();

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

    console.log('Semua model AI, label, dan data visual tangan berhasil dimuat!');
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
  const keypoints = new Float32Array(126);

  if (multiHandLandmarks && multiHandLandmarks.length > 0) {
    const numHands = Math.min(2, multiHandLandmarks.length);

    for (let i = 0; i < numHands; i++) {
      const handLandmarks = multiHandLandmarks[i];
      const wrist = handLandmarks[0];
      const startIdx = i * 63;

      for (let j = 0; j < 21; j++) {
        const lm = handLandmarks[j];
        keypoints[startIdx + j * 3]     = lm.x - wrist.x;
        keypoints[startIdx + j * 3 + 1] = lm.y - wrist.y;
        keypoints[startIdx + j * 3 + 2] = lm.z - wrist.z;
      }
    }
  }

  return keypoints;
}

// --- 3. MediaPipe Hands Setup (Optimized for High FPS) ---
function setupMediaPipe() {
  state.hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  // CRUCIAL FOR 60 FPS: modelComplexity: 0 (Lite model is 4x faster and smoother!)
  state.hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 0,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  });

  state.hands.onResults(onHandResults);
}

// --- 4. High-FPS Rendering & Decoupled Inference Loop ---
function onHandResults(results) {
  // 1. Calculate FPS
  state.frameCount++;
  const now = performance.now();
  if (now - state.fpsTimer >= 1000) {
    state.fps = Math.round((state.frameCount * 1000) / (now - state.fpsTimer));
    elements.badgeFps.innerText = `${state.fps} FPS`;
    state.frameCount = 0;
    state.fpsTimer = now;
  }

  // 2. Adjust Canvas Dimensions if changed
  if (elements.canvas.width !== elements.webcam.videoWidth && elements.webcam.videoWidth > 0) {
    elements.canvas.width = elements.webcam.videoWidth;
    elements.canvas.height = elements.webcam.videoHeight;
  }

  // 3. Render Camera Frame Immediately (60 FPS without waiting for AI inference)
  canvasCtx.drawImage(results.image, 0, 0, elements.canvas.width, elements.canvas.height);

  const numHands = results.multiHandLandmarks ? results.multiHandLandmarks.length : 0;
  elements.handsCountText.innerText = `${numHands} Tangan`;

  // 4. Draw Hand Landmarks Skeleton
  if (numHands > 0) {
    for (let h = 0; h < results.multiHandLandmarks.length; h++) {
      const landmarks = results.multiHandLandmarks[h];
      const isSecondHand = (h === 1);
      drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
        color: isSecondHand ? '#818cf8' : '#10b981',
        lineWidth: 3
      });
      drawLandmarks(canvasCtx, landmarks, {
        color: isSecondHand ? '#c084fc' : '#34d399',
        lineWidth: 1,
        radius: 4
      });
    }

    // 5. Throttled Non-blocking Async Inference (Leaves 60 FPS for camera rendering)
    if (state.modelsReady && !state.isPredicting && (now - state.lastPredictionTime >= state.predictionInterval)) {
      state.isPredicting = true;
      state.lastPredictionTime = now;
      predictGesturesAsync(results.multiHandLandmarks);
    }
  } else {
    state.pendingWord = '';
    elements.predictionHoldBar.style.width = '0%';
    elements.currentDetectionLabel.innerText = '-';
    elements.currentConfidenceLabel.innerText = '(0%)';
  }
}

// Asynchronous Prediction (does not block camera render loop)
async function predictGesturesAsync(multiHandLandmarks) {
  try {
    const keypoints = processLandmarks(multiHandLandmarks);

    const activeModel = state.isModeAbjad ? state.modelAbjad : state.modelKosakata;
    const activeLabels = state.isModeAbjad ? state.labelsAbjad : state.labelsKosakata;
    const threshold = state.isModeAbjad ? state.thresholdAbjad : state.thresholdKata;
    const currentType = state.isModeAbjad ? 'abjad' : 'kata';

    const inputTensor = tf.tensor2d(keypoints, [1, 126]);
    const predictionTensor = activeModel.predict(inputTensor);
    const probabilities = await predictionTensor.data();

    inputTensor.dispose();
    predictionTensor.dispose();

    // Find Argmax
    let maxIndex = 0;
    let maxConf = 0;
    for (let i = 0; i < probabilities.length; i++) {
      if (probabilities[i] > maxConf) {
        maxConf = probabilities[i];
        maxIndex = i;
      }
    }

    const detectedWord = activeLabels[maxIndex];

    // Smoothing & Debounce Decision Logic (faithful to app.py)
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

    // Debounce Timer & Appending
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

    // Update UI Labels
    if (detectedWord && maxConf > 0.3) {
      elements.currentDetectionLabel.innerText = detectedWord;
      elements.currentConfidenceLabel.innerText = `(${Math.round(maxConf * 100)}%)`;
    } else {
      elements.currentDetectionLabel.innerText = '-';
      elements.currentConfidenceLabel.innerText = '(0%)';
    }

  } catch (err) {
    console.warn('Inference error:', err);
  } finally {
    state.isPredicting = false;
  }
}

// --- 5. Holographic Vector Hand Skeleton Renderer ---
function drawHandSkeleton(ctx, hand1Coords, hand2Coords, width, height, time = 0, options = {}) {
  ctx.clearRect(0, 0, width, height);

  // Subtle dark gradient background
  const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 10, width / 2, height / 2, width * 0.7);
  bgGrad.addColorStop(0, '#0f172a');
  bgGrad.addColorStop(1, '#020617');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, width, height);

  const hasTwoHands = Boolean(hand2Coords && hand2Coords.length === 21);
  const scale = (options.scale || 1.6) * Math.min(width, height);

  // Gentle 3D perspective rotation angle
  const animAngle = options.animate ? Math.sin(time * 0.002) * 0.22 : (options.angle || 0);

  // Draw Hand 1 (Primary - Emerald)
  if (hand1Coords && hand1Coords.length === 21) {
    const cx1 = hasTwoHands ? width * 0.32 : width * 0.5;
    const cy1 = height * 0.78;
    renderSingleHand(ctx, hand1Coords, cx1, cy1, scale, animAngle, '#10b981', '#34d399');
  }

  // Draw Hand 2 (Secondary - Indigo/Purple)
  if (hasTwoHands) {
    const cx2 = width * 0.68;
    const cy2 = height * 0.78;
    renderSingleHand(ctx, hand2Coords, cx2, cy2, scale, -animAngle, '#818cf8', '#a78bfa');
  }
}

function renderSingleHand(ctx, points, cx, cy, scale, angle, primaryColor, jointColor) {
  const projected = [];
  const cosA = Math.cos(angle);
  const sinA = Math.sin(angle);

  // Project 3D points
  for (let i = 0; i < 21; i++) {
    const [dx, dy, dz] = points[i];
    const rotX = dx * cosA - dz * sinA;
    const rotZ = dx * sinA + dz * cosA;
    const persp = 1 / (1 - rotZ * 0.6);

    const px = cx + rotX * scale * persp;
    const py = cy + dy * scale * persp; // dy is negative upwards
    projected.push({ x: px, y: py });
  }

  // Draw glowing bones
  ctx.save();
  ctx.shadowColor = primaryColor;
  ctx.shadowBlur = 8;
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = primaryColor;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  ctx.beginPath();
  for (const [i, j] of HAND_CONNECTIONS_MAP) {
    ctx.moveTo(projected[i].x, projected[i].y);
    ctx.lineTo(projected[j].x, projected[j].y);
  }
  ctx.stroke();
  ctx.restore();

  // Draw joint nodes
  const fingerTips = new Set([4, 8, 12, 16, 20]);
  for (let i = 0; i < 21; i++) {
    const pt = projected[i];
    const isTip = fingerTips.has(i);

    ctx.save();
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, isTip ? 4 : 2.5, 0, Math.PI * 2);
    ctx.fillStyle = isTip ? '#ffffff' : jointColor;
    ctx.shadowColor = isTip ? '#ffffff' : jointColor;
    ctx.shadowBlur = isTip ? 10 : 4;
    ctx.fill();
    ctx.restore();
  }
}

// --- 6. Populate Visual Dictionary (with Skeleton Canvases) ---
function populateVisualDictionary() {
  if (!state.landmarksDictionary) return;

  const { abjad, kosakata } = state.landmarksDictionary;

  // 1. Populate 38 Kosakata
  elements.dictKataGrid.innerHTML = '';
  state.labelsKosakata.forEach((kata) => {
    const data = kosakata[kata];
    const card = document.createElement('div');
    card.className = 'dict-card-kata p-3 rounded-2xl bg-gray-900 border border-gray-800 hover:border-brand-500/60 hover:bg-gray-800/60 transition-all cursor-pointer flex flex-col items-center group shadow-md';
    card.setAttribute('data-name', kata.toLowerCase());

    const twoHandsBadge = data && data.twoHands
      ? `<span class="text-[9px] px-1.5 py-0.5 rounded font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">2 Tangan</span>`
      : `<span class="text-[9px] px-1.5 py-0.5 rounded font-semibold bg-brand-500/20 text-brand-400 border border-brand-500/30">1 Tangan</span>`;

    card.innerHTML = `
      <div class="w-full flex items-center justify-between mb-2">
        <span class="font-bold text-sm text-white group-hover:text-brand-400 transition-colors capitalize">${kata}</span>
        ${twoHandsBadge}
      </div>
      <div class="relative w-full aspect-[4/3] rounded-xl overflow-hidden bg-gray-950 border border-gray-800/80 mb-2 flex items-center justify-center">
        <canvas class="dict-thumb-canvas w-full h-full" width="160" height="120"></canvas>
      </div>
      <span class="text-[10px] text-gray-500 group-hover:text-gray-400 transition-colors">Klik untuk Pratinjau 3D</span>
    `;

    // Render thumbnail skeleton
    const thumbCanvas = card.querySelector('.dict-thumb-canvas');
    if (data && thumbCanvas) {
      const tctx = thumbCanvas.getContext('2d');
      drawHandSkeleton(tctx, data.hand1, data.hand2, 160, 120, 0, { animate: false, scale: 1.55 });
    }

    // Card click opens 3D Inspector Detail
    card.addEventListener('click', () => {
      openGestureDetail(data || { name: kata, type: 'kata', twoHands: false, hand1: null, hand2: null });
    });

    elements.dictKataGrid.appendChild(card);
  });

  // 2. Populate 26 Abjad (A-Z)
  elements.dictAbjadGrid.innerHTML = '';
  state.labelsAbjad.forEach((huruf) => {
    const data = abjad[huruf];
    const card = document.createElement('div');
    card.className = 'dict-card-abjad p-3 rounded-2xl bg-gray-900 border border-gray-800 hover:border-purple-500/60 hover:bg-gray-800/60 transition-all cursor-pointer flex flex-col items-center group shadow-md';
    card.setAttribute('data-name', huruf.toLowerCase());

    const twoHandsBadge = data && data.twoHands
      ? `<span class="text-[9px] px-1.5 py-0.5 rounded font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">2 Tangan</span>`
      : `<span class="text-[9px] px-1.5 py-0.5 rounded font-semibold bg-purple-500/20 text-purple-400 border border-purple-500/30">1 Tangan</span>`;

    card.innerHTML = `
      <div class="w-full flex items-center justify-between mb-2">
        <span class="font-extrabold text-lg text-purple-400 group-hover:text-purple-300 transition-colors">${huruf}</span>
        ${twoHandsBadge}
      </div>
      <div class="relative w-full aspect-[4/3] rounded-xl overflow-hidden bg-gray-950 border border-gray-800/80 mb-2 flex items-center justify-center">
        <canvas class="dict-thumb-canvas w-full h-full" width="160" height="120"></canvas>
      </div>
      <span class="text-[10px] text-gray-500 group-hover:text-gray-400 transition-colors">Pratinjau 3D</span>
    `;

    // Render thumbnail skeleton
    const thumbCanvas = card.querySelector('.dict-thumb-canvas');
    if (data && thumbCanvas) {
      const tctx = thumbCanvas.getContext('2d');
      drawHandSkeleton(tctx, data.hand1, data.hand2, 160, 120, 0, { animate: false, scale: 1.55 });
    }

    card.addEventListener('click', () => {
      openGestureDetail(data || { name: huruf, type: 'abjad', twoHands: false, hand1: null, hand2: null });
    });

    elements.dictAbjadGrid.appendChild(card);
  });
}

function filterDictionary(query) {
  const q = query.toLowerCase().trim();

  document.querySelectorAll('.dict-card-kata').forEach((c) => {
    c.classList.toggle('hidden', !c.getAttribute('data-name').includes(q));
  });

  document.querySelectorAll('.dict-card-abjad').forEach((c) => {
    c.classList.toggle('hidden', !c.getAttribute('data-name').includes(q));
  });
}

// --- 7. Gesture Detail 3D Hologram Modal Animation ---
function openGestureDetail(gestureData) {
  state.activeDetailGesture = gestureData;

  elements.detailGestureTitle.innerText = gestureData.name;
  elements.detailGestureTypeBadge.innerText = gestureData.type === 'abjad' ? 'Huruf Abjad' : 'Kosakata Kata';
  elements.detailGestureHandsBadge.innerText = gestureData.twoHands ? '2 Tangan (Kedua Tangan)' : '1 Tangan (Tangan Utama)';

  elements.detailGestureDesc.innerText = gestureData.twoHands
    ? `Isyarat "${gestureData.name}" menggunakan kedua tangan. Posisikan kedua tangan Anda sejajar di depan kamera dan tahan gerakan selama 0.6 detik.`
    : `Isyarat "${gestureData.name}" menggunakan satu tangan utama. Angkat tangan Anda di depan kamera dengan formasi jari sesuai visualisasi 3D di atas.`;

  elements.modalGestureDetail.classList.remove('hidden');

  // Start smooth 3D rotation animation loop for this gesture
  if (state.detailAnimFrameId) cancelAnimationFrame(state.detailAnimFrameId);

  function animateDetail(time) {
    if (!state.activeDetailGesture || elements.modalGestureDetail.classList.contains('hidden')) return;

    drawHandSkeleton(
      detailCanvasCtx,
      state.activeDetailGesture.hand1,
      state.activeDetailGesture.hand2,
      280,
      230,
      time,
      { animate: true, scale: 1.6 }
    );

    state.detailAnimFrameId = requestAnimationFrame(animateDetail);
  }

  state.detailAnimFrameId = requestAnimationFrame(animateDetail);
}

function closeGestureDetail() {
  elements.modalGestureDetail.classList.add('hidden');
  state.activeDetailGesture = null;
  if (state.detailAnimFrameId) {
    cancelAnimationFrame(state.detailAnimFrameId);
    state.detailAnimFrameId = null;
  }
}

// --- 8. Sentence Builder & NLP Grammar Smoothing ---
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
          displayText += word;
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

function smoothSentenceNLP(rawText) {
  if (!rawText || !rawText.trim()) return '';

  let text = rawText.trim().replace(/\s+/g, ' ');
  text = text.replace(/(^\w|\.\s+\w)/g, (c) => c.toUpperCase());

  if (!/[.!?]$/.test(text)) {
    text += '.';
  }

  return text;
}

// --- 9. Text-to-Speech (Web Speech API) ---
function speakText(text) {
  if (!text || !text.trim()) return;

  if (!('speechSynthesis' in window)) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text.trim());
  utterance.lang = 'id-ID';

  const voices = window.speechSynthesis.getVoices();
  const idVoice = voices.find(v => v.lang.startsWith('id') || v.lang.includes('ID'));
  if (idVoice) utterance.voice = idVoice;

  utterance.rate = 1.0;
  window.speechSynthesis.speak(utterance);
}

if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
  };
}

// --- 10. Two-Way Speech Recognition ---
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

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

// --- 11. Camera Controls (Optimized Constraints for 60 FPS) ---
async function startCamera() {
  if (state.isCameraRunning) return;

  try {
    elements.btnToggleCamText.innerText = 'Menyalakan...';

    const constraints = {
      video: {
        facingMode: state.facingMode,
        width: { ideal: 640, max: 640 },
        height: { ideal: 480, max: 480 },
        frameRate: { ideal: 30, max: 60 }
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

// --- 12. UI Mode Switcher ---
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

// --- 13. Event Listeners Setup ---
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
    elements.tabDictKata.className = 'px-3.5 py-1.5 rounded-md text-xs font-semibold bg-brand-600 text-white transition-all shadow-sm';
    elements.tabDictAbjad.className = 'px-3.5 py-1.5 rounded-md text-xs font-semibold text-gray-400 hover:text-white transition-all';
  });
  elements.tabDictAbjad.addEventListener('click', () => {
    elements.dictKataGrid.classList.add('hidden');
    elements.dictAbjadGrid.classList.remove('hidden');
    elements.tabDictAbjad.className = 'px-3.5 py-1.5 rounded-md text-xs font-semibold bg-purple-600 text-white transition-all shadow-sm';
    elements.tabDictKata.className = 'px-3.5 py-1.5 rounded-md text-xs font-semibold text-gray-400 hover:text-white transition-all';
  });
  elements.dictSearchInput.addEventListener('input', (e) => {
    filterDictionary(e.target.value);
  });

  // Modal 1B: Detail 3D Gesture Events
  elements.btnCloseGestureDetail.addEventListener('click', closeGestureDetail);
  elements.btnPracticeInCamera.addEventListener('click', () => {
    if (state.activeDetailGesture) {
      if (state.activeDetailGesture.type === 'abjad') {
        elements.radioModeAbjad.checked = true;
        setMode('abjad');
      } else {
        elements.radioModeKata.checked = true;
        setMode('kata');
      }
    }
    closeGestureDetail();
    elements.modalDictionary.classList.add('hidden');
    if (!state.isCameraRunning) {
      startCamera();
    }
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
