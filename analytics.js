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

/* 2. GA4 analytics loader (respects the ?notrack opt-out). */
(function () {
  // Self-exclusion: visit any page with ?notrack to permanently opt out on this browser
  // Visit with ?track to reverse it
  var params = new URLSearchParams(window.location.search);
  if (params.has('notrack')) localStorage.setItem('_notrack', '1');
  if (params.has('track')) localStorage.removeItem('_notrack');
  if (localStorage.getItem('_notrack')) return;

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
