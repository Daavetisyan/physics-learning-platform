(() => {
  const lab = document.querySelector('[data-simulation="distance-displacement"]');
  if (!lab) return;

  const points = [
    [330, 630], [380, 625], [440, 625], [505, 636], [565, 655], [620, 676],
    [680, 676], [735, 652], [795, 620], [850, 592], [915, 585], [980, 596],
    [1040, 624], [1100, 651], [1165, 676], [1230, 687], [1295, 681], [1360, 660],
    [1425, 631], [1490, 608], [1555, 602], [1620, 609], [1680, 600], [1735, 570],
    [1785, 520], [1820, 460], [1850, 400], [1900, 365],
  ];
  const distancePerStep = 32.5 / (points.length - 1);
  const destinationDisplacement = 9.4;
  let index = 0;
  let elapsed = 0;
  let timer = null;
  let directionMultiplier = 1;
  let showPath = true;

  const byId = (id) => document.getElementById(id);
  const traveler = byId('journeyTraveler');
  const path = byId('journeyPath');
  const displacementArrow = byId('journeyDisplacementArrow');
  const feedback = byId('journeyTaskFeedback');

  function formatNumber(value, digits = 1) {
    return value.toFixed(digits);
  }

  function render() {
    const [x, y] = points[index];
    traveler.style.left = `${(x / 2762) * 100}%`;
    traveler.style.top = `${(y / 1448) * 100}%`;
    const distance = index * distancePerStep;
    const signedDisplacement = directionMultiplier * destinationDisplacement * (index / (points.length - 1));
    const direction = signedDisplacement === 0 ? '—' : signedDisplacement > 0 ? 'East' : 'West';
    byId('journeyDistance').textContent = `${formatNumber(distance)} m`;
    byId('journeyDisplacement').textContent = `${formatNumber(Math.abs(signedDisplacement))} m ${direction === '—' ? '' : `to the ${direction.toLowerCase()}`}`.trim();
    byId('journeyDirectionValue').textContent = direction;
    byId('journeyTime').textContent = `${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`;
    byId('journeyAverage').textContent = `${elapsed ? formatNumber(distance / elapsed, 2) : '0.00'} m/s`;
    byId('journeyPosition').textContent = `${formatNumber(signedDisplacement)} m`;
    path.setAttribute('points', points.slice(0, index + 1).map((point) => point.join(',')).join(' '));
    path.style.opacity = showPath ? '1' : '0';
    displacementArrow.setAttribute('x2', String(x));
    displacementArrow.setAttribute('y2', String(y));
    displacementArrow.style.opacity = showPath ? '1' : '0';
    if (index === points.length - 1) {
      feedback.textContent = 'Mission complete: you reached the blue flag. Compare the 32.5 m path with the 9.4 m displacement.';
      feedback.classList.add('success');
      stop();
    }
  }

  function step(amount) {
    index = Math.max(0, Math.min(points.length - 1, index + amount));
    elapsed += Math.abs(amount);
    render();
  }

  function stop() {
    if (timer) window.clearInterval(timer);
    timer = null;
    byId('journeyRun').setAttribute('aria-label', 'Resume journey');
  }

  function toggleWalk() {
    if (timer) {
      stop();
      return;
    }
    if (index === points.length - 1) index = 0;
    timer = window.setInterval(() => step(1), window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 500 : 260);
    byId('journeyRun').setAttribute('aria-label', 'Pause journey');
  }

  function reset() {
    stop();
    index = 0;
    elapsed = 0;
    feedback.textContent = '';
    feedback.classList.remove('success');
    render();
  }

  byId('journeyRight').addEventListener('click', () => step(1));
  byId('journeyLeft').addEventListener('click', () => step(-1));
  byId('journeyAdd').addEventListener('click', () => step(1));
  byId('journeyUndo').addEventListener('click', () => step(-1));
  byId('journeyReset').addEventListener('click', reset);
  byId('journeyClear').addEventListener('click', reset);
  byId('journeyRun').addEventListener('click', toggleWalk);
  byId('journeySave').addEventListener('click', () => {
    feedback.textContent = 'Journey saved for comparison in Results.';
  });
  byId('journeyCheck').addEventListener('click', () => {
    feedback.textContent = index === points.length - 1 ? 'Mission complete.' : 'Continue toward the blue flag.';
  });
  byId('journeyHint').addEventListener('click', () => {
    feedback.textContent = 'Hint: distance follows every curve in the path; displacement joins your start directly to your current position.';
  });
  byId('journeyShowPath').addEventListener('click', () => {
    showPath = !showPath;
    byId('journeyShowPath').setAttribute('aria-pressed', String(showPath));
    render();
  });
  byId('journeyDirection').addEventListener('change', (event) => {
    directionMultiplier = event.target.value === 'left' ? -1 : 1;
    render();
  });
  document.querySelectorAll('[data-journey-tab]').forEach((button) => {
    button.addEventListener('click', () => {
      const label = button.dataset.journeyTab;
      feedback.textContent = `${label[0].toUpperCase()}${label.slice(1)} panel selected.`;
    });
  });
  byId('journeyStage').addEventListener('keydown', (event) => {
    if (['ArrowRight', 'd', 'D'].includes(event.key)) {
      event.preventDefault();
      step(1);
    } else if (['ArrowLeft', 'a', 'A'].includes(event.key)) {
      event.preventDefault();
      step(-1);
    } else if (event.key === ' ') {
      event.preventDefault();
      toggleWalk();
    }
  });

  render();
})();
