## 2026-02-06 - Search Result Accessibility
**Learning:** Clickable cards (`div` with `onClick`) are a common pattern that completely excludes keyboard users if not manually patched with `role="button"` and `onKeyDown`.
**Action:** Always wrap interactive "cards" in a semantic `<button>` or strictly enforce `role="button"` + `tabIndex` + key handlers (Enter/Space) pair immediately when adding `onClick`.

## 2026-05-21 - Modal Interaction Standards
**Learning:** The `SettingsModal` lacked standard keyboard (Escape) and mouse (Backdrop click) dismissal patterns, which are critical for accessibility and usability.
**Action:** Implemented `useEffect` for Escape key and backdrop `onClick` handler. Future modals must replicate this pattern to maintain interaction consistency.
