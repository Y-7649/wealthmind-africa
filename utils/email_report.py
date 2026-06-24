"""
utils/email_report.py
WealthMind Africa — Personalised assessment report email

Builds and sends each participant's results report. UI/communication layer only:
it reads the already-computed record and the existing display helpers — it never
scores, weights, or calculates anything.

Delivery uses the standard library only (no new dependencies, so nothing extra
to install on Streamlit Cloud):
    - Resend  → an HTTPS POST to the Resend REST API via urllib (preferred)
    - SMTP    → smtplib (fallback)

Configuration lives in Streamlit secrets (or environment variables):
    RESEND_API_KEY     - enables Resend delivery
    RESEND_FROM        - verified sender, e.g. "WealthMind Africa <reports@yourdomain>"
    SMTP_HOST/PORT/USER/PASSWORD/FROM   - alternative SMTP delivery
    APP_URL            - public app URL used for the Impact Report link

If no provider is configured, send_report_email() returns (False, ...) and the
results page shows the graceful "being prepared" message; the email is still
stored (database.save_report_request) as a queued send.
"""

import os
import json
import logging
import smtplib
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("wealthmind.email")

from core.assessment import (
    band_label,
    SCORE_EXPLANATIONS,
    strongest_and_opportunity,
    generate_assessment_insights,
)

EMAIL_SUBJECT = "Your WealthMind Africa Assessment Results"
DEFAULT_FROM = "WealthMind Africa <onboarding@resend.dev>"
DEFAULT_APP_URL = "https://wealthmind-africa.streamlit.app"


def _secret(key: str, default=None):
    """Read a config value from environment variables, then Streamlit secrets
    (wrapped so it never raises outside a Streamlit runtime, e.g. in tests)."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


def email_provider_configured() -> bool:
    """True if a Resend or SMTP provider is configured."""
    return bool(_secret("RESEND_API_KEY") or _secret("SMTP_HOST"))


# ── HTML REPORT ───────────────────────────────────────────────────────────────

def _score_block(label: str, value: float, sub: str, explanation: str) -> str:
    band = band_label(value)
    colour = "#00C49F" if value >= 70 else "#E08600" if value >= 40 else "#D64545"
    return (
        f'<tr><td style="padding:14px 0;border-bottom:1px solid #ECEFF3;">'
        f'<table width="100%" cellpadding="0" cellspacing="0"><tr>'
        f'<td style="vertical-align:top;">'
        f'<div style="font-size:13px;font-weight:700;color:#1B2733;">{label}</div>'
        f'<div style="font-size:12px;color:#7A8794;line-height:1.5;margin-top:2px;max-width:360px;">{explanation}</div>'
        f'</td>'
        f'<td style="vertical-align:top;text-align:right;white-space:nowrap;padding-left:10px;">'
        f'<div style="font-size:26px;font-weight:800;color:{colour};line-height:1;">{value:.0f}</div>'
        f'<div style="font-size:11px;font-weight:700;color:{colour};text-transform:uppercase;letter-spacing:0.5px;">{band}</div>'
        f'<div style="font-size:11px;color:#9AA6B2;margin-top:2px;">{sub}</div>'
        f'</td></tr></table></td></tr>'
    )


def build_report_html(record: dict) -> str:
    """Build a professional, mobile-friendly HTML report from a scored record."""
    app_url = _secret("APP_URL", DEFAULT_APP_URL).rstrip("/")
    strongest, opportunity = strongest_and_opportunity(record)
    insights = generate_assessment_insights(record)
    insight = insights[0] if insights else None

    scores_html = (
        _score_block("Financial Health", record["health_score"], "out of 100",
                     SCORE_EXPLANATIONS["health"]) +
        _score_block("Present Bias", record["present_bias_score"], record["present_bias_label"],
                     SCORE_EXPLANATIONS["present_bias"]) +
        _score_block("Emergency Resilience", record["resilience_score"],
                     f"≈ {record['emergency_fund_months']:.1f} months",
                     SCORE_EXPLANATIONS["resilience"]) +
        _score_block("Savings Rate", record["savings_score"],
                     f"≈ {record['savings_rate_pct']:.0f}% of income",
                     SCORE_EXPLANATIONS["savings"])
    )

    insight_html = ""
    if insight:
        insight_html = (
            f'<tr><td style="padding:16px;background:#0F1824;border-radius:10px;">'
            f'<div style="font-size:11px;font-weight:700;color:#00C49F;text-transform:uppercase;letter-spacing:0.6px;">'
            f'A behavioural economics insight · {insight["concept"]}</div>'
            f'<div style="font-size:13px;color:#D7E0EA;line-height:1.55;margin-top:6px;">{insight["suggests"]}</div>'
            f'<div style="font-size:12.5px;color:#9AA6B2;line-height:1.5;margin-top:8px;">'
            f'<strong style="color:#00C49F;">Try this:</strong> {insight["action"]}</div></td></tr>'
            f'<tr><td style="height:18px;"></td></tr>'
        )

    return f"""\
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F4F6F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F4F6F9;padding:20px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#FFFFFF;border-radius:14px;overflow:hidden;border:1px solid #E6EAF0;">

  <tr><td style="background:linear-gradient(135deg,#0E1117,#13202B);padding:26px 28px;">
    <div style="font-size:13px;font-weight:800;color:#00C49F;letter-spacing:0.5px;">🌍 WEALTHMIND AFRICA</div>
    <div style="font-size:20px;font-weight:800;color:#FFFFFF;margin-top:6px;">Your Assessment Results</div>
    <div style="font-size:12.5px;color:#8FA0AE;margin-top:4px;">A behavioural economics snapshot of how you save, spend, and plan.</div>
  </td></tr>

  <tr><td style="padding:8px 28px 0;">
    <table width="100%" cellpadding="0" cellspacing="0">{scores_html}</table>
  </td></tr>

  <tr><td style="padding:20px 28px 0;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="padding:14px 16px;background:#EAF8F3;border-radius:10px;border:1px solid #CDEBE0;">
        <div style="font-size:11px;font-weight:700;color:#00936F;text-transform:uppercase;letter-spacing:0.5px;">💪 Strongest Financial Habit</div>
        <div style="font-size:13.5px;color:#1B2733;margin-top:4px;line-height:1.5;">Your strongest habit is {strongest}.</div>
      </td></tr>
      <tr><td style="height:10px;"></td></tr>
      <tr><td style="padding:14px 16px;background:#FFF4E8;border-radius:10px;border:1px solid #F3DCC0;">
        <div style="font-size:11px;font-weight:700;color:#B5680A;text-transform:uppercase;letter-spacing:0.5px;">🎯 Biggest Opportunity</div>
        <div style="font-size:13.5px;color:#1B2733;margin-top:4px;line-height:1.5;">You could improve by {opportunity}.</div>
      </td></tr>
      <tr><td style="height:18px;"></td></tr>
      {insight_html}
    </table>
  </td></tr>

  <tr><td style="padding:6px 28px 26px;" align="center">
    <a href="{app_url}/impact" style="display:inline-block;background:#00C49F;color:#06231C;font-size:13.5px;font-weight:800;text-decoration:none;padding:12px 22px;border-radius:9px;">View the WealthMind Impact Report →</a>
    <div style="font-size:11.5px;color:#9AA6B2;margin-top:14px;line-height:1.6;">
      Your responses contribute to ongoing research into financial decision-making
      across different ages and life stages. Financial responses are stored separately
      from your email address.
    </div>
  </td></tr>

  <tr><td style="background:#0E1117;padding:16px 28px;text-align:center;">
    <div style="font-size:11px;color:#5A6B79;">WealthMind Africa · Applied Behavioural Economics · yashkaria.pro@gmail.com</div>
  </td></tr>

