// ── RANKS ─────────────────────────────────────────────────────────────────────
const RANKS = [
  [200, "🏆 LEGEND", "LEGEND"],
  [100, "💎 ELITE", "ELITE"],
  [50, "🌟 PRO", "PRO"],
  [20, "🍎 HEALTHY", "HEALTHY"],
  [0, "😐 NEUTRAL", "NEUTRAL"],
  [-50, "🍪 SNACKER", "SNACKER"],
  [-999, "💀 JUNK LORD", "JUNK"],
];

function getRank(score) {
  for (const [threshold, name, cls] of RANKS)
    if (score >= threshold) return [name, cls];
  return RANKS[RANKS.length - 1].slice(1);
}

// ── STATE ─────────────────────────────────────────────────────────────────────
let state = { score: 0, apples: 0, cookies: 0, streak: 0, log: [] };

// ── CLOCK ─────────────────────────────────────────────────────────────────────
function tickClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('en-CA', { hour12: false });
  const ds = now.toLocaleDateString('en-CA', { weekday: 'long', month: 'long', day: 'numeric' });
  document.getElementById('cam-date').textContent = ds;
  document.getElementById('foot-date').textContent =
    now.toLocaleDateString('en-CA', { year: 'numeric', month: 'long', day: 'numeric' });
}
setInterval(tickClock, 1000); tickClock();

// ── UI UPDATE ─────────────────────────────────────────────────────────────────
function updateUI(s) {
  const score = s.score;
  const [rankName, rankCls] = getRank(score);

  // Score number
  document.getElementById('score-num').textContent = score > 0 ? `+${score}` : score;
  document.querySelector('.score-center').style.color =
    score > 0 ? 'var(--apple)' : score < 0 ? 'var(--cookie)' : 'var(--text)';

  // Ring
  const pct = Math.max(0, Math.min(1, (score + 100) / 300));
  const circ = 2 * Math.PI * 54;
  const fill = document.getElementById('ring-fill');
  fill.style.strokeDashoffset = circ * (1 - pct);
  fill.style.stroke = score >= 0 ? 'var(--apple)' : 'var(--cookie)';

  // Rank badge
  const badge = document.getElementById('rank-badge');
  badge.textContent = rankName;
  badge.className = `rank-badge rank-${rankCls}`;

  // Counts
  document.getElementById('apple-count').textContent = s.apples;
  document.getElementById('cookie-count').textContent = s.cookies;

  // Goal bar
  const goalPct = Math.max(0, Math.min(1, score / 100));
  document.getElementById('goal-bar').style.width = (goalPct * 100) + '%';
  document.getElementById('goal-val').textContent = Math.round(goalPct * 100) + '%';
  document.getElementById('goal-bar').style.background =
    goalPct >= 1 ? 'var(--apple)' : 'var(--gold)';

  // Health bar
  const hPct = Math.max(0, Math.min(1, (score + 100) / 300));
  document.getElementById('health-bar').style.width = (hPct * 100) + '%';
  document.getElementById('health-val').textContent = Math.round(hPct * 100) + '%';
  document.getElementById('health-bar').style.background =
    hPct > 0.55 ? 'var(--apple)' : hPct > 0.3 ? 'var(--gold)' : 'var(--cookie)';

  // Streak
  const sv = document.getElementById('streak-val');
  sv.textContent = Math.abs(s.streak);
  sv.style.color = s.streak >= 0 ? 'var(--apple)' : 'var(--cookie)';

  // Live dot
  document.getElementById('live-dot').className = 'status-dot live';
  document.getElementById('live-label').textContent = 'LIVE';

  // Eating state
  const eating = s.eating;
  const isApple = s.last_item && s.last_item.toLowerCase() === 'apple';
  const flash = document.getElementById('eat-flash');
  const eatDot = document.getElementById('eat-dot');
  const eatLabel = document.getElementById('eat-label');
  const camWrap = document.getElementById('cam-wrap');

  if (eating) {
    flash.className = 'eat-flash ' + (isApple ? 'eating-apple' : 'eating-cookie');
    eatDot.className = 'status-dot eating';
    eatLabel.textContent = isApple ? '🍎 EATING' : '🍪 EATING';
    camWrap.classList.add('eating-active');
  } else {
    flash.className = 'eat-flash';
    eatDot.className = 'status-dot';
    eatLabel.textContent = s.snack_detected ? `👁 ${s.snack_detected.toUpperCase()} DETECTED` : 'IDLE';
    camWrap.classList.remove('eating-active');
  }

  // Cam detect label
  const cdl = document.getElementById('cam-detect-label');
  if (eating) {
    cdl.textContent = isApple ? '🍎 Apple bite confirmed!' : '🍪 Cookie bite detected!';
    cdl.style.color = isApple ? 'var(--apple)' : 'var(--cookie)';
  } else if (s.snack_detected) {
    cdl.textContent = `👁 ${s.snack_detected} in frame — bring closer to mouth`;
    cdl.style.color = 'var(--muted)';
  } else if (s.face_detected) {
    cdl.textContent = '😊 Face detected — show a snack!';
    cdl.style.color = 'var(--teal)';
  } else {
    cdl.textContent = 'Waiting for face + snack…';
    cdl.style.color = 'var(--muted)';
  }

  // Rebuild feed if log changed
  if (s.log && s.log.length !== state.log.length) {
    rebuildFeed(s.log);
  }

  state = s;
}

