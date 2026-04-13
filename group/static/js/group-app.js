/**
 * Home inventory: JSON list + DataTables, group modals (add/edit/clone) via HTML fetch + hydrateGroupFormBody.
 * Expects window.GROUP_GET_LIST_ROOT (from inventory template) for API paths when not on /edit/... pages.
 */
(function () {
  'use strict';

  function pathJoin(base, rel) {
    base = base == null ? '' : String(base).replace(/\/$/, '');
    rel = rel.charAt(0) === '/' ? rel : '/' + rel;
    return (base || '') + rel;
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, '&#39;');
  }

  function ucwords(str) {
    return (str + '').replace(/^([a-z])|\s+([a-z])/g, function ($1) {
      return $1.toUpperCase();
    });
  }

  function canonicalName(displayName) {
    return String(displayName || '').replace(/\s+\*$/, '').trim();
  }

  function cellText(val) {
    if (val == null) return '';
    if (typeof val === 'object') {
      try {
        return JSON.stringify(val);
      } catch (e) {
        return String(val);
      }
    }
    return String(val);
  }

  function isEmptyCell(val) {
    if (val == null) return true;
    if (typeof val === 'string' && val.trim() === '') return true;
    if (Array.isArray(val) && val.length === 0) return true;
    return false;
  }

  var groupTable = null;

  function destroyTable() {
    var el = document.getElementById('groupTable');
    if (!el) return;
    if (groupTable && typeof groupTable.destroy === 'function') {
      try {
        groupTable.destroy();
      } catch (e) {}
    } else if (typeof DataTable !== 'undefined' && DataTable.isDataTable && DataTable.isDataTable(el)) {
      try {
        DataTable.get(el).destroy();
      } catch (e2) {}
    }
    groupTable = null;
    $(el).empty();
  }

  function showListError(msg) {
    var $e = $('#groupListError');
    if (!$e.length) return;
    $e.text(msg || '').toggle(!!msg);
  }

  function buildColumns(fields) {
    var cols = [];
    for (var i = 0; i < fields.length; i++) {
      var f = fields[i];
      if (f === 'interfaces') {
        cols.push({
          title: 'Name',
          data: 'interfaces',
          defaultContent: '',
          className: 'tx-iface-cell',
          render: function (data) {
            if (!data || !Array.isArray(data) || data.length === 0) return '';
            return data.map(function (iface) {
              return '<div class="tx-iface-entry">' + escapeHtml(String(iface.interface || '')) + '</div>';
            }).join('');
          },
        });
        cols.push({
          title: 'Network',
          data: 'interfaces',
          defaultContent: '',
          className: 'tx-iface-cell',
          render: function (data) {
            if (!data || !Array.isArray(data) || data.length === 0) return '';
            return data.map(function (iface) {
              return '<div class="tx-iface-entry">' + escapeHtml(String(iface.network || '')) + '</div>';
            }).join('');
          },
        });
        continue;
      }
      cols.push((function (field) {
        return {
          title: ucwords(field.replace(/_/g, ' ')),
          data: field,
          defaultContent: '',
          render: function (data) {
            if (field === 'name') {
              var raw = data != null ? String(data) : '';
              var key = canonicalName(raw);
              if (!key) return escapeHtml(raw);
              return (
                '<button type="button" class="tx-name-link js-gf-open-edit" data-name="' +
                escapeAttr(key) + '">' + escapeHtml(raw) + '</button>'
              );
            }
            if (isEmptyCell(data)) {
              return '<span class="tx-na-box">NOT AVAILABLE</span>';
            }
            return escapeHtml(cellText(data));
          },
        };
      })(f));
    }
    cols.push({
      title: 'Actions',
      data: null,
      orderable: false,
      searchable: false,
      className: 'tx-col-actions',
      render: function (_data, _type, row) {
        var raw = row.name != null ? String(row.name) : '';
        var key = canonicalName(raw);
        if (!key) return '';
        return (
          '<div class="tx-action-icons">' +
          '<button type="button" class="tx-icon-act js-gf-clone" title="Clone" data-name="' +
          escapeAttr(key) + '"><i class="bx bx-copy-alt"></i></button>' +
          '<button type="button" class="tx-icon-act js-gf-ospush" title="OS Push" data-name="' +
          escapeAttr(key) + '"><i class="bx bx-upload"></i></button>' +
          '<button type="button" class="tx-icon-act tx-icon-act-danger js-gf-delete" title="Delete" data-name="' +
          escapeAttr(key) + '"><i class="bx bx-trash"></i></button>' +
          '</div>'
        );
      },
    });
    return cols;
  }

  function buildComplexHeader(tableEl, fields) {
    var thead = document.createElement('thead');
    var row1 = document.createElement('tr');
    var row2 = document.createElement('tr');
    var hasIface = fields.indexOf('interfaces') !== -1;

    for (var i = 0; i < fields.length; i++) {
      if (fields[i] === 'interfaces') {
        var thSpan = document.createElement('th');
        thSpan.setAttribute('colspan', '2');
        thSpan.className = 'tx-iface-header';
        thSpan.textContent = 'Interfaces';
        row1.appendChild(thSpan);

        var thName = document.createElement('th');
        thName.className = 'tx-iface-subheader';
        thName.textContent = 'Name';
        row2.appendChild(thName);

        var thNet = document.createElement('th');
        thNet.className = 'tx-iface-subheader';
        thNet.textContent = 'Network';
        row2.appendChild(thNet);
      } else {
        var th = document.createElement('th');
        th.textContent = ucwords(fields[i].replace(/_/g, ' '));
        if (hasIface) th.setAttribute('rowspan', '2');
        row1.appendChild(th);
      }
    }
    var thAct = document.createElement('th');
    thAct.textContent = 'Actions';
    if (hasIface) thAct.setAttribute('rowspan', '2');
    row1.appendChild(thAct);

    thead.appendChild(row1);
    if (hasIface) thead.appendChild(row2);
    tableEl.appendChild(thead);
  }

  function loadList() {
    var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
    var url = pathJoin(root, '/?format=json');
    showListError('');
    return fetch(url, { headers: { Accept: 'application/json' } })
      .then(function (r) {
        return r.json().then(function (j) {
          return { ok: r.ok, status: r.status, body: j };
        });
      })
      .then(function (res) {
        var body = res.body || {};
        if (!res.ok) {
          showListError(body.error || 'Failed to load list.');
          return;
        }
        if (body.error) {
          showListError(body.error);
        }
        var fields = body.fields || [];
        var groups = body.groups || [];
        window.__groupInventoryFields = fields;
        destroyTable();
        var el = document.getElementById('groupTable');
        buildComplexHeader(el, fields);
        var cols = buildColumns(fields);
        if (typeof DataTable === 'undefined') {
          showListError('DataTables is not loaded.');
          return;
        }
        groupTable = new DataTable('#groupTable', {
          data: groups,
          columns: cols,
          autoWidth: true,
          searching: true,
          orderCellsTop: true,
          layout: {
            topStart: null,
            topEnd: null,
            bottomStart: null,
            bottomEnd: null,
            top: null,
            bottom: ['pageLength', 'info', 'paging'],
          },
        });
        moveLengthSlot();
      })
      .catch(function () {
        showListError('Network error while loading list.');
      });
  }

  function moveLengthSlot() {
    var wrapper = document.querySelector('#groupTable_wrapper');
    if (!wrapper) return;
    var length = wrapper.querySelector('.dataTables_length');
    var lengthSlot = document.getElementById('txTableLengthSlot');
    if (length && lengthSlot && !lengthSlot.contains(length)) lengthSlot.appendChild(length);
  }

  function parseShellFromHtml(html) {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var shell = doc.querySelector('.tx-shell[data-group-page]');
    return shell;
  }

  function clearModal() {
    $('#groupModalBody').empty();
    $('#groupModal #formAuthentication').removeData('gf-record');
    $('#groupModal #formAuthentication').removeData('gf-remove-prefix');
  }

  function openModal(title) {
    $('#groupModalTitle').text(title || '');
    $('#groupModal').modal('show');
  }

  function loadFormModal(opts) {
    var htmlUrl = opts.htmlUrl;
    var jsonUrl = opts.jsonUrl;
    var title = opts.title || '';
    var recordName = opts.recordName || '';
    var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';

    clearModal();
    $('#groupModalBody').html('<p class="text-center text-muted p-4 mb-0">Loading…</p>');
    openModal(title);

    return Promise.all([
      fetch(htmlUrl, { headers: { Accept: 'text/html' } }).then(function (r) {
        if (!r.ok) throw new Error('Failed to load form page');
        return r.text();
      }),
      $.getJSON(jsonUrl),
    ])
      .then(function (pair) {
        var html = pair[0];
        var payload = pair[1];
        var shell = parseShellFromHtml(html);
        if (!shell) throw new Error('Form markup not found');
        $('#groupModalBody').empty().append(shell);
        $('#groupModalBody .tx-close').remove();
        var $form = $('#groupModal #formAuthentication');
        if (!$form.length) $form = $('#groupModal #formOspush');
        $form.data('gf-record', recordName);
        $form.data('gf-remove-prefix', root);
        var action = opts.formAction;
        if (action) $form.attr('action', action);

        $('#group-form-loading').hide();
        $('#group-form-error').hide();
        if (typeof window.hydrateGroupFormBody === 'function') {
          window.hydrateGroupFormBody(payload);
        }
        if (typeof window.resetGroupFormSerializedBaseline === 'function') {
          window.resetGroupFormSerializedBaseline();
        }
      })
      .catch(function (err) {
        $('#groupModalBody').html(
          '<div class="alert alert-danger m-3" role="alert">' + escapeHtml(err.message || String(err)) + '</div>'
        );
      });
  }

  function openAdd() {
    var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
    loadFormModal({
      htmlUrl: pathJoin(root, '/add'),
      jsonUrl: pathJoin(root, '/add?format=json'),
      title: 'Add Group',
      formAction: pathJoin(root, '/add'),
      recordName: '',
    });
  }

  function openEdit(name) {
    var key = canonicalName(name);
    var enc = encodeURIComponent(key);
    var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
    loadFormModal({
      htmlUrl: pathJoin(root, '/edit/' + enc),
      jsonUrl: pathJoin(root, '/edit/' + enc + '?format=json'),
      title: 'Edit ' + key,
      formAction: pathJoin(root, '/edit/' + enc),
      recordName: key,
    });
  }

  function closeModal() {
    $('#groupModal').modal('hide');
  }

  function handleJsonFormResponse(res, data) {
    var st = (data && data.status) || '';
    if (res.ok && (st === 'success' || res.status === 201 || res.status === 204)) {
      closeModal();
      clearModal();
      loadList();
      return;
    }
    var msg = (data && (data.message || data.error)) || res.statusText || 'Request failed';
    $('#group-form-error').text(msg).show();
  }

  function parseJsonResponse(res, text) {
    if (!text) return {};
    try {
      return JSON.parse(text);
    } catch (e) {
      return {};
    }
  }

  function bindEvents() {
    $('#txManualSearch').on('input', function () {
      if (groupTable) groupTable.search(this.value).draw();
    });

    $('#groupModalCloseBtn').on('click', function () {
      $('#groupModal').modal('hide');
    });

    $('#openAddGroupBtn').on('click', function () {
      openAdd();
    });

    $('#groupTable').on('click', '.js-gf-open-edit', function (e) {
      e.preventDefault();
      openEdit($(this).data('name'));
    });
    $('#groupTable').on('click', '.js-gf-clone', function (e) {
      e.preventDefault();
      var key = $(this).data('name');
      var enc = encodeURIComponent(key);
      var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
      loadFormModal({
        htmlUrl: pathJoin(root, '/clone/' + enc),
        jsonUrl: pathJoin(root, '/clone/' + enc + '?format=json'),
        title: 'Clone ' + key,
        formAction: pathJoin(root, '/clone/' + enc),
        recordName: key,
      });
    });
    $('#groupTable').on('click', '.js-gf-ospush', function (e) {
      e.preventDefault();
      var key = $(this).data('name');
      var enc = encodeURIComponent(key);
      var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
      loadFormModal({
        htmlUrl: pathJoin(root, '/ospush/' + enc),
        jsonUrl: pathJoin(root, '/ospush/' + enc + '?format=json'),
        title: 'OS Push — ' + key,
        formAction: pathJoin(root, '/ospush/' + enc),
        recordName: key,
      });
    });
    $('#groupTable').on('click', '.js-gf-delete', function () {
      var n = $(this).data('name');
      if (!n || !window.confirm('Delete group "' + n + '"?')) return;
      var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
      fetch(pathJoin(root, '/delete/' + encodeURIComponent(n)), { headers: { Accept: 'application/json' } })
        .then(function (r) {
          return r.json().then(function (j) { return { ok: r.ok, body: j }; });
        })
        .then(function (x) {
          if (x.ok && x.body && x.body.status === 'success') loadList();
          else alert((x.body && x.body.message) || 'Delete failed');
        })
        .catch(function () { alert('Delete request failed.'); });
    });

    $(document).on('submit', '#groupModal #formAuthentication', function (e) {
      e.preventDefault();
      var form = e.target;
      var fd = new FormData(form);
      var action = form.getAttribute('action') || '';
      fetch(action, {
        method: 'POST',
        body: fd,
        headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(function (r) {
          return r.text().then(function (text) {
            return { res: r, data: parseJsonResponse(r, text) };
          });
        })
        .then(function (x) {
          handleJsonFormResponse(x.res, x.data);
        })
        .catch(function () {
          $('#group-form-error').text('Network error on submit.').show();
        });
    });

    $(document).on('submit', '#groupModal #formOspush', function (e) {
      e.preventDefault();
      var form = e.target;
      var fd = new FormData(form);
      var action = form.getAttribute('action') || '';
      fetch(action, {
        method: 'POST',
        body: fd,
        headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(function (r) {
          return r.text().then(function (text) {
            return { res: r, data: parseJsonResponse(r, text) };
          });
        })
        .then(function (x) {
          handleJsonFormResponse(x.res, x.data);
        })
        .catch(function () {
          $('#group-form-error').text('Network error on submit.').show();
        });
    });

    $(document).on('click', '#toggle_interfaces', function () {
      var section = document.getElementById('interface_section');
      if (!section) return;
      var isHidden = section.style.display === 'none' || section.style.display === '';
      if (isHidden) {
        section.style.display = 'block';
        $(this).text('Hide Interfaces');
        if ($('#group-interface-rows').children('.tx-interface-block').length === 0 && window.group_interface) {
          $('#group-interface-rows').append(window.group_interface);
        }
      } else {
        section.style.display = 'none';
        $(this).text('+ Interfaces');
      }
    });

    $(document).on('click', '#toggle_advanced', function () {
      var section = document.getElementById('advanced_section');
      if (!section) return;
      if (section.style.display === 'none' || section.style.display === '') {
        section.style.display = 'block';
        $(this).html('Advanced &#9652;');
      } else {
        section.style.display = 'none';
        $(this).html('Advanced &#9662;');
      }
    });

    $('#groupModal').on('hidden.bs.modal', function () {
      clearModal();
    });
  }

  $(function () {
    if (!document.getElementById('groupTable')) return;
    bindEvents();
    loadList();
  });
})();
