/**
 * ПББ (Информатика) Ресми Симуляторы
 * Негізгі Басқару Скрипті
 */

// Official 12 topics specification
const TOPIC_SPECS = [
  { id: "info_processes", name: "Ақпаратты ұсыну және өлшеу. Ақпараттық процестер", count: 5 },
  { id: "computer_systems", name: "Компьютерлік жүйелер", count: 4 },
  { id: "logic_operations", name: "Логикалық операциялар", count: 2 },
  { id: "networks_security", name: "Компьютерлік желілер және қауіпсіздік", count: 6 },
  { id: "computer_graphics", name: "Компьютерлік графика", count: 2 },
  { id: "spreadsheets", name: "Есептерді электронды кестелердің көмегімен шешу, өңдеу", count: 4 },
  { id: "databases", name: "Мәліметтер қорымен жұмыс", count: 4 },
  { id: "programming_ide", name: "Программаларды құрудың кіріктірілген орталары", count: 7 },
  { id: "web_design", name: "Вебжобалау", count: 4 },
  { id: "text_multimedia", name: "Мәтіндік құжатпен жұмыс. Бейнеконтент", count: 1 },
  { id: "ai", name: "Жасанды интеллект", count: 1 },
  { id: "context", name: "Мәнмәтіндік тапсырмалар (Контекст)", count: 10 }
];

// App State
const AppState = {
  allQuestions: [],
  customQuestions: [],
  currentExam: {
    questions: [],
    userAnswers: {}, // { qIndex: selectedOptionIndex }
    flags: {}, // { qIndex: true/false }
    currentIndex: 0,
    timeLimitSeconds: 100 * 60, // 100 minutes default
    remainingSeconds: 100 * 60,
    timerId: null,
    isPaused: false,
    startTime: null,
    endTime: null
  },
  lastResult: null,
  history: []
};

// Initialize App
document.addEventListener("DOMContentLoaded", async () => {
  loadCustomQuestions();
  loadHistory();
  await loadDatabase();
  setupEventListeners();
  renderHome();
  renderHistoryTable();
  renderBankTopicsFilter();
  lucide.createIcons();
});

// Load Database
async function loadDatabase() {
  try {
    if (window.PBB_DATABASE && window.PBB_DATABASE.questions) {
      AppState.allQuestions = [...window.PBB_DATABASE.questions, ...AppState.customQuestions];
    } else {
      const resp = await fetch('data/questions.json');
      const data = await resp.json();
      AppState.allQuestions = [...data.questions, ...AppState.customQuestions];
    }
  } catch (err) {
    console.warn("Could not load from json fetch, using embedded fallback:", err);
    if (window.PBB_DATABASE) {
      AppState.allQuestions = [...window.PBB_DATABASE.questions, ...AppState.customQuestions];
    }
  }
  updateStatsBadge();
}

// Custom Questions & LocalStorage
function loadCustomQuestions() {
  const saved = localStorage.getItem('pbb_custom_questions');
  if (saved) {
    try {
      AppState.customQuestions = JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }
  }
}

function saveCustomQuestions() {
  localStorage.setItem('pbb_custom_questions', JSON.stringify(AppState.customQuestions));
  AppState.allQuestions = [...(window.PBB_DATABASE ? window.PBB_DATABASE.questions : []), ...AppState.customQuestions];
  updateStatsBadge();
}

function loadHistory() {
  const saved = localStorage.getItem('pbb_exam_history');
  if (saved) {
    try {
      AppState.history = JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }
  }
}

function saveHistory(result) {
  AppState.history.unshift(result);
  if (AppState.history.length > 50) AppState.history.pop();
  localStorage.setItem('pbb_exam_history', JSON.stringify(AppState.history));
  renderHistoryTable();
}

function updateStatsBadge() {
  const totalEl = document.getElementById("statTotalQuestions");
  if (totalEl) totalEl.textContent = AppState.allQuestions.length;
}

// Navigation between views
function showView(viewId) {
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.add("hidden"));
  const target = document.getElementById(viewId);
  if (target) {
    target.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  lucide.createIcons();
}

