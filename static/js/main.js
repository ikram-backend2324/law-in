/* ============================================
   Law In — Main JavaScript
   ============================================ */

(function () {
  'use strict';

  /* ---- THEME ---- */
  const THEME_KEY = 'lawin-theme';

  function getTheme() {
    return localStorage.getItem(THEME_KEY) || 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }

  function toggleTheme() {
    applyTheme(getTheme() === 'light' ? 'dark' : 'light');
  }

  applyTheme(getTheme());

  document.addEventListener('DOMContentLoaded', function () {

    /* Theme toggles */
    document.querySelectorAll('#themeToggle, .theme-toggle-auth').forEach(btn => {
      btn.addEventListener('click', toggleTheme);
    });

    /* ---- USER DROPDOWN — click-based, not hover ---- */
    const navUser = document.querySelector('.nav-user');
    const dropdown = navUser ? navUser.querySelector('.user-dropdown') : null;

    if (navUser && dropdown) {
      // Remove hover CSS control — we handle it in JS
      dropdown.style.display = 'none';
      let open = false;

      navUser.addEventListener('click', function (e) {
        e.stopPropagation();
        open = !open;
        dropdown.style.display = open ? 'block' : 'none';
        dropdown.style.animation = open ? 'dropIn .2s ease' : '';
      });

      // Close when clicking anywhere outside
      document.addEventListener('click', function () {
        open = false;
        dropdown.style.display = 'none';
      });

      // Don't close when clicking inside dropdown
      dropdown.addEventListener('click', function (e) {
        e.stopPropagation();
      });
    }

    /* ---- HAMBURGER ---- */
    const navContainer = document.querySelector('.nav-container');
    if (navContainer) {
      let hamburger = navContainer.querySelector('.nav-hamburger');
      if (!hamburger) {
        hamburger = document.createElement('button');
        hamburger.className = 'nav-hamburger';
        hamburger.setAttribute('aria-label', 'Toggle menu');
        hamburger.innerHTML = '<span></span><span></span><span></span>';
        const navRight = navContainer.querySelector('.nav-right');
        if (navRight) navContainer.insertBefore(hamburger, navRight);
      }

      hamburger.addEventListener('click', function (e) {
        e.stopPropagation();
        const links = navContainer.querySelector('.nav-links');
        if (links) links.classList.toggle('open');
      });

      const navLinks = navContainer.querySelector('.nav-links');
      if (navLinks) {
        navLinks.querySelectorAll('a').forEach(a => {
          a.addEventListener('click', () => navLinks.classList.remove('open'));
        });
      }
    }

    /* ---- AUTO DISMISS ALERTS ---- */
    document.querySelectorAll('.alert').forEach(function (alert) {
      setTimeout(function () {
        alert.style.transition = 'opacity .5s, transform .5s';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-8px)';
        setTimeout(() => alert.remove(), 500);
      }, 5000);
    });

    /* ---- STAGGER CARD ANIMATIONS ---- */
    document.querySelectorAll('.tests-grid .test-card').forEach(function (card, i) {
      card.style.animationDelay = (i * 0.08) + 's';
      card.style.animation = 'fadeInUp 0.5s ease both';
    });

    document.querySelectorAll('.stats-grid .stat-card').forEach(function (card, i) {
      card.style.animationDelay = (0.1 + i * 0.07) + 's';
      card.style.animation = 'fadeInUp 0.5s ease both';
    });

    /* ---- TABLE RESPONSIVE DATA LABELS ---- */
    document.querySelectorAll('.data-table').forEach(function (table) {
      const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
      table.querySelectorAll('tbody tr').forEach(function (row) {
        row.querySelectorAll('td').forEach(function (td, i) {
          if (headers[i]) td.setAttribute('data-label', headers[i]);
        });
      });
    });

    /* ---- TEST CARD 3D TILT ---- */
    document.querySelectorAll('.test-card').forEach(function (card) {
      card.addEventListener('mousemove', function (e) {
        const rect = card.getBoundingClientRect();
        const dx = ((e.clientX - rect.left) / rect.width - 0.5) * 4;
        const dy = ((e.clientY - rect.top) / rect.height - 0.5) * -4;
        card.style.transform = `translateY(-4px) rotateX(${dy}deg) rotateY(${dx}deg)`;
        card.style.transition = 'transform 0.1s';
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform = '';
        card.style.transition = 'all 0.3s cubic-bezier(0.4,0,0.2,1)';
      });
    });

  });

})();