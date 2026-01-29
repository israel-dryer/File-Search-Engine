
## 2024-10-18 - React List Memoization for Streaming Data
**Learning:** When streaming AI responses update a parent component frequently (e.g., every token), any non-memoized child lists (like search results) will be re-diffed on every update. Even if the DOM doesn't change, the React reconciliation cost for large lists (especially with `framer-motion`) is significant.
**Action:** Always isolate heavy lists into `React.memo` components or use `useMemo` when they are rendered alongside frequent high-speed state updates.
