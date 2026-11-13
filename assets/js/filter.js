// Platform filter for the home page and the archive.
// Works on any element with [data-platforms]; without JavaScript every post stays visible.
(function () {
  var bar = document.querySelector('.filters');
  if (!bar) return;
  var buttons = Array.prototype.slice.call(bar.querySelectorAll('button[data-filter]'));
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-platforms]'));
  var months = Array.prototype.slice.call(document.querySelectorAll('.month'));
  var empty = document.querySelector('.empty');
  var count = document.querySelector('[data-count]');

  function apply(filter) {
    if (!buttons.some(function (b) { return b.dataset.filter === filter; })) filter = 'all';
    buttons.forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.filter === filter ? 'true' : 'false');
    });
    var shown = 0;
    items.forEach(function (el) {
      var list = (el.dataset.platforms || '').split(' ');
      var visible = filter === 'all' || list.indexOf(filter) !== -1;
      el.hidden = !visible;
      if (visible) shown++;
    });
    months.forEach(function (m) {
      var visibleRows = m.querySelectorAll('[data-platforms]:not([hidden])').length;
      m.hidden = visibleRows === 0;
      var c = m.querySelector('.count');
      if (c) c.textContent = visibleRows + (visibleRows === 1 ? ' post' : ' posts');
    });
    if (empty) empty.hidden = shown !== 0;
    if (count) {
      count.textContent = shown + (shown === 1 ? ' post' : ' posts') +
        (filter === 'all' ? ', newest first.' : ' on ' + filter + '.');
    }
  }

  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.dataset.filter;
      apply(f);
      var url = f === 'all' ? location.pathname : location.pathname + '#' + f;
      history.replaceState(null, '', url);
    });
  });

  apply(location.hash.replace('#', '') || 'all');
})();
