function openModal(title, description) {
    document.getElementById('modal-title').innerText = title;
    document.getElementById('modal-description').innerText = description;
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

function openEditModal(title, description, color) {
  document.getElementById('edit-original-title').value = title;
  document.getElementById('edit-title').value = title;
  document.getElementById('edit-description').value = description;
  document.getElementById('edit-color').value = color;
  document.getElementById('edit-modal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('edit-modal').style.display = 'none';
}

