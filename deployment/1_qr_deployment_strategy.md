# QR-Code Deployment Strategy

**Goal:** get the most real, consented participants between now and September with the least friction. The assessment is a 2-minute, no-login experience — the QR code is the bridge from the physical world to a data point.

---

## The link

Everything points to one URL:

```
https://<your-live-app>/assessment
```

> ⚠️ Update `ASSESSMENT_URL` in `pages/00_assessment.py` to your real Streamlit Cloud URL before printing anything. Test the QR on two phones first.

**Make the QR:** any free generator (qr-code-generator.com, or `qrcode` Python lib). Generate **one** code for the `/assessment` URL. Optionally make 3–4 variants with a `?src=` tag you note manually (e.g. `/assessment?src=swim`) so you can record which channel produced how many — the app ignores the tag, but you track it on paper for "across 4 groups."

---

## The 10-second verbal ask (memorise this)

> "I built a behavioural-economics study on how people make money decisions. It's 2 minutes, completely anonymous, no sign-up. Mind scanning this and trying it? You'll get your own financial-behaviour scores at the end."

The "you get your own result" is the hook. Lead with it.

---

## July — warm network (target ~55)

| Channel | Tactic | Notes |
|---|---|---|
| **Family / relatives** | Send the link in the family WhatsApp; QR at a family dinner | Easiest yes; gives you the **adult** comparison group early |
| **Swim club** | QR card at training; ask swimmers **and parents** poolside at a meet | Captive, mixed-age audience — swim parents are gold for life-stage contrast |
| **Friends + their parents** | Personal WhatsApp; "send it to your mum too" | Doubles each contact into a young + adult data point |

Front-load adults in July so the **students-vs-adults** finding is possible before school starts.

## August — school (target 100–150)

| Channel | Tactic |
|---|---|
| **Economics club** | Run a 15-min session (see slide outline). Everyone scans the **QR on the projector**, then you show the live Impact Report you just generated |
| **Classrooms** | Ask 2–3 teachers for 3 minutes at the start of class; QR on the board |
| **Whole grade** | QR posters on noticeboards + a pinned message in year-group chats |

---

## Placement checklist
- [ ] QR on the **projector slide** during the club session (highest conversion)
- [ ] A5 **poster** on 3–4 noticeboards
- [ ] **Sticker/card** you carry to swim + family events
- [ ] **Pinned WhatsApp** message with the link (not just the QR — links work in chats)

## Conversion tips
- Always pair QR **with the link** (QR for posters, link for chats).
- Ask people to do it **then and there** (2 min) — "later" never happens.
- After the club session, announce the **live participant count** — social proof drives the next wave.

**Track weekly:** participants added, by channel. That weekly number is your growth curve (Wharton loves it).
