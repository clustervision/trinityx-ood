/**
 * Intercepts form submissions and navigation in popup (iframe) mode.
 * Loaded on all pages; activates only when ?popup=1 is present AND the page
 * is rendered inside an iframe.  Uses fetch() to POST form data so the
 * iframe never navigates away, eliminating flash-of-wrong-page and
 * infinite-reload bugs.
 */
(function () {
  if (window.location.search.indexOf('popup=1') === -1) return;

  var inFrame;
  try { inFrame = window.parent && window.parent !== window; }
  catch (e) { inFrame = false; }
  if (!inFrame) return;

  function tellParent(type) {
    window.parent.postMessage({ type: type }, '*');
  }

  // --- Click interceptor (capture phase, runs immediately) ---
  document.addEventListener('click', function (e) {
    if (e.target.closest('.tx-close')) {
      e.preventDefault();
      e.stopImmediatePropagation();
      tellParent('group-popup-close');
      return;
    }

    var link = e.target.closest('a[href]');
    if (link) {
      var href = link.getAttribute('href') || '';
      if (href.charAt(0) !== '#' && href.indexOf('javascript:') !== 0 && href.indexOf('popup=1') === -1) {
        e.preventDefault();
        e.stopImmediatePropagation();
        tellParent('group-popup-close');
      }
    }
  }, true);

  // --- Wait for DOM ready so the footer_js jQuery handler is attached first ---
  var initialState = '';
  $(function () {
    var $form = $('#formAuthentication');
    initialState = $form.length ? $form.serialize() : '';
    if ($form.length) $form.off('submit');
  });

  // --- Form submission interceptor (capture phase) ---
  // Runs before any target/bubble handlers (including jQuery's on the form).
  // e.stopPropagation() prevents the event from reaching the form element.
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || form.tagName !== 'FORM') return;

    e.preventDefault();
    e.stopPropagation();

    if (form.id === 'formAuthentication') {
      var statusEl = document.getElementById('form-status');

      if (initialState && initialState === $(form).serialize()) {
        if (statusEl) {
          statusEl.className = 'alert alert-danger';
          statusEl.textContent = 'Nothing is changed!';
        }
        return;
      }

      var nameEl  = document.getElementById('id_name');
      var newName = document.getElementById('id_newname');
      if (nameEl && newName && nameEl.value && newName.value && nameEl.value === newName.value) {
        if (statusEl) {
          statusEl.className = 'alert alert-danger';
          statusEl.textContent = 'Both Name can not be same, Kindly choose a different name.';
        }
        return;
      }
    }

    fetch(form.action || window.location.href, {
      method: 'POST',
      body: new FormData(form),
      redirect: 'follow'
    })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var err = doc.querySelector('.alert-error, .alert-danger');

        if (err) {
          var shell = document.querySelector('.tx-shell');
          if (shell) {
            shell.querySelectorAll('.alert').forEach(function (el) { el.remove(); });
            var div = document.createElement('div');
            div.className = err.className;
            div.setAttribute('role', 'alert');
            div.innerHTML = err.innerHTML;
            var header = shell.querySelector('.tx-header');
            if (header) header.insertAdjacentElement('afterend', div);
            else shell.prepend(div);
          }
        } else {
          tellParent('group-popup-saved');
        }
      })
      .catch(function () {
        tellParent('group-popup-saved');
      });
  }, true);

  // Tell parent iframe height so the modal can shrink to content (no fixed 68vh).
  function sendIframeHeight() {
    try {
      if (!window.parent || window.parent === window) return;
      var h = Math.max(
        document.body ? document.body.scrollHeight : 0,
        document.documentElement ? document.documentElement.scrollHeight : 0
      );
      if (h > 0) {
        window.parent.postMessage({ type: 'group-iframe-height', height: h }, '*');
      }
    } catch (e) {}
  }
  $(function () { sendIframeHeight(); });
  window.addEventListener('load', sendIframeHeight);
  setTimeout(sendIframeHeight, 300);
  setTimeout(sendIframeHeight, 900);
})();
