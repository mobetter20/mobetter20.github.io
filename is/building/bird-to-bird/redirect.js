// Authored compatibility redirect. Keep the selected puzzle and anchor intact.
const link = document.getElementById('new-url');
const target = new URL(link.href);
target.search = location.search;
target.hash = location.hash;
link.href = target.href;
location.replace(target.href);
