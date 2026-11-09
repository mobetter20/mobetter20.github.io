/*
 * Shared site script for ajin.im.
 *   1. Opens every link in a new tab (skips in-page #anchors). Always runs.
 *   2. Loads GA4 analytics (reuses the existing property; respects ?notrack).
 */

/* 1. New-tab links — independent of analytics, so it runs even under ?notrack. */
(function () {
  function retarget() {
    var links = document.querySelectorAll('a[href]');
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      var href = a.getAttribute('href') || '';
      if (href.charAt(0) === '#' || a.target) continue; // skip in-page anchors + explicit targets
      a.target = '_blank';
      if (!a.rel) a.rel = 'noopener noreferrer';
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', retarget);
  } else {
    retarget();
  }
}());

/* 2. GA4 analytics loader. Production only, excluding known test contexts. */
(function () {
  // Origin and automation gates are not preferences. ?track never overrides them.
  var origin = window.location.origin;
  if ((origin !== 'https://ajin.im' && origin !== 'http://ajin.im') || navigator.webdriver) return;

  // Self-exclusion: ?notrack wins if both flags are present. Storage failures are
  // private-by-default: most importantly, a failed opt-out must not leak this visit.
  var params = new URLSearchParams(window.location.search);
  try {
    if (params.has('notrack')) {
      localStorage.setItem('_notrack', '1');
      return;
    }
    if (params.has('track')) localStorage.removeItem('_notrack');
    if (localStorage.getItem('_notrack')) return;
  } catch (_) {
    return;
  }

  var measurementId = 'G-60PV5XGMSX';

  if (!measurementId) {
    return;
  }

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () {
    window.dataLayer.push(arguments);
  };

  var tag = document.createElement('script');
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
  tag.async = true;
  document.head.appendChild(tag);

  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });
}());
