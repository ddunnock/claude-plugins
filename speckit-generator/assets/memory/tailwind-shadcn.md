# TailwindCSS v4 & shadcn/ui Standards

> **Applies to**: All styling and UI components  
> **Version Constraint**: TailwindCSS v4.x, shadcn/ui latest  
> **Parent**: `constitution.md`

---

## 1. Design Principles (Avoiding AI Slop)

Generic, forgettable designs signal low effort. Every visual decision **MUST** be intentional and distinctive.

### 1.1 Core Philosophy

| Principle | Meaning |
|-----------|---------|
| **Intentional choices** | Every font, color, spacing decision has a reason |
| **High contrast** | Use extremes, not middle-ground compromises |
| **Distinctive > Safe** | Better to be memorable than forgettable |
| **Restraint** | One distinctive element, used decisively |

---

## 2. Typography System

### 2.1 Font Selection

**MUST NOT use** (generic/AI slop indicators):
- Inter, Roboto, Open Sans, Lato
- Arial, Helvetica, system-ui defaults
- Any font that "looks like every other website"

**Recommended fonts by context:**

| Context | Primary Choices | Fallback |
|---------|-----------------|----------|
| **Display/Headlines** | Playfair Display, Fraunces, Crimson Pro, Newsreader | Georgia |
| **Body/Technical** | IBM Plex Sans, Source Sans 3, Space Grotesk | system-ui |
| **Code/Data** | JetBrains Mono, Fira Code, IBM Plex Mono | monospace |
| **Distinctive/Brand** | Bricolage Grotesque, Instrument Serif, Satoshi | — |

### 2.2 Font Pairing Principles

**High contrast = interesting:**
- Display + Monospace (Playfair Display + JetBrains Mono)
- Serif + Geometric Sans (Crimson Pro + Space Grotesk)
- Variable font across extreme weights

**Weight contrast:**
```css
/* ❌ Bad: Subtle, forgettable */
h1 { font-weight: 600; }
p { font-weight: 400; }

/* ✅ Good: Dramatic, intentional */
h1 { font-weight: 900; }  /* or 100 for ultra-light */
p { font-weight: 400; }
```

### 2.3 Type Scale

Use **Major Third (1.250)** ratio for harmonious scaling:

| Step | Size | Usage |
|------|------|-------|
| -2 | 12px | Captions, labels |
| -1 | 15px | Small text |
| 0 | 19px | Body text (base) |
| 1 | 24px | Lead paragraphs |
| 2 | 30px | H4 |
| 3 | 37px | H3 |
| 4 | 46px | H2 |
| 5 | 58px | H1 |
| 6 | 72px | Display |

**Size jumps SHOULD be 3x+, not 1.5x** for headlines vs body.

### 2.4 TailwindCSS v4 Font Configuration

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  /* Typography - Distinctive choices */
  --font-display: "Playfair Display Variable", Georgia, serif;
  --font-sans: "IBM Plex Sans", system-ui, sans-serif;
  --font-mono: "JetBrains Mono Variable", ui-monospace, monospace;
  
  /* Type scale (Major Third 1.250) */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.9375rem;  /* 15px */
  --text-base: 1.1875rem; /* 19px */
  --text-lg: 1.5rem;     /* 24px */
  --text-xl: 1.875rem;   /* 30px */
  --text-2xl: 2.3125rem; /* 37px */
  --text-3xl: 2.875rem;  /* 46px */
  --text-4xl: 3.625rem;  /* 58px */
  --text-5xl: 4.5rem;    /* 72px */
}

