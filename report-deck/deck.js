/* report-deck: builds a top-right "Slides" button and a slide deck from <script type="application/json" id="deck-data">. */
(function () {
  var src = document.getElementById("deck-data");
  if (!src) return;
  var deck;
  try { deck = JSON.parse(src.textContent); } catch (e) { console.error("report-deck: bad deck-data JSON", e); return; }
  var slides = deck.slides || [];
  if (!slides.length) return;

  function h(tag, cls, html) {
    var el = document.createElement(tag);
    if (cls) el.className = cls;
    if (html != null) el.innerHTML = html;
    return el;
  }

  document.body.classList.add("dk-ready");
  var btn = h("button", "dk-btn", '<svg viewBox="0 0 10 10"><path d="M2 1l7 4-7 4z"/></svg>Slides');
  btn.type = "button";
  btn.setAttribute("aria-label", "Open slide version");
  document.body.appendChild(btn);

  var root = h("div", "dk");
  root.setAttribute("role", "dialog");
  root.setAttribute("aria-modal", "true");
  var top = h("div", "dk-top");
  var title = h("b", null, deck.title || document.title);
  var count = h("span");
  var close = h("button", "dk-x", "&times;");
  close.setAttribute("aria-label", "Close slides");
  var left = h("div");
  left.style.cssText = "display:flex;gap:12px;align-items:center;min-width:0";
  left.appendChild(title);
  left.appendChild(count);
  top.appendChild(left);
  top.appendChild(close);
  var stage = h("div", "dk-stage");
  var nav = h("div", "dk-nav");
  var prev = h("button", null, "Back");
  var next = h("button", null, "Next");
  var dots = h("div", "dk-dots");
  nav.appendChild(prev);
  nav.appendChild(dots);
  nav.appendChild(next);
  root.appendChild(top);
  root.appendChild(stage);
  root.appendChild(nav);
  document.body.appendChild(root);

  slides.forEach(function (_, i) {
    var d = h("button");
    d.setAttribute("aria-label", "Slide " + (i + 1));
    d.onclick = function () { show(i); };
    dots.appendChild(d);
  });

  var at = 0;
  function render(s) {
    var el = h("div", "dk-slide");
    if (s.kicker) el.appendChild(h("p", "dk-kicker", s.kicker));
    el.appendChild(h("h2", null, s.title || ""));
    if (s.tag) el.appendChild(h("span", "dk-tag " + (s.tag.tone || "warn"), s.tag.text));
    if (s.points && s.points.length) {
      var ul = h("ul", "dk-points");
      s.points.forEach(function (p) { ul.appendChild(h("li", null, p)); });
      el.appendChild(ul);
    }
    if (s.visual) el.appendChild(h("div", "dk-visual", s.visual));
    if (s.details && s.details.length) {
      var box = h("div", "dk-details");
      s.details.forEach(function (d) {
        var det = h("details");
        det.appendChild(h("summary", null, d.label));
        det.appendChild(h("div", "dk-body", d.body));
        box.appendChild(det);
      });
      el.appendChild(box);
    }
    Array.prototype.forEach.call(el.querySelectorAll("table"), function (t) {
      if (t.parentNode.classList.contains("dk-scroll")) return;
      var wrap = h("div", "dk-scroll");
      t.parentNode.insertBefore(wrap, t);
      wrap.appendChild(t);
    });
    return el;
  }
  function show(i) {
    at = Math.max(0, Math.min(slides.length - 1, i));
    stage.innerHTML = "";
    stage.appendChild(render(slides[at]));
    stage.scrollTop = 0;
    count.textContent = at + 1 + " / " + slides.length;
    prev.disabled = at === 0;
    next.textContent = at === slides.length - 1 ? "Done" : "Next";
    Array.prototype.forEach.call(dots.children, function (d, j) { d.setAttribute("aria-current", j === at ? "true" : "false"); });
    try { history.replaceState(null, "", "#slides-" + (at + 1)); } catch (e) {}
  }
  function open(i) {
    root.classList.add("open");
    document.documentElement.classList.add("dk-lock");
    show(i || 0);
    next.focus();
  }
  function shut() {
    root.classList.remove("open");
    document.documentElement.classList.remove("dk-lock");
    try { history.replaceState(null, "", location.pathname + location.search); } catch (e) {}
    btn.focus();
  }
  btn.onclick = function () { open(0); };
  close.onclick = shut;
  prev.onclick = function () { show(at - 1); };
  next.onclick = function () { at === slides.length - 1 ? shut() : show(at + 1); };
  document.addEventListener("keydown", function (e) {
    if (!root.classList.contains("open")) return;
    if (e.key === "Escape") shut();
    else if (e.key === "ArrowRight" || e.key === "PageDown") show(at + 1);
    else if (e.key === "ArrowLeft" || e.key === "PageUp") show(at - 1);
  });
  var sx = 0, sy = 0;
  stage.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
  stage.addEventListener("touchend", function (e) {
    var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) show(at + (dx < 0 ? 1 : -1));
  }, { passive: true });
  var m = /^#slides(?:-(\d+))?$/.exec(location.hash);
  if (m) open(m[1] ? Number(m[1]) - 1 : 0);
})();
