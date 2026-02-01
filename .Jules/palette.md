## 2026-05-21 - Modal Interaction Standards
**Learning:** The `SettingsModal` lacked standard keyboard (Escape) and mouse (Backdrop click) dismissal patterns, which are critical for accessibility and usability.
**Action:** Implemented `useEffect` for Escape key and backdrop `onClick` handler. Future modals must replicate this pattern to maintain interaction consistency.
