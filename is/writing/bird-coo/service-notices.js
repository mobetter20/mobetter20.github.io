(function() {
  function renameClass(root, oldName, newName) {
    root.querySelectorAll('.' + oldName).forEach(function(node) {
      node.classList.remove(oldName);
      node.classList.add(newName);
    });
  }

  function karenHref() {
    return window.location.pathname.indexOf('/bird-coo/issues/') !== -1
      ? '../../karen-hawk/'
      : '../karen-hawk/';
  }

  function wrapKarenNotice(block) {
    var parent = block.parentElement;
    if (parent && parent.matches('a.service-feature-link, a.display-ad-link')) {
      parent.classList.remove('display-ad-link');
      parent.classList.add('service-feature-link');
      if (!parent.getAttribute('href')) parent.setAttribute('href', karenHref());
      if (!parent.getAttribute('aria-label')) {
        parent.setAttribute('aria-label', 'Visit Karen Hawk, Attorney at Law');
      }
      return;
    }

    var link = document.createElement('a');
    link.className = 'service-feature-link';
    link.href = karenHref();
    link.setAttribute('aria-label', 'Visit Karen Hawk, Attorney at Law');
    block.parentNode.insertBefore(link, block);
    link.appendChild(block);
  }

  function normalizeSection(section) {
    var block = section.querySelector('.service-feature, .display-ad');
    if (!block) return;

    block.classList.remove('display-ad');
    block.classList.add('service-feature');

    renameClass(block, 'ad-tagline', 'service-tagline');
    renameClass(block, 'ad-body', 'service-body');
    renameClass(block, 'ad-testimonial', 'service-testimonial');
    renameClass(block, 'ad-contact', 'service-contact');

    var heading = block.querySelector('h3');
    var isKaren = heading && /karen hawk/i.test(heading.textContent || '');
    if (isKaren) wrapKarenNotice(block);
  }

  function init() {
    document.querySelectorAll('#services').forEach(normalizeSection);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
