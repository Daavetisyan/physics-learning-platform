(() => {
  const lab = document.querySelector('[data-simulation="distance-displacement"]');
  if (!lab) return;

  const route = [
    // Centerline of the illustrated path, from the lower-left entrance to the flag.
    [58, 540], [87, 521], [116, 501], [145, 487], [174, 474],
    [203, 469], [232, 469], [261, 459], [290, 444], [319, 421],
    [348, 389], [377, 369], [406, 358], [435, 357], [464, 362],
    [493, 373], [522, 385], [551, 397], [580, 405], [609, 412],
    [638, 414], [667, 413], [696, 408], [725, 397], [754, 383],
    [783, 363], [807, 341], [827, 316], [837, 290], [832, 263],
    [818, 237], [800, 212], [794, 188], [806, 166],
  ];
  const routeMeters = 32.5;
  const directMeters = 9.4;
  const missions = [
    { title: 'Reach the blue flag', text: 'Reach the blue flag. Compare the path with your displacement.', check: () => state.index === route.length - 1 },
    { title: 'Make distance larger', text: 'Walk forward, then back. Make distance greater than displacement.', check: () => distance() > magnitude() + 1 },
    { title: 'Make a round trip', text: 'Return to the start with a nonzero distance and zero displacement.', check: () => state.index === 0 && state.distance > 0 },
    { title: 'Compare two journeys', text: 'Save two journeys with different distances for comparison.', check: () => state.saved.length >= 2 && state.saved[0].distance !== state.saved[1].distance },
    { title: 'Reverse the positive direction', text: 'Change the positive direction and observe the displacement sign.', check: () => state.direction === -1 && state.index > 0 },
  ];
  const state = { index: 0, distance: 0, elapsed: 0, timer: null, direction: 1, showPath: true, history: [0], saved: [], mission: 0, complete: new Set() };
  const $ = (id) => document.getElementById(id);
  const segmentMeters = routeMeters / (route.length - 1);
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function displacement() {
    return state.direction * directMeters * state.index / (route.length - 1);
  }

  function magnitude() {
    return Math.abs(displacement());
  }

  function distance() {
    return state.distance;
  }

  function format(value, digits = 1) {
    const rounded = Math.abs(value) < 0.05 ? 0 : value;
    return rounded.toFixed(digits);
  }

  function routePoints() {
    return state.history.map((index) => route[index].join(',')).join(' ');
  }

  function render() {
    const [x, y] = route[state.index];
    const signed = displacement();
    const direction = signed === 0 ? '—' : signed > 0 ? 'East' : 'West';
    const elapsed = state.elapsed;

    $('journeyTraveler').style.left = `${x / 10}%`;
    $('journeyTraveler').style.top = `${y / 5.6}%`;
    $('journeyTraveler').classList.toggle('at-finish', state.index === route.length - 1);
    $('journeyPath').setAttribute('points', routePoints());
    $('journeyPath').style.opacity = state.showPath ? '1' : '0';
    $('journeyDisplacementArrow').setAttribute('x2', x);
    $('journeyDisplacementArrow').setAttribute('y2', y);
    $('journeyDisplacementArrow').style.opacity = state.showPath ? '1' : '0';

    $('journeyDistance').textContent = `${format(distance())} m`;
    $('journeyDisplacement').textContent = `${format(magnitude())} m`;
    $('journeyDirectionValue').textContent = direction;
    $('journeyTime').textContent = `${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`;
    $('journeyAverage').textContent = `${elapsed ? format(distance() / elapsed, 2) : '0.00'} m/s`;
    $('journeySceneDistance').textContent = `${format(distance())} m`;
    $('journeySceneDisplacement').textContent = `${signed >= 0 ? '+' : '−'}${format(magnitude())} m`;
    $('journeyResultDistance').textContent = `${format(distance())} m`;
    $('journeyResultDisplacement').textContent = `${signed >= 0 ? '+' : '−'}${format(magnitude())} m`;
    $('journeyScore').textContent = state.complete.size;
    $('journeyCompleted').textContent = `${state.complete.size} / ${missions.length}`;
    $('journeyMissionNumber').textContent = `${state.mission + 1} OF ${missions.length}`;
    $('journeyMissionText').textContent = missions[state.mission].text;
    $('journeyTaskTitle').textContent = missions[state.mission].title;
    $('journeyTaskPrompt').textContent = missions[state.mission].text;
    $('journeyShowPath').checked = state.showPath;
  }

  function move(amount) {
    const next = Math.max(0, Math.min(route.length - 1, state.index + amount));
    if (next === state.index) return;
    state.distance += Math.abs(next - state.index) * segmentMeters;
    state.index = next;
    state.history.push(next);
    state.elapsed += 1;
    render();
    if (state.index === route.length - 1 && state.mission === 0) checkMission(true);
  }

  function stop() {
    if (state.timer) window.clearInterval(state.timer);
    state.timer = null;
    $('journeyRun').innerHTML = '<span aria-hidden="true">▶</span><span>Walk</span>';
  }

  function toggleWalk() {
    if (state.timer) return stop();
    if (state.index === route.length - 1) reset();
    $('journeyRun').innerHTML = '<span aria-hidden="true">Ⅱ</span><span>Pause</span>';
    state.timer = window.setInterval(() => {
      move(1);
      if (state.index === route.length - 1) stop();
    }, prefersReducedMotion ? 550 : 260);
  }

  function reset() {
    stop();
    state.index = 0;
    state.distance = 0;
    state.elapsed = 0;
    state.history = [0];
    $('journeyTaskFeedback').textContent = '';
    render();
  }

  function clearPath() {
    stop();
    state.distance = 0;
    state.elapsed = 0;
    state.history = [state.index];
    render();
  }

  function undo() {
    if (state.history.length < 2) return;
    state.history.pop();
    state.index = state.history[state.history.length - 1];
    state.distance = Math.max(0, state.distance - segmentMeters);
    render();
  }

  function checkMission(auto = false) {
    const success = missions[state.mission].check();
    const feedback = $('journeyTaskFeedback');
    if (!success) {
      if (!auto) feedback.textContent = 'Keep experimenting—your current journey does not meet this mission yet.';
      return;
    }
    state.complete.add(state.mission);
    feedback.textContent = 'Mission complete. Your measurements support the relationship.';
    if (state.mission < missions.length - 1) state.mission += 1;
    render();
  }

  function saveJourney() {
    state.saved.push({ distance: distance(), displacement: displacement() });
    $('journeySavedCount').textContent = state.saved.length;
    $('journeySavedList').innerHTML = state.saved.map((item, index) =>
      `<p><strong>Journey ${index + 1}</strong><span>${format(item.distance)} m distance · ${item.displacement >= 0 ? '+' : '−'}${format(Math.abs(item.displacement))} m displacement</span></p>`
    ).join('');
    $('journeyTaskFeedback').textContent = 'Journey saved. Change your route and save another to compare.';
    checkMission(true);
  }

  function selectTab(name) {
    lab.querySelectorAll('[data-journey-tab]').forEach((button) => {
      const active = button.dataset.journeyTab === name;
      button.setAttribute('aria-selected', String(active));
      $(button.getAttribute('aria-controls')).hidden = !active;
    });
  }

  $('journeyLeft').addEventListener('click', () => move(-1));
  $('journeyRight').addEventListener('click', () => move(1));
  $('journeyAdd').addEventListener('click', () => move(1));
  $('journeyUndo').addEventListener('click', undo);
  $('journeyReset').addEventListener('click', reset);
  $('journeyClear').addEventListener('click', clearPath);
  $('journeyRun').addEventListener('click', toggleWalk);
  $('journeySave').addEventListener('click', saveJourney);
  $('journeyCheck').addEventListener('click', () => checkMission(false));
  $('journeyHint').addEventListener('click', () => {
    $('journeySceneFeedback').innerHTML = 'Hint: <strong>distance follows the curved path</strong>; displacement joins start to finish.';
  });
  $('journeyShowPath').addEventListener('change', (event) => {
    state.showPath = event.target.checked;
    render();
  });
  $('journeyDirection').addEventListener('change', (event) => {
    state.direction = event.target.value === 'left' ? -1 : 1;
    render();
    checkMission(true);
  });
  lab.querySelectorAll('[data-journey-tab]').forEach((button) => button.addEventListener('click', () => selectTab(button.dataset.journeyTab)));
  $('journeyStage').addEventListener('keydown', (event) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) return;
    if (['ArrowRight', 'd', 'D'].includes(event.key)) {
      event.preventDefault();
      move(1);
    } else if (['ArrowLeft', 'a', 'A'].includes(event.key)) {
      event.preventDefault();
      move(-1);
    } else if (event.key === ' ') {
      event.preventDefault();
      toggleWalk();
    }
  });

  render();
})();
