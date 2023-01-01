const showButton = document.getElementById('show-sidebar');
const hideButton = document.getElementById('hide-sidebar');
const sidebar = document.getElementById('sidebar');
const showIcon = document.getElementById('show-sidebar-icon');
const closeIcon = document.getElementById('close-sidebar-icon');

function swapButtons() {
    showButton.classList.toggle('hidden');
    if (showButton.classList.contains('hidden')) {
        showIcon.classList.add('hidden');
    } else {
        showIcon.classList.remove('hidden');
    }
}

function toggleSidebar() {
    sidebar.classList.toggle('hidden');
}

showButton.addEventListener('click', () => {
    toggleSidebar();
    swapButtons();
});

hideButton.addEventListener('click', () => {
    toggleSidebar();
    swapButtons();
});


