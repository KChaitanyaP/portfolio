function openModal(title, description, plan) {
  document.getElementById('modal-title').innerText = title;
  document.getElementById('modal-description').innerHTML = markdownToHTML(description);
  document.getElementById('modal-plan').innerHTML = `<h4>Plan</h4>` + markdownToHTML(plan || '');
  document.getElementById('modal').style.display = 'flex';
}


function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

window.onclick = function(event) {
  const modal = document.getElementById('modal');
  const formModal = document.getElementById('form-modal');
  const editModal = document.getElementById('edit-modal');

  if (event.target === modal) closeModal();
  if (event.target === formModal) closeFormModal();
  if (event.target === editModal) closeEditModal();
};


function openFormModal() {
    document.getElementById('form-modal').style.display = 'flex';
}

function closeFormModal() {
    document.getElementById('form-modal').style.display = 'none';
}

function openEditModal(title, description, color, plan) {
  document.getElementById('edit-original-title').value = title;
  document.getElementById('edit-title').value = title;
  document.getElementById('edit-description').value = description;
  document.getElementById('edit-plan').value = plan;
  document.getElementById('edit-color').value = color;
  document.getElementById('edit-modal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('edit-modal').style.display = 'none';
}

function markdownToHTML(text) {
  if (!text) return '';
  return text
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/\n/g, '<br>')
    .replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
}

let timerInterval = null;
let elapsedSeconds = 0;
let isRunning = false;
let targetSeconds = null;
let sessionStartTime = null;

let alarmSounds = [];

function loadAlarmSounds() {
  fetch('/get-alarm-sounds')
    .then(response => response.json())
    .then(data => {
      alarmSounds = data;
    })
    .catch(err => {
      console.error('Error loading alarm sounds:', err);
    });
}

function playAlarm() {
  if (alarmSounds.length === 0) return;
  const file = alarmSounds[Math.floor(Math.random() * alarmSounds.length)];
  new Audio(`/static/alarm_sounds/${file}`).play();
}

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600).toString().padStart(2, '0');
  const mins = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
  const secs = (seconds % 60).toString().padStart(2, '0');
  return `${hrs}:${mins}:${secs}`;
}

function saveSession() {
  const project = document.getElementById('project-name').value || 'Unnamed Project';
  const session = {
    project,
    duration: elapsedSeconds,
    startTime: sessionStartTime?.toISOString() || new Date().toISOString()
  };

  let sessions = JSON.parse(localStorage.getItem('workSessions')) || [];
  sessions.push(session);
  localStorage.setItem('workSessions', JSON.stringify(sessions));

  showSessionTable();
}

function resetTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
  isRunning = false;
  elapsedSeconds = 0;
  targetSeconds = null;
  sessionStartTime = null;
  document.getElementById('timer-display').textContent = '00:00:00';
  document.getElementById('project-name').value = '';
  document.getElementById('target-hours').value = '';
  document.getElementById('target-minutes').value = '';
  document.getElementById('timer-button').textContent = 'Start';
}

function startTimer() {
  if (timerInterval) return;

  const hours = parseInt(document.getElementById('target-hours').value) || 0;
  const minutes = parseInt(document.getElementById('target-minutes').value) || 0;
  targetSeconds = (hours * 60 + minutes) * 60 || null;

  sessionStartTime = new Date();
  isRunning = true;
  document.getElementById('timer-button').textContent = 'Pause';

  timerInterval = setInterval(() => {
    elapsedSeconds++;
    document.getElementById('timer-display').textContent = formatTime(elapsedSeconds);

    if (targetSeconds && elapsedSeconds >= targetSeconds) {
      playAlarm();
      clearInterval(timerInterval);
      timerInterval = null;
      isRunning = false;
      saveSession();
      resetTimer(); // reset automatically after session end
    }
  }, 1000);
}

function pauseTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
  isRunning = false;
  document.getElementById('timer-button').textContent = 'Start';
  // saveSession();
}

function formatDuration(seconds) {
  const hrs = Math.floor(seconds / 3600).toString().padStart(2, '0');
  const mins = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
  const secs = (seconds % 60).toString().padStart(2, '0');
  return `${hrs}:${mins}:${secs}`;
}

function showSessionTable() {
  const tableBody = document.querySelector('#session-table tbody');
  if (!tableBody) return;

  tableBody.innerHTML = ''; // clear old rows

  const sessions = JSON.parse(localStorage.getItem('workSessions')) || [];

    sessions
      .slice()
      .sort((a, b) => new Date(a.startTime) - new Date(b.startTime))
      .forEach(session => {
      const row = document.createElement('tr');

      const projectCell = document.createElement('td');
      projectCell.textContent = session.project;

      const durationCell = document.createElement('td');
      durationCell.textContent = formatDuration(session.duration);

      const startCell = document.createElement('td');
      const startDate = new Date(session.startTime);
      startCell.textContent = startDate.toLocaleString();

      row.appendChild(projectCell);
      row.appendChild(durationCell);
      row.appendChild(startCell);

      tableBody.appendChild(row);
    });
}

document.addEventListener('DOMContentLoaded', () => {
  loadAlarmSounds();
  document.getElementById('timer-button')?.addEventListener('click', () => {
    isRunning ? pauseTimer() : startTimer();
  });
  document.getElementById('reset-button')?.addEventListener('click', resetTimer);
  document.getElementById('end-button')?.addEventListener('click', endTimer);
  document.getElementById('clear-sessions-button')?.addEventListener('click', () => {
  if (confirm("Are you sure you want to reset all sessions? This cannot be undone.")) {
    localStorage.removeItem('workSessions');
    showSessionTable();
  }
});

  showSessionTable();

});

function endTimer() {
  if (!isRunning) return;

  clearInterval(timerInterval);
  timerInterval = null;
  isRunning = false;
  document.getElementById('timer-button').textContent = 'Start';

  saveSession();
  resetTimer();
}

