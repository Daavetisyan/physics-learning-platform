(function setupRelativePositionLab() {
  const lab = document.querySelector('[data-relative-position-lab]');
  if (!lab || !window.RelativePositionPhysics) return;

  const Physics = window.RelativePositionPhysics;
  const BOUNDS = { min: -10, max: 10 };
  const PLAYER_STEP = 0.5;
  const INITIAL_STATE = {
    playerWorldX: 0,
    buildingWorldX: -6,
    dogWorldX: -2,
    cyclistWorldX: 5,
    cyclistVelocity: 2,
    cyclistDirection: 1,
    isCyclistMoving: false,
    originWorldX: 0,
    originPreset: 'ground',
    positiveDirection: 'right',
    selectedReference: 'dog',
    currentMissionIndex: 0,
    score: 0,
    attempts: 0,
    correctAttempts: 0,
    completedMissions: [],
    elapsedTime: 0,
    bestStreak: 0,
    streak: 0,
    errors: [],
    trackingSeconds: 0,
  };
  const state = { ...INITIAL_STATE, completedMissions: [], errors: [] };
  const missions = [
    { type: 'physical_offset', reference: 'dog', target: 3, tolerance: 0.15, text: 'Stand 3 m to the right of the dog.', hint: 'The dog is at −2 m in the physical world. Move until you are at +1 m.', concept: 'relative' },
    { type: 'physical_offset', reference: 'building', target: -2, tolerance: 0.15, text: 'Stand 2 m to the left of the building.', hint: 'The building is fixed at −6 m. “Left” means a smaller world position.', concept: 'distance' },
    { type: 'distance', reference: 'cyclist', target: 4, tolerance: 0.15, text: 'Select the cyclist and stay exactly 4 m away.', hint: 'Pause the cyclist first if you want a stable target. Distance has no sign.', concept: 'distance' },
    { type: 'relative', reference: 'cyclist', target: 1, tolerance: 0.15, text: 'Choose the cyclist as reference and reach relative position +1 m.', hint: 'Check the positive-direction setting before interpreting +1 m.', concept: 'moving' },
    { type: 'origin', reference: 'building', tolerance: 0.15, text: 'Shift the displayed origin to the building without moving yourself.', hint: 'Use the Displayed origin menu. Physical objects should remain fixed.', concept: 'origin' },
    { type: 'direction', direction: 'left', text: 'Reverse the positive direction so left is positive.', hint: 'Only coordinate signs should change; the street must not move.', concept: 'direction' },
    { type: 'tracking', reference: 'cyclist', range: 1, seconds: 3, text: 'Stay within 1 m of the moving cyclist for three seconds.', hint: 'Select Cyclist, press Play, then use A/D or the movement buttons to follow.', concept: 'moving' },
  ];
  const labels = { building: 'Building', dog: 'Dog', cyclist: 'Cyclist', ground: 'Ground origin' };
  const elements = {
    scene: document.getElementById('streetScene'),
    player: document.getElementById('playerObject'),
    building: document.getElementById('buildingObject'),
    dog: document.getElementById('dogObject'),
    cyclist: document.getElementById('cyclistObject'),
    guide: document.getElementById('selectedGuide'),
    axis: document.getElementById('relativeAxis'),
    axisPositive: document.getElementById('axisPositiveLabel'),
    missionNumber: document.getElementById('missionNumber'),
    missionText: document.getElementById('missionText'),
    missionFeedback: document.getElementById('missionFeedback'),
    missionHint: document.getElementById('missionHint'),
    score: document.getElementById('labScore'),
    missionProgress: document.getElementById('missionProgress'),
    originPreset: document.getElementById('originPreset'),
    originSlider: document.getElementById('originSlider'),
    originSliderValue: document.getElementById('originSliderValue'),
    speed: document.getElementById('cyclistSpeed'),
    motionStatus: document.getElementById('cyclistMotionStatus'),
    playerCoordinate: document.getElementById('playerCoordinate'),
    bottomPlayerCoordinate: document.getElementById('bottomPlayerCoordinate'),
    bottomOriginValue: document.getElementById('bottomOriginValue'),
    buildingRelative: document.getElementById('buildingRelativeValue'),
    dogRelative: document.getElementById('dogRelativeValue'),
    cyclistRelative: document.getElementById('cyclistRelativeValue'),
    referenceCoordinate: document.getElementById('referenceCoordinate'),
    referenceCoordinateLabel: document.getElementById('referenceCoordinateLabel'),
    relative: document.getElementById('relativePositionValue'),
    distance: document.getElementById('physicalDistanceValue'),
    origin: document.getElementById('originValue'),
    direction: document.getElementById('directionValue'),
    cyclistVelocityRow: document.getElementById('cyclistVelocityRow'),
    cyclistVelocity: document.getElementById('cyclistVelocityValue'),
    interpretation: document.getElementById('relativeInterpretation'),
  };
  let lastFrame = performance.now();
  let animationFrame = null;
  let visible = true;
  let startedAt = performance.now();
  let feedbackTimer = null;
  let axisOriginMarker = null;
  const axisTicks = [];
  const axisProjections = {};

  function objects() {
    return {
      player: state.playerWorldX,
      building: state.buildingWorldX,
      dog: state.dogWorldX,
      cyclist: state.cyclistWorldX,
      ground: 0,
    };
  }

  function stateForMission() {
    return { ...state, objects: objects() };
  }

  function toPercent(worldX) {
    return ((worldX - BOUNDS.min) / (BOUNDS.max - BOUNDS.min)) * 100;
  }

  function currentOriginFromPreset() {
    const positions = objects();
    return state.originPreset === 'custom' ? Number(elements.originSlider.value) : positions[state.originPreset];
  }

  function makeAxis() {
    elements.axis.replaceChildren();
    axisTicks.length = 0;
    const axisLine = document.createElement('div');
    axisLine.className = 'relative-axis-line';
    elements.axis.appendChild(axisLine);
    for (let world = BOUNDS.min; world <= BOUNDS.max; world += 1) {
      const tick = document.createElement('span');
      tick.className = `relative-axis-tick${world % 2 === 0 ? ' major' : ''}`;
      tick.style.left = `${toPercent(world)}%`;
      tick.dataset.world = String(world);
      const coordinate = Physics.displayedCoordinate(world, state.originWorldX, state.positiveDirection);
      tick.innerHTML = `<i></i>${world % 2 === 0 ? `<small>${coordinate.toFixed(0)}</small>` : ''}`;
      elements.axis.appendChild(tick);
      axisTicks.push(tick);
    }
    const origin = document.createElement('span');
    origin.className = 'relative-origin-marker';
    origin.style.left = `${toPercent(state.originWorldX)}%`;
    origin.innerHTML = '<i></i><small>ORIGIN</small>';
    elements.axis.appendChild(origin);
    axisOriginMarker = origin;
    ['player', 'building', 'dog', 'cyclist'].forEach((key) => {
      const projection = document.createElement('span');
      projection.className = `axis-projection projection-${key}`;
      projection.style.left = `${toPercent(objects()[key])}%`;
      projection.setAttribute('aria-hidden', 'true');
      elements.axis.appendChild(projection);
      axisProjections[key] = projection;
    });
  }

  function updateAnimatedAxis() {
    axisProjections.cyclist.style.left = `${toPercent(state.cyclistWorldX)}%`;
    if (state.originPreset !== 'cyclist') return;
    axisOriginMarker.style.left = `${toPercent(state.originWorldX)}%`;
    axisTicks.forEach((tick) => {
      const label = tick.querySelector('small');
      if (label) {
        label.textContent = Physics.displayedCoordinate(
          Number(tick.dataset.world), state.originWorldX, state.positiveDirection,
        ).toFixed(0);
      }
    });
  }

  function renderScene() {
    elements.player.style.left = `${toPercent(state.playerWorldX)}%`;
    elements.building.style.left = `${toPercent(state.buildingWorldX)}%`;
    elements.dog.style.left = `${toPercent(state.dogWorldX)}%`;
    elements.cyclist.style.left = `${toPercent(state.cyclistWorldX)}%`;
    const referenceX = objects()[state.selectedReference];
    elements.guide.style.left = `${toPercent(referenceX)}%`;
    document.querySelectorAll('[data-object]').forEach((object) => {
      object.classList.toggle('selected-reference', object.dataset.object === state.selectedReference);
    });
  }

  function renderMeasurements() {
    const positions = objects();
    const referenceX = positions[state.selectedReference];
    const playerCoordinate = Physics.formatSigned(
      Physics.displayedCoordinate(state.playerWorldX, state.originWorldX, state.positiveDirection),
    );
    elements.playerCoordinate.textContent = playerCoordinate;
    elements.bottomPlayerCoordinate.textContent = playerCoordinate;
    elements.bottomOriginValue.textContent = `${state.originWorldX.toFixed(1)} m`;
    elements.buildingRelative.textContent = Physics.formatSigned(
      Physics.relativePosition(state.playerWorldX, state.buildingWorldX, state.positiveDirection),
    );
    elements.dogRelative.textContent = Physics.formatSigned(
      Physics.relativePosition(state.playerWorldX, state.dogWorldX, state.positiveDirection),
    );
    elements.cyclistRelative.textContent = Physics.formatSigned(
      Physics.relativePosition(state.playerWorldX, state.cyclistWorldX, state.positiveDirection),
    );
    elements.referenceCoordinate.textContent = Physics.formatSigned(
      Physics.displayedCoordinate(referenceX, state.originWorldX, state.positiveDirection),
    );
    elements.referenceCoordinateLabel.textContent = `${labels[state.selectedReference]} coordinate`;
    elements.relative.textContent = Physics.formatSigned(
      Physics.relativePosition(state.playerWorldX, referenceX, state.positiveDirection),
    );
    elements.distance.textContent = `${Physics.physicalDistance(state.playerWorldX, referenceX).toFixed(1)} m`;
    elements.origin.textContent = `${state.originWorldX.toFixed(1)} m world`;
    elements.direction.textContent = state.positiveDirection === 'right' ? 'Right →' : '← Left';
    elements.axisPositive.textContent = state.positiveDirection === 'right' ? 'Positive →' : '← Positive';
    elements.interpretation.textContent = Physics.describeRelativePosition(
      state.playerWorldX, referenceX, labels[state.selectedReference], state.positiveDirection,
    );
    elements.cyclistVelocityRow.hidden = state.selectedReference !== 'cyclist';
    const velocity = state.isCyclistMoving ? state.cyclistVelocity * state.cyclistDirection : 0;
    elements.cyclistVelocity.textContent = Physics.formatSigned(velocity, 'm/s');
    elements.originSliderValue.textContent = `${Number(elements.originSlider.value).toFixed(1)} m`;
  }

  function renderControls() {
    document.querySelectorAll('[data-reference]').forEach((button) => {
      const active = button.dataset.reference === state.selectedReference;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    document.querySelectorAll('[data-direction]').forEach((button) => {
      const active = button.dataset.direction === state.positiveDirection;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    elements.motionStatus.textContent = state.isCyclistMoving ? 'Moving' : 'Paused';
    elements.originPreset.value = state.originPreset;
  }

  function missionError(mission) {
    const positions = objects();
    if (mission.type === 'physical_offset') {
      return Math.abs((state.playerWorldX - positions[mission.reference]) - mission.target);
    }
    if (mission.type === 'distance') {
      return Math.abs(Physics.physicalDistance(state.playerWorldX, positions[mission.reference]) - mission.target);
    }
    if (mission.type === 'relative') {
      return Math.abs(Physics.relativePosition(state.playerWorldX, positions[mission.reference], state.positiveDirection) - mission.target);
    }
    return 0;
  }

  function renderMission() {
    const mission = missions[state.currentMissionIndex];
    elements.missionNumber.textContent = String(state.currentMissionIndex + 1);
    elements.missionText.textContent = mission.text;
    elements.score.textContent = String(state.score);
    elements.missionProgress.textContent = `${state.completedMissions.length} of ${missions.length} missions complete`;
    document.getElementById('challengeCompleted').textContent = `${state.completedMissions.length}/${missions.length}`;
    document.getElementById('challengeAttempts').textContent = String(state.attempts);
    document.getElementById('challengeAccuracy').textContent = state.attempts
      ? `${Math.round((100 * state.correctAttempts) / state.attempts)}%` : '—';
    document.getElementById('resultsCompleted').textContent = String(state.completedMissions.length);
    document.getElementById('resultsCorrect').textContent = String(state.correctAttempts);
    document.getElementById('resultsStreak').textContent = String(state.bestStreak);
    document.getElementById('resultsError').textContent = state.errors.length
      ? `${(state.errors.reduce((sum, value) => sum + value, 0) / state.errors.length).toFixed(2)} m` : '—';
    document.querySelectorAll('#challengeList li').forEach((item, index) => item.classList.toggle('complete', index < state.completedMissions.length));
    document.querySelectorAll('#conceptList [data-concept]').forEach((item) => {
      item.classList.toggle('demonstrated', state.completedMissions.some((entry) => entry.concept === item.dataset.concept));
    });
    const conceptFeedback = document.getElementById('conceptFeedback');
    conceptFeedback.textContent = state.completedMissions.length >= 5
      ? 'You correctly recognized that coordinates depend on a chosen system while physical separation does not.'
      : 'Keep comparing the signed relative position with the unsigned physical separation.';
  }

  function render() {
    renderScene();
    state.originWorldX = currentOriginFromPreset();
    makeAxis();
    renderMeasurements();
    renderControls();
    renderMission();
  }

  function showFeedback(message, success = false) {
    clearTimeout(feedbackTimer);
    elements.missionFeedback.textContent = message;
    elements.missionFeedback.classList.toggle('success', success);
    feedbackTimer = window.setTimeout(() => {
      if (!success) elements.missionFeedback.textContent = '';
    }, 3500);
  }

  function completeCurrentMission() {
    const mission = missions[state.currentMissionIndex];
    if (state.completedMissions.some((entry) => entry.index === state.currentMissionIndex)) return;
    state.completedMissions.push({ index: state.currentMissionIndex, concept: mission.concept });
    state.correctAttempts += 1;
    state.score += 100 + state.streak * 10;
    state.streak += 1;
    state.bestStreak = Math.max(state.bestStreak, state.streak);
    showFeedback('Mission complete. Excellent observation!', true);
    if (state.currentMissionIndex < missions.length - 1) {
      window.setTimeout(() => {
        state.currentMissionIndex += 1;
        state.trackingSeconds = 0;
        elements.missionFeedback.textContent = '';
        render();
      }, 900);
    } else {
      document.getElementById('resultsTab').click();
      renderMission();
    }
  }

  function checkMission(manual = false) {
    const mission = missions[state.currentMissionIndex];
    const valid = Physics.validateMission(mission, stateForMission());
    if (manual) {
      state.attempts += 1;
      state.errors.push(missionError(mission));
    }
    if (valid && mission.type !== 'tracking') {
      completeCurrentMission();
    } else if (manual && !valid) {
      state.streak = 0;
      showFeedback('Not yet—compare the live relative position and physical distance, then try again.');
      renderMission();
    }
  }

  function movePlayer(direction) {
    state.playerWorldX = Math.max(BOUNDS.min, Math.min(BOUNDS.max, state.playerWorldX + direction * PLAYER_STEP));
    render();
    checkMission(false);
  }

  function animate(now) {
    const delta = Math.min((now - lastFrame) / 1000, 0.05);
    lastFrame = now;
    state.elapsedTime = (now - startedAt) / 1000;
    if (visible && state.isCyclistMoving) {
      state.cyclistWorldX += state.cyclistVelocity * state.cyclistDirection * delta;
      if (state.cyclistWorldX >= BOUNDS.max || state.cyclistWorldX <= BOUNDS.min) {
        state.cyclistWorldX = Math.max(BOUNDS.min, Math.min(BOUNDS.max, state.cyclistWorldX));
        state.cyclistDirection *= -1;
      }
      if (state.originPreset === 'cyclist') state.originWorldX = state.cyclistWorldX;
      renderScene();
      updateAnimatedAxis();
      renderMeasurements();
      const mission = missions[state.currentMissionIndex];
      if (mission.type === 'tracking' && Physics.validateMission(mission, stateForMission())) {
        state.trackingSeconds += delta;
        elements.missionFeedback.textContent = `Hold the position… ${Math.min(mission.seconds, state.trackingSeconds).toFixed(1)} / ${mission.seconds.toFixed(1)} s`;
        if (state.trackingSeconds >= mission.seconds) completeCurrentMission();
      } else if (mission.type === 'tracking') {
        state.trackingSeconds = 0;
      }
    }
    document.getElementById('challengeTime').textContent = `${Math.floor(state.elapsedTime / 60)}:${String(Math.floor(state.elapsedTime % 60)).padStart(2, '0')}`;
    animationFrame = requestAnimationFrame(animate);
  }

  document.querySelectorAll('[data-reference]').forEach((button) => {
    button.addEventListener('click', () => {
      state.selectedReference = button.dataset.reference;
      render();
      checkMission(false);
    });
  });
  document.querySelectorAll('[data-direction]').forEach((button) => {
    button.addEventListener('click', () => {
      state.positiveDirection = button.dataset.direction;
      render();
      checkMission(false);
    });
  });
  document.getElementById('moveLeft').addEventListener('click', () => movePlayer(-1));
  document.getElementById('moveRight').addEventListener('click', () => movePlayer(1));
  document.getElementById('playCyclist').addEventListener('click', () => { state.isCyclistMoving = true; renderControls(); });
  document.getElementById('pauseCyclist').addEventListener('click', () => { state.isCyclistMoving = false; renderControls(); });
  elements.speed.addEventListener('change', () => { state.cyclistVelocity = Number(elements.speed.value); renderMeasurements(); });
  elements.originPreset.addEventListener('change', () => {
    state.originPreset = elements.originPreset.value;
    state.originWorldX = currentOriginFromPreset();
    render();
    checkMission(false);
  });
  elements.originSlider.addEventListener('input', () => {
    state.originPreset = 'custom';
    state.originWorldX = Number(elements.originSlider.value);
    render();
  });
  elements.missionHint.addEventListener('click', () => {
    const expanded = elements.missionHint.getAttribute('aria-expanded') === 'true';
    elements.missionHint.setAttribute('aria-expanded', String(!expanded));
    showFeedback(expanded ? '' : missions[state.currentMissionIndex].hint);
  });
  document.getElementById('checkMission').addEventListener('click', () => checkMission(true));
  document.getElementById('resetLab').addEventListener('click', () => {
    Object.assign(state, INITIAL_STATE, { completedMissions: [], errors: [] });
    startedAt = performance.now();
    elements.originSlider.value = '0';
    elements.speed.value = '2';
    elements.missionFeedback.textContent = '';
    render();
  });
  document.addEventListener('keydown', (event) => {
    if (event.target.matches('input, select, textarea, button')) return;
    if (event.key === 'ArrowLeft' || event.key.toLowerCase() === 'a') {
      event.preventDefault();
      movePlayer(-1);
    }
    if (event.key === 'ArrowRight' || event.key.toLowerCase() === 'd') {
      event.preventDefault();
      movePlayer(1);
    }
  });

  document.querySelectorAll('[role="tab"]').forEach((tab) => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('[role="tab"]').forEach((item) => item.setAttribute('aria-selected', String(item === tab)));
      document.querySelectorAll('.lab-tab-panel').forEach((panel) => {
        const active = panel.id === tab.getAttribute('aria-controls');
        panel.hidden = !active;
        panel.classList.toggle('active', active);
      });
    });
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; }, { threshold: 0.05 });
    observer.observe(lab);
  }
  window.addEventListener('pagehide', () => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
  }, { once: true });

  render();
  animationFrame = requestAnimationFrame(animate);
}());