// ── FEED ─────────────────────────────────────────────────────────────────────
function rebuildFeed(log) {
  const el = document.getElementById('feed-list');
  if (!log || !log.length) return;
  el.innerHTML = '';
  const items = [...log].reverse().slice(0, 30);
  for (const entry of items) {
    const isA = entry.item.toLowerCase() === 'apple';
    const div = document.createElement('div');
    div.className = 'feed-item';
    div.innerHTML = `
      <span class="feed-emoji">${isA ? '🍎' : '🍪'}</span>
      <span class="feed-label">${entry.item}</span>
      <span class="feed-time">${entry.time}</span>
      <span class="feed-pts ${isA ? 'apple' : 'cookie'}">${entry.pts > 0 ? '+' : ''}${entry.pts}</span>
    `;
    el.prepend(div);
  }
}

// ── TOAST ─────────────────────────────────────────────────────────────────────
function showToast(item, pts) {
  const isA = item.toLowerCase() === 'apple';
  const container = document.getElementById('toasts');
  const t = document.createElement('div');
  t.className = `toast ${isA ? 'apple' : 'cookie'}`;
  const messages = isA
    ? ["Great choice! 💪", "Body fuel! ⚡", "Keep it up! 🌱", "Power move! 🏋️"]
    : ["Treat yourself…", "Sugar rush! ⚠️", "Watch those points!", "Junk alert! 🚨"];
  const msg = messages[Math.floor(Math.random() * messages.length)];
  t.innerHTML = `
    <span class="toast-icon">${isA ? '🍎' : '🍪'}</span>
    <div class="toast-text">
      <div style="font-weight:600">${msg}</div>
      <div style="font-size:0.72rem;color:var(--muted);margin-top:2px">${item} bite detected</div>
    </div>
    <span class="toast-pts ${isA ? 'apple' : 'cookie'}">${pts > 0 ? '+' : ''}${pts}</span>
  `;
  container.appendChild(t);
  spawnParticles(isA);
  setTimeout(() => {
    t.classList.add('out');
    setTimeout(() => t.remove(), 350);
  }, 3000);
}

// ── PARTICLES ─────────────────────────────────────────────────────────────────
const canvas = document.getElementById('particles');
const ctx2d = canvas.getContext('2d');
let particles = [];

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize); resize();

class Particle {
  constructor(x, y, color) {
    this.x = x; this.y = y;
    this.vx = (Math.random() - 0.5) * 8;
    this.vy = Math.random() * -10 - 2;
    this.life = 1; this.decay = Math.random() * 0.025 + 0.015;
    this.color = color;
    this.r = Math.random() * 5 + 2;
    this.shape = Math.random() > 0.5 ? 'circle' : 'star';
  }
  update() { this.x += this.vx; this.vy += 0.3; this.y += this.vy; this.life -= this.decay; }
  draw(ctx) {
    ctx.globalAlpha = this.life;
    ctx.fillStyle = this.color;
    if (this.shape === 'circle') {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.font = `${this.r * 3}px sans-serif`;
      ctx.fillText('✦', this.x, this.y);
    }
    ctx.globalAlpha = 1;
  }
}

function spawnParticles(isApple) {
  const colors = isApple
    ? ['#3dda6e', '#34d5d5', '#7ef5a0', '#f5c842']
    : ['#f0622a', '#ff9a3c', '#ffd166', '#e03030'];
  const cx = window.innerWidth * 0.5;
  const cy = window.innerHeight * 0.4;
  for (let i = 0; i < 40; i++) {
    particles.push(new Particle(
      cx + (Math.random() - 0.5) * 200,
      cy + (Math.random() - 0.5) * 100,
      colors[Math.floor(Math.random() * colors.length)]
    ));
  }
}

function animateParticles() {
  ctx2d.clearRect(0, 0, canvas.width, canvas.height);
  particles = particles.filter(p => { p.update(); p.draw(ctx2d); return p.life > 0; });
  requestAnimationFrame(animateParticles);
}
animateParticles();

// ── SSE ───────────────────────────────────────────────────────────────────────
function connectSSE() {
  const es = new EventSource('/events');
  es.onmessage = (e) => {
    const ev = JSON.parse(e.data);
    if (ev.type === 'score') {
      showToast(ev.item, ev.pts);
      fetchState();
    }
  };
  es.onerror = () => { setTimeout(connectSSE, 2000); es.close(); };
}
connectSSE();

// ── POLL STATE ────────────────────────────────────────────────────────────────
function fetchState() {
  fetch('/state').then(r => r.json()).then(updateUI).catch(() => { });
}
setInterval(fetchState, 800);
fetchState();

// ── RESET ─────────────────────────────────────────────────────────────────────
function resetData() {
  if (!confirm('Reset today\'s score and log?')) return;
  fetch('/reset', { method: 'POST' }).then(() => fetchState());
  document.getElementById('feed-list').innerHTML =
    '<div style="color:var(--muted);font-size:0.78rem;text-align:center;padding:20px 0">No snacks yet!</div>';
}
