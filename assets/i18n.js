/* =============================================================
   Olbiatech — shared bilingual (EN / TR) i18n engine
   -------------------------------------------------------------
   Lay-the-foundations replacement for the old per-page inline
   setPageLang(). Backward compatible: same global name
   `setPageLang`, same button IDs (lang-en / lang-tr / -mob),
   same `window.translations = { en:{}, tr:{} }` dictionary shape.

   What it adds over the old in-page version:
     • persists the choice to localStorage (was missing → language
       reset to EN on every navigation / reload)
     • applies the saved language automatically on page load
     • falls back to the browser language, then 'en'
     • sets <html lang="..">  and optional <title> via data-i18n-title
     • toggles long-form blocks via [data-lang-content="en|tr"]
       (for legal pages — full prose per language, not per-string)
     • exposes window.onLangChange(lang) hook for page-specific bits
       (e.g. the chatbot placeholder/welcome strings on the homepage)

   Usage on a page:
     <html lang="en" data-i18n-title="page-title">
     ...content with data-i18n / data-i18n-html / data-lang-content...
     <script>window.translations = { en: {...}, tr: {...} };</script>
     <script src="/assets/i18n.js"></script>
   ============================================================= */
(function () {
  'use strict';

  var STORAGE_KEY = 'olbiatech_lang';
  var DEFAULT_LANG = 'en';
  var SUPPORTED = ['en', 'tr'];

  function isSupported(lang) { return SUPPORTED.indexOf(lang) !== -1; }

  function getInitialLang() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved && isSupported(saved)) return saved;
    } catch (e) { /* localStorage blocked (private mode) — ignore */ }
    var nav = (navigator.language || navigator.userLanguage || '').slice(0, 2).toLowerCase();
    return isSupported(nav) ? nav : DEFAULT_LANG;
  }

  function dict() { return window.translations || {}; }

  function applyButtons(lang) {
    var isTr = lang === 'tr';
    var states = [
      ['lang-en', !isTr], ['lang-tr', isTr],
      ['lang-en-mob', !isTr], ['lang-tr-mob', isTr]
    ];
    states.forEach(function (pair) {
      var btn = document.getElementById(pair[0]);
      if (!btn) return; // page may only have one switcher
      btn.style.opacity = pair[1] ? '1' : '0.45';
      btn.style.boxShadow = pair[1] ? '0 0 0 2px #0565fe' : 'none';
      btn.setAttribute('aria-pressed', pair[1] ? 'true' : 'false');
    });
  }

  window.pageLang = window.pageLang || DEFAULT_LANG;

  window.setPageLang = function (lang) {
    if (!isSupported(lang)) lang = DEFAULT_LANG;
    window.pageLang = lang;
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* ignore */ }

    document.documentElement.setAttribute('lang', lang);
    applyButtons(lang);

    var t = dict()[lang] || {};

    // short strings: text
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (t[key] !== undefined) el.textContent = t[key];
    });
    // short strings: rich (allows inline markup)
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-html');
      if (t[key] !== undefined) el.innerHTML = t[key];
    });
    // long-form blocks: show only the active language's prose
    document.querySelectorAll('[data-lang-content]').forEach(function (el) {
      el.style.display = (el.getAttribute('data-lang-content') === lang) ? '' : 'none';
    });

    // <title> via data-i18n-title on <html>
    var titleKey = document.documentElement.getAttribute('data-i18n-title');
    if (titleKey && t[titleKey]) document.title = t[titleKey];

    // page-specific hook (chatbot strings, etc.)
    if (typeof window.onLangChange === 'function') {
      try { window.onLangChange(lang); } catch (e) { /* page hook error — ignore */ }
    }
  };

  function init() { window.setPageLang(getInitialLang()); }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
