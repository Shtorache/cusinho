console.log('navbar.js carregado');
document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.querySelector('.navbar-toggle');
  const menu   = document.querySelector('.navbar-menu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    menu.classList.toggle('active');
    toggle.classList.toggle('active');
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
      menu.classList.remove('active');
      toggle.classList.remove('active');
    }
  });
});
