(function setupRelativePositionLab() {
  const lab = document.querySelector('[data-position-line-lab]');
  if (!lab) return;

  const MIN_X = -10;
  const MAX_X = 10;
  const TOLERANCE = .16;
  const layout = {
    axisLeftPercent: 12.3,
    axisWidthPercent: 75.4,
    groundBottomPercent: 39,
    player: { initialX: 0, widthPercent: 5.3 },
    dog: { x: -3, widthPercent: 7.2 },
    cyclist: { initialX: 3, widthPercent: 9.5 },
    coffee: { x: 6.2 },
    origin: { x: 0 },
  };
  window.RELATIVE_POSITION_SCENE_LAYOUT = layout;

  const missions = [
    { text: 'Stand 3 m to the right of the dog.', hint: 'The dog is at −3 m. Move to 0 m.', reference: 'dog', target: 3 },
    { text: 'Stand 2 m to the left of the coffee shop.', hint: 'Select Coffee shop, then approach it from the left.', reference: 'coffee', target: -2 },
    { text: 'Stand exactly 4 m from the dog.', hint: 'Either side works because distance is unsigned.', reference: 'dog', distance: 4 },
    { text: 'Choose the cyclist and stand 1 m to its right.', hint: 'Pause the cyclist first if that helps.', reference: 'cyclist', target: 1 },
    { text: 'Reach the same position as the dog.', hint: 'Aim for zero relative position and zero separation.', reference: 'dog', target: 0 },
    { text: 'Change the reference to the coffee shop without moving.', hint: 'Only choose Coffee shop. Your physical position should stay fixed.', reference: 'coffee', selectionOnly: true },
    { text: 'Choose Ground origin and return to 0 m.', hint: 'The orange origin marker is at 0 m.', reference: 'origin', target: 0 },
  ];

  const initial = {
    playerX: layout.player.initialX,
    cyclistX: layout.cyclist.initialX,
    cyclistDirection: 1,
    cyclistMoving: false,
    cyclistSpeed: 1.5,
    reference: 'dog',
    positiveDirection: 'right',
    missionIndex: 0,
    score: 0,
    attempts: 0,
    correct: 0,
    completed: 0,
    streak: 0,
    bestStreak: 0,
    elapsed: 0,
  };
  const state = { ...initial };
  const pressed = new Set();
  let visible = true;
  let previousTime = performance.now();
  let secondAccumulator = 0;
  let animationFrame;

  const byId = (id) => document.getElementById(id);
  const nodes = {
    scene: byId('lineScene'),
    player: byId('linePlayer'),
    dog: byId('lineDog'),
    cyclist: byId('lineCyclist'),
    coffee: byId('lineCoffee'),
    line: byId('lineRelationLine'),
    marker: byId('lineReferenceMarker'),
    lineLabel: byId('lineRelationDistance'),
    missionNumber: byId('lineMissionNumber'),
    missionText: byId('lineMissionText'),
    score: byId('lineScore'),
    relation: byId('lineRelationText'),
    detail: byId('lineDistanceText'),
    message: byId('lineMessage'),
    coordinate: byId('linePlayerCoordinate'),
    measurePlayer: byId('measurePlayer'),
    measureRelative: byId('measureRelative'),
    measureDistance: byId('measureDistance'),
    cyclistToggle: byId('lineCyclistToggle'),
    cyclistSpeed: byId('lineCyclistSpeed'),
  };

  const clamp = (value) => Math.max(MIN_X, Math.min(MAX_X, value));
  const signMultiplier = () => state.positiveDirection === 'right' ? 1 : -1;
  const screenPercent = (x) => layout.axisLeftPercent + ((x - MIN_X) / (MAX_X - MIN_X)) * layout.axisWidthPercent;
  const signed = (value) => `${value >= 0 ? '+' : '−'}${Math.abs(value).toFixed(1)} m`;
  const referenceX = () => {
    if (state.reference === 'dog') return layout.dog.x;
    if (state.reference === 'cyclist') return state.cyclistX;
    if (state.reference === 'coffee') return layout.coffee.x;
    return layout.origin.x;
  };
  const referenceName = () => ({ dog: 'dog', cyclist: 'cyclist', coffee: 'coffee shop', origin: 'ground origin' }[state.reference]);
  const physicalRelative = () => state.playerX - referenceX();
  const displayedRelative = () => physicalRelative() * signMultiplier();
  const distance = () => Math.abs(physicalRelative());

  function positionObject(node, x, widthPercent) {
    node.style.left = `${screenPercent(x)}%`;
    node.style.bottom = `${layout.groundBottomPercent}%`;
    if (widthPercent) node.style.width = `${widthPercent}%`;
  }

  function relationSentence() {
    if (distance() < .05) return `You and the ${referenceName()} are at the same position.`;
    return `You are ${distance().toFixed(1)} m to the ${physicalRelative() > 0 ? 'right' : 'left'} of the ${referenceName()}.`;
  }

  function renderGuide() {
    const width = nodes.scene.clientWidth;
    const height = nodes.scene.clientHeight;
    const playerPixel = width * screenPercent(state.playerX) / 100;
    const referencePixel = width * screenPercent(referenceX()) / 100;
    const y = height * .61;
    nodes.line.setAttribute('x1', playerPixel);
    nodes.line.setAttribute('x2', referencePixel);
    nodes.line.setAttribute('y1', y);
    nodes.line.setAttribute('y2', y);
    nodes.marker.setAttribute('cx', referencePixel);
    nodes.marker.setAttribute('cy', y);
    nodes.lineLabel.setAttribute('x', (playerPixel + referencePixel) / 2);
    nodes.lineLabel.setAttribute('y', y - 9);
    nodes.lineLabel.textContent = `${distance().toFixed(1)} m`;
  }

  function updateSummary() {
    const set = (id, value) => { const node = byId(id); if (node) node.textContent = value; };
    set('challengeCompleted', `${state.completed}/7`);
    set('challengeAttempts', state.attempts);
    set('challengeTime', `${Math.floor(state.elapsed / 60)}:${String(state.elapsed % 60).padStart(2, '0')}`);
    set('challengeAccuracy', state.attempts ? `${Math.round(state.correct / state.attempts * 100)}%` : '—');
    set('resultsCompleted', state.completed);
    set('resultsCorrect', state.correct);
    set('resultsStreak', state.bestStreak);
  }

  function render() {
    positionObject(nodes.player, state.playerX, layout.player.widthPercent);
    positionObject(nodes.dog, layout.dog.x, layout.dog.widthPercent);
    positionObject(nodes.cyclist, state.cyclistX, layout.cyclist.widthPercent);
    nodes.coffee.style.left = `${screenPercent(layout.coffee.x)}%`;
    nodes.coffee.style.bottom = '69%';
    nodes.player.classList.toggle('facing-left', pressed.has('a') || pressed.has('arrowleft'));
    nodes.player.classList.toggle('walking', pressed.size > 0);
    nodes.cyclist.classList.toggle('facing-left', state.cyclistDirection < 0);

    document.querySelectorAll('[data-line-object]').forEach((node) => node.classList.toggle('selected-reference', node.dataset.lineObject === state.reference));
    document.querySelectorAll('[data-line-reference]').forEach((button) => {
      const active = button.dataset.lineReference === state.reference;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    document.querySelectorAll('[data-line-direction]').forEach((button) => {
      const active = button.dataset.lineDirection === state.positiveDirection;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });

    const mission = missions[state.missionIndex];
    nodes.missionNumber.textContent = state.missionIndex + 1;
    nodes.missionText.textContent = mission.text;
    nodes.score.textContent = state.score;
    nodes.relation.textContent = relationSentence();
    nodes.detail.textContent = `Signed relative position: ${signed(displayedRelative())} · Physical separation: ${distance().toFixed(1)} m`;
    nodes.coordinate.textContent = signed(state.playerX * signMultiplier());
    nodes.measurePlayer.textContent = signed(state.playerX * signMultiplier());
    nodes.measureRelative.textContent = signed(displayedRelative());
    nodes.measureDistance.textContent = `${distance().toFixed(1)} m`;
    nodes.cyclistToggle.textContent = state.cyclistMoving ? '❚❚ Pause' : '▶ Play';
    nodes.cyclistToggle.setAttribute('aria-pressed', String(state.cyclistMoving));
    renderGuide();
    updateSummary();
  }

  function movePlayer(direction) {
    state.playerX = clamp(Math.round((state.playerX + direction * .5) * 2) / 2);
    render();
  }

  function missionIsComplete() {
    const mission = missions[state.missionIndex];
    if (state.reference !== mission.reference) return false;
    if (mission.selectionOnly) return true;
    if (mission.distance !== undefined) return Math.abs(distance() - mission.distance) <= TOLERANCE;
    return Math.abs(displayedRelative() - mission.target) <= TOLERANCE;
  }

  document.querySelectorAll('[data-line-move]').forEach((button) => button.addEventListener('click', () => movePlayer(button.dataset.lineMove === 'left' ? -1 : 1)));
  document.querySelectorAll('[data-line-reference]').forEach((button) => button.addEventListener('click', () => { state.reference = button.dataset.lineReference; nodes.message.textContent = ''; render(); }));
  nodes.dog.addEventListener('click', () => { state.reference = 'dog'; render(); });
  nodes.cyclist.addEventListener('click', () => { state.reference = 'cyclist'; render(); });
  document.querySelectorAll('[data-line-direction]').forEach((button) => button.addEventListener('click', () => { state.positiveDirection = button.dataset.lineDirection; render(); }));
  nodes.cyclistToggle.addEventListener('click', () => { state.cyclistMoving = !state.cyclistMoving; render(); });
  nodes.cyclistSpeed.addEventListener('change', () => { state.cyclistSpeed = Number(nodes.cyclistSpeed.value); });
  byId('lineHint').addEventListener('click', () => { nodes.message.className = 'line-message'; nodes.message.textContent = missions[state.missionIndex].hint; });
  byId('lineCheckMission').addEventListener('click', () => {
    state.attempts += 1;
    if (missionIsComplete()) {
      state.correct += 1;
      state.completed += 1;
      state.streak += 1;
      state.bestStreak = Math.max(state.bestStreak, state.streak);
      state.score += 100;
      nodes.message.className = 'line-message success';
      nodes.message.textContent = state.missionIndex === missions.length - 1 ? 'All missions complete!' : 'Mission complete. Next mission ready.';
      if (state.missionIndex < missions.length - 1) state.missionIndex += 1;
    } else {
      state.streak = 0;
      nodes.message.className = 'line-message';
      nodes.message.textContent = 'Not yet. Use the live relationship, then try again.';
    }
    render();
  });
  byId('lineReset').addEventListener('click', () => {
    Object.assign(state, initial);
    nodes.cyclistSpeed.value = state.cyclistSpeed;
    nodes.message.textContent = '';
    render();
  });

  const isTyping = (target) => target instanceof HTMLElement && (target.matches('input, textarea, select') || target.isContentEditable);
  window.addEventListener('keydown', (event) => {
    if (isTyping(event.target)) return;
    const key = event.key.toLowerCase();
    if (!['a', 'd', 'arrowleft', 'arrowright'].includes(key)) return;
    event.preventDefault();
    pressed.add(key);
  });
  window.addEventListener('keyup', (event) => pressed.delete(event.key.toLowerCase()));
  window.addEventListener('blur', () => pressed.clear());
  window.addEventListener('resize', renderGuide);

  document.querySelectorAll('.lab-tabs [role=tab]').forEach((tab) => tab.addEventListener('click', () => {
    document.querySelectorAll('.lab-tabs [role=tab]').forEach((item) => item.setAttribute('aria-selected', String(item === tab)));
    document.querySelectorAll('.lab-tab-panel').forEach((panel) => {
      const active = panel.id === tab.getAttribute('aria-controls');
      panel.hidden = !active;
      panel.classList.toggle('active', active);
    });
  }));

  function animate(now) {
    const delta = Math.min((now - previousTime) / 1000, .05);
    previousTime = now;
    if (visible) {
      const left = pressed.has('a') || pressed.has('arrowleft');
      const right = pressed.has('d') || pressed.has('arrowright');
      if (left !== right) state.playerX = clamp(state.playerX + (right ? 1 : -1) * 3 * delta);
      if (state.cyclistMoving) {
        state.cyclistX += state.cyclistDirection * state.cyclistSpeed * delta;
        if (state.cyclistX >= 8 || state.cyclistX <= -8) state.cyclistDirection *= -1;
      }
      secondAccumulator += delta;
      if (secondAccumulator >= 1) { state.elapsed += 1; secondAccumulator -= 1; }
      render();
    }
    animationFrame = requestAnimationFrame(animate);
  }
  if ('IntersectionObserver' in window) new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; }, { threshold: .05 }).observe(lab);
  window.addEventListener('pagehide', () => cancelAnimationFrame(animationFrame), { once: true });
  render();
  animationFrame = requestAnimationFrame(animate);
}());