</table>
</td></tr></table>
</body></html>"""


# ── DELIVERY ──────────────────────────────────────────────────────────────────

def _send_via_resend(api_key: str, from_addr: str, to_email: str, subject: str, html: str):
    payload = json.dumps({
        "from": from_addr, "to": [to_email], "subject": subject, "html": html,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails", data=payload, method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return (200 <= resp.status < 300), f"resend:{resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"resend_http:{e.code}:{e.read().decode('utf-8', 'ignore')[:200]}"
    except Exception as e:  # noqa: BLE001
        return False, f"resend_error:{e}"


def _send_via_smtp(to_email: str, subject: str, html: str):
    host = _secret("SMTP_HOST")
    port = int(_secret("SMTP_PORT", 587) or 587)
    user = _secret("SMTP_USER")
    password = _secret("SMTP_PASSWORD")
    from_addr = _secret("SMTP_FROM", user) or user
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(from_addr, [to_email], msg.as_string())
        return True, "smtp:ok"
    except Exception as e:  # noqa: BLE001
        return False, f"smtp_error:{e}"


def send_report_email(to_email: str, record: dict):
    """
    Send the personalised report. Returns (success: bool, detail: str).

    Delivery order:
        1. SMTP (Gmail) is the PRIMARY provider — if SMTP_HOST is set, it is
           always tried first.
        2. Resend is the FALLBACK — used only if SMTP is unconfigured, or if a
           configured SMTP attempt fails and RESEND_API_KEY is available.
        3. If neither is configured, returns (False, "not_configured"); the
           caller shows the graceful "being prepared" message and the row stays
           queued (sent = 0) for a later resend.

    All failures are logged (visible in the Streamlit Cloud app logs).
    """
    if not to_email:
        return False, "no_recipient"
    html = build_report_html(record)

    smtp_configured = bool(_secret("SMTP_HOST"))
    resend_key = _secret("RESEND_API_KEY")

    # 1. SMTP first (primary)
    if smtp_configured:
        ok, detail = _send_via_smtp(to_email, EMAIL_SUBJECT, html)
        if ok:
            return True, detail
        logger.warning("SMTP delivery failed for report email: %s", detail)
        # 2. Resend fallback after an SMTP failure
        if resend_key:
            ok2, detail2 = _send_via_resend(resend_key, _secret("RESEND_FROM", DEFAULT_FROM),
                                            to_email, EMAIL_SUBJECT, html)
            if not ok2:
                logger.warning("Resend fallback also failed: %s", detail2)
            return ok2, (detail2 if ok2 else f"smtp_failed[{detail}]+resend_failed[{detail2}]")
        return False, detail

    # SMTP not configured → Resend only
    if resend_key:
        ok, detail = _send_via_resend(resend_key, _secret("RESEND_FROM", DEFAULT_FROM),
                                      to_email, EMAIL_SUBJECT, html)
        if not ok:
            logger.warning("Resend delivery failed for report email: %s", detail)
        return ok, detail

    logger.info("No email provider configured — report queued (sent=0).")
    return False, "not_configured"
