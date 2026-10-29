/* Autofy run dashboard — reads data/stats.json (deploy/autofy-stats.py). No deps. */
(function () {
  "use strict";

  var SCRIPTS = [
    { name: "Backup", file: "Backup.py", cron: "täglich 03:00", maxAgeH: 26 },
    { name: "Dubstep", file: "Dubstep.py", cron: "Mo 04:00", maxAgeH: 24 * 7 + 2 },
    { name: "LoFi", file: "LoFi.py", cron: "Mo 04:30", maxAgeH: 24 * 7 + 2 },
  ];
  var STATUS_DE = {
    ok: "ok", partial: "teilweise", failed: "fehlgeschlagen", added: "neu", uptodate: "aktuell",
    skipped: "übersprungen", error: "Fehler", no_tracks: "keine Tracks", failing: "fehlerhaft", stale: "entfernt",
  };
  var REFRESH_MS = 5 * 60 * 1000;

  var state = {
    data: null, range: 30, target: null,
    tSort: { key: "name", asc: true }, histLimit: 50,
  };

  // ---------- helpers ----------
  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function d(iso) { var t = iso ? new Date(iso) : null; return t && !isNaN(t) ? t : null; }
  function fmtDate(iso, withYear) {
    var t = d(iso); if (!t) return "–";
    return t.toLocaleString("de-DE", {
      day: "2-digit", month: "2-digit", year: withYear ? "numeric" : undefined, hour: "2-digit", minute: "2-digit",
    });
  }
  function fmtDay(iso) { var t = d(iso); return t ? t.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" }) : ""; }
  function ago(iso) {
    var t = d(iso); if (!t) return "nie";
    var s = (Date.now() - t.getTime()) / 1000;
    if (s < 0) return "gerade eben";
    if (s < 90) return "vor " + Math.round(s) + " s";
    if (s < 5400) return "vor " + Math.round(s / 60) + " min";
    if (s < 36 * 3600) return "vor " + Math.round(s / 3600) + " h";
    return "vor " + Math.round(s / 86400) + " Tagen";
  }
  function ageH(iso) { var t = d(iso); return t ? (Date.now() - t.getTime()) / 3600000 : Infinity; }
  function dur(s) {
    if (s == null || isNaN(s)) return "–";
    s = Number(s);
    if (s < 60) return s.toFixed(s < 10 ? 1 : 0) + " s";
    var m = Math.floor(s / 60), r = Math.round(s % 60);
    return m < 60 ? m + " min " + r + " s" : Math.floor(m / 60) + " h " + (m % 60) + " min";
  }
  function n(v) { return (Number(v) || 0).toLocaleString("de-DE"); }
  function badge(status, label) {
    var st = status || "none";
    return '<span class="badge b-' + esc(st) + '">' + esc(label || STATUS_DE[st] || st || "–") + "</span>";
  }
  function spotifyLink(id) {
    var m = String(id || "").match(/([A-Za-z0-9]{22})/);
    var short = String(id || "");
    if (!m) return '<span class="id">' + esc(short) + "</span>";
    return '<a class="id" href="https://open.spotify.com/playlist/' + m[1] + '" target="_blank" rel="noreferrer">' + esc(m[1]) + "</a>";
  }
  function errText(e) {
    if (!e) return "";
    return (e.http ? "[" + e.http + "] " : "") + (e.type && e.type !== "str" ? e.type + ": " : "") + (e.msg || "");
  }
  function script(name) {
    var s = state.data && state.data.scripts && state.data.scripts[name];
    return s || { runs_total: 0, history: [], targets: [], sources: [] };
  }

  // ---------- tooltip ----------
  var tip = $("tip");
  function showTip(html, ev) {
    tip.innerHTML = html; tip.hidden = false;
    var x = ev.clientX + 14, y = ev.clientY + 14, r = tip.getBoundingClientRect();
    if (x + r.width > window.innerWidth - 8) x = ev.clientX - r.width - 14;
    if (y + r.height > window.innerHeight - 8) y = ev.clientY - r.height - 14;
    tip.style.left = Math.max(8, x) + "px"; tip.style.top = Math.max(8, y) + "px";
  }
  function hideTip() { tip.hidden = true; }
  function row(l, v) { return '<div class="row"><span>' + esc(l) + "</span><span>" + esc(v) + "</span></div>"; }
  function runTip(r) {
    return "<b>" + esc(fmtDate(r.start, true)) + "</b>" +
      row("Status", STATUS_DE[r.status] || r.status) + row("Tracks neu", n(r.added)) +
      row("Dauer", dur(r.duration_s)) + row("Exit", r.exit_code == null ? "–" : r.exit_code) +
      (r.failed_sources ? row("Quellen fehlerhaft", r.failed_sources) : "") +
      (r.errors && r.errors.length ? '<div class="row"><span>' + esc(errText(r.errors[0]).slice(0, 120)) + "</span></div>" : "");
  }

  // ---------- cards ----------
  function renderCards() {
    var html = SCRIPTS.map(function (sc) {
      var s = script(sc.name), last = s.last;
      if (!last) {
        return '<article class="card"><div class="card-head"><span class="card-title">' + esc(sc.file) +
          "</span>" + badge("none", "kein Lauf") + '</div><div class="card-when muted">noch nie</div>' +
          '<dl><dt>Zeitplan</dt><dd>' + esc(sc.cron) + "</dd></dl></article>";
      }
      var stale = ageH(last.start) > sc.maxAgeH;
      var cls = "card" + (last.status === "failed" ? " is-failed" : stale ? " is-stale" : "");
      var streak = s.streak && s.streak.count > 1 ? s.streak.count + "× " + (STATUS_DE[s.streak.status] || s.streak.status) : "–";
      var err = last.errors && last.errors[0];
      return '<article class="' + cls + '">' +
        '<div class="card-head"><span class="card-title">' + esc(sc.file) + "</span>" + badge(last.status) + "</div>" +
        '<div class="card-when" title="' + esc(fmtDate(last.start, true)) + '">' + esc(ago(last.start)) + "</div>" +
        "<dl>" +
        "<dt>Start</dt><dd>" + esc(fmtDate(last.start, true)) + "</dd>" +
        "<dt>Dauer</dt><dd>" + esc(dur(last.duration_s)) + "</dd>" +
        "<dt>Exit</dt><dd>" + esc(last.exit_code == null ? "–" : last.exit_code) + "</dd>" +
        "<dt>Tracks</dt><dd>" + n(last.added) + "</dd>" +
        (last.failed_sources ? "<dt>Quellen ✕</dt><dd>" + n(last.failed_sources) + "</dd>" : "") +
        "<dt>Serie</dt><dd>" + esc(streak) + "</dd>" +
        "<dt>Letzter Erfolg</dt><dd>" + esc(s.last_ok ? ago(s.last_ok) : "nie") + "</dd>" +
        "<dt>Läufe</dt><dd>" + n(s.runs_total) + " &middot; " + esc(sc.cron) + "</dd>" +
        "</dl>" +
        (stale ? '<div class="warn">⚠ überfällig — erwartet ' + esc(sc.cron) + "</div>" : "") +
        (err ? '<div class="err">' + esc(errText(err)) + (last.errors_n > 1 ? " (+" + (last.errors_n - 1) + ")" : "") + "</div>" : "") +
        "</article>";
    }).join("");
    $("cards").innerHTML = html;
  }

  // ---------- backup chart ----------
  function windowRuns() {
    var h = script("Backup").history || [];
    return state.range ? h.slice(-state.range) : h.slice();
  }
  function niceMax(v) {
    if (v <= 5) return 5;
    var p = Math.pow(10, Math.floor(Math.log10(v))), m = v / p;
    return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 5 ? 5 : 10) * p;
  }

  function renderKpis(runs) {
    var total = 0, ok = 0, durs = [];
    runs.forEach(function (r) {
      total += r.added || 0;
      if (r.status === "ok") ok++;
      if (r.duration_s != null) durs.push(r.duration_s);
    });
    var avgDur = durs.length ? durs.reduce(function (a, b) { return a + b; }, 0) / durs.length : null;
    var failing = (script("Backup").sources || []).filter(function (s) { return s.current && s.consecutive_failures; }).length;
    var k = [
      [n(total), "Tracks gesichert (" + runs.length + " Läufe)"],
      [runs.length ? Math.round((ok / runs.length) * 100) + " %" : "–", "Läufe ohne Fehler"],
      [dur(avgDur), "Ø Dauer"],
      [n(failing), "Quellen aktuell fehlerhaft"],
    ];
    $("kpis").innerHTML = k.map(function (x) {
      return '<div class="kpi"><div class="v">' + esc(x[0]) + '</div><div class="l">' + esc(x[1]) + "</div></div>";
    }).join("");
  }

  function renderChart(runs) {
    var el = $("chart-added");
    var W = Math.max(280, el.clientWidth || 600), H = el.clientHeight || 200;
    var padL = 36, padR = 6, padT = 8, padB = 22;
    var iw = W - padL - padR, ih = H - padT - padB;
    if (!runs.length) { el.innerHTML = '<p class="muted small">Keine Backup-Läufe im Zeitraum.</p>'; return; }
    var max = niceMax(Math.max.apply(null, runs.map(function (r) { return r.added || 0; })));
    var step = iw / runs.length, bw = Math.max(1, Math.min(28, step - 2));
    var y = function (v) { return padT + ih - (v / max) * ih; };
    var parts = ['<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Tracks gesichert pro Backup-Lauf">'];
    parts.push('<g class="grid">');
    [0, 0.5, 1].forEach(function (f) {
      var v = max * f, yy = y(v).toFixed(1);
      parts.push('<line x1="' + padL + '" x2="' + (W - padR) + '" y1="' + yy + '" y2="' + yy + '"/>');
    });
    parts.push('</g><g class="axis">');
    [0, 0.5, 1].forEach(function (f) {
      var v = max * f;
      parts.push('<text x="' + (padL - 6) + '" y="' + (y(v) + 4).toFixed(1) + '" text-anchor="end">' + n(v) + "</text>");
    });
    var labelIdx = runs.length <= 1 ? [0] : [0, Math.floor((runs.length - 1) / 2), runs.length - 1];
    labelIdx.forEach(function (i, j) {
      var x = padL + step * i + step / 2;
      var anchor = j === 0 ? "start" : j === labelIdx.length - 1 ? "end" : "middle";
      if (labelIdx.length === 1) anchor = "middle";
      parts.push('<text x="' + (anchor === "start" ? padL : anchor === "end" ? W - padR : x).toFixed(1) + '" y="' + (H - 6) + '" text-anchor="' + anchor + '">' + esc(fmtDay(runs[i].start)) + "</text>");
    });
    parts.push("</g><g>");
    runs.forEach(function (r, i) {
      var x = padL + step * i + (step - bw) / 2, base = padT + ih;
      parts.push('<rect class="hit" data-i="' + i + '" x="' + (padL + step * i).toFixed(1) + '" y="' + padT + '" width="' + step.toFixed(1) + '" height="' + ih + '"/>');
      if (r.status === "failed") {
        parts.push('<rect class="fail-mark" x="' + x.toFixed(1) + '" y="' + (base - 4) + '" width="' + bw.toFixed(1) + '" height="4" rx="1"/>');
      } else if (!r.added) {
        parts.push('<rect class="zero-mark" x="' + x.toFixed(1) + '" y="' + (base - 2) + '" width="' + bw.toFixed(1) + '" height="2" rx="1"/>');
      } else {
        var top = y(r.added), h = Math.max(2, base - top);
        parts.push('<rect class="bar" x="' + x.toFixed(1) + '" y="' + (base - h).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + h.toFixed(1) + '" rx="' + Math.min(4, bw / 2).toFixed(1) + '"/>');
      }
    });
    parts.push("</g></svg>");
    el.innerHTML = parts.join("");
    el.querySelectorAll(".hit").forEach(function (h) {
      h.addEventListener("mousemove", function (ev) {
        var r = runs[+h.getAttribute("data-i")];
        if (r) showTip(runTip(r), ev);
        var bar = h.nextElementSibling; if (bar) bar.classList.add("hover");
      });
      h.addEventListener("mouseleave", function () {
        hideTip(); var bar = h.nextElementSibling; if (bar) bar.classList.remove("hover");
      });
    });
  }

  function renderStrip(runs) {
    var el = $("strip");
    el.innerHTML = runs.map(function (r, i) {
      return '<span class="s-' + esc(r.status) + '" data-i="' + i + '" aria-label="' + esc(fmtDate(r.start) + " " + (STATUS_DE[r.status] || r.status)) + '"></span>';
    }).join("");
    el.querySelectorAll("span").forEach(function (s) {
      s.addEventListener("mousemove", function (ev) { showTip(runTip(runs[+s.getAttribute("data-i")]), ev); });
      s.addEventListener("mouseleave", hideTip);
    });
  }

  // ---------- targets ----------
  function sparkline(series, since) {
    var pts = series.filter(function (p) { return !since || String(p[0]) >= since; }).slice(-90);
    if (!pts.length) return "";
    var W = 120, H = 22, max = Math.max(1, Math.max.apply(null, pts.map(function (p) { return p[1] || 0; })));
    var step = W / pts.length, bw = Math.max(1, step - 1);
    return '<svg class="spark" viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" aria-hidden="true">' +
      pts.map(function (p, i) {
        var v = p[1] || 0, h = v ? Math.max(2, (v / max) * H) : 1.5;
        var cls = p[2] === "error" ? "f" : v ? "" : "z";
        return '<rect class="' + cls + '" x="' + (i * step).toFixed(2) + '" y="' + (H - h).toFixed(2) + '" width="' + bw.toFixed(2) + '" height="' + h.toFixed(2) + '"><title>' +
          esc(fmtDay(p[0]) + ": " + v) + "</title></rect>";
      }).join("") + "</svg>";
  }

  function renderTargets(runs) {
    var since = runs.length ? String(runs[0].start) : null;
    var rows = (script("Backup").targets || []).map(function (t) {
      var ra = 0;
      (t.series || []).forEach(function (p) { if (!since || String(p[0]) >= since) ra += p[1] || 0; });
      return Object.assign({}, t, { range_added: ra });
    });
    var k = state.tSort.key, asc = state.tSort.asc ? 1 : -1;
    rows.sort(function (a, b) {
      if (a.current !== b.current) return a.current ? -1 : 1;
      var x = a[k], y = b[k];
      if (typeof x === "string" || typeof y === "string") return String(x || "").localeCompare(String(y || ""), "de") * asc;
      return ((x || 0) - (y || 0)) * asc;
    });
    document.querySelectorAll("#targets th[data-sort]").forEach(function (th) {
      th.classList.toggle("sorted", th.getAttribute("data-sort") === k);
      th.classList.toggle("asc", th.getAttribute("data-sort") === k && state.tSort.asc);
    });
    var tb = $("targets").tBodies[0];
    if (!rows.length) { tb.innerHTML = '<tr><td colspan="6" class="muted">Noch keine Ziel-Playlists aufgezeichnet.</td></tr>'; return; }
    tb.innerHTML = rows.map(function (t) {
      var src = t.sources_n == null ? "–" : (t.failing_n ? '<span class="fail-n" title="fehlerhaft">' + n(t.failing_n) + " ✕</span> / " : "") + n(t.sources_n);
      return '<tr class="clickable' + (t.current ? "" : " stale") + (state.target === t.name ? " sel" : "") + '" tabindex="0" data-name="' + esc(t.name) + '">' +
        '<td><div class="name">' + esc(t.name) + "</div>" + (t.set ? spotifyLink(t.set) : "") + "</td>" +
        "<td>" + (t.current ? badge(t.last_status) : badge("stale")) + "</td>" +
        '<td class="num">' + n(t.range_added) + '<div class="muted small">gesamt ' + n(t.total_added) + "</div></td>" +
        '<td class="spark-col">' + sparkline(t.series || [], since) + "</td>" +
        '<td class="nowrap">' + esc(t.last_added_at ? fmtDate(t.last_added_at) : "–") + "</td>" +
        '<td class="num">' + src + "</td></tr>";
    }).join("");
    tb.querySelectorAll("tr[data-name]").forEach(function (tr) {
      var pick = function () {
        var nm = tr.getAttribute("data-name");
        state.target = state.target === nm ? null : nm;
        renderTargets(windowRuns()); renderSources();
      };
      tr.addEventListener("click", function (ev) { if (!ev.target.closest("a")) pick(); });
      tr.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); pick(); } });
    });
  }

  // ---------- sources ----------
  function renderSources() {
    var onlyFail = $("only-failing").checked, stale = $("show-stale").checked;
    var all = script("Backup").sources || [];
    var rows = all.filter(function (s) {
      if (state.target && s.target !== state.target) return false;
      if (!stale && !s.current) return false;
      if (onlyFail && !s.consecutive_failures) return false;
      return true;
    });
    var chip = $("target-filter");
    chip.hidden = !state.target; chip.textContent = state.target || "";
    var tb = $("sources").tBodies[0], empty = $("sources-empty");
    tb.innerHTML = rows.map(function (s) {
      var st = !s.current ? "stale" : s.consecutive_failures ? "failing" : "ok";
      return '<tr class="' + (s.current ? "" : "stale") + '">' +
        "<td>" + esc(s.target) + "</td>" +
        "<td>" + spotifyLink(s.id) + (s.tracks != null ? '<div class="muted small">' + n(s.tracks) + " Tracks</div>" : "") + "</td>" +
        "<td>" + badge(st) + "</td>" +
        '<td class="num">' + (s.consecutive_failures ? n(s.consecutive_failures) : "–") +
        '<div class="muted small">' + n(s.fail_total) + " / " + n(s.seen) + " gesamt</div></td>" +
        '<td class="nowrap">' + esc(s.failing_since ? fmtDate(s.failing_since) : "–") + "</td>" +
        '<td class="nowrap">' + esc(s.last_success ? fmtDate(s.last_success) + " (" + ago(s.last_success) + ")" : "nie") + "</td>" +
        '<td class="errmsg">' + esc(s.last_error ? errText(s.last_error) : "") +
        (s.last_error_at && !s.consecutive_failures ? '<div class="muted small">' + esc(fmtDate(s.last_error_at)) + "</div>" : "") + "</td></tr>";
    }).join("");
    empty.hidden = rows.length > 0;
    empty.textContent = !all.length ? "Noch keine Quell-Playlists aufgezeichnet."
      : onlyFail ? "✓ Keine fehlerhaften Quellen" + (state.target ? " in „" + state.target + "“" : "") + "."
      : "Keine Einträge für diesen Filter.";
  }

  // ---------- history ----------
  function renderHistory() {
    var fs = $("hist-script").value, fst = $("hist-status").value;
    var all = [];
    SCRIPTS.concat(Object.keys((state.data && state.data.scripts) || {})
      .filter(function (k) { return !SCRIPTS.some(function (s) { return s.name === k; }); })
      .map(function (k) { return { name: k }; }))
      .forEach(function (sc) {
        (script(sc.name).history || []).forEach(function (r) { all.push(Object.assign({ script: sc.name }, r)); });
      });
    all = all.filter(function (r) { return (!fs || r.script === fs) && (!fst || r.status === fst); });
    all.sort(function (a, b) { return String(b.start).localeCompare(String(a.start)); });
    var shown = all.slice(0, state.histLimit);
    var tb = $("history").tBodies[0];
    tb.innerHTML = shown.length ? shown.map(function (r) {
      var errs = r.errors || [], e = "";
      if (errs.length === 1 && r.errors_n <= 1) e = '<span class="errmsg">' + esc(errText(errs[0])) + "</span>";
      else if (errs.length) {
        e = "<details><summary>" + n(r.errors_n) + " Fehler</summary><ul>" + errs.map(function (x) {
          return "<li>" + esc((x.target ? x.target + ": " : "") + errText(x)) + "</li>";
        }).join("") + (r.errors_n > errs.length ? "<li>…</li>" : "") + "</ul></details>";
      } else if (r.failed_sources) e = '<span class="muted">' + n(r.failed_sources) + " Quelle(n) fehlerhaft</span>";
      return "<tr>" +
        '<td class="nowrap">' + esc(fmtDate(r.start, true)) + "</td>" +
        "<td>" + esc(r.script) + "</td>" +
        "<td>" + badge(r.status) + "</td>" +
        '<td class="num nowrap">' + esc(dur(r.duration_s)) + "</td>" +
        '<td class="num">' + esc(r.exit_code == null ? "–" : r.exit_code) + "</td>" +
        '<td class="num">' + n(r.added) + "</td>" +
        "<td>" + e + "</td></tr>";
    }).join("") : '<tr><td colspan="7" class="muted">Keine Läufe für diesen Filter.</td></tr>';
    var more = $("hist-more");
    more.hidden = all.length <= state.histLimit;
    more.textContent = "mehr anzeigen (" + (all.length - shown.length) + " weitere)";
  }

  // ---------- main ----------
  function renderBackup() {
    var runs = windowRuns();
    renderKpis(runs); renderChart(runs); renderStrip(runs); renderTargets(runs); renderSources();
  }

  function render() {
    var data = state.data, total = data ? data.runs_total || 0 : 0;
    $("generated").textContent = data && data.generated ? "Stand " + fmtDate(data.generated) + " (" + ago(data.generated) + ")" : "keine Daten";
    $("empty").hidden = total > 0;
    renderCards();
    var hasBackup = script("Backup").runs_total > 0;
    ["backup", "targets-panel", "sources-panel"].forEach(function (id) { $(id).hidden = !hasBackup; });
    $("history-panel").hidden = total === 0;
    var sel = $("hist-script");
    if (sel.options.length === 1 && data) {
      Object.keys(data.scripts || {}).forEach(function (k) {
        var o = document.createElement("option"); o.value = k; o.textContent = k; sel.appendChild(o);
      });
    }
    if (hasBackup) renderBackup();
    if (total) renderHistory();
  }

  function banner(msg) { var b = $("banner"); b.hidden = !msg; b.textContent = msg || ""; }

  function load() {
    return fetch("data/stats.json?t=" + Date.now(), { cache: "no-store" })
      .then(function (r) {
        if (r.status === 404) return null;
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (j) {
        state.data = j;
        banner(j ? (j.schema !== 1 ? "Unbekanntes stats.json-Schema " + j.schema + " — Seite evtl. veraltet." : "")
          : "data/stats.json fehlt — läuft der autofy-Container (deploy/autofy.yml)?");
        render();
      })
      .catch(function (e) {
        banner("stats.json konnte nicht geladen werden: " + e.message);
        if (!state.data) render();
      });
  }

  // events
  $("range").addEventListener("click", function (ev) {
    var b = ev.target.closest("button"); if (!b) return;
    state.range = +b.getAttribute("data-n");
    this.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === b); });
    renderBackup();
  });
  document.querySelectorAll("#targets th[data-sort]").forEach(function (th) {
    th.addEventListener("click", function () {
      var k = th.getAttribute("data-sort");
      state.tSort = { key: k, asc: state.tSort.key === k ? !state.tSort.asc : k === "name" };
      renderTargets(windowRuns());
    });
  });
  $("only-failing").addEventListener("change", renderSources);
  $("show-stale").addEventListener("change", renderSources);
  $("target-filter").addEventListener("click", function () { state.target = null; renderTargets(windowRuns()); renderSources(); });
  $("hist-script").addEventListener("change", function () { state.histLimit = 50; renderHistory(); });
  $("hist-status").addEventListener("change", function () { state.histLimit = 50; renderHistory(); });
  $("hist-more").addEventListener("click", function () { state.histLimit += 100; renderHistory(); });
  $("reload").addEventListener("click", load);
  var rz;
  window.addEventListener("resize", function () {
    clearTimeout(rz);
    rz = setTimeout(function () { if (script("Backup").runs_total) renderChart(windowRuns()); }, 150);
  });
  document.addEventListener("scroll", hideTip, { passive: true });

  load();
  setInterval(load, REFRESH_MS);
})();
