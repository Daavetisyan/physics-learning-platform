(() => {
  const root = document.querySelector('[data-simulation="distance-displacement"]');
  if (!root) return;

  const tasks = [
    'Create a journey where distance equals displacement magnitude.',
    'Create a journey where distance is greater than displacement magnitude.',
    'Create a journey with zero displacement and nonzero distance.',
    'Save two journeys with equal displacement but different distances.',
    'Reverse the positive direction and observe which sign changes.',
  ];
  let positions = [0];
  let cursor = 0;
  let direction = 1;
  let taskIndex = 0;
  let saved = [];

  const byId = (id) => document.getElementById(id);
  const percent = (x) => ((x + 10) / 20) * 100;
  const distance = () => positions.slice(1).reduce((sum, value, index) => sum + Math.abs(value - positions[index]), 0);
  const displacement = () => direction * (positions[positions.length - 1] - positions[0]);
  const signed = (value) => `${value > 0 ? '+' : ''}${value} m`;

  function render() {
    const start = positions[0];
    const end = positions[positions.length - 1];
    byId('journeyTraveler').style.left = `${percent(cursor)}%`;
    byId('journeyStart').style.left = `${percent(start)}%`;
    byId('journeyPosition').textContent = signed(direction * cursor);
    byId('journeyDistance').textContent = `${distance()} m`;
    byId('journeyDisplacement').textContent = signed(displacement());
    const low = Math.min(start, end);
    const width = Math.abs(end - start);
    const arrow = byId('journeyDisplacementArrow');
    arrow.style.left = `${percent(low)}%`;
    arrow.style.width = `${width * 5}%`;
    arrow.classList.toggle('reverse', end < start);
    arrow.hidden = width === 0;
    byId('journeyPath').innerHTML = positions.slice(1).map((value, index) => {
      const from = positions[index];
      const left = percent(Math.min(from, value));
      return `<span style="left:${left}%;width:${Math.abs(value - from) * 5}%"></span>`;
    }).join('');
    byId('journeyNegative').textContent = direction === 1 ? '← negative' : '← positive';
    byId('journeyPositive').textContent = direction === 1 ? 'positive →' : 'negative →';
  }

  function move(delta) {
    cursor = Math.max(-10, Math.min(10, cursor + delta));
    render();
  }
  function addStep() {
    if (cursor === positions[positions.length - 1]) return;
    positions.push(cursor);
    render();
  }
  function reset() {
    positions = [0]; cursor = 0; direction = 1; taskIndex = 0; saved = [];
    byId('journeyDirection').value = 'right';
    byId('journeyTaskFeedback').textContent = '';
    byId('journeyComparisons').innerHTML = '<p>Save up to two journeys to compare their paths and endpoints.</p>';
    showTask(); render();
  }
  function showTask() {
    byId('journeyTaskCount').textContent = `Task ${taskIndex + 1} of ${tasks.length}`;
    byId('journeyTask').textContent = tasks[taskIndex];
  }
  function taskComplete() {
    const d = distance();
    const dx = Math.abs(displacement());
    if (taskIndex === 0) return d > 0 && d === dx;
    if (taskIndex === 1) return d > dx;
    if (taskIndex === 2) return d > 0 && dx === 0;
    if (taskIndex === 3) return saved.length >= 2 && Math.abs(saved[0].displacement) === Math.abs(saved[1].displacement) && saved[0].distance !== saved[1].distance;
    return direction === -1;
  }
  function checkTask() {
    const feedback = byId('journeyTaskFeedback');
    if (!byId('journeyPrediction').value.trim()) {
      feedback.textContent = 'Write a prediction before checking the task.';
      return;
    }
    if (!taskComplete()) {
      feedback.textContent = 'Keep investigating. Use the path segments for distance and the two endpoints for displacement.';
      return;
    }
    feedback.textContent = 'Task complete. Explain your observation, then continue.';
    if (taskIndex < tasks.length - 1) {
      taskIndex += 1;
      window.setTimeout(showTask, 600);
    }
  }
  function saveJourney() {
    if (positions.length < 2) return;
    saved = [...saved.slice(-1), { positions: [...positions], distance: distance(), displacement: displacement() }];
    byId('journeyComparisons').innerHTML = saved.map((item, index) => `<div><strong>Journey ${index + 1}</strong><span>${item.positions.join(' → ')} m</span><span>distance ${item.distance} m · Δx ${signed(item.displacement)}</span></div>`).join('');
  }
  async function run() {
    const traveler = byId('journeyTraveler');
    for (const value of positions) {
      traveler.style.left = `${percent(value)}%`;
      await new Promise((resolve) => window.setTimeout(resolve, window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 30 : 450));
    }
    cursor = positions[positions.length - 1]; render();
  }

  byId('journeyLeft').addEventListener('click', () => move(-1));
  byId('journeyRight').addEventListener('click', () => move(1));
  byId('journeyAdd').addEventListener('click', addStep);
  byId('journeyUndo').addEventListener('click', () => { if (positions.length > 1) positions.pop(); cursor = positions[positions.length - 1]; render(); });
  byId('journeyRun').addEventListener('click', run);
  byId('journeySave').addEventListener('click', saveJourney);
  byId('journeyReset').addEventListener('click', reset);
  byId('journeyCheck').addEventListener('click', checkTask);
  byId('journeyDirection').addEventListener('change', (event) => { direction = event.target.value === 'right' ? 1 : -1; render(); });
  byId('journeyStage').addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); move(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); move(1); }
    if (event.key === 'Enter') { event.preventDefault(); addStep(); }
  });
  render();
})();
