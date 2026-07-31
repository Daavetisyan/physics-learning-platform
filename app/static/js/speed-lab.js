(() => {
  const lab = document.querySelector('[data-simulation="speed-lab"]');
  if (!lab) return;
  const $ = (id) => document.getElementById(id);
  const controls = ['speedStart', 'speedDistance', 'speedA', 'speedB', 'speedDuration', 'speedStop'];
  const tasks = [
    ['Keep distance constant and change time', 'Run two trials to see how covering the same distance in less time requires greater speed.'],
    ['Keep time constant and change distance', 'Use equal durations and compare the distances covered.'],
    ['Double the speed', 'Predict the distance effect when Object A speed doubles.'],
    ['Compare equal-distance trials', 'Adjust speeds and compare the times needed for one target.'],
    ['Compare equal-time trials', 'Keep duration fixed and compare the final positions.'],
    ['Create equal average speeds', 'Save two different distance-time pairs with the same quotient.'],
    ['Include a stop', 'Add a stop and observe its effect on complete-trip average speed.'],
  ];
  const state = { elapsed: 0, timer: null, paused: false, graphA: [[0, 0]], graphB: [[0, 0]], saved: [], task: 0, complete: new Set() };

  const number = (id) => Number($(id).value);
  const settings = () => ({
    start: number('speedStart'), target: number('speedDistance'), a: number('speedA'),
    b: number('speedB'), duration: number('speedDuration'), stop: number('speedStop'),
  });
  const stopActive = (time, duration) => duration > 0 && time >= duration / 2 && time < duration / 2 + number('speedStop');
  const movingTime = (elapsed, s) => Math.max(0, elapsed - Math.min(s.stop, Math.max(0, elapsed - s.duration / 2)));
  const distanceAt = (speed, elapsed, s) => Math.min(s.target, speed * movingTime(elapsed, s));
  const graphPoint = (time, distance, maxTime) => [46 + 352 * time / maxTime, 215 - 195 * distance / 100];

  function renderSettings() {
    const maximumDistance = 100 - number('speedStart');
    $('speedDistance').max = String(maximumDistance);
    if (number('speedDistance') > maximumDistance) $('speedDistance').value = String(maximumDistance);
    $('speedStartOutput').textContent = `${number('speedStart')} m`;
    $('speedDistanceOutput').textContent = `${number('speedDistance')} m`;
    $('speedAOutput').textContent = `${number('speedA')} m/s`;
    $('speedBOutput').textContent = `${number('speedB')} m/s`;
    $('speedDurationOutput').textContent = `${number('speedDuration')} s`;
    $('speedTarget').style.left = `${number('speedStart') + number('speedDistance')}%`;
  }
  function render() {
    const s = settings();
    const da = distanceAt(s.a, state.elapsed, s);
    const db = distanceAt(s.b, state.elapsed, s);
    $('speedRunnerA').style.left = `${Math.min(100, s.start + da)}%`;
    $('speedRunnerB').style.left = `${Math.min(100, s.start + db)}%`;
    $('speedLiveDistance').textContent = `${da.toFixed(1)} m`;
    $('speedLiveTime').textContent = `${state.elapsed.toFixed(1)} s`;
    $('speedLiveSpeed').textContent = `${state.elapsed ? (da / state.elapsed).toFixed(2) : '0.00'} m/s`;
    $('speedGraphA').setAttribute('points', state.graphA.map((p) => p.join(',')).join(' '));
    $('speedGraphB').setAttribute('points', state.graphB.map((p) => p.join(',')).join(' '));
    $('speedTasksComplete').textContent = `${state.complete.size} / ${tasks.length}`;
    $('speedTaskTitle').textContent = tasks[state.task][0];
    $('speedTaskText').textContent = tasks[state.task][1];
  }
  function step() {
    const s = settings();
    const maxTime = s.duration + s.stop;
    state.elapsed = Math.min(maxTime, state.elapsed + 0.1);
    const da = distanceAt(s.a, state.elapsed, s);
    const db = distanceAt(s.b, state.elapsed, s);
    state.graphA.push(graphPoint(state.elapsed, da, maxTime));
    state.graphB.push(graphPoint(state.elapsed, db, maxTime));
    render();
    if (state.elapsed >= maxTime || (da >= s.target && db >= s.target)) finish();
  }
  function run() {
    if (state.timer) return;
    if (state.elapsed >= settings().duration + settings().stop) reset();
    state.paused = false;
    state.timer = window.setInterval(step, 50);
    $('speedLabFeedback').textContent = stopActive(state.elapsed, settings().duration) ? 'Stopped: time continues while distance stays constant.' : 'Trial running: animation and calculations use d = vt.';
  }
  function pause() {
    if (state.timer) window.clearInterval(state.timer);
    state.timer = null;
    state.paused = true;
    $('speedLabFeedback').textContent = 'Paused. No time or distance is being added.';
  }
  function finish() {
    pause();
    const s = settings();
    const distance = distanceAt(s.a, state.elapsed, s);
    $('speedLabFeedback').textContent = `Trial complete: Object A covered ${distance.toFixed(1)} m in ${state.elapsed.toFixed(1)} s; average speed ${(distance / state.elapsed).toFixed(2)} m/s.`;
  }
  function reset() {
    pause();
    state.elapsed = 0;
    state.graphA = [[46, 215]];
    state.graphB = [[46, 215]];
    $('speedLabFeedback').textContent = 'Reset complete. Values are ready for another prediction.';
    renderSettings(); render();
  }
  function save() {
    const s = settings();
    const distance = distanceAt(s.a, Math.max(state.elapsed, s.duration + s.stop), s);
    const time = Math.max(state.elapsed, s.duration + s.stop);
    state.saved.push({ distance, time, speed: distance / time, stop: s.stop });
    $('speedSavedTrials').innerHTML = state.saved.map((trial, i) => `<p><strong>Trial ${i + 1}</strong><span>${trial.distance.toFixed(1)} m ÷ ${trial.time.toFixed(1)} s = ${trial.speed.toFixed(2)} m/s${trial.stop ? ` · ${trial.stop}s stop` : ''}</span></p>`).join('');
  }
  controls.forEach((id) => $(id).addEventListener('input', () => { renderSettings(); if (!state.timer) reset(); }));
  $('speedRun').addEventListener('click', run);
  $('speedPause').addEventListener('click', pause);
  $('speedReset').addEventListener('click', reset);
  $('speedSave').addEventListener('click', save);
  $('speedCheckTask').addEventListener('click', () => {
    if (!$('speedPrediction').value.trim() || !$('speedExplanation').value.trim()) {
      $('speedLabFeedback').textContent = 'Add both a prediction and an explanation before checking.';
      return;
    }
    state.complete.add(state.task);
    if (state.task < tasks.length - 1) state.task += 1;
    render();
    $('speedLabFeedback').textContent = 'Task recorded. Continue to the next investigation.';
    fetch(`/api/progress/${window.LESSON_SLUG}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({status: 'in_progress'}) }).catch(() => {});
  });
  renderSettings(); reset();
})();
