function setFeedback(element, message, isCorrect) {
  if (!element) return;
  element.textContent = message;
  element.classList.toggle('correct-feedback', Boolean(isCorrect));
  element.classList.toggle('incorrect-feedback', !isCorrect);
}

function setupCheckpointCards() {
  document.querySelectorAll('.checkpoint-card').forEach((card) => {
    const correct = card.dataset.correct;
    const explanation = card.dataset.explanation || '';
    const feedback = card.querySelector('.checkpoint-feedback');
    card.querySelectorAll('.checkpoint-option').forEach((button) => {
      button.addEventListener('click', () => {
        card.querySelectorAll('.checkpoint-option').forEach((item) => {
          item.classList.remove('selected', 'correct-option', 'incorrect-option');
        });
        button.classList.add('selected');
        const isCorrect = button.dataset.answer === correct;
        button.classList.add(isCorrect ? 'correct-option' : 'incorrect-option');
        if (!isCorrect) {
          const correctButton = [...card.querySelectorAll('.checkpoint-option')]
            .find((item) => item.dataset.answer === correct);
          if (correctButton) correctButton.classList.add('correct-option');
        }
        setFeedback(
          feedback,
          `${isCorrect ? 'Correct.' : 'Not yet.'} ${explanation}`,
          isCorrect,
        );
      });
    });
  });
}

function signed(value) {
  if (Math.abs(value) < 1e-9) return '0 m';
  return `${value > 0 ? '+' : ''}${value} m`;
}

function setupPositionSimulation() {
  const simulation = document.querySelector('[data-simulation="position-reference-frame"]');
  if (!simulation) return;

  const objectAInput = document.getElementById('objectAPosition');
  const objectBInput = document.getElementById('objectBPosition');
  const referenceSelect = document.getElementById('referenceSelect');
  const directionSelect = document.getElementById('positiveDirectionSelect');
  const objectA = document.getElementById('objectA');
  const objectB = document.getElementById('objectB');
  const originMarker = document.getElementById('originMarker');
  const axis = document.getElementById('coordinateAxis');

  function physicalToPercent(value) {
    return ((value + 10) / 20) * 100;
  }

  function referencePhysicalPosition(a, b) {
    if (referenceSelect.value === 'a') return a;
    if (referenceSelect.value === 'b') return b;
    return 0;
  }

  function update() {
    const a = Number(objectAInput.value);
    const b = Number(objectBInput.value);
    const reference = referencePhysicalPosition(a, b);
    const orientation = directionSelect.value === 'right' ? 1 : -1;
    const aCoordinate = orientation * (a - reference);
    const bCoordinate = orientation * (b - reference);
    const aRelativeToB = orientation * (a - b);
    const separation = Math.abs(a - b);

    objectA.style.left = `${physicalToPercent(a)}%`;
    objectB.style.left = `${physicalToPercent(b)}%`;
    originMarker.style.left = `${physicalToPercent(reference)}%`;

    document.getElementById('objectAPositionLabel').textContent = `${signed(a)} from laboratory zero`;
    document.getElementById('objectBPositionLabel').textContent = `${signed(b)} from laboratory zero`;
    document.getElementById('objectAReadout').textContent = signed(aCoordinate);
    document.getElementById('objectBReadout').textContent = signed(bCoordinate);
    document.getElementById('relativeAReadout').textContent = signed(aRelativeToB);
    document.getElementById('separationReadout').textContent = `${separation} m`;

    const referenceName = referenceSelect.value === 'a'
      ? 'Object A'
      : referenceSelect.value === 'b'
        ? 'Object B'
        : 'The laboratory zero';
    const directionText = directionSelect.value === 'right' ? 'right' : 'left';
    document.getElementById('frameExplanation').textContent =
      `${referenceName} is the displayed origin, and ${directionText} is positive. ` +
      `The separation remains ${separation} m because changing a coordinate system does not move the objects.`;
    document.getElementById('negativeDirection').textContent = directionSelect.value === 'right' ? '← Negative' : '← Positive';
    document.getElementById('positiveDirection').textContent = directionSelect.value === 'right' ? 'Positive →' : 'Negative →';
  }

  for (let tick = -10; tick <= 10; tick += 2) {
    const marker = document.createElement('span');
    marker.className = 'axis-tick';
    marker.style.left = `${physicalToPercent(tick)}%`;
    marker.innerHTML = `<i></i><small>${tick}</small>`;
    axis.appendChild(marker);
  }

  [objectAInput, objectBInput, referenceSelect, directionSelect].forEach((element) => {
    element.addEventListener('input', update);
    element.addEventListener('change', update);
  });
  update();

  const prediction = simulation.querySelector('.simulation-prediction');
  if (prediction) {
    const correct = prediction.dataset.correct;
    const explanation = prediction.dataset.explanation || '';
    const feedback = prediction.querySelector('.simulation-prediction-feedback');
    prediction.querySelectorAll('.simulation-prediction-option').forEach((button) => {
      button.addEventListener('click', () => {
        prediction.querySelectorAll('.simulation-prediction-option').forEach((item) => {
          item.classList.remove('correct-option', 'incorrect-option');
        });
        const isCorrect = button.dataset.answer === correct;
        button.classList.add(isCorrect ? 'correct-option' : 'incorrect-option');
        setFeedback(feedback, `${isCorrect ? 'Correct.' : 'Try again.'} ${explanation}`, isCorrect);
      });
    });
  }
}

let lastQuizScore = window.EXISTING_SCORE === null || window.EXISTING_SCORE === undefined
  ? null
  : Number(window.EXISTING_SCORE);

