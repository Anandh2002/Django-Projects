// Placeholder JS if needed in future
document.addEventListener('DOMContentLoaded', () => {
    console.log("Dashboard loaded!");
  });

  function toggleDarkMode() {
    document.body.classList.toggle('dark');
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
  }
  
  // Load saved theme
  document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') === 'dark') {
      document.body.classList.add('dark');
    }
  });
  