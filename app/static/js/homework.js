const homeworkForm = document.getElementById('homeworkForm');

if (homeworkForm) {
  const problems = [...document.querySelectorAll('.homework-problem')];
  const navButtons = [...document.querySelectorAll('.question-nav-button')];
  const previousButton = document.getElementById('previousProblem');
  const nextButton = document.getElementById('nextProblem');
  const positionLabel = document.getElementById('problemPosition');
  const progressValue = document.getElementById('workspaceProgressValue');
  const progressBar = document.getElementById('workspaceProgressBar');
  let currentIndex = 0;

  function problemHasAnswer(problem) {
    const radio = problem.querySelector('input[type="radio"]:checked');
    if (problem.querySelector('input[type="radio"]')) return Boolean(radio);
    const valueInput = problem.querySelector('input[name^="answer_"]');
    const unitInput = problem.querySelector('input[name^="unit_"]');
    return Boolean(valueInput && valueInput.value.trim() && (!unitInput || unitInput.value.trim()));
  }

  function updateProgress() {
    const answered = problems.filter(problemHasAnswer).length;
    const percentage = problems.length ? Math.round((100 * answered) / problems.length) : 0;
    progressValue.textContent = `${percentage}%`;
    progressBar.style.width = `${percentage}%`;
    navButtons.forEach((button, index) => button.classList.toggle('answered', problemHasAnswer(problems[index])));
  }

  function showProblem(index) {
    currentIndex = Math.max(0, Math.min(index, problems.length - 1));
    problems.forEach((problem, problemIndex) => problem.classList.toggle('active', problemIndex === currentIndex));
    navButtons.forEach((button, buttonIndex) => {
      const active = buttonIndex === currentIndex;
      button.classList.toggle('active', active);
      button.setAttribute('aria-current', active ? 'step' : 'false');
    });
    previousButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex === problems.length - 1;
    positionLabel.textContent = `Question ${currentIndex + 1} of ${problems.length}`;
    problems[currentIndex].querySelector('input, textarea')?.focus({ preventScroll: true });
  }

  navButtons.forEach((button) => button.addEventListener('click', () => showProblem(Number(button.dataset.questionTarget))));
  previousButton.addEventListener('click', () => showProblem(currentIndex - 1));
  nextButton.addEventListener('click', () => showProblem(currentIndex + 1));
  homeworkForm.addEventListener('input', updateProgress);
  homeworkForm.addEventListener('change', updateProgress);
  document.getElementById('submitHomeworkWorkspace').addEventListener('click', (event) => {
    if (!window.confirm('Submit this homework now? You will not be able to change it unless revision is requested.')) {
      event.preventDefault();
    }
  });

  updateProgress();
  showProblem(0);
}
