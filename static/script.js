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
