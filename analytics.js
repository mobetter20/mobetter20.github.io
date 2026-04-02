/*
 * Shared analytics loader for ajin.im writing pages.
 * Reuses the existing GA4 property already used elsewhere in Ajin's sites.
 */
(function () {
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
