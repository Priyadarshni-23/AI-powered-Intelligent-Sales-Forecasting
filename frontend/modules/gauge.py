import math


def render_score_gauge(score, label=None, size=170, stroke=14):
    """
    Returns an HTML/SVG snippet for a premium ring gauge:
    a gradient arc on a track circle, with the score centered
    inside and an optional pill-shaped qualifier label below.
    """
    score = max(0, min(100, int(score)))
    radius = (200 - stroke) / 2
    circumference = 2 * math.pi * radius
    dash = circumference * (score / 100)
    gap = max(circumference - dash, 0)

    if score >= 80:
        grad_from, grad_to = "#5fd68a", "#2f9e5f"
        tier_class = "tier-high"
        tier_text = "Highly Qualified"
    elif score >= 60:
        grad_from, grad_to = "#f0c674", "#c98a26"
        tier_class = "tier-mid"
        tier_text = "Qualified Lead"
    else:
        grad_from, grad_to = "#f0897a", "#c0392b"
        tier_class = "tier-low"
        tier_text = "Needs Qualification"

    gradient_id = f"gaugeGrad{score}{stroke}{int(size)}"
    display_label = label if label else tier_text

    return f"""
    <div class="score-gauge-outer">
      <div class="score-gauge-wrap" style="width:{size}px;height:{size}px;">
        <svg viewBox="0 0 200 200" width="{size}" height="{size}">
          <defs>
            <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="{grad_from}" />
              <stop offset="100%" stop-color="{grad_to}" />
            </linearGradient>
          </defs>
          <circle cx="100" cy="100" r="{radius}" fill="none"
                  stroke="#f1e6da" stroke-width="{stroke}" />
          <circle cx="100" cy="100" r="{radius}" fill="none"
                  stroke="url(#{gradient_id})" stroke-width="{stroke}"
                  stroke-linecap="round"
                  stroke-dasharray="{dash:.2f} {gap:.2f}"
                  transform="rotate(-90 100 100)" />
        </svg>
        <div class="score-gauge-center">
          <div class="score-gauge-num">{score}</div>
          <div class="score-gauge-sub">out of 100</div>
        </div>
      </div>
      <div class="score-gauge-label {tier_class}">{display_label}</div>
    </div>
    """


def render_engagement_badge(level):
    """
    Returns an HTML pill badge for a lead's engagement level, auto-colored
    the same way the score gauge is: High -> green, Medium -> amber,
    Low -> red, anything else -> neutral.
    """
    raw = (level or "").strip()
    normalized = raw.lower()

    if normalized == "high":
        css_class, icon = "level-high", "&#128293;"      # 🔥
    elif normalized == "medium":
        css_class, icon = "level-medium", "&#9889;"        # ⚡
    elif normalized == "low":
        css_class, icon = "level-low", "&#127793;"         # 🌱
    else:
        css_class, icon = "level-unknown", "&#10067;"      # ❔

    display_text = raw if raw else "Unknown"

    return (
        f'<span class="engagement-badge {css_class}">'
        f'{icon} {display_text}</span>'
    )


def render_conversion_bar(probability):
    """
    Returns an HTML/CSS gradient probability bar (0.0-1.0 input) with a
    marker positioned at the current value and a color-coded percentage +
    tier label, auto-colored the same way the score gauge is.
    """
    try:
        probability = float(probability or 0)
    except (TypeError, ValueError):
        probability = 0.0

    probability = max(0.0, min(1.0, probability))
    pct = probability * 100

    if pct >= 70:
        tier_class, tier_text = "tier-high", "High Probability"
    elif pct >= 40:
        tier_class, tier_text = "tier-mid", "Medium Probability"
    else:
        tier_class, tier_text = "tier-low", "Low Probability"

    return f"""
    <div class="conv-bar-wrap">
      <div class="conv-bar-pct {tier_class}">{pct:.0f}%</div>
      <div class="conv-bar-track">
        <div class="conv-bar-marker" style="left:{pct:.1f}%;"></div>
      </div>
      <div class="conv-bar-scale"><span>Low</span><span>Medium</span><span>High</span></div>
      <div class="conv-bar-tier-label {tier_class}">{tier_text}</div>
    </div>
    """
