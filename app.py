"""
Placement Prep Assistant — AI Interview Coach (Product v5)
Persistent conversational interface with follow-up system,
learning paths, context-aware chips, and full coaching UX.
"""

import re
import time
import urllib.parse
import streamlit as st
from html import escape
from rag_pipeline import RAGPipeline

st.set_page_config(
    page_title="Placement Prep Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

:root {
  --bg:           #050816;
  --surface:      #080f1e;
  --card:         #0d1626;
  --card-raised:  #111e30;
  --border:       #172035;
  --border-hi:    #263354;
  --primary:      #7C5CFF;
  --primary-lo:   rgba(124,92,255,0.09);
  --primary-md:   rgba(124,92,255,0.18);
  --primary-glow: rgba(124,92,255,0.24);
  --secondary:    #5B8CFF;
  --text:         #EFF6FF;
  --muted:        #8B9EC0;
  --subtle:       #3D5070;
  --success:      #10B981;
  --success-lo:   rgba(16,185,129,0.10);
  --amber:        #F59E0B;
  --amber-lo:     rgba(245,158,11,0.10);
  --rose:         #F43F5E;
  --rose-lo:      rgba(244,63,94,0.08);
  --sky:          #38BDF8;
  --r-xs: 6px; --r-sm: 8px; --r-md: 12px; --r-lg: 16px; --r-xl: 24px;
  --sh-sm: 0 2px 8px rgba(0,0,0,0.35);
  --sh-md: 0 6px 28px rgba(0,0,0,0.50);
  --sh-px: 0 4px 20px rgba(124,92,255,0.28);
}

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }

.stApp {
  background:
    radial-gradient(ellipse 90% 50% at 12% -8%,  rgba(124,92,255,0.11) 0%, transparent 55%),
    radial-gradient(ellipse 60% 40% at 88% 100%, rgba(91,140,255,0.08) 0%, transparent 52%),
    var(--bg) !important;
}

/* ── Animations ── */
@keyframes fadeUp   { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes blink    { 0%,100%{opacity:1;box-shadow:0 0 5px var(--success)} 50%{opacity:.3;box-shadow:none} }
@keyframes slideL   { from{opacity:0;transform:translateX(-6px)} to{opacity:1;transform:none} }
@keyframes slideUp  { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
@keyframes shimmer  { 0%{background-position:-800px 0} 100%{background-position:800px 0} }
@keyframes pulse    { 0%,100%{opacity:1} 50%{opacity:0.5} }
@keyframes typingDot{ 0%,80%,100%{transform:scale(0.6);opacity:.4} 40%{transform:scale(1);opacity:1} }
@keyframes chipIn   { from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:none} }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 4px; }

/* ── Typography ── */
/* ── Body text — 17px base ──────────────────────────────── */
p, li,
.stMarkdown p, .stMarkdown li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--muted) !important;
  line-height: 1.75 !important;
  font-size: 1.0625rem !important;   /* 17px */
  letter-spacing: -0.006em !important;
}
strong, b  { color: var(--text) !important; font-weight: 600 !important; }
h1,h2,h3   { color: var(--text) !important; letter-spacing: -0.025em !important; }
hr { border-color: var(--border) !important; margin: 0.5rem 0 !important; opacity: 0.55; }
code {
  background: rgba(124,92,255,0.13) !important; color: #a78bfa !important;
  border-radius: 4px !important; padding: 2px 7px !important; font-size: 0.85rem !important;
}
pre { background: #070c18 !important; border: 1px solid var(--border) !important;
      border-radius: var(--r-md) !important; padding: 14px !important; }
