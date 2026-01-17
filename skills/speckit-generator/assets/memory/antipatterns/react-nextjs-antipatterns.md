# React/Next.js Anti-Patterns Reference

> **Purpose**: Detailed detection patterns and remediation for React/Next.js anti-patterns
> **Parent**: `react-nextjs.md` (Section 11)
> **Usage**: Reference for antipattern-detector agent and /lint command

---

## Detection Patterns

Use these patterns to identify anti-patterns in code review:

### AP-RN-01: Using `useEffect` for Derived State

**Detection**:
```javascript
Pattern: /useEffect\([^)]*set\w+\([^)]*\)[^)]*,\s*\[[^\]]*\]/g
Pattern: useEffect that only calls a setter based on props/state
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Why It's Wrong**:
- Extra render cycle
- Stale state bugs
- Unnecessary complexity
- Performance overhead

**Remediation**:
```jsx
// ❌ Bad - useEffect for derived state
const [fullName, setFullName] = useState('');

useEffect(() => {
  setFullName(`${firstName} ${lastName}`);
}, [firstName, lastName]);

// ✅ Good - Calculate during render
const fullName = `${firstName} ${lastName}`;

// ✅ Good - useMemo for expensive calculations
const sortedItems = useMemo(() =>
  items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);
```

---

### AP-RN-02: Missing Dependency Array Items

**Detection**:
```javascript
Pattern: ESLint react-hooks/exhaustive-deps warnings
Pattern: useEffect/useCallback/useMemo referencing variables not in deps
```

**Severity**: HIGH
**Auto-fixable**: Partially (ESLint can suggest)

**Why It's Dangerous**:
- Stale closures
- Inconsistent behavior
- Hard-to-debug bugs
- Race conditions

**Remediation**:
```jsx
// ❌ Bad - Missing dependency
useEffect(() => {
  fetchData(userId);  // userId not in deps
}, []);

// ✅ Good - Include all dependencies
useEffect(() => {
  fetchData(userId);
}, [userId]);

// ✅ Good - Use useCallback for stable references
const fetchUserData = useCallback(() => {
  fetchData(userId);
}, [userId]);

useEffect(() => {
  fetchUserData();
}, [fetchUserData]);
```

---

### AP-RN-03: Prop Drilling

**Detection**:
```javascript
Pattern: Same prop passed through 3+ component levels
Pattern: Component receiving props only to pass to children
Pattern: Many props with similar prefixes (user, userData, userProfile)
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Indicators**:
- Components with 8+ props
- Props passed unchanged through intermediate components
- Renaming same data at each level

**Remediation**:
```jsx
// ❌ Bad - Drilling through layers
<GrandParent user={user}>
  <Parent user={user}>
    <Child user={user}>
      <GrandChild user={user} />

// ✅ Good - Context for global data
const UserContext = createContext(null);

function App() {
  return (
    <UserContext.Provider value={user}>
      <GrandParent />
    </UserContext.Provider>
  );
}

function GrandChild() {
  const user = useContext(UserContext);
  return <span>{user.name}</span>;
}

// ✅ Good - Composition pattern
<GrandParent>
  <UserProfile user={user} />
</GrandParent>
```

---

### AP-RN-04: Inline Function Props

**Detection**:
```jsx
Pattern: /onClick=\{(?:\(\)\s*=>|\(\w+\)\s*=>|function)/g
Pattern: Callbacks defined in JSX attributes
```

**Severity**: LOW
**Auto-fixable**: Partially

**Why It's Problematic**:
- New function reference every render
- Breaks React.memo optimization
- Unnecessary child re-renders

**When Acceptable**:
- Simple components without memo
- Event handlers that don't affect children
- Infrequent renders

**Remediation**:
```jsx
// ❌ Bad - New function every render
<Button onClick={() => handleClick(item.id)} />

// ✅ Good - Stable reference
const handleButtonClick = useCallback(() => {
  handleClick(item.id);
}, [item.id]);

<Button onClick={handleButtonClick} />

// ✅ Good - Data attribute pattern
const handleClick = useCallback((e) => {
  const id = e.currentTarget.dataset.id;
  processItem(id);
}, []);

<Button data-id={item.id} onClick={handleClick} />
```

---

### AP-RN-05: Direct DOM Manipulation

**Detection**:
```javascript
Pattern: /document\.(getElementById|querySelector|getElementsBy)/g
Pattern: Direct DOM property assignments
Pattern: /\.appendChild\(/g
```

**Severity**: HIGH
**Auto-fixable**: No

**Why It's Wrong**:
- Bypasses React's reconciliation
- Causes inconsistent state
- Memory leaks
- SSR incompatibility

**Remediation**:
```jsx
// ❌ Bad - Direct DOM manipulation
useEffect(() => {
  const el = document.getElementById('title');
  el.textContent = title;  // Bypasses React!
}, [title]);

// ✅ Good - React state
return <h1>{title}</h1>;

// ✅ Good - ref when necessary
const inputRef = useRef(null);

useEffect(() => {
  inputRef.current?.focus();
}, []);

return <input ref={inputRef} />;
```

---

### AP-RN-06: Not Memoizing Expensive Renders

**Detection**:
```javascript
Pattern: Large list renders without React.memo
Pattern: Components with expensive calculations without useMemo
Pattern: Frequent re-renders shown in React DevTools Profiler
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Indicators**:
- Laggy UI on state changes
- Lists with 50+ items re-rendering
- Components doing calculations in render

**Remediation**:
```jsx
// ❌ Bad - Re-renders on any parent update
function ExpensiveList({ items }) {
  return items.map(item => (
    <ExpensiveItem key={item.id} item={item} />
  ));
}