// Setup Event Listeners
function setupEventListeners() {
  // Navigation Links
  document.querySelectorAll("[data-nav]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const navTarget = btn.getAttribute("data-nav");
      
      // Prevent leaving active exam without confirmation
      if (AppState.currentExam.timerId && navTarget !== 'viewExam') {
        if (!confirm("Тестілеу әлі жүріп жатыр. Тестті тоқтатқыңыз келе ме?")) {
          return;
        }
        clearInterval(AppState.currentExam.timerId);
        AppState.currentExam.timerId = null;
      }
      showView(navTarget);
      if (navTarget === 'viewBank') renderBankList();
      if (navTarget === 'viewHistory') renderHistoryTable();
    });
  });

  // Start Exam Button
  const btnStart = document.getElementById("btnStartExam");
  if (btnStart) {
    btnStart.addEventListener("click", () => {
      const timeSelect = document.getElementById("examTimeSelect");
      const minutes = parseInt(timeSelect ? timeSelect.value : "100", 10);
      startNewExam(minutes);
    });
  }

  // Keyboard navigation for exam
  window.addEventListener("keydown", (e) => {
    const examView = document.getElementById("viewExam");
    if (examView && !examView.classList.contains("hidden")) {
      // 1, 2, 3, 4 or A, B, C, D
      const key = e.key.toUpperCase();
      if (['1', 'A'].includes(key)) selectOption(0);
      else if (['2', 'B'].includes(key)) selectOption(1);
      else if (['3', 'C'].includes(key)) selectOption(2);
      else if (['4', 'D'].includes(key)) selectOption(3);
      else if (e.key === 'ArrowRight') nextQuestion();
      else if (e.key === 'ArrowLeft') prevQuestion();
      else if (e.key === 'f' || e.key === 'F' || e.key === 'а' || e.key === 'А') toggleFlag();
    }
  });

  // Finish exam button
  const btnFinish = document.getElementById("btnFinishExam");
  if (btnFinish) {
    btnFinish.addEventListener("click", openFinishModal);
  }

  // Confirm Finish in Modal
  const btnConfirmFinish = document.getElementById("btnConfirmFinish");
  if (btnConfirmFinish) {
    btnConfirmFinish.addEventListener("click", () => {
      closeFinishModal();
      finishExam();
    });
  }

  // Cancel Finish in Modal
  const btnCancelFinish = document.getElementById("btnCancelFinish");
  if (btnCancelFinish) {
    btnCancelFinish.addEventListener("click", closeFinishModal);
  }

  // Add Question Modal triggers
  const btnOpenAddModal = document.getElementById("btnOpenAddQuestion");
  if (btnOpenAddModal) {
    btnOpenAddModal.addEventListener("click", () => {
      document.getElementById("modalAddQuestion").classList.remove("hidden");
    });
  }

  const btnCloseAddModal = document.getElementById("btnCloseAddQuestion");
  if (btnCloseAddModal) {
    btnCloseAddModal.addEventListener("click", () => {
      document.getElementById("modalAddQuestion").classList.add("hidden");
    });
  }

  // Save new question form
  const formAddQuestion = document.getElementById("formAddQuestion");
  if (formAddQuestion) {
    formAddQuestion.addEventListener("submit", handleAddQuestionSubmit);
  }

  // Search and filter in Bank
  const bankSearch = document.getElementById("bankSearchInput");
  if (bankSearch) {
    bankSearch.addEventListener("input", renderBankList);
  }
  const bankFilter = document.getElementById("bankTopicFilter");
  if (bankFilter) {
    bankFilter.addEventListener("change", renderBankList);
  }

  // Export JSON
  const btnExport = document.getElementById("btnExportQuestions");
  if (btnExport) {
    btnExport.addEventListener("click", exportQuestionsJSON);
  }

  // Import JSON
  const btnImport = document.getElementById("btnImportQuestions");
  const fileImport = document.getElementById("fileImportJSON");
  if (btnImport && fileImport) {
    btnImport.addEventListener("click", () => fileImport.click());
    fileImport.addEventListener("change", handleImportJSON);
  }
}

