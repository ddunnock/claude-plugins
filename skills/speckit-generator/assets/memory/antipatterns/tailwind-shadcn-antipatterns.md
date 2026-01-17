# Tailwind/shadcn Anti-Patterns Reference

> **Purpose**: Detailed detection patterns and remediation for Tailwind/shadcn anti-patterns
> **Parent**: `tailwind-shadcn.md` (Section 14)
> **Usage**: Reference for antipattern-detector agent and /lint command

---

## Detection Patterns

Use these patterns to identify anti-patterns in code review:

### AP-TW-01: Inline Styles Instead of Tailwind

**Detection**:
```jsx
Pattern: /style=\{?\{[^}]+\}\}?/g
Pattern: CSS-in-JS libraries alongside Tailwind
Pattern: <style> tags in components
```

**Severity**: LOW
**Auto-fixable**: Partially

**When Acceptable**:
- Dynamic values (transforms, dimensions from calculations)
- CSS variables for theming
- Animation keyframes

**Remediation**:
```jsx
// ❌ Bad - Inline styles
<div style={{ marginTop: '16px', padding: '8px', backgroundColor: '#f0f0f0' }}>

// ✅ Good - Tailwind classes
<div className="mt-4 p-2 bg-gray-100">

// ✅ Acceptable - Dynamic values
<div style={{ transform: `translateX(${offset}px)` }}>

// ✅ Acceptable - CSS custom properties
<div style={{ '--progress': `${percent}%` } as React.CSSProperties}>
```

---

### AP-TW-02: Hardcoded Colors

**Detection**:
```jsx
Pattern: /(?:bg|text|border)-\[#[0-9a-fA-F]+\]/g
Pattern: Arbitrary color values not from theme
Pattern: RGB/HSL values in classes
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Why It's Wrong**:
- Breaks theme consistency
- Dark mode won't work
- Hard to maintain
- No semantic meaning

**Remediation**:
```jsx
// ❌ Bad - Hardcoded colors
<button className="bg-[#3b82f6] text-[#ffffff] border-[#2563eb]">

// ✅ Good - Theme colors
<button className="bg-primary text-primary-foreground border-primary/80">

// ✅ Good - Semantic colors
<button className="bg-blue-500 text-white border-blue-600">

// If custom color needed, add to tailwind.config.js:
// colors: { brand: { DEFAULT: '#3b82f6', dark: '#2563eb' } }
```

---

### AP-TW-03: Rebuilding shadcn Components

**Detection**:
```jsx
Pattern: Custom Button/Input/Dialog components when shadcn has them
Pattern: Recreating component variants manually
Pattern: Custom accessibility implementations
```

**Severity**: HIGH
**Auto-fixable**: No

**Why It's Wrong**:
- Missing accessibility features
- Inconsistent with design system
- Duplicated effort
- Missing keyboard navigation

**Remediation**:
```bash
# Install instead of building
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
```

```jsx
// ❌ Bad - Custom button
function MyButton({ children, variant }) {
  return (
    <button className={`px-4 py-2 ${variant === 'primary' ? 'bg-blue-500' : 'bg-gray-500'}`}>
      {children}
    </button>
  );
}

// ✅ Good - shadcn Button
import { Button } from "@/components/ui/button";

<Button variant="default">Click me</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="destructive">Delete</Button>
```

---

### AP-TW-04: Inconsistent Spacing

**Detection**:
```jsx
Pattern: Mix of p-3 and p-4 in similar contexts
Pattern: Arbitrary spacing values [12px] when scale exists
Pattern: margin/padding inconsistency in same component group
```

**Severity**: LOW
**Auto-fixable**: Partially

**Spacing Scale Reference**:
| Class | Value |
|-------|-------|
| 1 | 0.25rem (4px) |
| 2 | 0.5rem (8px) |
| 4 | 1rem (16px) |
| 6 | 1.5rem (24px) |
| 8 | 2rem (32px) |

**Remediation**:
```jsx
// ❌ Bad - Inconsistent spacing
<div className="p-3">  {/* 12px */}
  <div className="mb-[14px]">  {/* arbitrary */}
    <div className="p-4">  {/* 16px - different from parent */}

// ✅ Good - Consistent scale
<div className="p-4">  {/* 16px */}
  <div className="mb-4">  {/* 16px */}
    <div className="p-4">  {/* 16px */}
```

---

### AP-TW-05: !important Overuse

**Detection**:
```jsx
Pattern: /![\w-]+/g in className
Pattern: Multiple !important on same element
Pattern: !important used to override shadcn
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Why It's Wrong**:
- Indicates specificity war
- Hard to override later
- Sign of component boundary issues

**Remediation**:
```jsx
// ❌ Bad - !important abuse
<div className="!p-0 !m-0 !bg-white">

// ✅ Good - Proper class order (later wins)
<div className="bg-red-500 bg-blue-500">  {/* blue wins */}

// ✅ Good - Use cn() for conditional
import { cn } from "@/lib/utils";

<Button className={cn("bg-blue-500", isActive && "bg-green-500")}>

// ✅ Good - Component variants
const buttonVariants = cva("base-classes", {
  variants: {
    variant: {
      default: "bg-primary",
      custom: "bg-custom-color",
    }
  }
});
```

---

### AP-TW-06: Missing Dark Mode Support

**Detection**:
```jsx
Pattern: bg-white without dark:bg-* counterpart
Pattern: text-black without dark:text-*
Pattern: Hard-coded color values without dark variants
```

**Severity**: MEDIUM
**Auto-fixable**: Partially