@layer base {
  html {
    font-family: var(--font-sans);
    font-size: 16px;
  }
  
  h1, h2, h3 {
    font-family: var(--font-display);
    font-weight: 700;
  }
  
  code, pre {
    font-family: var(--font-mono);
  }
}
```

### 2.5 Google Fonts Loading

```tsx
// app/layout.tsx
import { Playfair_Display, IBM_Plex_Sans, JetBrains_Mono } from "next/font/google";

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const ibmPlex = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${playfair.variable} ${ibmPlex.variable} ${jetbrains.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

---

## 3. Color Strategy

### 3.1 The 60-30-10 Rule

| Proportion | Role | Example |
|------------|------|---------|
| **60%** | Dominant (backgrounds, large surfaces) | `--color-background` |
| **30%** | Secondary (cards, sections, containers) | `--color-card`, `--color-muted` |
| **10%** | Accent (CTAs, highlights, focus states) | `--color-primary`, `--color-accent` |

### 3.2 Palette Generation

Start with brand primary → derive 9 shades using OKLCH:

```css
@theme {
  /* Primary palette - derived from brand color */
  --color-primary-50: oklch(97% 0.01 250);
  --color-primary-100: oklch(94% 0.02 250);
  --color-primary-200: oklch(88% 0.04 250);
  --color-primary-300: oklch(78% 0.08 250);
  --color-primary-400: oklch(65% 0.12 250);
  --color-primary-500: oklch(55% 0.15 250);  /* Brand primary */
  --color-primary-600: oklch(47% 0.14 250);
  --color-primary-700: oklch(39% 0.12 250);
  --color-primary-800: oklch(32% 0.10 250);
  --color-primary-900: oklch(25% 0.08 250);
  --color-primary-950: oklch(18% 0.06 250);
}
```

### 3.3 Contrast Requirements

| Standard | Ratio | Usage |
|----------|-------|-------|
| **WCAG AA** | 4.5:1 minimum | All text |
| **WCAG AA Large** | 3:1 minimum | Text ≥18px or ≥14px bold |
| **WCAG AAA** | 7:1 | Target for critical content |

### 3.4 Dark Mode Strategy

**Invert luminance, NOT hue:**

```css
@theme {
  /* Light mode */
  --color-background: oklch(100% 0 0);           /* L: 100% */
  --color-foreground: oklch(14% 0.004 285);      /* L: 14% */
  --color-primary: oklch(55% 0.15 250);          /* L: 55% */
}

@theme dark {
  /* Dark mode - flip luminance axis */
  --color-background: oklch(14% 0.004 285);      /* L: 14% (was 100%) */
  --color-foreground: oklch(98% 0 0);            /* L: 98% (was 14%) */
  --color-primary: oklch(70% 0.12 250);          /* L: 70% (boosted for dark bg) */
}
```

---

## 4. Motion Language

### 4.1 Timing Functions

```css
@theme {
  /* Easing curves */
  --ease-out: cubic-bezier(0.0, 0.0, 0.2, 1);      /* Decelerate */
  --ease-in: cubic-bezier(0.4, 0.0, 1, 1);         /* Accelerate */
  --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);   /* Material feel */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy */
}
```

### 4.2 Animation Patterns

**Page load - Stagger children:**
```css
.stagger-children > * {
  opacity: 0;
  animation: fade-in 0.3s var(--ease-out) forwards;
}

.stagger-children > *:nth-child(1) { animation-delay: 0ms; }
.stagger-children > *:nth-child(2) { animation-delay: 50ms; }
.stagger-children > *:nth-child(3) { animation-delay: 100ms; }
.stagger-children > *:nth-child(4) { animation-delay: 150ms; }
.stagger-children > *:nth-child(5) { animation-delay: 200ms; }

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

**Hover - Scale + shadow lift:**
```css
.hover-lift {
  transition: transform 150ms var(--ease-out), box-shadow 150ms var(--ease-out);
}

.hover-lift:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 40px -10px oklch(0% 0 0 / 0.2);
}
```

### 4.3 Animation Rules

| Rule | Guideline |
|------|-----------|
| **Duration** | 150-300ms for micro-interactions, max 500ms |
| **Stagger** | 50ms between children |
| **Never** | Infinite animations, >500ms duration, jarring easing |
| **Reduce motion** | Respect `prefers-reduced-motion` |

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 5. Background Treatment

### 5.1 Gradient Layers

Use 2-3 gradient layers with blend modes for depth:

```css
.rich-background {
  background: 
    /* Layer 3: Accent glow */
    radial-gradient(
      ellipse 80% 50% at 50% -20%,
      oklch(70% 0.15 250 / 0.15),
      transparent 50%
    ),
    /* Layer 2: Warm undertone */
    linear-gradient(
      to bottom right,
      oklch(98% 0.01 30 / 0.5),
      transparent 60%
    ),
    /* Layer 1: Base */
    var(--color-background);
}
```

### 5.2 Noise Texture

Add subtle noise for depth (opacity 0.02-0.05):

```css
.textured {
  position: relative;
}