pre code { background: transparent !important; color: #93c5fd !important; padding: 0 !important; }

/* ════════════════════════════════════════════════════════
   COMPACT HEADER (conversation active state)
════════════════════════════════════════════════════════ */
.compact-header {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease;
}
.compact-logo {
  width: 24px; height: 24px; border-radius: 6px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem;
}
.compact-name {
  font-size: 0.82rem; font-weight: 600; color: var(--text);
  letter-spacing: -0.018em;
}
.compact-sep { color: var(--border-hi); font-size: 0.75rem; }
.compact-tag {
  font-size: 0.65rem; color: var(--subtle); letter-spacing: 0.02em;
}
.compact-spacer { flex: 1; }
.compact-q-count {
  font-size: 0.65rem; font-weight: 500;
  background: var(--primary-lo); border: 1px solid var(--primary-md);
  color: #a78bfa; border-radius: 10px; padding: 2px 9px;
}

/* ════════════════════════════════════════════════════════
   FULL HERO (empty state)
════════════════════════════════════════════════════════ */
.hero {
  position: relative; padding: 1.6rem 0 0.4rem;
  animation: fadeUp 0.45s ease both;
}
.hero-eyebrow {
  font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--primary); margin-bottom: 0.55rem;
  display: flex; align-items: center; gap: 8px;
}
.hero-eyebrow-line { display: inline-block; width: 20px; height: 1px; background: var(--primary); opacity: 0.5; }
.hero-title {
  font-size: 3.5rem; font-weight: 700; line-height: 1.05; letter-spacing: -0.04em;  /* 56px */
  background: linear-gradient(135deg, #e0e7ff 0%, #c4b5fd 50%, #93c5fd 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 0.6rem;
}
.hero-sub {
  font-size: 1.0rem; color: var(--muted); line-height: 1.7;
  letter-spacing: -0.008em; margin-bottom: 1rem; max-width: 560px;
}
.hero-sub em { color: #a78bfa; font-style: normal; font-weight: 500; }

/* Trust signal bar */
.trust-bar {
  display: flex; align-items: center; flex-wrap: wrap; gap: 0;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-md); overflow: hidden;
  margin-bottom: 1.5rem; animation: fadeUp 0.5s ease 0.1s both;
}
.trust-item {
  flex: 1; padding: 10px 16px; text-align: center;
  border-right: 1px solid var(--border);
  transition: background 0.18s;
  min-width: 100px;
}
.trust-item:last-child { border-right: none; }
.trust-item:hover { background: var(--card-raised); }
.trust-val {
  font-size: 1.05rem; font-weight: 700; letter-spacing: -0.03em;
  background: linear-gradient(90deg, #c4b5fd, #93c5fd);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  line-height: 1.2; display: block;
}
.trust-lbl {
  font-size: 0.59rem; font-weight: 500; letter-spacing: 0.05em;
  text-transform: uppercase; color: var(--subtle); margin-top: 2px; display: block;
}

/* Live indicator */
.live-dot {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.65rem; color: #34d399; font-weight: 500;
}
.live-dot::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: var(--success); display: block;
  animation: blink 2s infinite;
}

/* ════════════════════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  width: 280px !important; min-width: 280px !important; max-width: 280px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1rem 0.8rem !important; }

.sb-brand {
  display: flex; align-items: center; gap: 8px;
  padding-bottom: 0.75rem; border-bottom: 1px solid var(--border); margin-bottom: 0.85rem;
}
.sb-logo {
  width: 26px; height: 26px; border-radius: var(--r-sm); flex-shrink: 0;
  background: linear-gradient(135deg,var(--primary),var(--secondary));
  display: flex; align-items: center; justify-content: center;
  box-shadow: var(--sh-px);
}
.sb-logo svg { width: 13px; height: 13px; stroke: #fff; fill: none; }
.sb-wordmark { font-size: 0.9375rem; font-weight: 700; color: var(--text); letter-spacing: -0.02em; }  /* 15px */
.sb-sub      { font-size: 0.6875rem; color: var(--subtle); margin-top: 1px; }  /* 11px */
.sb-q-badge  {
  margin-left: auto; background: var(--primary-lo); border: 1px solid var(--primary-md);
  color: #a78bfa; border-radius: 10px; padding: 2px 8px;
  font-size: 0.6875rem; font-weight: 600; white-space: nowrap;
}

.sb-section-label {
  font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.08em;   /* 11px */
  text-transform: uppercase; color: var(--subtle); margin: 0.8rem 0 0.35rem 1px;
}
.sb-category-label {
  font-size: 0.625rem; font-weight: 600; letter-spacing: 0.1em;  /* 10px */
  text-transform: uppercase; color: var(--subtle); opacity: 0.55;
  margin: 0.55rem 0 0.2rem 2px;
}

.tp {
  display: flex; align-items: flex-start; gap: 7px;
  padding: 5px 7px; margin: 2px 0; border-radius: var(--r-sm);
  border: 1px solid transparent;
  transition: background 0.16s, border-color 0.16s;
  animation: slideL 0.3s ease both;
}
.tp:hover { background: var(--primary-lo); border-color: var(--primary-md); }
.tp-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--primary); opacity: 0.65; margin-top: 5px; flex-shrink: 0; }
.tp-dot-amber { background: var(--amber); }
.tp-name { font-size: 0.875rem; font-weight: 600; color: #c4b5fd; }  /* 14px */
.tp-sub  { font-size: 0.6875rem; color: var(--subtle); margin-top: 2px; line-height: 1.45; }  /* 11px */
.tp-trend {
  font-size: 0.5625rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  background: rgba(245,158,11,0.12); color: var(--amber); border: 1px solid rgba(245,158,11,0.22);
  border-radius: 3px; padding: 1px 4px; margin-left: auto; flex-shrink: 0; align-self: center;
}

/* Learning path in sidebar */
.sb-path-title {
  font-size: 0.68rem; font-weight: 600; color: #c4b5fd; margin-bottom: 4px;
  display: flex; align-items: center; gap: 5px;
}
.sb-path-steps {
  display: flex; flex-direction: column; gap: 0; margin-bottom: 8px;
}
.sb-path-step {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.65rem; color: var(--subtle); padding: 2px 0;
}
.sb-path-step::before {
  content: ''; width: 1px; height: 12px; background: var(--border-hi);
  flex-shrink: 0; margin-left: 4px;
}
.sb-path-step:first-child::before { display: none; }
.sb-path-node {
  width: 5px; height: 5px; border-radius: 50%; background: var(--primary-md);
  border: 1px solid var(--primary); flex-shrink: 0;
}

[data-testid="stSidebar"] .stButton > button {
  background: rgba(239,68,68,0.06) !important; border: 1px solid rgba(239,68,68,0.16) !important;
  color: #f87171 !important; border-radius: var(--r-sm) !important;
  font-size: 0.74rem !important; font-weight: 500 !important;
  padding: 5px 12px !important; transition: all 0.16s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(239,68,68,0.12) !important; border-color: rgba(239,68,68,0.30) !important;
}
.sb-tech {
  margin-top: 0.9rem; padding: 6px 9px; text-align: center;
  background: rgba(124,92,255,0.04); border: 1px solid rgba(124,92,255,0.10); border-radius: var(--r-sm);
}
.sb-tech-lbl { font-size: 0.57rem; color: var(--subtle); }
.sb-tech-val {
  font-size: 0.66rem; font-weight: 600;
  background: linear-gradient(90deg,#a78bfa,#93c5fd);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* ════════════════════════════════════════════════════════
   WELCOME / EMPTY STATE
════════════════════════════════════════════════════════ */
.welcome-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 0.85rem 1.4rem;   /* reduced 25% */
  margin: 0 0 1rem; animation: fadeUp 0.4s ease 0.05s both;
}
.welcome-card h3 {
  font-size: 1.125rem; font-weight: 600; color: var(--text); margin: 0 0 0.2rem;  /* 18px */
  letter-spacing: -0.018em;
}
.welcome-card p {
  font-size: 0.9375rem !important; color: var(--muted) !important;  /* 15px */
  margin: 0; line-height: 1.65 !important;
}

.section-label {
  font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.08em;  /* 11px */
  text-transform: uppercase; color: var(--subtle);
  display: flex; align-items: center; gap: 10px; margin: 1.25rem 0 0.65rem;
}
.section-label::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

/* Suggested Q grid */
.sq-grid {
  display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin: 0;
}
.sq-card {
  display: flex; flex-direction: column; gap: 9px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 14px 16px;
  text-decoration: none !important; cursor: pointer; min-height: 90px;
  transition: border-color 0.18s, background 0.18s, transform 0.20s, box-shadow 0.20s;
  animation: slideUp 0.35s ease both; will-change: transform;
}
.sq-card:nth-child(1){animation-delay:0.04s}.sq-card:nth-child(2){animation-delay:0.08s}
.sq-card:nth-child(3){animation-delay:0.12s}.sq-card:nth-child(4){animation-delay:0.16s}
.sq-card:nth-child(5){animation-delay:0.20s}.sq-card:nth-child(6){animation-delay:0.24s}
.sq-card:nth-child(7){animation-delay:0.28s}.sq-card:nth-child(8){animation-delay:0.32s}
.sq-card:nth-child(9){animation-delay:0.36s}
.sq-card:hover {
  border-color: var(--border-hi); background: var(--card-raised);
  transform: translateY(-3px); box-shadow: 0 8px 28px rgba(0,0,0,0.45);
}
.sq-badge {
  display: inline-block; font-size: 0.56rem; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 2px 7px; border-radius: 4px;
  line-height: 1.5; width: fit-content;
}
.sq-badge-dsa  { background: rgba(124,92,255,0.12); color: #a78bfa; border: 1px solid rgba(124,92,255,0.25); }
.sq-badge-dbms { background: rgba(56,189,248,0.10); color: #7dd3fc; border: 1px solid rgba(56,189,248,0.25); }
.sq-badge-os   { background: rgba(244,63,94,0.09);  color: #fb7185; border: 1px solid rgba(244,63,94,0.22); }
.sq-badge-oop  { background: rgba(20,184,166,0.09); color: #2dd4bf; border: 1px solid rgba(20,184,166,0.22); }
.sq-badge-ml   { background: rgba(245,158,11,0.09); color: #fbbf24; border: 1px solid rgba(245,158,11,0.22); }
.sq-title {
  font-size: 0.875rem; font-weight: 500; color: var(--muted);  /* 14px */
  line-height: 1.5; letter-spacing: -0.01em; flex: 1;
  transition: color 0.15s;
}
.sq-card:hover .sq-title { color: var(--text); }
.sq-meta { font-size: 0.6875rem; color: var(--subtle); letter-spacing: 0.02em; margin-top: auto; }  /* 11px */

/* Learning paths */
.lp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 0; }
.lp-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 14px 16px;
  animation: slideUp 0.4s ease both;
}
.lp-card:nth-child(1){animation-delay:0.05s}.lp-card:nth-child(2){animation-delay:0.12s}
.lp-card-title {
  font-size: 0.72rem; font-weight: 600; color: var(--text);
  letter-spacing: -0.01em; margin-bottom: 10px;
  display: flex; align-items: center; gap: 6px;
}
.lp-card-icon { font-size: 0.85rem; }
.lp-steps { display: flex; align-items: center; flex-wrap: wrap; gap: 0; }
.lp-step {
  font-size: 0.65rem; color: var(--muted); font-weight: 500;
  background: rgba(255,255,255,0.03); border: 1px solid var(--border);
  border-radius: 4px; padding: 3px 8px; white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
}
.lp-step:hover { color: #a78bfa; border-color: var(--primary-md); }
.lp-arrow {
  font-size: 0.6rem; color: var(--subtle); padding: 0 4px; flex-shrink: 0;
}

/* Popular topics chips */
.pop-topics-wrap { display: flex; flex-wrap: wrap; gap: 7px; margin: 0; }
.pop-chip {
  display: inline-flex; align-items: center;
  background: transparent; border: 1px solid var(--border-hi);
  border-radius: 20px; padding: 5px 14px;
  font-size: 0.73rem; font-weight: 500; color: var(--subtle);
  text-decoration: none !important; white-space: nowrap; cursor: pointer;
  transition: background 0.14s, border-color 0.14s, color 0.14s;
}
.pop-chip:hover { background: var(--primary-lo); border-color: var(--primary-md); color: #c4b5fd; }

/* ════════════════════════════════════════════════════════
   CHAT MESSAGES
════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
  border-radius: var(--r-md) !important;
  margin: 6px 0 !important;
  animation: fadeUp 0.22s ease !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: rgba(124,92,255,0.07) !important;
  border: 1px solid rgba(124,92,255,0.15) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
  background: transparent !important; border: none !important; padding: 0 !important;
}

/* ════════════════════════════════════════════════════════
   ANSWER SECTIONS
════════════════════════════════════════════════════════ */
.ans-wrap { display: flex; flex-direction: column; gap: 14px; margin: 6px 0 12px; }

.ans-section {
  border-radius: 12px; padding: 16px 20px;   /* spec: 16px padding, 12px radius */
  border-left: 3px solid; border-top: 1px solid; border-right: 1px solid; border-bottom: 1px solid;
  animation: fadeUp 0.3s ease both; will-change: transform;
}
.ans-section:nth-child(1){animation-delay:0.04s}.ans-section:nth-child(2){animation-delay:0.09s}
.ans-section:nth-child(3){animation-delay:0.14s}.ans-section:nth-child(4){animation-delay:0.19s}
.ans-section:nth-child(5){animation-delay:0.24s}.ans-section:nth-child(6){animation-delay:0.29s}
.ans-section:nth-child(7){animation-delay:0.34s}

.ans-def { background:rgba(59,130,246,0.06);  border-left-color:#3b82f6;
           border-top-color:rgba(59,130,246,0.14);  border-right-color:rgba(59,130,246,0.06); border-bottom-color:rgba(59,130,246,0.06); }
.ans-exp { background:rgba(124,92,255,0.07);  border-left-color:var(--primary);
           border-top-color:var(--primary-md); border-right-color:rgba(124,92,255,0.06); border-bottom-color:rgba(124,92,255,0.06); }
.ans-ex  { background:rgba(16,185,129,0.06);  border-left-color:#10b981;
           border-top-color:rgba(16,185,129,0.15); border-right-color:rgba(16,185,129,0.06); border-bottom-color:rgba(16,185,129,0.06); }
.ans-tip { background:rgba(245,158,11,0.06);  border-left-color:var(--amber);
           border-top-color:rgba(245,158,11,0.15); border-right-color:rgba(245,158,11,0.06); border-bottom-color:rgba(245,158,11,0.06); }
.ans-key { background:rgba(20,184,166,0.06);  border-left-color:#14b8a6;
           border-top-color:rgba(20,184,166,0.15); border-right-color:rgba(20,184,166,0.06); border-bottom-color:rgba(20,184,166,0.06); }
.ans-fup { background:rgba(244,63,94,0.05);   border-left-color:var(--rose);
           border-top-color:rgba(244,63,94,0.13); border-right-color:rgba(244,63,94,0.05); border-bottom-color:rgba(244,63,94,0.05); }
.ans-mis { background:rgba(236,72,153,0.05);  border-left-color:#ec4899;
           border-top-color:rgba(236,72,153,0.14); border-right-color:rgba(236,72,153,0.05); border-bottom-color:rgba(236,72,153,0.05); }
.ans-gen { background:var(--card); border-left-color:var(--border-hi);
           border-top-color:var(--border); border-right-color:var(--border); border-bottom-color:var(--border); }

.ans-label {
  font-size: 0.6875rem; font-weight: 700; letter-spacing: 0.09em;  /* 11px */
  text-transform: uppercase; margin-bottom: 9px;
  display: flex; align-items: center; gap: 7px;
}
.ans-label-def { color: #60a5fa; }
.ans-label-exp { color: #a78bfa; }
.ans-label-ex  { color: #34d399; }
.ans-label-tip { color: #fbbf24; }
.ans-label-key { color: #2dd4bf; }
.ans-label-fup { color: #fb7185; }
.ans-label-mis { color: #f472b6; }
.ans-label-gen { color: var(--muted); }
.ans-label-bar { display: inline-block; width: 16px; height: 2px; border-radius: 2px; opacity: 0.7; flex-shrink: 0; }

.ans-body {
  font-size: 1.0rem !important; color: var(--muted) !important;  /* ~16px */
  line-height: 1.78 !important; letter-spacing: -0.005em !important; margin: 0 !important;
}
.ans-body strong, .ans-body b { color: var(--text) !important; font-weight: 600 !important; }
.ans-body code {
  background: rgba(124,92,255,0.13) !important; color: #a78bfa !important;
  border-radius: 4px !important; padding: 1px 6px !important; font-size: 0.84rem !important;
}
.ans-body ul, .ans-body ol { margin: 8px 0; padding-left: 20px; }
.ans-body li { margin: 5px 0; }

.ans-plain {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 18px 22px;
  font-size: 1.0rem !important; color: var(--muted) !important;
  line-height: 1.78 !important; animation: fadeUp 0.25s ease both;
}
.ans-plain strong, .ans-plain b { color: var(--text) !important; font-weight: 600 !important; }

/* ════════════════════════════════════════════════════════
   SECTION HEADS (Sources / Reading / Videos / Follow-ups)
════════════════════════════════════════════════════════ */
.sec-head {
  display: flex; align-items: center; gap: 8px;
  margin: 2.5rem 0 0.75rem; padding-top: 0.85rem;  /* stronger hierarchy: 40px top */
  border-top: 1px solid var(--border);
}
.sec-head-icon { font-size: 0.85rem; opacity: 0.75; flex-shrink: 0; }
.sec-head-label {
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em;  /* 12px, stronger */
  text-transform: uppercase; color: var(--subtle); white-space: nowrap;
}

/* ════════════════════════════════════════════════════════
   AI COACH CHIPS
════════════════════════════════════════════════════════ */
.coach-row {
  display: flex; flex-wrap: wrap; gap: 7px; margin: 12px 0 6px;
}
.coach-chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 11px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 500; border: 1px solid; line-height: 1.5;  /* 12px */
}
.cc-diff { background:rgba(56,189,248,0.07); border-color:rgba(56,189,248,0.20); color:#7dd3fc; }
.cc-freq { background:rgba(124,92,255,0.07); border-color:var(--primary-md); color:#c4b5fd; }
.cc-tip  { background:rgba(245,158,11,0.07); border-color:rgba(245,158,11,0.20); color:#fcd34d; }
.cc-label { font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; font-size: 0.625rem; opacity: 0.75; margin-right: 1px; }

/* ════════════════════════════════════════════════════════
   FOLLOW-UP QUESTIONS
════════════════════════════════════════════════════════ */
.fu-section {
  margin: 2.5rem 0 0.5rem; padding-top: 0.85rem; border-top: 1px solid var(--border);
}
.fu-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 0.65rem;
}
.fu-header-icon { font-size: 0.85rem; }
.fu-header-label {
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em;  /* 12px */
  text-transform: uppercase; color: var(--subtle);
}
.fu-row { display: flex; flex-wrap: wrap; gap: 8px; }
.fu-chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(124,92,255,0.06); border: 1px solid rgba(124,92,255,0.20);
  border-radius: 10px; padding: 7px 14px;
  font-size: 0.875rem; font-weight: 400; color: var(--muted);  /* 14px */
  text-decoration: none !important; cursor: pointer;
  transition: background 0.18s, border-color 0.18s, color 0.18s, transform 0.20s, box-shadow 0.20s;
  animation: chipIn 0.3s ease both; will-change: transform;
  line-height: 1.45;
}
.fu-chip:nth-child(1){animation-delay:0.08s}.fu-chip:nth-child(2){animation-delay:0.14s}
.fu-chip:nth-child(3){animation-delay:0.20s}.fu-chip:nth-child(4){animation-delay:0.26s}
.fu-chip:hover {
  background: var(--primary-lo); border-color: rgba(124,92,255,0.45);
  color: #c4b5fd; transform: translateY(-2px); box-shadow: 0 4px 14px rgba(124,92,255,0.15);
}
.fu-chip-arrow { font-size: 0.7rem; opacity: 0.5; flex-shrink: 0; }

/* ════════════════════════════════════════════════════════
   SOURCES EXPANDER
════════════════════════════════════════════════════════ */
details {
  background: rgba(13,22,38,0.6) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important; padding: 3px 11px !important;
}
details summary { color: var(--subtle); font-size: 0.74rem; cursor: pointer; font-weight: 500; }
details summary:hover { color: #a78bfa; }
.src-chip {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(124,92,255,0.08); color: #a78bfa; border: 1px solid rgba(124,92,255,0.16);
  border-radius: 4px; padding: 1px 7px; font-size: 0.69rem; font-weight: 500; margin: 2px 2px;
}
.src-prev {
  background: #050c18; border: 1px solid var(--border); border-radius: var(--r-sm);
  padding: 9px 13px; font-size: 0.76rem; color: var(--muted);
  line-height: 1.7; margin-bottom: 7px; white-space: pre-wrap; word-break: break-word;
}

/* ════════════════════════════════════════════════════════
   RESOURCE CARDS
════════════════════════════════════════════════════════ */
.res-list { display: flex; flex-direction: column; gap: 6px; margin: 6px 0; }
.res-card {
  display: flex; align-items: center; gap: 12px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-sm); padding: 11px 16px;
  text-decoration: none !important; width: 100%; box-sizing: border-box;
  transition: border-color 0.18s, background 0.18s, transform 0.18s, box-shadow 0.18s;
  animation: fadeIn 0.3s ease both;
}
.res-card:hover {
  border-color: var(--primary); background: var(--card-raised);
  transform: translateX(3px); box-shadow: var(--sh-sm);
}
.res-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.res-content { flex: 1; min-width: 0; overflow: hidden; }
.res-title {
  font-size: 0.875rem; font-weight: 500; color: #c4b5fd;  /* 14px */
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  line-height: 1.4; display: block;
}
.res-meta-row { display: flex; align-items: center; gap: 6px; margin-top: 4px; flex-wrap: nowrap; }
.res-meta { font-size: 0.75rem; color: var(--subtle); white-space: nowrap; }  /* 12px */
.res-sep  { font-size: 0.75rem; color: var(--border-hi); flex-shrink: 0; }
.res-badge {
  font-size: 0.6875rem; font-weight: 600; padding: 2px 7px; border-radius: 4px;  /* 11px */
  background: var(--primary-lo); color: #a78bfa; border: 1px solid var(--primary-md);
  white-space: nowrap; flex-shrink: 0;
}
.res-diff-badge { font-size: 0.6875rem; font-weight: 600; padding: 2px 7px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; }
.res-diff-beg { background: var(--success-lo); color: #34d399; border: 1px solid rgba(16,185,129,0.22); }
.res-diff-int { background: var(--amber-lo);   color: #fbbf24; border: 1px solid rgba(245,158,11,0.22); }
.res-arrow { color: var(--subtle); flex-shrink: 0; transition: color 0.16s, transform 0.18s; display: flex; align-items: center; }
.res-card:hover .res-arrow { color: var(--primary); transform: translateX(3px); }

/* ════════════════════════════════════════════════════════
   VIDEO CARDS
════════════════════════════════════════════════════════ */
.yt-grid {
  display: grid; grid-template-columns: repeat(auto-fill,minmax(188px,1fr));
  gap: 11px; margin-bottom: 0.4rem;
}
.yt-card {
  display: flex; flex-direction: column;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-md); overflow: hidden; text-decoration: none !important;
  transition: transform 0.25s cubic-bezier(0.34,1.3,0.64,1), box-shadow 0.25s ease, border-color 0.22s ease;
  animation: fadeUp 0.4s ease both; will-change: transform;
}
.yt-card:nth-child(1){animation-delay:0.05s}.yt-card:nth-child(2){animation-delay:0.12s}.yt-card:nth-child(3){animation-delay:0.19s}
.yt-card:hover {
  transform: translateY(-4px) scale(1.015);  /* spec: translateY(-4px) + slight scale */
  box-shadow: 0 20px 50px rgba(0,0,0,0.60), 0 4px 20px rgba(124,92,255,0.22);
  border-color: var(--primary);
}
.yt-thumb {
  position: relative; width: 100%; padding-top: 56.25%; background: #04091a; overflow: hidden;
}
.yt-thumb img {
  position: absolute; inset: 0; width: 100%; height: 100%;
  object-fit: cover; display: block; transition: transform 0.35s ease;
}
.yt-card:hover .yt-thumb img { transform: scale(1.06); }
.yt-thumb-fb { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--border-hi); font-size: 1.8rem; }
.yt-overlay {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(5,8,22,0.45); opacity: 0; transition: opacity 0.22s;
}
.yt-card:hover .yt-overlay { opacity: 1; }
.yt-play {
  width: 40px; height: 40px; border-radius: 50%; background: rgba(124,92,255,0.90);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 20px rgba(124,92,255,0.6);
  transform: scale(0.85); transition: transform 0.2s ease;
}
.yt-card:hover .yt-play { transform: scale(1); }
.yt-play svg { width: 13px; height: 13px; fill: #fff; margin-left: 2px; }
.yt-bage {
  position: absolute; bottom: 6px; right: 6px;
  background: rgba(0,0,0,0.82); border-radius: 4px; padding: 2px 6px;
  display: flex; align-items: center; gap: 3px;
}
.yt-bage svg { width: 10px; height: 10px; fill: #ff0000; }
.yt-bage span { font-size: 0.59rem; font-weight: 700; color: #fff; }
.yt-duration {
  position: absolute; bottom: 6px; left: 6px;
  background: rgba(0,0,0,0.82); border-radius: 4px;
  padding: 2px 6px; font-size: 0.59rem; font-weight: 600; color: #fff;
}
.yt-info { padding: 11px 13px 13px; }
.yt-title {
  font-size: 0.875rem; font-weight: 500; color: var(--text); line-height: 1.45;  /* 14px */
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.yt-channel { font-size: 0.75rem; color: var(--subtle); margin-top: 5px; }  /* 12px */
.yt-card-meta { display: flex; align-items: center; gap: 5px; margin-top: 5px; }
.yt-topic-tag {
  font-size: 0.57rem; font-weight: 600; padding: 1px 5px; border-radius: 3px;
  background: var(--primary-lo); color: #a78bfa; border: 1px solid var(--primary-md);
}

/* ════════════════════════════════════════════════════════
   LOADING PIPELINE
════════════════════════════════════════════════════════ */
.ai-pipeline {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 18px 20px; animation: fadeUp 0.2s ease;
}
.pipeline-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.pipeline-dots { display: flex; gap: 5px; }
.pipeline-dot {
  width: 7px; height: 7px; border-radius: 50%; background: var(--primary); opacity: 0.6;
  animation: typingDot 1.4s infinite ease-in-out;
}
.pipeline-dot:nth-child(2){animation-delay:0.2s}.pipeline-dot:nth-child(3){animation-delay:0.4s}
.pipeline-title { font-size: 0.80rem; font-weight: 600; color: var(--text); letter-spacing: -0.01em; }
.pipeline-steps { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.pipeline-step { display: flex; align-items: center; gap: 10px; }
.step-icon {
  width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-size: 0.65rem; font-weight: 700; flex-shrink: 0;
}
.step-icon-done   { background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.30); }
.step-icon-active { background:var(--primary-lo); color:var(--primary); border:1px solid var(--primary-md); animation:pulse 1.2s infinite; }
.step-icon-wait   { background:transparent; color:var(--subtle); border:1px solid var(--border-hi); }
.step-label { font-size: 0.77rem; letter-spacing: -0.005em; }
.step-label-done   { color: #34d399; }
.step-label-active { color: var(--text); font-weight: 500; }
.step-label-wait   { color: var(--subtle); }
.pipeline-bar-wrap { height: 2px; background: var(--border); border-radius: 2px; overflow: hidden; }
.pipeline-bar {
  height: 100%; border-radius: 2px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  animation: shimmer 2s linear infinite;
  background-size: 400px 100%;
}
.skel {
  height: 10px; border-radius: 6px; margin: 7px 0;
  background: linear-gradient(90deg, var(--border) 25%, var(--border-hi) 50%, var(--border) 75%);
  background-size: 800px 100%; animation: shimmer 1.8s infinite linear;
}
.skel-short { width: 45%; } .skel-med { width: 70%; } .skel-long { width: 100%; }

/* ════════════════════════════════════════════════════════
   BOTTOM INPUT
════════════════════════════════════════════════════════ */
div[data-testid="stBottom"] {
  background: linear-gradient(to top, rgba(5,8,22,0.98) 0%, rgba(5,8,22,0.88) 65%, transparent 100%) !important;
  backdrop-filter: blur(24px) saturate(160%) !important;
  -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
  border-top: 1px solid rgba(23,32,53,0.55) !important;
  padding-top: 6px !important; padding-bottom: 3px !important;  /* -20% vertical */
}
div[data-testid="stBottom"] > div { background: transparent !important; }
/* ── Input card: slim, elegant (ChatGPT/Claude style) ── */
div[data-testid="stChatInput"] {
  background: rgba(11,20,40,0.95) !important; border: 1px solid var(--border-hi) !important;
  border-radius: 14px !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.35), 0 3px 12px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.025) !important;
  transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
div[data-testid="stChatInput"]:hover { border-color: rgba(124,92,255,0.32) !important; }
div[data-testid="stChatInput"]:focus-within {
  border-color: rgba(124,92,255,0.65) !important;
  box-shadow: 0 0 0 3px rgba(124,92,255,0.10), 0 6px 24px rgba(124,92,255,0.14), inset 0 1px 0 rgba(255,255,255,0.03) !important;
}
div[data-testid="stChatInput"] > div {
  background: transparent !important;
  padding: 1px 5px !important;   /* slim inner wrapper */
}
div[data-testid="stChatInput"] textarea {
  background: transparent !important; color: var(--text) !important;
  font-family: 'Inter', sans-serif !important; font-size: 0.9375rem !important;  /* 15px */
  line-height: 1.5 !important; border: none !important; box-shadow: none !important;
  caret-color: var(--primary) !important; padding: 3px 2px !important;   /* -20% padding */
  min-height: 18px !important; max-height: 100px !important; resize: none !important;
  letter-spacing: -0.01em !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
  color: var(--subtle) !important; font-size: 0.9rem !important; opacity: 0.65 !important;
}
div[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, #7C5CFF 0%, #5B8CFF 100%) !important;
  border: none !important; border-radius: 10px !important;
  width: 28px !important; height: 28px !important; min-width: 28px !important;  /* -20% size */
  padding: 0 !important; margin: 0 5px 0 3px !important;
  align-self: center !important; flex-shrink: 0 !important;
  box-shadow: 0 2px 8px rgba(124,92,255,0.28), inset 0 1px 0 rgba(255,255,255,0.18) !important;
  transition: transform 0.16s cubic-bezier(0.34,1.56,0.64,1), opacity 0.16s ease !important;
  opacity: 0.45 !important; cursor: pointer !important;
}
div[data-testid="stChatInput"]:focus-within button,
div[data-testid="stChatInput"]:hover button { opacity: 1 !important; }
div[data-testid="stChatInput"] button:hover { transform: scale(1.08) !important; opacity: 1 !important; }
div[data-testid="stChatInput"] button:active { transform: scale(0.94) !important; }
div[data-testid="stChatInput"] button svg {
  fill: rgba(255,255,255,0.95) !important; stroke: rgba(255,255,255,0.95) !important;
  width: 12px !important; height: 12px !important;
}

/* Input context chips */
.input-chips-wrap { display: flex; flex-direction: column; align-items: center; gap: 6px; margin-bottom: 7px; }
.input-chips-label { font-size: 0.625rem; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: var(--subtle); opacity: 0.55; }
.input-chips { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
.input-chip {
  display: inline-flex; align-items: center;
  background: rgba(13,22,38,0.90); border: 1px solid rgba(38,51,84,0.90);
  border-radius: 20px; padding: 4px 13px; font-size: 0.8125rem; font-weight: 500;  /* 13px */
  color: #6b82a8; text-decoration: none !important; white-space: nowrap; cursor: pointer;
  letter-spacing: -0.005em;
  transition: background 0.18s, border-color 0.18s, color 0.18s, transform 0.18s;
  animation: chipIn 0.35s ease both;
}
.input-chip:nth-child(1){animation-delay:0.04s}.input-chip:nth-child(2){animation-delay:0.09s}
.input-chip:nth-child(3){animation-delay:0.14s}.input-chip:nth-child(4){animation-delay:0.19s}
.input-chip:hover { background:rgba(124,92,255,0.10); border-color:rgba(124,92,255,0.38); color:#c4b5fd; transform:translateY(-1px); }

/* Keyboard hint — inside chips block above the pinned input */
.input-hint-bar { display:flex; align-items:center; justify-content:center; gap:10px; margin-top:8px; margin-bottom:0; opacity:0.6; }
.input-hint-seg { display:inline-flex; align-items:center; gap:5px; font-size:0.75rem; color:var(--subtle); }  /* 12px spec */
.input-hint-seg kbd {
  display:inline-flex; align-items:center; justify-content:center;
  background:rgba(255,255,255,0.04); border:1px solid rgba(38,51,84,0.95);
  border-bottom-width:2px; border-radius:4px; padding:1px 6px;
  font-size:0.6875rem; font-family:'Inter',sans-serif; color:#8B9EC0; line-height:1.5;
}
.input-hint-dot { width:2px; height:2px; border-radius:50%; background:var(--border-hi); flex-shrink:0; }

/* ════════════════════════════════════════════════════════
   MISC
════════════════════════════════════════════════════════ */
section.main > div { padding-bottom: 5.5rem !important; }
html { scroll-behavior: smooth; }
.stButton > button {
  background: var(--primary-lo) !important; border: 1px solid var(--primary-md) !important;
  color: #c4b5fd !important; border-radius: 20px !important;
  font-size: 0.875rem !important; font-weight: 500 !important;  /* 14px */
  padding: 5px 15px !important; transition: all 0.16s !important;
}
.stButton > button:hover {
  background: var(--primary-md) !important; color: #e9d5ff !important;
  transform: translateY(-1px) !important; box-shadow: 0 3px 12px rgba(124,92,255,0.2) !important;
}

/* ════════════════════════════════════════════════════════
   RESPONSIVE
════════════════════════════════════════════════════════ */
@media (max-width: 1024px) {
  .hero-title { font-size: 2.8rem; }
}
@media (max-width: 900px) {
  .hero-title { font-size: 2.2rem; }
  .yt-grid { grid-template-columns: repeat(auto-fill,minmax(160px,1fr)); }
  .lp-grid { grid-template-columns: 1fr; }
  .sq-grid { grid-template-columns: repeat(2,1fr); }
}
@media (max-width: 640px) {
  .hero-title { font-size: 1.8rem; }
  .sq-grid { grid-template-columns: repeat(2,1fr); }
  .yt-grid { grid-template-columns: 1fr 1fr; }
  .res-badge, .res-diff-badge { display: none; }
  .ans-section { padding: 13px 15px; }
  .fu-row { gap: 6px; }
  .fu-chip { font-size: 0.8125rem; padding: 6px 11px; }
}
@media (max-width: 480px) {
  .sq-grid { grid-template-columns: 1fr; }
  .yt-grid { grid-template-columns: 1fr; }
  .lp-steps { flex-wrap: wrap; }
  .hero-title { font-size: 1.55rem; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
QUICK_PROMPTS = [
    "Dynamic Programming", "ACID Properties", "Deadlock Prevention",
    "OOP Concepts", "Bias-Variance Tradeoff", "Binary Search Tree",
    "SQL Joins", "Process vs Thread",
]

RES_DOMAIN_META = {
    "geeksforgeeks.org": ("#22c55e", "Tutorial",   "GeeksforGeeks",  "8 min",  "Beginner"),
    "w3schools.com":     ("#3b82f6", "Reference",  "W3Schools",      "5 min",  "Beginner"),
    "programiz.com":     ("#f59e0b", "Tutorial",   "Programiz",      "7 min",  "Beginner"),
    "javatpoint.com":    ("#ec4899", "Tutorial",   "JavaTPoint",     "9 min",  "Intermediate"),
    "tutorialspoint.com":("#14b8a6", "Guide",      "TutorialsPoint", "10 min", "Intermediate"),
}

COACH_TOPIC_MAP = {
    "dynamic programming":  ("Hard",         ["Amazon", "Google", "Microsoft"]),
    "dp":                   ("Hard",         ["Amazon", "Google"]),
    "binary search":        ("Medium",       ["Google", "Meta", "Microsoft"]),
    "binary search tree":   ("Medium",       ["Amazon", "Flipkart", "Adobe"]),
    "tree":                 ("Medium",       ["Amazon", "Microsoft", "Paytm"]),
    "graph":                ("Hard",         ["Google", "Amazon", "Meta"]),
    "deadlock":             ("Intermediate", ["Microsoft", "Oracle", "IBM"]),
    "acid":                 ("Intermediate", ["Amazon", "Microsoft", "Oracle"]),
    "dbms":                 ("Intermediate", ["TCS", "Infosys", "Microsoft"]),
    "sql":                  ("Beginner",     ["TCS", "Cognizant", "Wipro"]),
    "normalization":        ("Intermediate", ["Oracle", "IBM", "TCS"]),
    "oop":                  ("Intermediate", ["Infosys", "TCS", "Wipro"]),
    "polymorphism":         ("Intermediate", ["Infosys", "Adobe", "Capgemini"]),
    "process":              ("Intermediate", ["Microsoft", "Amazon", "Apple"]),
    "thread":               ("Intermediate", ["Microsoft", "Amazon", "Apple"]),
    "scheduling":           ("Intermediate", ["Google", "Microsoft", "VMware"]),
    "mutex":                ("Intermediate", ["Microsoft", "Apple", "VMware"]),
    "semaphore":            ("Intermediate", ["Microsoft", "Apple", "VMware"]),
    "cap theorem":          ("Hard",         ["Amazon", "Google", "Stripe"]),
    "bias":                 ("Intermediate", ["Google", "Amazon", "Meta"]),
    "regression":           ("Intermediate", ["Amazon", "Flipkart", "Paytm"]),
    "machine learning":     ("Intermediate", ["Google", "Amazon", "Meta"]),
    "sorting":              ("Beginner",     ["TCS", "Infosys", "Amazon"]),
    "hashing":              ("Medium",       ["Google", "Amazon", "Adobe"]),
    "linked list":          ("Beginner",     ["Amazon", "Flipkart", "Zoho"]),
    "stack":                ("Beginner",     ["Amazon", "Google", "Zoho"]),
    "queue":                ("Beginner",     ["Amazon", "Google", "Zoho"]),
    "heap":                 ("Medium",       ["Amazon", "Google", "Microsoft"]),
    "recursion":            ("Medium",       ["Amazon", "Google", "Microsoft"]),
    "array":                ("Beginner",     ["TCS", "Infosys", "Amazon"]),
}

# Follow-up question map: keyword → list of 3-4 contextual follow-ups
FOLLOW_UP_MAP = {
    "deadlock": [
        "What is Deadlock Detection?",
        "Banker's Algorithm explained",
        "Deadlock Prevention vs Avoidance",
        "What are OS Scheduling Algorithms?",
    ],
    "mutex": [
        "Semaphore vs Mutex in depth",
        "What is a Race Condition?",
        "Producer-Consumer Problem",
        "What is a Monitor in OS?",
    ],
    "semaphore": [
        "Mutex vs Semaphore differences",
        "What is the Dining Philosophers Problem?",
        "What is a Race Condition?",
        "Binary vs Counting Semaphore",
    ],
    "process": [
        "What is a Thread vs Process?",
        "What is Context Switching?",
        "Inter-Process Communication (IPC)",
        "What is a PCB in OS?",
    ],
    "thread": [
        "Process vs Thread — key differences",
        "What is Multithreading?",
        "Thread synchronization explained",
        "What is a Deadlock?",
    ],
    "scheduling": [
        "Round Robin vs FCFS Scheduling",
        "What is CPU Burst Time?",
        "Preemptive vs Non-Preemptive Scheduling",
        "What is Starvation in OS?",
    ],
    "acid": [
        "What is Database Isolation Level?",
        "ACID vs BASE in distributed systems",
        "What is a Transaction in DBMS?",
        "CAP Theorem explained",
    ],
    "dbms": [
        "Explain Database Normalization",
        "What are SQL Joins?",
        "What is Indexing in databases?",
        "ACID Properties with examples",
    ],
    "normalization": [
        "1NF vs 2NF vs 3NF explained",
        "What is BCNF?",
        "When should you denormalize?",
        "What are Functional Dependencies?",
    ],
    "sql": [
        "INNER JOIN vs LEFT JOIN explained",
        "What are SQL Indexes?",
        "GROUP BY vs HAVING clause",
        "What is a Subquery?",
    ],
    "dynamic programming": [
        "Memoization vs Tabulation",
        "What is the Knapsack Problem?",
        "Longest Common Subsequence",
        "Coin Change Problem explained",
    ],
    "dp": [
        "Memoization vs Tabulation",
        "What is the Knapsack Problem?",
        "Coin Change Problem",
        "Matrix Chain Multiplication",
    ],
    "binary search": [
        "Binary Search on Answer technique",
        "Binary Search Tree operations",
        "Lower Bound vs Upper Bound",
        "Search in a Rotated Array",
    ],
    "binary search tree": [
        "AVL Tree vs BST",
        "BST Insertion and Deletion",
        "Inorder traversal of BST",
        "Red-Black Tree basics",
    ],
    "tree": [
        "BFS vs DFS Traversal",
        "Binary Search Tree explained",
        "What is a Segment Tree?",
        "Lowest Common Ancestor (LCA)",
    ],
    "graph": [
        "BFS vs DFS for Graphs",
        "Dijkstra's Algorithm explained",
        "What is a Topological Sort?",
        "Detect Cycle in a Graph",
    ],
    "oop": [
        "Inheritance vs Composition",
        "What is Polymorphism?",
        "Abstract Class vs Interface",
        "SOLID Principles explained",
    ],
    "polymorphism": [
        "Compile-time vs Runtime Polymorphism",
        "Method Overloading vs Overriding",
        "What is Duck Typing?",
        "Abstract Class vs Interface",
    ],
    "machine learning": [
        "Bias-Variance Tradeoff explained",
        "Overfitting vs Underfitting",
        "Supervised vs Unsupervised Learning",
        "What is Cross-Validation?",
    ],
    "bias": [
        "Overfitting vs Underfitting",
        "Regularization (L1 vs L2)",
        "How does Cross-Validation work?",
        "What is a Validation Set?",
    ],
    "sorting": [
        "QuickSort vs MergeSort comparison",
        "What is HeapSort?",
        "Stable vs Unstable Sorting",
        "When to use each sorting algorithm?",
    ],
    "hashing": [
        "Collision Resolution techniques",
        "Open Addressing vs Chaining",
        "What is a Hash Map?",
        "Consistent Hashing explained",
    ],
    "linked list": [
        "Singly vs Doubly Linked List",
        "Detect a Cycle in Linked List",
        "Reverse a Linked List",
        "Skip List data structure",
    ],
    "recursion": [
        "Recursion vs Iteration trade-offs",
        "What is Tail Recursion?",
        "Tower of Hanoi explained",
        "Backtracking vs Recursion",
    ],
    "cap theorem": [
        "ACID vs BASE systems",
        "What is Eventual Consistency?",
        "CP vs AP systems explained",
        "Distributed Systems basics",
    ],
}

LEARNING_PATHS = [
    {
        "title": "Operating Systems",
        "icon": "🖥️",
        "steps": ["Process vs Thread", "Synchronization", "Deadlocks", "Scheduling", "Memory Management"],
        "params": [("pt", 7), ("sq", 0), ("sq", 6), None, None],
    },
    {
        "title": "DBMS Roadmap",
        "icon": "🗄️",
        "steps": ["Normalization", "Transactions", "ACID Properties", "Indexing", "SQL Joins"],
        "params": [None, None, ("sq", 1), None, ("pt", 6)],
    },
]

_SUGGESTED_Q_META = [
    ("Difference between Mutex and Semaphore",   "os",   "Synchronization"),
    ("Explain ACID properties with examples",     "dbms", "Transactions"),
    ("What is Dynamic Programming?",              "dsa",  "Optimization"),
    ("Process vs Thread — key differences",       "os",   "Concurrency"),
    ("What is Polymorphism in OOP?",              "oop",  "Core Concept"),
    ("What is the Bias-Variance tradeoff?",        "ml",   "Model Evaluation"),
    ("Explain Deadlock prevention techniques",     "os",   "Deadlocks"),
    ("Most asked DBMS interview questions",        "dbms", "Interview Prep"),
    ("How does Binary Search work?",              "dsa",  "Searching"),
]
_SQ_BADGE_LABELS = {"dsa":"DSA","dbms":"DBMS","os":"OS","oop":"OOP","ml":"ML"}

_SQ_LIST = [q for q, _, _ in _SUGGESTED_Q_META]

_SIDEBAR_TOPICS = [
    ("DSA",  "Arrays · Trees · Graphs · DP",      "trending", True),
    ("ML",   "Regression · Bias-Variance",         "trending", True),
    ("DBMS", "SQL · ACID · Normalization",         "core",     False),
    ("OS",   "Processes · Scheduling · Deadlocks", "core",     False),
    ("OOP",  "Encapsulation · Polymorphism",       "core",     False),
]

_LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 '
    '3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>'
    '<path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 '
    '3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>'
    '</svg>'
)

_ARROW_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
    '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'
)

_YT_ICON = (
    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5'
    'A3 3 0 0 0 .5 6.2C0 8.1 0 12 0 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1'
    'c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1C24 15.9 24 12 24 12'
    's0-3.9-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/></svg>'
)

_DURATION_HINTS = ["10-15 min", "8-12 min", "12-18 min", "6-10 min", "15-20 min"]

_PIPELINE_STEPS = [
    "Analyzing Question",
    "Searching Knowledge Base",
    "Finding Resources",
    "Generating Answer",
]

# ═══════════════════════════════════════════════════════════════════════════════
# ANSWER SECTION PARSER
# ═══════════════════════════════════════════════════════════════════════════════
_SECTION_MAP = {
    "definition":                ("ans-def", "ans-label-def", "#3b82f6", "Definition"),
    "explanation":               ("ans-exp", "ans-label-exp", "#7c5cff", "Explanation"),
    "example":                   ("ans-ex",  "ans-label-ex",  "#10b981", "Example"),
    "interview tip":             ("ans-tip", "ans-label-tip", "#f59e0b", "Interview Insight"),
    "interview insight":         ("ans-tip", "ans-label-tip", "#f59e0b", "Interview Insight"),
    "key takeaway":              ("ans-key", "ans-label-key", "#14b8a6", "Key Takeaways"),
    "key takeaways":             ("ans-key", "ans-label-key", "#14b8a6", "Key Takeaways"),
    "common mistakes":           ("ans-mis", "ans-label-mis", "#ec4899", "Common Mistakes"),
    "common mistake":            ("ans-mis", "ans-label-mis", "#ec4899", "Common Mistakes"),
    "common follow-up questions":("ans-fup", "ans-label-fup", "#f43f5e", "Common Follow-up Questions"),
    "follow-up questions":       ("ans-fup", "ans-label-fup", "#f43f5e", "Common Follow-up Questions"),
    "follow up questions":       ("ans-fup", "ans-label-fup", "#f43f5e", "Common Follow-up Questions"),
}

_SECTION_RE = re.compile(
    r"(?:^|\n)\*\*("
    r"Definition|Explanation|Example|Interview Tip|Interview Insight"
    r"|Key Takeaways?|Key Takeaway"
    r"|Common Mistakes?|Common Mistake"
    r"|Common Follow-up Questions?|Follow-up Questions?|Follow up Questions?"
    r"):?\*\*:?\s*",
    re.IGNORECASE | re.MULTILINE,
)


def _md_to_html(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    lines, out, in_ul, in_ol = text.split("\n"), [], False, False
    for line in lines:
        stripped = line.lstrip()
        num_match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        if stripped.startswith(("- ", "• ", "* ")):
            if in_ol: out.append("</ol>"); in_ol = False
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li>{stripped[2:].strip()}</li>")
        elif num_match:
            if in_ul: out.append("</ul>"); in_ul = False
            if not in_ol: out.append("<ol>"); in_ol = True
            out.append(f"<li>{num_match.group(2).strip()}</li>")
        else:
            if in_ul: out.append("</ul>"); in_ul = False
            if in_ol: out.append("</ol>"); in_ol = False
            out.append(line if not line.strip() else f"<p>{line}</p>")
    if in_ul: out.append("</ul>")
    if in_ol: out.append("</ol>")
    return "\n".join(out)


def _build_answer_html(text: str) -> str:
    parts = _SECTION_RE.split(text)
    if len(parts) <= 1:
        return f'<div class="ans-plain">{_md_to_html(text.strip())}</div>'
    sections_html = ""
    preamble = parts[0].strip()
    if preamble:
        sections_html += (
            f'<div class="ans-section ans-gen">'
            f'<div class="ans-body">{_md_to_html(preamble)}</div>'
            f'</div>'
        )
    i = 1
    while i < len(parts) - 1:
        section_name = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        i += 2
        key = section_name.lower()
        css_mod, lbl_cls, bar_color, display = _SECTION_MAP.get(
            key, ("ans-gen", "ans-label-gen", "#6b7280", section_name.title())
        )
        bar = f'<span class="ans-label-bar" style="background:{bar_color}"></span>'
        body = _md_to_html(content) if content else ""
        sections_html += (
            f'<div class="ans-section {css_mod}">'
            f'  <div class="ans-label {lbl_cls}">{bar}{display}</div>'
            f'  <div class="ans-body">{body}</div>'
            f'</div>'
        )
    return f'<div class="ans-wrap">{sections_html}</div>'


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def _domain_meta(url: str):
    for domain, meta in RES_DOMAIN_META.items():
        if domain in url:
            return meta
    return ("#6b7280", "Article", "External", "6 min", "Intermediate")


def infer_coach_data(prompt: str):
    p_lower = prompt.lower()
    for keyword, (diff, companies) in COACH_TOPIC_MAP.items():
        if keyword in p_lower:
            return diff, companies[:3]
    return "Intermediate", ["Amazon", "Google", "Microsoft"]


def generate_follow_ups(prompt: str) -> list[str]:
    """Return 3-4 contextual follow-up questions based on the prompt."""
    p_lower = prompt.lower()
    for keyword, questions in FOLLOW_UP_MAP.items():
        if keyword in p_lower:
            return questions[:4]
    # Generic fallback based on common CS categories
    if any(w in p_lower for w in ["sort", "array", "list", "tree", "graph", "search"]):
        return [
            "Time and Space Complexity analysis",
            "Best sorting algorithm for this case?",
            "When would you use this data structure?",
            "Most common interview patterns for DSA",
        ]
    if any(w in p_lower for w in ["class", "inherit", "encapsul", "abstract", "interface"]):
        return [
            "SOLID Principles in OOP",
            "Abstract Class vs Interface",
            "Design Patterns overview",
            "What is Dependency Injection?",
        ]
    return [
        "Most asked interview questions on this topic",
        "How does this concept apply in system design?",
        "Common mistakes beginners make here",
        "Real-world examples of this concept",
    ]


def _extract_topic(prompt: str) -> str:
    p = prompt.strip()
    p = re.sub(r"^(explain|what is|what are|describe|tell me about)\s+", "", p, flags=re.IGNORECASE)
    return p[:40].strip().title()


def _get_contextual_chips(messages: list) -> list[tuple]:
    """
    Return 4 context-aware quick chips.
    When conversation is active, chips relate to the last question.
    When empty, return defaults.
    """
    defaults = [
        ("Dynamic Programming",  "pt", 0),
        ("ACID Properties",      "pt", 1),
        ("Deadlock Prevention",  "pt", 2),
        ("Process vs Thread",    "pt", 7),
    ]
    if not messages:
        return defaults
    # Find last user message
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    if not last_user:
        return defaults
    p = last_user.lower()
    # Return related chips
    if any(w in p for w in ["deadlock", "mutex", "semaphore", "process", "thread", "scheduling"]):
        return [
            ("Process vs Thread",     "pt", 7),
            ("Deadlock Prevention",   "pt", 2),
            ("CPU Scheduling",        "sq", 0),
            ("OS Interview Questions","sq", 6),
        ]
    if any(w in p for w in ["acid", "dbms", "sql", "normaliz", "transaction"]):
        return [
            ("ACID Properties",       "pt", 1),
            ("SQL Joins",             "pt", 6),
            ("DBMS Questions",        "sq", 7),
            ("Normalization",         "sq", 1),
        ]
    if any(w in p for w in ["dp", "dynamic", "recursion", "graph", "tree", "sort", "binary"]):
        return [
            ("Dynamic Programming",   "pt", 0),
            ("Binary Search",         "sq", 8),
            ("DSA Interview Prep",    "sq", 2),
            ("OOP Concepts",          "pt", 3),
        ]
    if any(w in p for w in ["oop", "class", "inherit", "polymorphism", "encapsul"]):
        return [
            ("OOP Concepts",          "pt", 3),
            ("Polymorphism",          "sq", 4),
            ("Abstract vs Interface", "sq", 4),
            ("SOLID Principles",      "sq", 4),
        ]
    return defaults


# ═══════════════════════════════════════════════════════════════════════════════
# RENDER COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════
def render_answer(text: str) -> None:
    st.markdown(_build_answer_html(text), unsafe_allow_html=True)


def render_coach_chips(prompt: str) -> None:
    difficulty, companies = infer_coach_data(prompt)
    diff_cls = {"Beginner":"cc-diff","Medium":"cc-diff","Intermediate":"cc-freq","Hard":"cc-tip"}.get(difficulty,"cc-diff")
    companies_str = " · ".join(companies)
    st.markdown(
        f'<div class="coach-row">'
        f'  <span class="coach-chip {diff_cls}"><span class="cc-label">Difficulty</span>{difficulty}</span>'
        f'  <span class="coach-chip cc-freq"><span class="cc-label">Asked In</span>{companies_str}</span>'
        f'  <span class="coach-chip cc-tip"><span class="cc-label">Tip</span>Recruiters often ask follow-ups</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_sources(sources: list) -> None:
    if not sources: return
    st.markdown(
        '<div class="sec-head"><span class="sec-head-icon">📄</span>'
        '<span class="sec-head-label">Knowledge Sources</span></div>',
        unsafe_allow_html=True,
    )
    with st.expander(f"View {len(sources)} source{'s' if len(sources)!=1 else ''}", expanded=False):
        chip_html = "".join(
            f'<span class="src-chip">{escape(str(s.get("source","Unknown")))}</span>'
            for s in sources
        )
        st.markdown(chip_html, unsafe_allow_html=True)
        st.markdown("")
        for i, s in enumerate(sources, 1):
            fname = s.get("source","Unknown"); content = s.get("content",""); score = s.get("score")
            label = f"**{i}. `{fname}`**"
            if score is not None: label += f"  ·  relevance {score:.3f}"
            st.markdown(label)
            st.markdown(f'<div class="src-prev">{escape(content)}</div>', unsafe_allow_html=True)


def render_resource_cards(links: list) -> None:
    if not links: return
    st.markdown(
        '<div class="sec-head"><span class="sec-head-icon">📚</span>'
        '<span class="sec-head-label">Recommended Reading</span></div>',
        unsafe_allow_html=True,
    )
    cards = '<div class="res-list">'
    for link in links:
        title = escape(str(link.get("title","") or "Untitled"))
        url   = escape(str(link.get("url","") or "#"))
        color, badge, domain_name, read_time, difficulty = _domain_meta(link.get("url",""))
        diff_cls = "res-diff-beg" if difficulty == "Beginner" else "res-diff-int"
        cards += (
            f'<a class="res-card" href="{url}" target="_blank" rel="noopener noreferrer">'
            f'  <div class="res-dot" style="background:{color};box-shadow:0 0 6px {color}66"></div>'
            f'  <div class="res-content">'
            f'    <div class="res-title">{title}</div>'
            f'    <div class="res-meta-row">'
            f'      <span class="res-meta">{domain_name}</span>'
            f'      <span class="res-sep">·</span>'
            f'      <span class="res-meta">{read_time} read</span>'
            f'      <span class="res-sep">·</span>'
            f'      <span class="res-meta">{badge}</span>'
            f'    </div>'
            f'  </div>'
            f'  <span class="res-diff-badge {diff_cls}">{difficulty}</span>'
            f'  <span class="res-arrow">{_ARROW_SVG}</span>'
            f'</a>'
        )
    cards += '</div>'
    st.markdown(cards, unsafe_allow_html=True)


def _video_card_html(v: dict, idx: int = 0) -> str:
    if not isinstance(v, dict): return ""
    title    = escape(str(v.get("title","") or "Untitled"))
    channel  = escape(str(v.get("channel","") or "YouTube"))
    url      = escape(str(v.get("video_url","") or "#"))
    thumb    = escape(str(v.get("thumbnail_url","") or ""))
    duration = _DURATION_HINTS[idx % len(_DURATION_HINTS)]
    thumb_html = (
        f'<img src="{thumb}" alt="{title}" loading="lazy">'
        if thumb else '<div class="yt-thumb-fb">▶</div>'
    )
    overlay = (
        '<div class="yt-overlay">'
        '  <div class="yt-play"><svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg></div>'
        '</div>'
    )
    return (
        f'<a class="yt-card" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'  <div class="yt-thumb">'
        f'    {thumb_html}{overlay}'
        f'    <div class="yt-duration">{duration}</div>'
        f'    <div class="yt-bage">{_YT_ICON}<span>YouTube</span></div>'
        f'  </div>'
        f'  <div class="yt-info">'
        f'    <div class="yt-title">{title}</div>'
        f'    <div class="yt-channel">{channel}</div>'
        f'  </div>'
        f'</a>'
    )


def render_youtube_cards(videos: list) -> None:
    if not videos: return
    cards = [_video_card_html(v, i) for i, v in enumerate(videos)]
    cards = [c for c in cards if c]
    if not cards: return
    st.markdown(
        '<div class="sec-head"><span class="sec-head-icon">🎬</span>'
        '<span class="sec-head-label">Recommended Videos</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="yt-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_follow_ups(prompt: str, follow_ups: list) -> None:
    if not follow_ups: return
    chips_html = '<div class="fu-row">'
    for q in follow_ups:
        encoded = urllib.parse.quote(q, safe="")
        chips_html += (
            f'<a class="fu-chip" href="?fq={encoded}" target="_self">'
            f'{escape(q)}'
            f'<span class="fu-chip-arrow">→</span>'
            f'</a>'
        )
    chips_html += '</div>'
    st.markdown(
        f'<div class="fu-section">'
        f'  <div class="fu-header">'
        f'    <span class="fu-header-icon">💡</span>'
        f'    <span class="fu-header-label">Continue Learning</span>'
        f'  </div>'
        f'  {chips_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_assistant_message(msg: dict) -> None:
    render_answer(msg["content"])
    render_coach_chips(msg.get("prompt", ""))
    render_sources(msg.get("sources", []))
    render_resource_cards(msg.get("links", []))
    render_youtube_cards(msg.get("videos", []))
    render_follow_ups(msg.get("prompt", ""), msg.get("follow_ups", []))


def _pipeline_html(active_idx: int) -> str:
    steps_html = ""
    for i, label in enumerate(_PIPELINE_STEPS):
        if i < active_idx:
            icon_cls, label_cls, icon_char = "step-icon-done", "step-label-done", "✓"
        elif i == active_idx:
            icon_cls, label_cls, icon_char = "step-icon-active", "step-label-active", "◉"
        else:
            icon_cls, label_cls, icon_char = "step-icon-wait", "step-label-wait", "○"
        steps_html += (
            f'<div class="pipeline-step">'
            f'  <div class="step-icon {icon_cls}">{icon_char}</div>'
            f'  <span class="step-label {label_cls}">{label}</span>'
            f'</div>'
        )
    skels = (
        '<div class="skel skel-long"></div>'
        '<div class="skel skel-med"></div>'
        '<div class="skel skel-short"></div>'
    )
    return (
        f'<div class="ai-pipeline">'
        f'  <div class="pipeline-header">'
        f'    <div class="pipeline-dots">'
        f'      <div class="pipeline-dot"></div><div class="pipeline-dot"></div><div class="pipeline-dot"></div>'
        f'    </div>'
        f'    <span class="pipeline-title">{_PIPELINE_STEPS[active_idx]}</span>'
        f'  </div>'
        f'  <div class="pipeline-steps">{steps_html}</div>'
        f'  <div class="pipeline-bar-wrap"><div class="pipeline-bar"></div></div>'
        f'  <div style="margin-top:12px">{skels}</div>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECRETS GUARD
# ═══════════════════════════════════════════════════════════════════════════════
for _k in ("GROQ_API_KEY",):
    if _k not in st.secrets:
        st.error(
            f"`{_k}` missing from Streamlit secrets.\n\n"
            "Add to `.streamlit/secrets.toml`:\n"
            "```toml\nGROQ_API_KEY = \"your_key\"\nTAVILY_API_KEY = \"your_key\"\n```"
        )
        st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE LOADER
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_pipeline():
    try:
        rag = RAGPipeline(groq_api_key=st.secrets["GROQ_API_KEY"])
        rag.initialize(rebuild_vector_store=False)
        return rag
    except Exception as e:
        st.error(f"Failed to initialise pipeline: {e}"); st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "messages"       not in st.session_state: st.session_state.messages       = []
if "pending_prompt" not in st.session_state: st.session_state.pending_prompt = None
if "recent_topics"  not in st.session_state: st.session_state.recent_topics  = []

# ═══════════════════════════════════════════════════════════════════════════════
# QUERY PARAM HANDLER  (must run before any rendering)
# ═══════════════════════════════════════════════════════════════════════════════
_qp = st.query_params

if "sq" in _qp:
    try:
        _idx = int(_qp["sq"])
        if 0 <= _idx < len(_SQ_LIST):
            st.session_state.pending_prompt = _SQ_LIST[_idx]
    except (ValueError, IndexError): pass
    st.query_params.clear(); st.rerun()

if "pt" in _qp:
    try:
        _idx = int(_qp["pt"])
        if 0 <= _idx < len(QUICK_PROMPTS):
            st.session_state.pending_prompt = f"Explain {QUICK_PROMPTS[_idx]}"
    except (ValueError, IndexError): pass
    st.query_params.clear(); st.rerun()

if "fq" in _qp:
    try:
        _q = urllib.parse.unquote(_qp["fq"]).strip()
        if _q:
            st.session_state.pending_prompt = _q
    except Exception: pass
    st.query_params.clear(); st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])

    st.markdown(f"""
    <div class="sb-brand">
      <div class="sb-logo">{_LOGO_SVG}</div>
      <div style="flex:1">
        <div class="sb-wordmark">Prep Assistant</div>
        <div class="sb-sub">AI Interview Coach</div>
      </div>
      {f'<span class="sb-q-badge">{msg_count} Q</span>' if msg_count > 0 else ''}
    </div>
    """, unsafe_allow_html=True)

    # Learning Paths in sidebar
    st.markdown('<p class="sb-section-label">Learning Paths</p>', unsafe_allow_html=True)
    for path in LEARNING_PATHS:
        steps_html = "".join(
            f'<div class="sb-path-step"><div class="sb-path-node"></div>{escape(s)}</div>'
            for s in path["steps"][:4]
        )
        st.markdown(f"""
        <div style="margin-bottom:10px; padding:8px 10px; background:rgba(124,92,255,0.04); border:1px solid var(--border); border-radius:var(--r-sm);">
          <div class="sb-path-title"><span>{path['icon']}</span>{escape(path['title'])}</div>
          <div class="sb-path-steps">{steps_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # Knowledge Base topics
    st.markdown('<p class="sb-section-label">Knowledge Base</p>', unsafe_allow_html=True)
    current_cat = None
    for i, (name, sub, cat, is_trending) in enumerate(_SIDEBAR_TOPICS):
        if cat != current_cat:
            current_cat = cat
            cat_label = "🔥 Trending" if cat == "trending" else "Core Subjects"
            st.markdown(f'<p class="sb-category-label">{cat_label}</p>', unsafe_allow_html=True)
        dot_cls   = "tp-dot tp-dot-amber" if is_trending else "tp-dot"
        trend_tag = '<span class="tp-trend">HOT</span>' if is_trending else ""
        st.markdown(f"""
        <div class="tp" style="animation-delay:{i*0.06}s">
          <div class="{dot_cls}"></div>
          <div style="flex:1"><div class="tp-name">{name}</div><div class="tp-sub">{sub}</div></div>
          {trend_tag}
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑  Clear Chat", use_container_width=True):
        st.session_state.messages       = []
        st.session_state.pending_prompt = None
        st.session_state.recent_topics  = []
        st.rerun()

    st.markdown("""
    <div class="sb-tech">
      <div class="sb-tech-lbl">Powered by</div>
      <div class="sb-tech-val">Groq · LangChain · FAISS · Tavily</div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
with st.spinner("Initialising knowledge base…"):
    rag_pipeline = load_pipeline()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AREA — HERO OR COMPACT HEADER
# ═══════════════════════════════════════════════════════════════════════════════
has_messages = bool(st.session_state.messages)

if not has_messages:
    # ── Full hero (empty state) ──────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
      <div class="hero-eyebrow">
        <span class="hero-eyebrow-line"></span>
        AI Interview Coach
        <span class="live-dot" style="margin-left:8px">Live</span>
      </div>
      <div class="hero-title">Placement Prep Assistant</div>
      <div class="hero-sub">
        Your AI coach for <em>DSA</em>, <em>DBMS</em>, <em>OS</em>, <em>OOP</em> and <em>ML</em> interviews.
        Get structured, interview-ready answers with examples, insights and curated resources.
      </div>
    </div>

    <div class="trust-bar">
      <div class="trust-item">
        <span class="trust-val">24</span>
        <span class="trust-lbl">Topics</span>
      </div>
      <div class="trust-item">
        <span class="trust-val">150+</span>
        <span class="trust-lbl">Resources</span>
      </div>
      <div class="trust-item">
        <span class="trust-val">100+</span>
        <span class="trust-lbl">Videos</span>
      </div>
      <div class="trust-item">
        <span class="trust-val">AI</span>
        <span class="trust-lbl">Powered</span>
      </div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    # Welcome card
    st.markdown("""
    <div class="welcome-card">
      <h3>Start preparing for your next interview</h3>
      <p>Click any question below or type your own. Every answer includes a definition,
      explanation, real examples, interview insights, and curated learning resources.</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggested Questions
    st.markdown('<div class="section-label">Suggested Questions</div>', unsafe_allow_html=True)
    sq_html = '<div class="sq-grid">'
    for idx, (q_text, cat_key, meta_label) in enumerate(_SUGGESTED_Q_META):
        badge_label = _SQ_BADGE_LABELS.get(cat_key, cat_key.upper())
        sq_html += (
            f'<a class="sq-card" href="?sq={idx}" target="_self">'
            f'  <span class="sq-badge sq-badge-{cat_key}">{badge_label}</span>'
            f'  <span class="sq-title">{escape(q_text)}</span>'
            f'  <span class="sq-meta">{escape(meta_label)}</span>'
            f'</a>'
        )
    sq_html += '</div>'
    st.markdown(sq_html, unsafe_allow_html=True)

    # Learning Paths
    st.markdown('<div class="section-label" style="margin-top:1.8rem">Learning Paths</div>', unsafe_allow_html=True)
    lp_html = '<div class="lp-grid">'
    for path in LEARNING_PATHS:
        steps_html = ""
        for j, step in enumerate(path["steps"]):
            if j > 0:
                steps_html += '<span class="lp-arrow">→</span>'
            steps_html += f'<span class="lp-step">{escape(step)}</span>'
        lp_html += (
            f'<div class="lp-card">'
            f'  <div class="lp-card-title"><span class="lp-card-icon">{path["icon"]}</span>{escape(path["title"])}</div>'
            f'  <div class="lp-steps">{steps_html}</div>'
            f'</div>'
        )
    lp_html += '</div>'
    st.markdown(lp_html, unsafe_allow_html=True)

    # Popular Topics
    st.markdown('<div class="section-label" style="margin-top:1.8rem">Popular Topics</div>', unsafe_allow_html=True)
    chips_html = '<div class="pop-topics-wrap">'
    for idx, label in enumerate(QUICK_PROMPTS):
        chips_html += f'<a class="pop-chip" href="?pt={idx}" target="_self">{escape(label)}</a>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

else:
    # ── Compact header (conversation active) ─────────────────────────────────
    q_label = f"{msg_count} question{'s' if msg_count != 1 else ''} asked"
    st.markdown(f"""
    <div class="compact-header">
      <div class="compact-logo">🎯</div>
      <span class="compact-name">Placement Prep Assistant</span>
      <span class="compact-sep">·</span>
      <span class="compact-tag">AI Interview Coach</span>
      <span class="compact-spacer"></span>
      <span class="compact-q-count">{q_label}</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PERSISTENT CHAT HISTORY REPLAY
# ═══════════════════════════════════════════════════════════════════════════════
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            render_assistant_message(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY HANDLER
# ═══════════════════════════════════════════════════════════════════════════════
def run_query(prompt: str) -> None:
    # 1. Append + render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Track topic
    topic = _extract_topic(prompt)
    rv = st.session_state.recent_topics
    if topic not in rv: rv.append(topic)
    if len(rv) > 8: rv.pop(0)
    st.session_state.recent_topics = rv

    # 3. Progressive loading + API call
    with st.chat_message("assistant"):
        loading_slot = st.empty()

        loading_slot.markdown(_pipeline_html(0), unsafe_allow_html=True)
        time.sleep(0.55)

        loading_slot.markdown(_pipeline_html(1), unsafe_allow_html=True)
        time.sleep(0.50)

        loading_slot.markdown(_pipeline_html(2), unsafe_allow_html=True)
        try:
            answer, sources, links, videos = rag_pipeline.query(prompt)
        except Exception as e:
            answer = f"Something went wrong: {e}"
            sources, links, videos = [], [], []

        loading_slot.markdown(_pipeline_html(3), unsafe_allow_html=True)
        time.sleep(0.30)
        loading_slot.empty()

        # Compute follow-ups before rendering
        follow_ups = generate_follow_ups(prompt)

        render_answer(answer)
        render_coach_chips(prompt)
        render_sources(sources)
        render_resource_cards(links)
        render_youtube_cards(videos)
        render_follow_ups(prompt, follow_ups)

    # 4. Save complete message to session state
    st.session_state.messages.append({
        "role":       "assistant",
        "content":    answer,
        "prompt":     prompt,
        "sources":    sources,
        "links":      links,
        "videos":     videos,
        "follow_ups": follow_ups,
    })

    # 5. Auto-scroll
    st.markdown(
        '<div id="chat-bottom"></div>'
        '<script>setTimeout(()=>{document.getElementById("chat-bottom")'
        '.scrollIntoView({behavior:"smooth"})},100);</script>',
        unsafe_allow_html=True,
    )


# ── Pending prompt (from query params or follow-up chips) ─────────────────────
if st.session_state.pending_prompt:
    p = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    run_query(p)

# ── Context-aware input chips + keyboard hint (one block, always above input) ──
_ctx_chips = _get_contextual_chips(st.session_state.messages)
_chips_inner = "".join(
    f'<a class="input-chip" href="?{p}={i}" target="_self">{escape(lbl)}</a>'
    for lbl, p, i in _ctx_chips
)
st.markdown(
    f'<div class="input-chips-wrap">'
    f'  <span class="input-chips-label">Quick start</span>'
    f'  <div class="input-chips">{_chips_inner}</div>'
    f'  <div class="input-hint-bar">'
    f'    <span class="input-hint-seg"><kbd>Enter</kbd> to send</span>'
    f'    <span class="input-hint-dot"></span>'
    f'    <span class="input-hint-seg"><kbd>Shift</kbd> + <kbd>Enter</kbd> new line</span>'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask an interview question or explore a topic…"):
    run_query(prompt)
