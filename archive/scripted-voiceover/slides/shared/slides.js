/* ADK Course — Slide Engine
   Adapted from barcik-training-exin-ai-foundation/slides/js/slides.js.
   Per-module decks; lightweight nav with keyboard, touch, hash routing,
   font controls, theme toggle. */

(function () {
  'use strict';

  const slides = document.querySelectorAll('.slide');
  const total = slides.length;
  let current = 0;

  function goTo(index) {
    if (index < 0 || index >= total) return;
    slides[current].classList.remove('active');
    current = index;
    slides[current].classList.add('active');
    updateCounter();
    window.scrollTo(0, 0);
    history.replaceState(null, '', '#slide-' + (current + 1));
  }

  function next() { goTo(current + 1); }
  function prev() { goTo(current - 1); }

  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
      case ' ':
        e.preventDefault();
        next();
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault();
        prev();
        break;
      case 'Home':
        e.preventDefault();
        goTo(0);
        break;
      case 'End':
        e.preventDefault();
        goTo(total - 1);
        break;
    }
  });

  var viewport = document.querySelector('.slide-viewport');
  if (viewport) {
    viewport.addEventListener('click', function (e) {
      if (e.target === this || e.target.classList.contains('slide')) {
        var rect = this.getBoundingClientRect();
        var x = e.clientX - rect.left;
        if (x > rect.width * 0.75) next();
        else if (x < rect.width * 0.25) prev();
      }
    });
  }

  var counter = document.querySelector('.slide-counter');
  function updateCounter() {
    if (counter) counter.textContent = (current + 1) + ' / ' + total;
  }

  var baseFontSize = parseInt(localStorage.getItem('adkSlideFontSize')) || 18;
  applyFontSize();

  window.adjustFont = function (delta) {
    if (delta === 0) {
      baseFontSize = 18;
    } else {
      baseFontSize = Math.max(14, Math.min(28, baseFontSize + delta));
    }
    applyFontSize();
    localStorage.setItem('adkSlideFontSize', baseFontSize);
  };

  function applyFontSize() {
    document.documentElement.style.setProperty('--slide-font-size', baseFontSize + 'px');
  }

  var themeBtn = document.querySelector('.theme-toggle');
  var savedTheme = localStorage.getItem('adkTheme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var html = document.documentElement;
      var nextTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', nextTheme);
      localStorage.setItem('adkTheme', nextTheme);
    });
  }

  var touchStartX = 0;
  var touchStartY = 0;

  document.addEventListener('touchstart', function (e) {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });

  document.addEventListener('touchend', function (e) {
    var dx = e.changedTouches[0].screenX - touchStartX;
    var dy = e.changedTouches[0].screenY - touchStartY;
    if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
      if (dx < 0) next();
      else prev();
    }
  }, { passive: true });

  var hash = window.location.hash;
  if (hash && hash.startsWith('#slide-')) {
    var n = parseInt(hash.replace('#slide-', ''));
    if (!isNaN(n) && n >= 1 && n <= total) {
      current = n - 1;
    }
  }

  slides[current].classList.add('active');
  updateCounter();

  window.addEventListener('hashchange', function () {
    var h = window.location.hash;
    if (h && h.startsWith('#slide-')) {
      var n = parseInt(h.replace('#slide-', ''));
      if (!isNaN(n) && n >= 1 && n <= total && n - 1 !== current) {
        goTo(n - 1);
      }
    }
  });

})();