// EXAM GENERATION ENGINE (50 Questions strict PBB formula)
function startNewExam(timeLimitMinutes = 100) {
  const examQuestions = [];

  // 1. For topics 1-11, randomly pick the exact target count
  for (const topic of TOPIC_SPECS) {
    if (topic.id === "context") continue;
    const pool = AppState.allQuestions.filter(q => q.topicId === topic.id);
    const shuffled = [...pool].sort(() => 0.5 - Math.random());
    const count = Math.min(topic.count, shuffled.length);
    examQuestions.push(...shuffled.slice(0, count));
  }

  // 2. For Topic 12 (Context): select 2 unique context scenarios (5 questions each = 10 questions)
  const contextPool = AppState.allQuestions.filter(q => q.topicId === "context");
  
  // Group by contextId
  const contextGroups = {};
  for (const q of contextPool) {
    const cid = q.contextId || "generic_ctx";
    if (!contextGroups[cid]) contextGroups[cid] = [];
    contextGroups[cid].push(q);
  }

  const contextIds = Object.keys(contextGroups).sort(() => 0.5 - Math.random());
  let pickedContextQuestions = [];

  for (const cid of contextIds) {
    if (pickedContextQuestions.length >= 10) break;
    const qs = contextGroups[cid];
    pickedContextQuestions.push(...qs.slice(0, 5));
  }

  // Fallback if less than 10 context questions
  if (pickedContextQuestions.length < 10) {
    const remaining = 10 - pickedContextQuestions.length;
    const extra = contextPool.filter(q => !pickedContextQuestions.includes(q)).slice(0, remaining);
    pickedContextQuestions.push(...extra);
  }

  examQuestions.push(...pickedContextQuestions.slice(0, 10));

  // Initialize Exam State
  AppState.currentExam = {
    questions: examQuestions,
    userAnswers: {},
    flags: {},
    currentIndex: 0,
    timeLimitSeconds: timeLimitMinutes * 60,
    remainingSeconds: timeLimitMinutes * 60,
    timerId: null,
    isPaused: false,
    startTime: new Date(),
    endTime: null
  };

  // Start Countdown Timer
  startTimer();

  // Render Exam View
  showView("viewExam");
  renderExamQuestion(0);
  renderExamGrid();
}

// Timer Functions
function startTimer() {
  if (AppState.currentExam.timerId) clearInterval(AppState.currentExam.timerId);
  
  updateTimerUI();
  
  AppState.currentExam.timerId = setInterval(() => {
    if (AppState.currentExam.isPaused) return;

    AppState.currentExam.remainingSeconds--;
    updateTimerUI();

    if (AppState.currentExam.remainingSeconds <= 0) {
      clearInterval(AppState.currentExam.timerId);
      AppState.currentExam.timerId = null;
      alert("Уақыт аяқталды! Тест автоматты түрде аяқталады.");
      finishExam();
    }
  }, 1000);
}

function updateTimerUI() {
  const timerEl = document.getElementById("examTimerDisplay");
  if (!timerEl) return;

  const totalSecs = Math.max(0, AppState.currentExam.remainingSeconds);
  const mins = Math.floor(totalSecs / 60);
  const secs = totalSecs % 60;
  timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

  if (totalSecs < 300) { // < 5 mins
    timerEl.classList.add("timer-urgent");
  } else {
    timerEl.classList.remove("timer-urgent");
  }
}

// Render Current Exam Question
function renderExamQuestion(index) {
  AppState.currentExam.currentIndex = index;
  const q = AppState.currentExam.questions[index];
  if (!q) return;

  // Header indicators
  document.getElementById("currentQNum").textContent = index + 1;
  document.getElementById("totalQCount").textContent = AppState.currentExam.questions.length;
  document.getElementById("currentTopicBadge").textContent = q.topicName || "Информатика";

  // Flag button state
  const isFlagged = !!AppState.currentExam.flags[index];
  const btnFlag = document.getElementById("btnToggleFlag");
  if (btnFlag) {
    if (isFlagged) {
      btnFlag.classList.add("bg-amber-50", "border-amber-400", "text-amber-800");
      btnFlag.innerHTML = `<i data-lucide="bookmark-check" class="w-4 h-4 text-amber-600"></i> Белгіленген`;
    } else {
      btnFlag.classList.remove("bg-amber-50", "border-amber-400", "text-amber-800");
      btnFlag.innerHTML = `<i data-lucide="bookmark" class="w-4 h-4 text-slate-500"></i> Күмәнді сұрақ`;
    }
  }

  // Context container
  const contextBox = document.getElementById("examContextContainer");
  if (q.contextText) {
    contextBox.classList.remove("hidden");
    document.getElementById("examContextTitle").textContent = q.contextTitle || "Мәнмәтіндік тапсырма";
    document.getElementById("examContextText").innerHTML = q.contextText.replace(/\n/g, '<br>');
  } else {
    contextBox.classList.add("hidden");
  }

  // Question Text
  const qTextEl = document.getElementById("examQuestionText");
  qTextEl.innerHTML = formatText(q.text);

  // Options
  const letters = ['A', 'B', 'C', 'D', 'E'];
  const optsContainer = document.getElementById("examOptionsContainer");
  optsContainer.innerHTML = "";

  const selectedIdx = AppState.currentExam.userAnswers[index];

  q.options.forEach((optText, optIdx) => {
    const isSelected = selectedIdx === optIdx;
    const card = document.createElement("div");
    card.className = `option-card p-4 rounded-xl flex items-start gap-3 ${isSelected ? 'selected' : ''}`;
    card.onclick = () => selectOption(optIdx);

    card.innerHTML = `
      <div class="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center font-bold text-sm border ${isSelected ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-slate-100 text-slate-700 border-slate-200'}">
        ${letters[optIdx]}
      </div>
      <div class="flex-grow pt-0.5 text-base font-medium text-slate-800 select-none">
        ${formatText(optText)}
      </div>
      <div class="flex-shrink-0 mt-0.5">
        <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center ${isSelected ? 'border-emerald-600 bg-emerald-600' : 'border-slate-300'}">
          ${isSelected ? '<div class="w-2 h-2 rounded-full bg-white"></div>' : ''}
        </div>
      </div>
    `;
    optsContainer.appendChild(card);
  });

  // Navigation button states
  const btnPrev = document.getElementById("btnPrevQ");
  const btnNext = document.getElementById("btnNextQ");
  if (btnPrev) btnPrev.disabled = index === 0;
  if (btnNext) {
    if (index === AppState.currentExam.questions.length - 1) {
      btnNext.innerHTML = `Аяқтау <i data-lucide="check-circle" class="w-4 h-4 ml-1"></i>`;
      btnNext.onclick = openFinishModal;
    } else {
      btnNext.innerHTML = `Келесі <i data-lucide="arrow-right" class="w-4 h-4 ml-1"></i>`;
      btnNext.onclick = nextQuestion;
    }
  }

  renderExamGrid();
  lucide.createIcons();
}

