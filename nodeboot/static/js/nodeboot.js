/**
 * NODE BOOT — live provisioning view.
 * Polls /api/status and re-renders the session cards each tick.
 */

function getBaseUrl(fullUrl) {
  const url = new URL(fullUrl);
  const pathSegments = url.pathname.split('/');
  const punIndex = pathSegments.findIndex(segment => segment === 'pun');
  if (punIndex !== -1) {
    const basePath = pathSegments.slice(0, punIndex + 3).join('/');
    return `${url.origin}${basePath}`;
  }
  return url.origin;
}

const baseUrl = getBaseUrl(window.location.href);

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function rackHtml(r) {
  const cls = r.kind === 'done' ? 'is-done' : (r.kind === 'error' ? 'is-error' : '');
  const count = r.count > 1 ? ` <span class="nb-count">×${r.count}</span>` : '';
  return `
    <div class="nb-rack">
      <div class="nb-rack-top">
        <span class="nb-rack-name">${esc(r.name)}${count}</span>
        <span class="nb-rack-meta">
          <span class="nb-stage">${esc(r.stage)}</span>
          <span class="nb-pct">${r.pct}%</span>
        </span>
      </div>
      <div class="nb-bar ${cls}"><div class="nb-bar-fill" style="width:${r.pct}%"></div></div>
    </div>`;
}

function cardHtml(s) {
  const overallCls = s.overall >= 100 ? 'nb-done' : '';
  return `
    <div class="nb-card" data-id="${esc(s.id)}">
      <div class="nb-boxes">
        <div class="nb-box"><div class="nb-box-label"><i class="bx bx-hdd"></i> image</div>
          <div class="nb-box-value">${esc(s.image)}</div></div>
        <div class="nb-box"><div class="nb-box-label"><i class="bx bx-server"></i> nodes</div>
          <div class="nb-box-value">${esc(s.nodes)}</div></div>
        <div class="nb-box"><div class="nb-box-label"><i class="bx bx-network-chart"></i> network</div>
          <div class="nb-box-value">${esc(s.network)}</div></div>
        <div class="nb-box"><div class="nb-box-label"><i class="bx bx-chip"></i> boot</div>
          <div class="nb-box-value nb-boot">${esc(s.boot)}</div></div>
        <div class="nb-box nb-box-overall"><div class="nb-box-label"><i class="bx bx-run"></i> session</div>
          <div class="nb-box-value ${overallCls}">${s.overall}%</div></div>
      </div>
      <div class="nb-racks">${s.racks.map(rackHtml).join('')}</div>
    </div>`;
}

function render(data) {
  const errBox = document.getElementById('nb-error');
  errBox.innerHTML = data.error
    ? `<div class="alert alert-danger" role="alert"><strong>API error ::</strong> ${esc(data.error)}</div>`
    : '';

  const sessions = data.sessions || [];
  const box = document.getElementById('nb-sessions');
  box.innerHTML = sessions.length
    ? sessions.map(cardHtml).join('')
    : (data.error ? '' : '<p class="nb-empty">No nodes found.</p>');
}

function poll() {
  fetch(baseUrl + '/api/status', { cache: 'no-store' })
    .then(r => r.json())
    .then(render)
    .catch(e => render({ sessions: [], error: e.message }));
}

document.addEventListener('DOMContentLoaded', () => {
  poll();
  setInterval(poll, 2000);
});
