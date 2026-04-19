// Theme Management - Load immediately to prevent flash
(function() {
  // Get saved theme from localStorage, default to 'light'
  const savedTheme = localStorage.getItem('theme') || 'light';
  
  // Set theme immediately before page renders
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

// Toggle theme function
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  // Update DOM
  document.documentElement.setAttribute('data-theme', newTheme);
  
  // Save to localStorage
  localStorage.setItem('theme', newTheme);
  
  // Update icon
  const icon = document.getElementById('themeIcon');
  if (icon) {
    if (newTheme === 'dark') {
      icon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
    } else {
      icon.innerHTML = '<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>';
    }
  }
  
  // Rebuild chart if it exists (for dashboard)
  if (typeof rebuildChart === 'function') {
    rebuildChart();
  }
}
