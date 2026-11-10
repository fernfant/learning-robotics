// Draws Robo-Helper's room as a picture. Use: <div class="room" data-robot="1,1" data-path="1,1 2,1 3,1"
//   data-cat="4,1" data-blocks="red:2,1 blue:6,3 green:1,5" data-label="Week 1: it bumps the cat"></div>
// Optional: data-room="##########|#........#|..." (rows joined by |), data-mark="4,1" (a red ring), data-est="x,y" (metres: a guess).
(function () {
  const ROOM = ["##########", "#........#", "#..##....#", "#..#.....#", "#....##..#", "#........#", "#.#....B.#", "##########"];
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const pt = s => s.split(",").map(Number);
  const list = s => (s || "").trim().split(/\s+/).filter(Boolean);
  function draw(el) {
    const room = el.dataset.room ? el.dataset.room.split("|") : ROOM;
    const S = 40, W = room[0].length * S, H = room.length * S;
    const colour = { red: "#e5484d", blue: "#3e7bfa", green: "#30a46c" };
    let g = "";
    room.forEach((row, y) => [...row].forEach((ch, x) => {
      g += `<rect x="${x * S}" y="${y * S}" width="${S}" height="${S}" fill="${ch === "#" ? css("--wall") : ch === "?" ? css("--line") : css("--floor")}" stroke="${css("--line")}" stroke-width="1"/>`;
      if (ch === "B") g += `<text x="${x * S + S / 2}" y="${y * S + S * 0.7}" font-size="24" text-anchor="middle">🪣</text>`;
    }));
    const path = list(el.dataset.path).map(pt);
    if (path.length > 1) g += `<polyline points="${path.map(([x, y]) => `${x * S + S / 2},${y * S + S / 2}`).join(" ")}" fill="none" stroke="${css("--path")}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>`;
    list(el.dataset.blocks).forEach(b => { const [c, p] = b.split(":"); const [x, y] = pt(p);
      g += `<rect x="${x * S + 9}" y="${y * S + 9}" width="${S - 18}" height="${S - 18}" rx="4" fill="${colour[c] || c}"/>`; });
    if (el.dataset.cat) { const [x, y] = pt(el.dataset.cat); g += `<text x="${x * S + S / 2}" y="${y * S + S * 0.72}" font-size="26" text-anchor="middle">🐱</text>`; }
    if (el.dataset.mark) list(el.dataset.mark).forEach(m => { const [x, y] = pt(m);
      g += `<circle cx="${x * S + S / 2}" cy="${y * S + S / 2}" r="${S * 0.46}" fill="none" stroke="#e5484d" stroke-width="3"/>`; });
    if (el.dataset.est) { const [x, y] = pt(el.dataset.est); const px = x / 0.5 * S, py = y / 0.5 * S;
      g += `<circle cx="${px}" cy="${py}" r="9" fill="none" stroke="${css("--idea")}" stroke-width="3" stroke-dasharray="4 3"/>`; }
    if (el.dataset.robot) { const [x, y] = pt(el.dataset.robot); g += `<text x="${x * S + S / 2}" y="${y * S + S * 0.72}" font-size="26" text-anchor="middle">🤖</text>`; }
    const label = el.dataset.label ? `<p class="room-caption">${el.dataset.label}</p>` : "";
    el.innerHTML = `<svg class="room-pic" viewBox="0 0 ${W} ${H}" role="img" aria-label="${(el.dataset.label || "Robo-Helper's room").replace(/"/g, "")}">${g}</svg>${label}`;
  }
  const all = () => document.querySelectorAll(".room").forEach(draw);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", all); else all();
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", all);
  window.drawRoom = draw;
})();
