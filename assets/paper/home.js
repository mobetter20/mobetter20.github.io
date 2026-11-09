// A closing detail should animate when reached, not while it is offscreen.
if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const journey = document.querySelector('.running');
  const observer = new IntersectionObserver((entries) => {
    if (entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= .6)) {
      journey.classList.add('is-arriving');
      observer.disconnect();
    }
  }, { threshold: .6 });
  observer.observe(journey);
}