.textured::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.03;
  pointer-events: none;
  mix-blend-mode: overlay;
}
```

### 5.3 SVG Patterns

Use SVG for scalable patterns, CSS for performance:

```css
.pattern-dots {
  background-image: radial-gradient(
    circle at center,
    var(--color-border) 1px,
    transparent 1px
  );
  background-size: 24px 24px;
}

.pattern-grid {
  background-image: 
    linear-gradient(var(--color-border) 1px, transparent 1px),
    linear-gradient(90deg, var(--color-border) 1px, transparent 1px);
  background-size: 40px 40px;
}
```

---

## 6. Complete TailwindCSS v4 Theme

### 6.1 Build Tool Configuration

**Vite is the preferred build tool.** Only use PostCSS if there are incompatibilities with other packages/tooling.

**vite.config.ts** (Preferred)
```typescript
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
});
```

**postcss.config.mjs** (Fallback only)
```js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  }
}
```

### 6.2 Monorepo Source Directives

In a monorepo, the app's CSS file **MUST** use `@source` directives to include any packages that contain Tailwind classes. Without this, classes from imported packages will not be included in the build.

```css
/* apps/web/src/app/globals.css */
@import "tailwindcss";

/* Required: Source any packages with Tailwind classes */
@source "../../packages/ui/src";
@source "../../packages/editor/src";
@source "../../packages/components/src";

@theme {
  /* ... theme configuration ... */
}
```

**Rules for `@source` directives:**
- Add one `@source` for each package that contains Tailwind utility classes
- Paths are relative to the CSS file location
- Place `@source` directives after `@import "tailwindcss"` but before `@theme`
- If a package doesn't use Tailwind classes, no `@source` is needed

### 6.3 Complete Theme

This comprehensive theme incorporates all design standards from sections 2-5:

```css
/* app/globals.css */
@import "tailwindcss";

/* Monorepo: Source packages with Tailwind classes */
@source "../../packages/ui/src";
@source "../../packages/editor/src";

