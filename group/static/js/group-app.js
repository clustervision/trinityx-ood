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
    var cols = fields.map(function (f) {
      return {
        title: ucwords(f.replace(/_/g, ' ')),
        data: f,
        defaultContent: '',
        render: function (data) {
          return escapeHtml(cellText(data));
        },
      };
    });
    cols.push({
      title: 'Actions',
      data: null,
      orderable: false,
      searchable: false,
      render: function (_data, _type, row) {
        var raw = row.name != null ? String(row.name) : '';
        var key = canonicalName(raw);
        if (!key) return '';
        var enc = encodeURIComponent(key);
        var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
        var p = function (suffix) {
          return pathJoin(root, suffix);
        };
        return (
          '<div class="tx-row-actions">' +
          '<a class="tx-btn tx-btn-sm tx-btn-outline-blue js-gf-edit" href="' +
          escapeAttr(p('/edit/' + enc)) +
          '" data-name="' +
          escapeAttr(key) +
          '">Edit</a> ' +
          '<a class="tx-btn tx-btn-sm tx-btn-outline-blue js-gf-clone" href="' +
          escapeAttr(p('/clone/' + enc)) +
          '" data-name="' +
          escapeAttr(key) +
          '">Clone</a> ' +
          '<a class="tx-btn tx-btn-sm tx-btn-outline-blue js-gf-ospush" href="' +
          escapeAttr(p('/ospush/' + enc)) +
          '" data-name="' +
          escapeAttr(key) +
          '">OS Push</a> ' +
          '<button type="button" class="tx-btn tx-btn-sm tx-btn-orange js-gf-member" data-name="' +
          escapeAttr(key) +
          '">Members</button> ' +
          '<button type="button" class="tx-btn tx-btn-sm tx-btn-dark js-gf-delete" data-name="' +
          escapeAttr(key) +
          '">Delete</button>' +
          '</div>'
        );
      },
    });
    return cols;
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
        var cols = buildColumns(fields);
        if (typeof DataTable === 'undefined') {
          showListError('DataTables is not loaded.');
          return;
        }
        groupTable = new DataTable('#groupTable', {
          data: groups,
          columns: cols,
          layout: {
            topStart: null,
            topEnd: null,
            bottomStart: null,
            bottomEnd: null,
            top: ['search'],
            bottom: ['pageLength', 'info', 'paging'],
          },
        });
        moveGroupTableControls();
        $('#groupTable').on('draw.dt', function () {
          moveGroupTableControls();
        });
      })
      .catch(function () {
        showListError('Network error while loading list.');
      });
  }

  function moveGroupTableControls() {
    var wrapper = document.querySelector('#groupTable_wrapper');
    if (!wrapper) return;
    var search = wrapper.querySelector('.dataTables_filter');
    var length = wrapper.querySelector('.dataTables_length');
    var searchSlot = document.getElementById('txTableSearchSlot');
    var lengthSlot = document.getElementById('txTableLengthSlot');
    if (search && searchSlot && !searchSlot.contains(search)) searchSlot.appendChild(search);
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
    openModal(title);

    return fetch(htmlUrl, { headers: { Accept: 'text/html' } })
      .then(function (r) {
        if (!r.ok) throw new Error('Failed to load form page');
        return r.text();
      })
      .then(function (html) {
        var shell = parseShellFromHtml(html);
        if (!shell) throw new Error('Form markup not found');
        $('#groupModalBody').empty().append(shell);
        var $form = $('#groupModal #formAuthentication');
        $form.data('gf-record', recordName);
        $form.data('gf-remove-prefix', root);
        var action = opts.formAction;
        if (action) $form.attr('action', action);

        $('#group-form-loading').show();
        $('#group-form-error').hide();
        return $.getJSON(jsonUrl)
          .done(function (payload) {
            $('#group-form-loading').hide();
            if (typeof window.hydrateGroupFormBody === 'function') {
              window.hydrateGroupFormBody(payload);
            }
            if (typeof window.resetGroupFormSerializedBaseline === 'function') {
              window.resetGroupFormSerializedBaseline();
            }
          })
          .fail(function (xhr) {
            $('#group-form-loading').hide();
            var msg = 'Failed to load form data.';
            try {
              var j = JSON.parse(xhr.responseText || '{}');
              if (j && j.error) msg = j.error;
            } catch (e) {}
            $('#group-form-error').text(msg).show();
          });
      })
      .catch(function (err) {
        $('#groupModalBody').html(
          '<div class="alert alert-danger" role="alert">' + escapeHtml(err.message || String(err)) + '</div>'
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

  function openClone(name) {
    var key = canonicalName(name);
    var enc = encodeURIComponent(key);
    var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
    loadFormModal({
      htmlUrl: pathJoin(root, '/clone/' + enc),
      jsonUrl: pathJoin(root, '/clone/' + enc + '?format=json'),
      title: 'Clone ' + key,
      formAction: pathJoin(root, '/clone/' + enc),
      recordName: key,
    });
  }

  function buildOspushMarkup(record, payload) {
    var d = payload.data || {};
    var gl = payload.group_list || { options: [], selected: record };
    var ol = payload.osimage_list || { options: [], selected: d.osimage || '' };
    var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
    var action = pathJoin(root, '/ospush/' + encodeURIComponent(canonicalName(record)));
    var h =
      '<div class="tx-shell" data-group-page="ospush">' +
      '<div id="group-form-body">' +
      '<div class="tx-header"><h2 class="tx-title">OS Push — ' +
      escapeHtml(canonicalName(record)) +
      '</h2></div>' +
      '<form id="formOspush" method="POST" action="' +
      escapeAttr(action) +
      '" class="mb-3">' +
      '<div class="tx-fields">' +
      '<div class="tx-field"><span class="tx-label">Group:</span><select name="name" required id="osp_name"></select></div>' +
      '<div class="tx-field"><span class="tx-label">OS Image:</span><select name="osimage" id="osp_osimage"></select></div>' +
      '<div class="tx-field"><span class="tx-label">No Dry:</span><input type="checkbox" name="nodry" id="osp_nodry" /></div>' +
      '</div>' +
      '<div class="tx-form-footer"><span></span><button type="submit" class="tx-btn tx-btn-blue">Push OS Image</button></div>' +
      '</form></div></div>';
    return { html: h, groupList: gl, osimageList: ol };
  }

  function openOspush(name) {
    var key = canonicalName(name);
    var enc = encodeURIComponent(key);
    var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
    clearModal();
    openModal('OS Push — ' + key);
    $('#groupModalBody').html('<p class="text-muted p-3">Loading…</p>');
    $.getJSON(pathJoin(root, '/ospush/' + enc))
      .done(function (payload) {
        var built = buildOspushMarkup(key, payload);
        $('#groupModalBody').html(built.html);
        if (typeof window.fillGroupSelect === 'function') {
          window.fillGroupSelect($('#osp_name'), built.groupList, 'Select group');
          window.fillGroupSelect($('#osp_osimage'), built.osimageList, 'Select OS image');
        }
      })
      .fail(function () {
        $('#groupModalBody').html('<div class="alert alert-danger">Failed to load OS push form.</div>');
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
    $('#openAddGroupBtn').on('click', function () {
      openAdd();
    });

    $('#groupTable').on('click', '.js-gf-edit', function (e) {
      e.preventDefault();
      openEdit($(this).data('name'));
    });
    $('#groupTable').on('click', '.js-gf-clone', function (e) {
      e.preventDefault();
      openClone($(this).data('name'));
    });
    $('#groupTable').on('click', '.js-gf-ospush', function (e) {
      e.preventDefault();
      openOspush($(this).data('name'));
    });
    $('#groupTable').on('click', '.js-gf-member', function () {
      var n = $(this).data('name');
      if (n && typeof window.member === 'function') {
        window.member('group', n);
      }
    });
    $('#groupTable').on('click', '.js-gf-delete', function () {
      var n = $(this).data('name');
      if (!n || !window.confirm('Delete group "' + n + '"?')) return;
      var root = window.GROUP_GET_LIST_ROOT != null ? String(window.GROUP_GET_LIST_ROOT).replace(/\/$/, '') : '';
      fetch(pathJoin(root, '/delete/' + encodeURIComponent(n)), { headers: { Accept: 'application/json' } })
        .then(function (r) {
          return r.json().then(function (j) {
            return { ok: r.ok, body: j };
          });
        })
        .then(function (x) {
          if (x.ok && x.body && x.body.status === 'success') loadList();
          else alert((x.body && x.body.message) || 'Delete failed');
        })
        .catch(function () {
          alert('Delete request failed.');
        });
    });

    $('#groupTable').on('click', 'tbody td', function (e) {
      if ($(e.target).closest('a,button,.tx-row-actions').length) return;
      var el = document.getElementById('groupTable');
      if (!el || typeof DataTable === 'undefined' || !DataTable.isDataTable(el)) return;
      var api = DataTable.get(el);
      var idx = api.cell(this).index();
      if (!idx) return;
      var fields = window.__groupInventoryFields || [];
      var nameIdx = fields.indexOf('name');
      if (nameIdx < 0) nameIdx = 0;
      if (idx.column !== nameIdx) return;
      var row = api.row(idx.row).data();
      if (row && row.name != null) openEdit(row.name);
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
          if (x.res.ok && x.data && x.data.status === 'success') {
            if (x.data.request_id && typeof window.clone_osimage === 'function') {
              window.clone_osimage(x.data.request_id, x.data.message || '');
            }
            closeModal();
            clearModal();
            return;
          }
          $('#groupModalBody').prepend(
            '<div class="alert alert-danger">' + escapeHtml((x.data && x.data.message) || 'OS Push failed') + '</div>'
          );
        })
        .catch(function () {
          $('#groupModalBody').prepend('<div class="alert alert-danger">Network error.</div>');
        });
    });

    $(document).on('click', '#groupModal #toggle_interfaces', function () {
      var section = document.getElementById('interface_section');
      if (!section) return;
      if (section.style.display === 'none' || section.style.display === '') {
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

    $(document).on('click', '#groupModal #toggle_advanced', function () {
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
