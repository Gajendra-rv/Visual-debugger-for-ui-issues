/**
 * main.js — Global JavaScript utilities
 */

// ── Header scroll effect ──────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const header = document.getElementById('site-header');
  if (header) {
    header.classList.toggle('scrolled', window.scrollY > 10);
  }
});

// ── User dropdown ─────────────────────────────────────────────────────────
function toggleUserMenu() {
  const dropdown = document.getElementById('user-dropdown');
  if (dropdown) dropdown.classList.toggle('open');
}
document.addEventListener('click', (e) => {
  const btn = document.getElementById('user-btn');
  const dropdown = document.getElementById('user-dropdown');
  if (dropdown && btn && !btn.contains(e.target) && !dropdown.contains(e.target)) {
    dropdown.classList.remove('open');
  }
});

// ── Mobile nav toggle ─────────────────────────────────────────────────────
function toggleMobileMenu() {
  const nav = document.getElementById('header-nav');
  if (nav) nav.classList.toggle('open');
}

// ── Counter animation ─────────────────────────────────────────────────────
function animateCounters() {
  const counters = document.querySelectorAll('.counter');
  counters.forEach(counter => {
    const target = parseFloat(counter.dataset.target || 0);
    const suffix = counter.dataset.suffix || '';
    const isDecimal = target % 1 !== 0;
    const duration = 1400;
    const step = 16;
    const steps = duration / step;
    const increment = target / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      counter.textContent = isDecimal
        ? current.toFixed(1) + suffix
        : Math.floor(current) + suffix;
    }, step);
  });
}

// ── Auto-dismiss flash messages ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  animateCounters();

  // Auto-dismiss flash after 5s
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(100%)';
      flash.style.transition = 'all 0.4s ease';
      setTimeout(() => flash.remove(), 400);
    }, 5000);
  });

  // Fade-in elements
  document.querySelectorAll('.section, .stat-card, .chart-card').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(12px)';
    el.style.transition = `opacity 0.5s ease ${i * 0.05}s, transform 0.5s ease ${i * 0.05}s`;
    requestAnimationFrame(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
  });
});

// ── Toast Notification ────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('flash-container') ||
    (() => {
      const c = document.createElement('div');
      c.id = 'flash-container';
      c.className = 'flash-container';
      document.body.appendChild(c);
      return c;
    })();

  const toast = document.createElement('div');
  toast.className = `flash flash-${type}`;
  toast.innerHTML = `<span>${message}</span><button onclick="this.parentElement.remove()" class="flash-close">✕</button>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}
