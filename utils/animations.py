"""
utils/animations.py
WealthMind Africa — Canvas Animations

Provides self-contained HTML/JS snippets for animated financial visuals.
Embed the return value with:

    import streamlit.components.v1 as components
    components.html(get_animated_market_html(), height=220)

All animations are canvas-based — no external dependencies required.
The background colour matches the app's dark theme (#0E1117).
"""


def get_animated_market_html(height: int = 220) -> str:
    """
    Return a self-contained HTML block with a canvas-based animated
    financial market chart.

    Three series are simulated using Brownian motion with a slight
    positive drift, imitating the visual language of live financial
    terminals.  The primary (teal) line carries a gradient area fill
    and a subtle glow effect.  The chart scrolls continuously as new
    data points are generated.

    Parameters
    ----------
    height : int
        Height in pixels.  Pass the same value to
        ``st.components.v1.html(..., height=height)``.  Default 220.
    """
    return f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0E1117; overflow:hidden; }}
  canvas {{ display:block; width:100%; height:{height}px; }}
  .lbl {{
    position:absolute; bottom:8px; right:14px;
    font-family:-apple-system,'Inter',sans-serif;
    font-size:10px; color:rgba(0,196,159,0.38);
    letter-spacing:0.1em; text-transform:uppercase;
    pointer-events:none;
  }}
</style>
</head>
<body>
<canvas id="wmc"></canvas>
<div class="lbl">Live Simulation</div>
<script>
(function() {{
  const cvs = document.getElementById('wmc');
  const ctx = cvs.getContext('2d');

  /* ── Palette ─────────────────────────────────── */
  const BG   = '#0E1117';
  const TEAL = '#00C49F';
  const WARM = '#FF8C42';
  const COOL = '#9488FF';
  const GRID = 'rgba(255,255,255,0.032)';

  /* ── Config ──────────────────────────────────── */
  const H   = {height};   /* canvas height in px           */
  const N   = 100;        /* visible data points per series */
  const FPT = 3;          /* frames between each new tick   */

  /* ── Series definitions ──────────────────────── */
  const series = [
    {{ color:TEAL, w:2.2, a:1.00, val:58, d:0.06, data:[] }},
    {{ color:WARM, w:1.5, a:0.48, val:44, d:0.03, data:[] }},
    {{ color:COOL, w:1.5, a:0.38, val:36, d:0.02, data:[] }},
  ];

  /* Seed initial data so the chart isn't blank on load */
  for (let i = 0; i < N + 15; i++) {{
    for (const s of series) {{
      s.val += (Math.random() - 0.49) * 2.0 + s.d;
      s.val  = Math.max(5, Math.min(95, s.val));
      s.data.push(s.val);
    }}
  }}

  /* ── Resize handler ──────────────────────────── */
  function resize() {{
    cvs.width  = window.innerWidth || 640;
    cvs.height = H;
  }}
  resize();
  window.addEventListener('resize', resize);

  /* ── Add one new data point per series ───────── */
  function tick() {{
    for (const s of series) {{
      s.val += (Math.random() - 0.49) * 2.2 + s.d;
      s.val  = Math.max(5, Math.min(95, s.val));
      s.data.push(s.val);
      if (s.data.length > N + 20) s.data.shift();
    }}
  }}

  /* ── Map a data value to a canvas y-coordinate ── */
  function yOf(v, lo, hi, pad) {{
    if (hi === lo) return H / 2;
    return pad + (1 - (v - lo) / (hi - lo)) * (H - pad * 2);
  }}

  let frame = 0;

  /* ── Main render loop ────────────────────────── */
  function draw() {{
    if (frame % FPT === 0) tick();
    frame++;

    const W   = cvs.width;
    const PAD = 18;

    /* Background */
    ctx.fillStyle = BG;
    ctx.fillRect(0, 0, W, H);

    /* Horizontal grid lines */
    ctx.strokeStyle = GRID;
    ctx.lineWidth = 1;
    for (let i = 1; i <= 3; i++) {{
      const y = (H / 4) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }}

    /* Unified vertical scale across all series */
    const all = series.flatMap(s => s.data.slice(-N));
    const lo  = Math.min(...all) - 5;
    const hi  = Math.max(...all) + 5;
    const dX  = W / (N - 1);

    /* Draw each series */
    for (const s of series) {{
      const pts = s.data.slice(-N);
      if (pts.length < 2) continue;

      ctx.save();
      ctx.globalAlpha = s.a;
      ctx.strokeStyle = s.color;
      ctx.lineWidth   = s.w;
      ctx.lineJoin    = 'round';
      ctx.lineCap     = 'round';

      /* Glow on primary line */
      if (s.color === TEAL) {{
        ctx.shadowBlur  = 10;
        ctx.shadowColor = 'rgba(0,196,159,0.55)';
      }}

      /* Draw smooth bezier curve */
      ctx.beginPath();
      let px = 0, py = yOf(pts[0], lo, hi, PAD);
      ctx.moveTo(px, py);
      for (let i = 1; i < pts.length; i++) {{
        const nx = i * dX;
        const ny = yOf(pts[i], lo, hi, PAD);
        const cx = (px + nx) / 2;
        ctx.bezierCurveTo(cx, py, cx, ny, nx, ny);
        px = nx;
        py = ny;
      }}
      ctx.stroke();

      /* Gradient area fill under teal line */
      if (s.color === TEAL) {{
        ctx.lineTo(W, H + 2);
        ctx.lineTo(0, H + 2);
        ctx.closePath();
        ctx.shadowBlur = 0;
        const g = ctx.createLinearGradient(0, PAD, 0, H);
        g.addColorStop(0, 'rgba(0,196,159,0.18)');
        g.addColorStop(1, 'rgba(0,196,159,0.00)');
        ctx.fillStyle = g;
        ctx.fill();
      }}

      ctx.restore();
    }}

    /* Left edge fade — blends lines into background */
    const gL = ctx.createLinearGradient(0, 0, 52, 0);
    gL.addColorStop(0, BG);
    gL.addColorStop(1, 'rgba(14,17,23,0)');
    ctx.fillStyle = gL;
    ctx.fillRect(0, 0, 52, H);

    /* Right edge fade */
    const gR = ctx.createLinearGradient(W - 52, 0, W, 0);
    gR.addColorStop(0, 'rgba(14,17,23,0)');
    gR.addColorStop(1, BG);
    ctx.fillStyle = gR;
    ctx.fillRect(W - 52, 0, 52, H);

    requestAnimationFrame(draw);
  }}

  draw();
}})();
</script>
</body>
</html>"""