@theme {
  /* ===== TYPOGRAPHY (see §2) ===== */
  --font-display: "Playfair Display Variable", Georgia, serif;
  --font-sans: "IBM Plex Sans", system-ui, sans-serif;
  --font-mono: "JetBrains Mono Variable", ui-monospace, monospace;
  
  /* Type scale (Major Third 1.250) */
  --text-xs: 0.75rem;
  --text-sm: 0.9375rem;
  --text-base: 1.1875rem;
  --text-lg: 1.5rem;
  --text-xl: 1.875rem;
  --text-2xl: 2.3125rem;
  --text-3xl: 2.875rem;
  --text-4xl: 3.625rem;
  --text-5xl: 4.5rem;

  /* ===== COLORS (see §3) ===== */
  --color-background: oklch(100% 0 0);
  --color-foreground: oklch(14.08% 0.004 285.82);
  
  --color-primary: oklch(55% 0.15 250);
  --color-primary-foreground: oklch(98% 0 0);
  
  --color-secondary: oklch(96.76% 0.001 286.38);
  --color-secondary-foreground: oklch(20.47% 0.006 285.88);
  
  --color-muted: oklch(96.76% 0.001 286.38);
  --color-muted-foreground: oklch(55.19% 0.014 285.94);
  
  --color-accent: oklch(96.76% 0.001 286.38);
  --color-accent-foreground: oklch(20.47% 0.006 285.88);
  
  --color-destructive: oklch(57.71% 0.215 27.33);
  --color-destructive-foreground: oklch(98.51% 0 0);
  
  --color-border: oklch(91.97% 0.004 286.32);
  --color-input: oklch(91.97% 0.004 286.32);
  --color-ring: oklch(55% 0.15 250);
  
  --color-card: oklch(100% 0 0);
  --color-card-foreground: oklch(14.08% 0.004 285.82);

  /* ===== SPACING & RADIUS ===== */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;

  /* ===== MOTION (see §4) ===== */
  --ease-out: cubic-bezier(0.0, 0.0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0.0, 1, 1);
  --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 350ms;

  /* ===== SHADOWS ===== */
  --shadow-sm: 0 1px 2px 0 oklch(0% 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px oklch(0% 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px oklch(0% 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px oklch(0% 0 0 / 0.1);
  --shadow-lift: 0 10px 40px -10px oklch(0% 0 0 / 0.2);
}

/* Dark mode - invert luminance, not hue (see §3.4) */
@theme dark {
  --color-background: oklch(14.08% 0.004 285.82);
  --color-foreground: oklch(98.51% 0 0);
  
  --color-primary: oklch(70% 0.12 250);
  --color-primary-foreground: oklch(14% 0.004 285);
  
  --color-secondary: oklch(26.92% 0.006 286.03);
  --color-secondary-foreground: oklch(98.51% 0 0);
  
  --color-muted: oklch(26.92% 0.006 286.03);
  --color-muted-foreground: oklch(70.9% 0.011 286.03);
  
  --color-accent: oklch(26.92% 0.006 286.03);
  --color-accent-foreground: oklch(98.51% 0 0);
  
  --color-border: oklch(26.92% 0.006 286.03);
  --color-input: oklch(26.92% 0.006 286.03);
  --color-ring: oklch(70% 0.12 250);
  
  --color-card: oklch(18% 0.004 285.82);
  --color-card-foreground: oklch(98.51% 0 0);
}

/* ===== BASE STYLES ===== */
@layer base {
  * {
    @apply border-border;
  }
  
  html {
    font-family: var(--font-sans);
  }
  
  body {
    @apply bg-background text-foreground;
  }
  
  h1, h2, h3 {
    font-family: var(--font-display);
    font-weight: 700;
  }
  
  code, pre, kbd {
    font-family: var(--font-mono);
  }
}

/* ===== MOTION UTILITIES (see §4) ===== */
@layer utilities {
  .animate-fade-in {
    animation: fade-in 0.3s var(--ease-out) forwards;
  }
  
  .animate-slide-up {
    animation: slide-up 0.3s var(--ease-out) forwards;
  }
  
  .hover-lift {
    transition: transform var(--duration-fast) var(--ease-out),
                box-shadow var(--duration-fast) var(--ease-out);
  }
  
  .hover-lift:hover {
    transform: scale(1.02);
    box-shadow: var(--shadow-lift);
  }
  
  /* Stagger children animation */
  .stagger-children > * {
    opacity: 0;
    animation: fade-in 0.3s var(--ease-out) forwards;
  }
  .stagger-children > *:nth-child(1) { animation-delay: 0ms; }
  .stagger-children > *:nth-child(2) { animation-delay: 50ms; }
  .stagger-children > *:nth-child(3) { animation-delay: 100ms; }
  .stagger-children > *:nth-child(4) { animation-delay: 150ms; }
  .stagger-children > *:nth-child(5) { animation-delay: 200ms; }
  
  /* Background patterns (see §5) */
  .pattern-dots {
    background-image: radial-gradient(circle at center, var(--color-border) 1px, transparent 1px);
    background-size: 24px 24px;
  }
  
  .pattern-grid {
    background-image: 
      linear-gradient(var(--color-border) 1px, transparent 1px),
      linear-gradient(90deg, var(--color-border) 1px, transparent 1px);
    background-size: 40px 40px;
  }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== ACCESSIBILITY ===== */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 7. Biome + TailwindCSS v4 Compatibility

### 2.1 Decision Matrix

| TailwindCSS v4 Usage | CSS Formatter | Configuration |
|---------------------|---------------|---------------|
| Not using TailwindCSS | Biome | Standard `biome.json` |
| Basic (`@theme`, `@apply`, `@variant`) | Biome | Enable `tailwindDirectives` |
| Advanced (`@plugin` with options) | Prettier fallback | Until Biome support matures |

### 2.2 Biome Configuration

```json
{
  "$schema": "https://biomejs.dev/schemas/2.3.0/schema.json",
  "css": {
    "parser": { "tailwindDirectives": true },
    "formatter": { "enabled": true },
    "linter": { "enabled": true }
  }
}
```

### 2.3 Prettier Fallback (When Needed)

```json
{ "plugins": ["prettier-plugin-tailwindcss"], "tailwindFunctions": ["clsx", "cva", "cn"] }
```

---

## 8. Utility Class Guidelines

### 3.1 MUST Follow

- Use semantic color tokens (`text-foreground`, `bg-primary`)
- Use spacing scale consistently (`gap-4`, `p-6`, `m-2`)
- Use responsive prefixes for breakpoint-specific styles
- Use state prefixes (`hover:`, `focus:`, `disabled:`)
- Group related utilities logically

### 3.2 MUST NOT

- Use arbitrary values `[...]` without documented justification
- Mix px/rem/em units inconsistently
- Override Tailwind utilities with custom CSS without necessity

### 3.3 Class Order

```tsx
<div className={cn(
  "flex flex-col items-center",     // Layout
  "w-full max-w-md",                // Sizing
  "p-6 gap-4",                      // Spacing
  "text-sm font-medium",            // Typography
  "bg-card text-card-foreground",   // Colors
  "border rounded-lg shadow-sm",    // Borders/Effects
  "hover:bg-accent focus:ring-2",   // States
  "md:flex-row md:p-8"              // Responsive
)} />
```

---

## 9. shadcn/ui Integration

### 4.1 Utils

```typescript
// lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### 4.2 Button Pattern

```typescript
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3",
        lg: "h-11 px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
```

---

## 10. Component Creation Pattern

### 5.1 With CVA Variants

```typescript
"use client";

import { forwardRef, type ComponentPropsWithoutRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const componentVariants = cva("base-classes", {
  variants: {
    variant: { default: "...", outline: "..." },
    size: { default: "...", sm: "...", lg: "..." },
  },
  defaultVariants: { variant: "default", size: "default" },
});

export interface ComponentProps
  extends ComponentPropsWithoutRef<"div">,
    VariantProps<typeof componentVariants> {
  // Additional props
}

export const Component = forwardRef<HTMLDivElement, ComponentProps>(
  ({ className, variant, size, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(componentVariants({ variant, size }), className)}
      {...props}
    />
  )
);

Component.displayName = "Component";
```

---

## 11. Dark Mode

### 6.1 ThemeProvider Setup

```typescript
// components/providers/ThemeProvider.tsx
"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}
```

### 6.2 Theme Toggle

```typescript
"use client";

import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Moon, Sun } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
```

---

## 12. Responsive Design

### 7.1 Breakpoints

| Prefix | Min Width | Usage |
|--------|-----------|-------|
| `sm:` | 640px | Small tablets |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Laptops |
| `xl:` | 1280px | Desktops |
| `2xl:` | 1536px | Large screens |

### 7.2 Mobile-First Pattern

```tsx
<div className="
  flex flex-col gap-4 p-4
  md:flex-row md:gap-6 md:p-6
  lg:gap-8 lg:p-8
">
  {/* Content */}
</div>
```

---

## 13. Animation Quick Reference

### 8.1 Built-in Animations

```tsx
<div className="animate-spin" />      // Spinner
<div className="animate-ping" />      // Ping effect
<div className="animate-pulse" />     // Pulse/skeleton
<div className="animate-bounce" />    // Bounce
```

### 8.2 Custom Animations

```css
@theme {
  --animate-fade-in: fade-in 0.2s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
```