// ✅ Good - Memoized component
const ExpensiveItem = React.memo(function ExpensiveItem({ item }) {
  return <div>{/* expensive render */}</div>;
});

// ✅ Good - Memoized calculation
const sortedItems = useMemo(() =>
  [...items].sort((a, b) => a.score - b.score),
  [items]
);
```

---

### AP-RN-07: Using Index as Key

**Detection**:
```jsx
Pattern: /\.map\([^)]*,\s*\w+\)\s*=>\s*<\w+[^>]*key=\{\s*\w+\s*\}/g
Pattern: key={index} or key={i}
```

**Severity**: HIGH
**Auto-fixable**: No

**Why It's Wrong**:
- Breaks reconciliation on reorder
- Causes state bugs in controlled inputs
- Performance issues on insert/delete

**When Acceptable**:
- Static lists that never reorder
- No component state in list items
- Read-only display lists

**Remediation**:
```jsx
// ❌ Bad - Index as key
{items.map((item, index) => (
  <Item key={index} item={item} />
))}

// ✅ Good - Stable unique ID
{items.map(item => (
  <Item key={item.id} item={item} />
))}

// ✅ Good - Generated ID if none exists
const itemsWithIds = useMemo(() =>
  items.map((item, i) => ({ ...item, _id: item.id ?? `item-${i}` })),
  [items]
);
```

---

### AP-RN-08: State Updates in Render

**Detection**:
```javascript
Pattern: setState/dispatch called outside useEffect/handlers
Pattern: State update that triggers during render phase
Pattern: "Too many re-renders" error
```

**Severity**: HIGH
**Auto-fixable**: No

**Why It's Wrong**:
- Infinite render loops
- React warnings/errors
- Unpredictable state

**Remediation**:
```jsx
// ❌ Bad - setState during render
function Component({ data }) {
  const [processed, setProcessed] = useState(null);

  if (data && !processed) {
    setProcessed(process(data)); // Triggers re-render!
  }
}

// ✅ Good - Derived state
function Component({ data }) {
  const processed = useMemo(() =>
    data ? process(data) : null,
    [data]
  );
}

// ✅ Good - useEffect for side effects
function Component({ data }) {
  const [processed, setProcessed] = useState(null);

  useEffect(() => {
    if (data) {
      setProcessed(process(data));
    }
  }, [data]);
}
```

---

### AP-RN-09: Ignoring Server/Client Boundary (Next.js)

**Detection**:
```javascript
Pattern: 'use client' in components that could be server
Pattern: Hooks in app/layout.tsx without 'use client'
Pattern: Browser APIs (window, document) in server components
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Indicators**:
- Unnecessary 'use client' directives
- Hydration errors
- `window is not defined` errors

**Remediation**:
```jsx
// ❌ Bad - Client directive when not needed
'use client'  // Unnecessary!
function StaticCard({ title, content }) {
  return <div><h2>{title}</h2><p>{content}</p></div>;
}

// ✅ Good - Server component (default)
function StaticCard({ title, content }) {
  return <div><h2>{title}</h2><p>{content}</p></div>;
}

// ✅ Good - Client only when needed
'use client'
function InteractiveButton({ onClick }) {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

---

### AP-RN-10: Fetching in useEffect Without Cleanup

**Detection**:
```javascript
Pattern: useEffect with fetch/axios without AbortController
Pattern: useEffect with async without cleanup function
Pattern: setState after component unmount warnings
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Why It's Wrong**:
- Memory leaks
- State updates on unmounted components
- Race conditions

**Remediation**:
```jsx
// ❌ Bad - No cleanup
useEffect(() => {
  fetch(`/api/users/${id}`)
    .then(res => res.json())
    .then(data => setUser(data));
}, [id]);

// ✅ Good - With AbortController
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${id}`, { signal: controller.signal })
    .then(res => res.json())
    .then(data => setUser(data))
    .catch(err => {
      if (err.name !== 'AbortError') throw err;
    });

  return () => controller.abort();
}, [id]);

// ✅ Best - Use React Query / SWR
const { data: user } = useQuery(['user', id], () =>
  fetch(`/api/users/${id}`).then(r => r.json())
);
```

---

## Quick Reference Table

| Code | Name | Severity | Fixable |
|------|------|----------|---------|
| AP-RN-01 | useEffect for Derived State | MEDIUM | No |
| AP-RN-02 | Missing Dependencies | HIGH | Partial |
| AP-RN-03 | Prop Drilling | MEDIUM | No |
| AP-RN-04 | Inline Function Props | LOW | Partial |
| AP-RN-05 | Direct DOM Manipulation | HIGH | No |
| AP-RN-06 | No Memoization | MEDIUM | No |
| AP-RN-07 | Index as Key | HIGH | No |
| AP-RN-08 | State Updates in Render | HIGH | No |
| AP-RN-09 | Server/Client Boundary | MEDIUM | No |
| AP-RN-10 | Fetch Without Cleanup | MEDIUM | No |

---

## ESLint Configuration

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "error",
    "react/jsx-key": ["error", { "checkFragmentShorthand": true }],
    "react/no-direct-mutation-state": "error",
    "@next/next/no-html-link-for-pages": "error"
  }
}
```
