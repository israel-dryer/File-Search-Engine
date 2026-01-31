## 2026-02-06 - Search Result Accessibility
**Learning:** Clickable cards (`div` with `onClick`) are a common pattern that completely excludes keyboard users if not manually patched with `role="button"` and `onKeyDown`.
**Action:** Always wrap interactive "cards" in a semantic `<button>` or strictly enforce `role="button"` + `tabIndex` + key handlers (Enter/Space) pair immediately when adding `onClick`.