function formatText(str) {
  if (!str) return "";
  // format code blocks if any
  return str.replace(/`([^`]+)`/g, '<code class="bg-slate-100 text-slate-900 px-1.5 py-0.5 rounded font-mono text-sm border border-slate-200">$1</code>');
}

// Select an Option
function selectOption(optIdx) {
  const currentIdx = AppState.currentExam.currentIndex;
  AppState.currentExam.userAnswers[currentIdx] = optIdx;
  renderExamQuestion(currentIdx);
  renderExamGrid();
}

function clearOption() {
  const currentIdx = AppState.currentExam.currentIndex;
  delete AppState.currentExam.userAnswers[currentIdx];
  renderExamQuestion(currentIdx);
  renderExamGrid();
}

function nextQuestion() {
  if (AppState.currentExam.currentIndex < AppState.currentExam.questions.length - 1) {
    renderExamQuestion(AppState.currentExam.currentIndex + 1);
  }
}

function prevQuestion() {
  if (AppState.currentExam.currentIndex > 0) {
    renderExamQuestion(AppState.currentExam.currentIndex - 1);
  }
}

function toggleFlag() {
  const currentIdx = AppState.currentExam.currentIndex;
  AppState.currentExam.flags[currentIdx] = !AppState.currentExam.flags[currentIdx];
  renderExamQuestion(currentIdx);
  renderExamGrid();
}

// Render 1-50 Question Matrix Grid
function renderExamGrid() {
  const grid = document.getElementById("examGridContainer");
  if (!grid) return;
  grid.innerHTML = "";

  const total = AppState.currentExam.questions.length;
  let answeredCount = 0;

  for (let i = 0; i < total; i++) {
    const isAnswered = AppState.currentExam.userAnswers[i] !== undefined;
    const isCurrent = AppState.currentExam.currentIndex === i;
    const isFlagged = !!AppState.currentExam.flags[i];

    if (isAnswered) answeredCount++;

    const cell = document.createElement("div");
    cell.className = `grid-cell ${isAnswered ? 'answered' : ''} ${isCurrent ? 'active' : ''} ${isFlagged ? 'flagged' : ''}`;
    cell.textContent = i + 1;
    cell.onclick = () => renderExamQuestion(i);
    grid.appendChild(cell);
  }

  // Update counts
  const ansCountEl = document.getElementById("answeredCountDisplay");
  if (ansCountEl) ansCountEl.textContent = answeredCount;
  const remCountEl = document.getElementById("remainingCountDisplay");
  if (remCountEl) remCountEl.textContent = total - answeredCount;
}

// Finish Modal
function openFinishModal() {
  const modal = document.getElementById("modalFinishExam");
  if (!modal) return;

  const total = AppState.currentExam.questions.length;
  const answered = Object.keys(AppState.currentExam.userAnswers).length;
  const unanswered = total - answered;

  document.getElementById("modalAnsweredCount").textContent = answered;
  document.getElementById("modalUnansweredCount").textContent = unanswered;

  modal.classList.remove("hidden");
  lucide.createIcons();
}

function closeFinishModal() {
  const modal = document.getElementById("modalFinishExam");
  if (modal) modal.classList.add("hidden");
}

// FINISH EXAM & EVALUATE
function finishExam() {
  if (AppState.currentExam.timerId) {
    clearInterval(AppState.currentExam.timerId);
    AppState.currentExam.timerId = null;
  }

  AppState.currentExam.endTime = new Date();
  const timeSpentSecs = Math.round((AppState.currentExam.endTime - AppState.currentExam.startTime) / 1000);

  let totalScore = 0;
  const totalQuestions = AppState.currentExam.questions.length;
  const topicStats = {};

  TOPIC_SPECS.forEach(t => {
    topicStats[t.id] = { name: t.name, total: 0, correct: 0 };
  });

  const questionResults = [];

  AppState.currentExam.questions.forEach((q, idx) => {
    const userAns = AppState.currentExam.userAnswers[idx];
    const isCorrect = userAns === q.correctIndex;
    if (isCorrect) totalScore += 1;

    const tid = q.topicId || "info_processes";
    if (!topicStats[tid]) {
      topicStats[tid] = { name: q.topicName || tid, total: 0, correct: 0 };
    }
    topicStats[tid].total += 1;
    if (isCorrect) topicStats[tid].correct += 1;

    questionResults.push({
      question: q,
      userAnswer: userAns,
      isCorrect: isCorrect,
      explanation: q.explanation
    });
  });

  // Calculate Qualification Category (Official PBB thresholds)
  let category = "Табалдырықтан өтпеді";
  let badgeColor = "bg-rose-100 text-rose-800 border-rose-300";

  if (totalScore >= 45) {
    category = "Педагог-Шебер (90-100%)";
    badgeColor = "bg-emerald-100 text-emerald-900 border-emerald-400";
  } else if (totalScore >= 40) {
    category = "Педагог-Зерттеуші (80-89%)";
    badgeColor = "bg-emerald-50 text-emerald-800 border-emerald-300";
  } else if (totalScore >= 35) {
    category = "Педагог-Сарапшы (70-79%)";
    badgeColor = "bg-teal-50 text-teal-800 border-teal-300";
  } else if (totalScore >= 30) {
    category = "Педагог-Модератор (60-69%)";
    badgeColor = "bg-blue-50 text-blue-800 border-blue-300";
  }

  const resultData = {
    id: "res_" + Date.now(),
    date: new Date().toLocaleString("kk-KZ"),
    score: totalScore,
    total: totalQuestions,
    percentage: Math.round((totalScore / totalQuestions) * 100),
    timeSpentSecs: timeSpentSecs,
    category: category,
    badgeColor: badgeColor,
    topicStats: topicStats,
    questionResults: questionResults
  };

  AppState.lastResult = resultData;
  saveHistory(resultData);

  // Trigger victory confetti if passed (>= 30)
  if (totalScore >= 30 && typeof confetti === 'function') {
    confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
  }

  renderResults(resultData);
  showView("viewResults");
}

// RENDER RESULTS VIEW
function renderResults(res) {
  document.getElementById("resScoreDisplay").textContent = `${res.score} / ${res.total}`;
  document.getElementById("resPercentage").textContent = `${res.percentage}%`;
  
  const mins = Math.floor(res.timeSpentSecs / 60);
  const secs = res.timeSpentSecs % 60;
  document.getElementById("resTimeSpent").textContent = `${mins} мин ${secs} сек`;

  const catBadge = document.getElementById("resCategoryBadge");
  catBadge.textContent = res.category;
  catBadge.className = `px-4 py-1.5 rounded-full font-bold text-sm border inline-block ${res.badgeColor}`;

  // Render Topic Breakdown Table
  const topicContainer = document.getElementById("resTopicBreakdown");
  topicContainer.innerHTML = "";

  TOPIC_SPECS.forEach(t => {
    const stat = res.topicStats[t.id];
    if (!stat || stat.total === 0) return;

    const percent = Math.round((stat.correct / stat.total) * 100);
    const row = document.createElement("div");
    row.className = "flex flex-col gap-1.5 p-3 rounded-xl bg-slate-50 border border-slate-100";
    row.innerHTML = `
      <div class="flex justify-between items-center text-sm">
        <span class="font-semibold text-slate-800">${stat.name}</span>
        <span class="font-mono font-bold ${percent >= 70 ? 'text-emerald-700' : percent >= 50 ? 'text-amber-600' : 'text-rose-600'}">
          ${stat.correct} / ${stat.total} (${percent}%)
        </span>
      </div>
      <div class="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
        <div class="h-2 rounded-full ${percent >= 70 ? 'bg-emerald-600' : percent >= 50 ? 'bg-amber-500' : 'bg-rose-500'}" style="width: ${percent}%"></div>
      </div>
    `;
    topicContainer.appendChild(row);
  });

  // Render Error / Questions Review
  renderQuestionReview(res, 'all');

  // Filter tab events
  document.querySelectorAll("[data-review-filter]").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll("[data-review-filter]").forEach(b => {
        b.classList.remove("bg-slate-900", "text-white");
        b.classList.add("bg-slate-100", "text-slate-700");
      });
      btn.classList.add("bg-slate-900", "text-white");
      btn.classList.remove("bg-slate-100", "text-slate-700");
      renderQuestionReview(res, btn.getAttribute("data-review-filter"));
    };
  });

  // Action buttons
  document.getElementById("btnRetakeErrors").onclick = () => {
    const wrongQs = res.questionResults.filter(r => !r.isCorrect).map(r => r.question);
    if (wrongQs.length === 0) {
      alert("Барлық сұрақтар дұрыс! Қате жоқ.");
      return;
    }
    startCustomExamWithQuestions(wrongQs);
  };

  document.getElementById("btnNewExamFromResults").onclick = () => {
    showView("viewHome");
  };

  document.getElementById("btnPrintResults").onclick = () => {
    window.print();
  };
}

function renderQuestionReview(res, filterType) {
  const container = document.getElementById("resReviewList");
  container.innerHTML = "";

  const letters = ['A', 'B', 'C', 'D', 'E'];
  let filtered = res.questionResults;
  if (filterType === 'wrong') filtered = res.questionResults.filter(r => !r.isCorrect);
  else if (filterType === 'correct') filtered = res.questionResults.filter(r => r.isCorrect);

  if (filtered.length === 0) {
    container.innerHTML = `<div class="p-8 text-center text-slate-500">Бұл санатта сұрақтар жоқ.</div>`;
    return;
  }

  filtered.forEach((item, fIdx) => {
    const q = item.question;
    const isCorrect = item.isCorrect;
    const card = document.createElement("div");
    card.className = `clean-card p-5 rounded-2xl mb-4 border ${isCorrect ? 'border-emerald-200 bg-white' : 'border-rose-200 bg-rose-50/20'}`;

    let optionsHtml = '';
    q.options.forEach((opt, optIdx) => {
      let optStyle = 'border-slate-200 bg-slate-50 text-slate-700';
      let icon = '';

      if (optIdx === q.correctIndex) {
        optStyle = 'border-emerald-500 bg-emerald-50 text-emerald-950 font-semibold ring-1 ring-emerald-500';
        icon = '<i data-lucide="check" class="w-4 h-4 text-emerald-600 inline ml-1"></i>';
      } else if (optIdx === item.userAnswer && !isCorrect) {
        optStyle = 'border-rose-400 bg-rose-50 text-rose-950 font-semibold';
        icon = '<i data-lucide="x" class="w-4 h-4 text-rose-600 inline ml-1"></i> (Сіздің қате жауабыңыз)';
      }

      optionsHtml += `
        <div class="p-3 rounded-xl border text-sm flex items-start gap-2.5 ${optStyle}">
          <span class="font-bold">${letters[optIdx]})</span>
          <span class="flex-grow">${formatText(opt)} ${icon}</span>
        </div>
      `;
    });

    card.innerHTML = `
      <div class="flex items-start justify-between gap-3 mb-2">
        <span class="text-xs font-bold px-2.5 py-1 rounded-md ${isCorrect ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
          ${isCorrect ? 'Дұрыс (+1)' : 'Қате (0)'}
        </span>
        <span class="text-xs font-medium text-slate-500">${q.topicName || ''}</span>
      </div>
      <h4 class="font-bold text-slate-900 text-base mb-3">${formatText(q.text)}</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
        ${optionsHtml}
      </div>
      <div class="p-3 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-700">
        <strong class="text-emerald-800 font-bold block mb-1 flex items-center gap-1">
          <i data-lucide="info" class="w-3.5 h-3.5 text-emerald-600"></i> Түсіндірме:
        </strong>
        ${item.explanation || 'Бұл сұраққа ресми анықтама бойынша жауап берілді.'}
      </div>
    `;
    container.appendChild(card);
  });

  lucide.createIcons();
}

function startCustomExamWithQuestions(questions) {
  AppState.currentExam = {
    questions: questions,
    userAnswers: {},
    flags: {},
    currentIndex: 0,
    timeLimitSeconds: questions.length * 2 * 60,
    remainingSeconds: questions.length * 2 * 60,
    timerId: null,
    isPaused: false,
    startTime: new Date(),
    endTime: null
  };
  startTimer();
  showView("viewExam");
  renderExamQuestion(0);
  renderExamGrid();
}

// Render History Table
function renderHistoryTable() {
  const container = document.getElementById("historyTableBody");
  if (!container) return;
  container.innerHTML = "";

  if (AppState.history.length === 0) {
    container.innerHTML = `<tr><td colspan="5" class="p-6 text-center text-slate-400">Әзірге тест тапсыру тарихы жоқ. «Тестілеуді бастау» батырмасын басыңыз!</td></tr>`;
    return;
  }

  AppState.history.forEach((h, idx) => {
    const mins = Math.floor(h.timeSpentSecs / 60);
    const secs = h.timeSpentSecs % 60;
    const tr = document.createElement("tr");
    tr.className = "border-b border-slate-100 hover:bg-slate-50 text-sm";
    tr.innerHTML = `
      <td class="p-3 font-mono text-slate-500">${h.date}</td>
      <td class="p-3 font-bold text-slate-900">${h.score} / ${h.total} (${h.percentage}%)</td>
      <td class="p-3"><span class="px-2.5 py-1 rounded-full text-xs font-semibold ${h.badgeColor}">${h.category}</span></td>
      <td class="p-3 text-slate-600">${mins}м ${secs}с</td>
      <td class="p-3">
        <button class="text-xs font-semibold text-emerald-700 hover:underline" onclick="viewHistoryDetail(${idx})">Талдау</button>
      </td>
    `;
    container.appendChild(tr);
  });
}

function viewHistoryDetail(historyIndex) {
  const res = AppState.history[historyIndex];
  if (!res) return;
  AppState.lastResult = res;
  renderResults(res);
  showView("viewResults");
}

function clearAllHistory() {
  if (confirm("Барлық тапсыру тарихын өшіргіңіз келе ме?")) {
    AppState.history = [];
    localStorage.removeItem('pbb_exam_history');
    renderHistoryTable();
  }
}

// Render Question Bank View
function renderBankTopicsFilter() {
  const select = document.getElementById("bankTopicFilter");
  if (!select) return;
  select.innerHTML = `<option value="all">Барлық тақырыптар (1 054+)</option>`;
  TOPIC_SPECS.forEach(t => {
    select.innerHTML += `<option value="${t.id}">${t.name}</option>`;
  });
}

function renderBankList() {
  const container = document.getElementById("bankQuestionsList");
  if (!container) return;
  container.innerHTML = "";

  const query = (document.getElementById("bankSearchInput")?.value || "").toLowerCase().trim();
  const topicFilter = document.getElementById("bankTopicFilter")?.value || "all";

  let filtered = AppState.allQuestions.filter(q => {
    if (topicFilter !== 'all' && q.topicId !== topicFilter) return false;
    if (query && !q.text.toLowerCase().includes(query)) return false;
    return true;
  });

  document.getElementById("bankFilteredCount").textContent = filtered.length;

  if (filtered.length === 0) {
    container.innerHTML = `<div class="p-12 text-center text-slate-400">Сұрақтар табылмады.</div>`;
    return;
  }

  const letters = ['A', 'B', 'C', 'D'];
  // Limit render to first 100 for fast responsiveness
  filtered.slice(0, 100).forEach((q, idx) => {
    const card = document.createElement("div");
    card.className = "clean-card p-4 rounded-xl border border-slate-200 mb-3";

    let optionsHtml = '';
    q.options.forEach((opt, oIdx) => {
      const isCorrect = oIdx === q.correctIndex;
      optionsHtml += `
        <div class="text-xs p-2 rounded-lg border ${isCorrect ? 'border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold' : 'border-slate-200 bg-slate-50 text-slate-700'}">
          ${letters[oIdx]}) ${formatText(opt)} ${isCorrect ? '✓' : ''}
        </div>
      `;
    });

    card.innerHTML = `
      <div class="flex justify-between items-center text-xs text-slate-500 mb-1.5">
        <span class="font-bold text-slate-700">№ ${idx + 1} (${q.id})</span>
        <span class="bg-slate-100 px-2 py-0.5 rounded">${q.topicName || q.topicId}</span>
      </div>
      <p class="font-semibold text-slate-900 text-sm mb-3">${formatText(q.text)}</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
        ${optionsHtml}
      </div>
      ${q.explanation ? `<div class="text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-100"><strong>Түсіндірме:</strong> ${q.explanation}</div>` : ''}
    `;
    container.appendChild(card);
  });

  if (filtered.length > 100) {
    const moreNotice = document.createElement("div");
    moreNotice.className = "p-4 text-center text-sm font-semibold text-slate-500";
    moreNotice.textContent = `... тағы ${filtered.length - 100} сұрақ бар. Нақтылау үшін іздеу өрісін пайдаланыңыз.`;
    container.appendChild(moreNotice);
  }
}

// Add Custom Question Submit
function handleAddQuestionSubmit(e) {
  e.preventDefault();
  const topicId = document.getElementById("addTopicSelect").value;
  const topicObj = TOPIC_SPECS.find(t => t.id === topicId) || TOPIC_SPECS[0];
  const qText = document.getElementById("addQuestionText").value.trim();
  const optA = document.getElementById("addOptA").value.trim();
  const optB = document.getElementById("addOptB").value.trim();
  const optC = document.getElementById("addOptC").value.trim();
  const optD = document.getElementById("addOptD").value.trim();
  const correctIdx = parseInt(document.getElementById("addCorrectOpt").value, 10);
  const explanation = document.getElementById("addExplanation").value.trim();

  if (!qText || !optA || !optB || !optC || !optD) {
    alert("Барлық өрістерді толтырыңыз!");
    return;
  }

  const newQ = {
    id: "custom_" + Date.now(),
    topicId: topicId,
    topicName: topicObj.name,
    text: qText,
    options: [optA, optB, optC, optD],
    correctIndex: correctIdx,
    explanation: explanation || "Қолданушы қосқан сұрақ.",
    source: "Менің сұрағым",
    contextId: null,
    contextTitle: null,
    contextText: null
  };

  AppState.customQuestions.push(newQ);
  saveCustomQuestions();

  alert("Сұрақ базаға сәтті қосылды және тест генераторына енгізілді!");
  document.getElementById("formAddQuestion").reset();
  document.getElementById("modalAddQuestion").classList.add("hidden");
  renderBankList();
}

// Export / Import
function exportQuestionsJSON() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(AppState.allQuestions, null, 2));
  const dlAnchor = document.createElement('a');
  dlAnchor.setAttribute("href", dataStr);
  dlAnchor.setAttribute("download", `pbb_questions_backup_${Date.now()}.json`);
  dlAnchor.click();
}

function handleImportJSON(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (event) => {
    try {
      const imported = JSON.parse(event.target.result);
      const list = Array.isArray(imported) ? imported : imported.questions;
      if (!list || !Array.isArray(list)) {
        alert("Қате формат! JSON ішінде сұрақтар тізімі болуы керек.");
        return;
      }
      AppState.customQuestions.push(...list);
      saveCustomQuestions();
      alert(`Сәтті қосылды: ${list.length} сұрақ!`);
      renderBankList();
    } catch (err) {
      alert("Файлды оқу кезінде қате орын алды: " + err.message);
    }
  };
  reader.readAsText(file);
}

// Render Home View Specification Table
function renderHome() {
  const tbody = document.getElementById("specTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  TOPIC_SPECS.forEach((t, i) => {
    const tr = document.createElement("tr");
    tr.className = "border-b border-slate-100 hover:bg-slate-50/70";
    tr.innerHTML = `
      <td class="py-2.5 px-3 text-slate-400 font-mono text-xs">${i + 1}</td>
      <td class="py-2.5 px-3 font-semibold text-slate-800 text-sm">${t.name}</td>
      <td class="py-2.5 px-3 font-mono font-bold text-center text-emerald-800 bg-emerald-50/50 text-sm">${t.count}</td>
      <td class="py-2.5 px-3 font-mono text-center text-slate-600 text-sm">${t.count}</td>
    `;
    tbody.appendChild(tr);
  });
}