function setupQuiz() {
  const quizForm = document.getElementById('quizForm');
  if (!quizForm) return;

  quizForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const fields = [...event.currentTarget.querySelectorAll('fieldset')];
    let correct = 0;
    let answered = 0;

    fields.forEach((field) => {
      const selected = field.querySelector('input:checked');
      const feedback = field.querySelector('.question-feedback');
      field.classList.remove('question-correct', 'question-incorrect');
      if (!selected) {
        setFeedback(feedback, 'Choose an answer before checking.', false);
        return;
      }
      answered += 1;
      const isCorrect = selected.value === field.dataset.correct;
      if (isCorrect) correct += 1;
      field.classList.add(isCorrect ? 'question-correct' : 'question-incorrect');
      setFeedback(
        feedback,
        isCorrect ? 'Correct.' : `Review this idea. The correct answer is: ${field.dataset.correct}`,
        isCorrect,
      );
    });

    if (answered < fields.length) {
      document.getElementById('quizResult').textContent = `Answer all ${fields.length} questions before calculating your mastery score.`;
      return;
    }

    lastQuizScore = Math.round((100 * correct) / fields.length);
    const threshold = Number(window.MASTERY_THRESHOLD || 75);
    const message = lastQuizScore >= threshold
      ? `Mastery reached: ${correct}/${fields.length} (${lastQuizScore}%). Review any missed question before continuing.`
      : `You scored ${correct}/${fields.length} (${lastQuizScore}%). Revisit the highlighted theory chapters and try again.`;
    const result = document.getElementById('quizResult');
    setFeedback(result, message, lastQuizScore >= threshold);

    await fetch(`/api/progress/${window.LESSON_SLUG}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'in_progress', score: lastQuizScore }),
    });
  });
}

function setupChat() {
  const chatForm = document.getElementById('chatForm');
  if (!chatForm) return;

  let chatMode = 'explain';
  document.querySelectorAll('.mode').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.mode').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      chatMode = button.dataset.mode;
    });
  });

  const chatInput = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');
  function addMessage(text, kind) {
    const div = document.createElement('div');
    div.className = kind === 'user' ? 'user-message' : 'bot-message';
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    addMessage(message, 'user');
    chatInput.value = '';
    const response = await fetch('/api/ai-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, mode: chatMode, lesson_slug: window.LESSON_SLUG }),
    });
    const data = await response.json();
    addMessage(data.reply, 'bot');
  });

  const voiceButton = document.getElementById('voiceButton');
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (Recognition) {
    const recognition = new Recognition();
    recognition.lang = 'en-US';
    recognition.onresult = (event) => {
      chatInput.value = event.results[0][0].transcript;
    };
    recognition.onstart = () => { voiceButton.textContent = '◉'; };
    recognition.onend = () => { voiceButton.textContent = '●'; };
    voiceButton.addEventListener('click', () => recognition.start());
  } else {
    voiceButton.addEventListener('click', () => alert('Voice input is not supported in this browser.'));
  }
}

function setupLessonCompletion() {
  const button = document.getElementById('completeLesson');
  if (!button) return;
  button.addEventListener('click', async () => {
    const threshold = Number(window.MASTERY_THRESHOLD || 75);
    if (lastQuizScore === null) {
      alert('Complete the mastery assessment first.');
      return;
    }
    if (lastQuizScore < threshold) {
      alert(`Reach at least ${threshold}% before marking the lesson complete.`);
      return;
    }
    const response = await fetch(`/api/progress/${window.LESSON_SLUG}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'completed', score: lastQuizScore }),
    });
    if (response.ok) {
      button.textContent = 'Completed ✓';
      button.disabled = true;
    }
  });
}

function setupLessonNavigationPosition() {
  const activeStep = document.querySelector('.lesson-step-link[aria-current="step"]');
  if (!activeStep) return;

  const panel = document.querySelector('.lesson-player-nav');
  const list = document.querySelector('.lesson-step-list');
  const storageKey = `lesson-nav-position:${window.LESSON_SLUG || 'lesson'}`;
  let savedPosition = null;

  try {
    savedPosition = JSON.parse(window.sessionStorage.getItem(storageKey));
  } catch (error) {
    savedPosition = null;
  }

  if (savedPosition) {
    if (panel) panel.scrollTop = Number(savedPosition.panel) || 0;
    if (list) list.scrollTop = Number(savedPosition.list) || 0;
  }

  document.querySelectorAll('.lesson-step-link').forEach((link) => {
    link.addEventListener('click', () => {
      try {
        window.sessionStorage.setItem(storageKey, JSON.stringify({
          panel: panel ? panel.scrollTop : 0,
          list: list ? list.scrollTop : 0,
        }));
      } catch (error) {
        // Navigation still works when storage is unavailable.
      }
    });
  });

  if (savedPosition) return;

  let scrollContainer = activeStep.parentElement;
  while (scrollContainer && !scrollContainer.classList.contains('lesson-player-nav')) {
    const style = window.getComputedStyle(scrollContainer);
    const canScroll = scrollContainer.scrollHeight > scrollContainer.clientHeight
      && ['auto', 'scroll'].includes(style.overflowY);
    if (canScroll) break;
    scrollContainer = scrollContainer.parentElement;
  }

  if (!scrollContainer) return;
  const containerRect = scrollContainer.getBoundingClientRect();
  const activeRect = activeStep.getBoundingClientRect();
  const isVisible = activeRect.top >= containerRect.top && activeRect.bottom <= containerRect.bottom;
  if (isVisible) return;

  const centeredTop = scrollContainer.scrollTop
    + activeRect.top
    - containerRect.top
    - scrollContainer.clientHeight / 2
    + activeRect.height / 2;
  scrollContainer.scrollTop = Math.max(0, centeredTop);
}

setupCheckpointCards();
setupPositionSimulation();
setupQuiz();
setupChat();
setupLessonCompletion();
setupLessonNavigationPosition();