**Remediation**:
```jsx
// ❌ Bad - No dark mode
<div className="bg-white text-black border-gray-200">

// ✅ Good - With dark mode
<div className="bg-white dark:bg-gray-900 text-black dark:text-white border-gray-200 dark:border-gray-700">

// ✅ Better - Use semantic colors
<div className="bg-background text-foreground border-border">
```

---

### AP-TW-07: Excessive Class Strings

**Detection**:
```jsx
Pattern: className with 15+ classes
Pattern: Repeated class patterns across components
Pattern: Long conditional class logic
```

**Severity**: LOW
**Auto-fixable**: No (requires extraction)

**Remediation**:
```jsx
// ❌ Bad - Too many classes
<button className="px-4 py-2 bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white font-medium rounded-lg shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">

// ✅ Good - Extract to component/variant
// components/ui/button.tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-blue-500 text-white hover:bg-blue-600 shadow-md hover:shadow-lg",
      },
    },
  }
);

// Usage
<Button variant="default">Click me</Button>
```

---

### AP-TW-08: Not Using CVA for Variants

**Detection**:
```jsx
Pattern: Ternary operators for class variants
Pattern: Complex className template literals
Pattern: Multiple boolean props controlling styles
```

**Severity**: LOW
**Auto-fixable**: No

**Remediation**:
```jsx
// ❌ Bad - Manual variant handling
function Badge({ variant, size }) {
  return (
    <span className={`
      ${variant === 'success' ? 'bg-green-100 text-green-800' : ''}
      ${variant === 'error' ? 'bg-red-100 text-red-800' : ''}
      ${size === 'sm' ? 'px-2 py-0.5 text-xs' : ''}
      ${size === 'lg' ? 'px-4 py-2 text-base' : ''}
    `}>

// ✅ Good - CVA variants
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center rounded-full font-medium",
  {
    variants: {
      variant: {
        success: "bg-green-100 text-green-800",
        error: "bg-red-100 text-red-800",
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        lg: "px-4 py-2 text-base",
      },
    },
    defaultVariants: {
      variant: "success",
      size: "sm",
    },
  }
);

function Badge({ variant, size }: VariantProps<typeof badgeVariants>) {
  return <span className={badgeVariants({ variant, size })} />;
}
```

---

### AP-TW-09: Missing Responsive Considerations

**Detection**:
```jsx
Pattern: Fixed widths without responsive breakpoints
Pattern: No sm:/md:/lg: prefixes in layouts
Pattern: Components that break on mobile
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Breakpoints**:
| Prefix | Min-width |
|--------|-----------|
| sm: | 640px |
| md: | 768px |
| lg: | 1024px |
| xl: | 1280px |
| 2xl: | 1536px |

**Remediation**:
```jsx
// ❌ Bad - Fixed layout
<div className="flex">
  <aside className="w-64">
  <main className="w-[800px]">

// ✅ Good - Responsive layout
<div className="flex flex-col md:flex-row">
  <aside className="w-full md:w-64">
  <main className="flex-1">

// ✅ Good - Responsive spacing
<div className="p-4 md:p-6 lg:p-8">

// ✅ Good - Responsive typography
<h1 className="text-2xl md:text-3xl lg:text-4xl">
```

---

### AP-TW-10: Ignoring Accessibility Classes

**Detection**:
```jsx
Pattern: Missing sr-only for icon-only buttons
Pattern: No focus-visible: states
Pattern: Missing aria-* attributes on interactive elements
```

**Severity**: HIGH
**Auto-fixable**: No

**Remediation**:
```jsx
// ❌ Bad - No accessibility
<button className="p-2">
  <IconClose />
</button>

// ✅ Good - Accessible
<button
  className="p-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
  aria-label="Close dialog"
>
  <IconClose aria-hidden="true" />
</button>

// ✅ Good - Screen reader text
<button className="p-2">
  <IconClose aria-hidden="true" />
  <span className="sr-only">Close dialog</span>
</button>

// ✅ Good - Focus states
<input className="
  focus:outline-none
  focus-visible:ring-2
  focus-visible:ring-ring
  focus-visible:ring-offset-2
" />
```

---

## Quick Reference Table

| Code | Name | Severity | Fixable |
|------|------|----------|---------|
| AP-TW-01 | Inline Styles | LOW | Partial |
| AP-TW-02 | Hardcoded Colors | MEDIUM | No |
| AP-TW-03 | Rebuilding shadcn | HIGH | No |
| AP-TW-04 | Inconsistent Spacing | LOW | Partial |
| AP-TW-05 | !important Overuse | MEDIUM | No |
| AP-TW-06 | Missing Dark Mode | MEDIUM | Partial |
| AP-TW-07 | Excessive Classes | LOW | No |
| AP-TW-08 | Not Using CVA | LOW | No |
| AP-TW-09 | Missing Responsive | MEDIUM | No |
| AP-TW-10 | Ignoring A11y | HIGH | No |

---

## ESLint/Prettier Configuration

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['tailwindcss'],
  rules: {
    'tailwindcss/classnames-order': 'warn',
    'tailwindcss/no-custom-classname': 'warn',
    'tailwindcss/no-contradicting-classname': 'error',
  },
};
```

```javascript
// prettier.config.js
module.exports = {
  plugins: ['prettier-plugin-tailwindcss'],
  tailwindConfig: './tailwind.config.js',
};
```

---

## Tailwind Config Best Practices

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Use CSS variables for theming
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
      },
    },
  },
};
```
