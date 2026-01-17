# React & Next.js Standards

> **Applies to**: All React components and Next.js applications  
> **Version Constraint**: React ≥18.0, Next.js ≥14.0 (App Router)  
> **Parent**: `constitution.md`

---

## 1. Version and Framework

| Constraint | Value | Rationale |
|------------|-------|-----------|
| React | ≥18.0 | Concurrent features, Suspense, transitions |
| Next.js | ≥14.0 | App Router, Server Components, Server Actions |
| Router | App Router | File-based routing, layouts, streaming |

---

## 2. Project Structure

### 2.1 Next.js App Structure

```
apps/web/
├── app/
│   ├── (auth)/                 # Route group (no URL segment)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/            # Route group
│   │   ├── layout.tsx          # Dashboard layout
│   │   ├── page.tsx            # Dashboard home
│   │   └── settings/
│   │       └── page.tsx
│   ├── api/                    # API routes
│   │   └── resources/
│   │       └── route.ts
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── error.tsx               # Error boundary
│   ├── loading.tsx             # Loading UI
│   ├── not-found.tsx           # 404 page
│   └── globals.css             # Global styles
├── components/
│   ├── features/               # Feature-specific components
│   │   └── [feature]/
│   │       ├── index.ts        # Public exports
│   │       ├── FeatureName.tsx
│   │       └── FeatureName.test.tsx
│   ├── layouts/                # Layout components
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   └── providers/              # Context providers
│       ├── ThemeProvider.tsx
│       └── index.tsx
├── lib/
│   ├── actions/                # Server actions
│   │   └── resources.ts
│   ├── api/                    # API client utilities
│   ├── hooks/                  # Custom hooks
│   ├── stores/                 # State management (Zustand)
│   └── utils/                  # Utility functions
├── public/
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

---

## 3. Component Patterns

### 3.1 Component File Structure

```typescript
// components/features/ResourceList/ResourceList.tsx

/**
 * @module components/features/ResourceList
 */

"use client"; // Only if client-side interactivity needed

import { forwardRef, type ComponentPropsWithoutRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

/**
 * Variant definitions using CVA for type-safe styling.
 */
const resourceListVariants = cva(
  "grid gap-4",
  {
    variants: {
      layout: {
        grid: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
        list: "grid-cols-1",
      },
      density: {
        comfortable: "gap-6",
        compact: "gap-2",
      },
    },
    defaultVariants: {
      layout: "grid",
      density: "comfortable",
    },
  }
);

/**
 * Props for the ResourceList component.
 */
export interface ResourceListProps
  extends ComponentPropsWithoutRef<"div">,
    VariantProps<typeof resourceListVariants> {
  /** Array of resources to display */
  resources: Resource[];
  /** Callback when a resource is selected */
  onSelect?: (resource: Resource) => void;
  /** Whether the list is in loading state */
  isLoading?: boolean;
}

/**
 * Displays a list of resources in grid or list layout.
 *
 * @component
 * @example
 * <ResourceList
 *   resources={resources}
 *   layout="grid"
 *   onSelect={handleSelect}
 * />
 */
export const ResourceList = forwardRef<HTMLDivElement, ResourceListProps>(
  ({ className, resources, onSelect, isLoading, layout, density, ...props }, ref) => {
    if (isLoading) {
      return <ResourceListSkeleton layout={layout} />;
    }

    return (
      <div
        ref={ref}
        className={cn(resourceListVariants({ layout, density }), className)}
        {...props}
      >
        {resources.map((resource) => (
          <ResourceCard
            key={resource.id}
            resource={resource}
            onClick={() => onSelect?.(resource)}
          />
        ))}
      </div>
    );
  }
);

ResourceList.displayName = "ResourceList";
```

### 3.2 Server Components (Default)

```typescript
// app/resources/page.tsx

import { Suspense } from "react";
import { ResourceList } from "@/components/features/ResourceList";
import { ResourceListSkeleton } from "@/components/features/ResourceList/Skeleton";
import { getResources } from "@/lib/api/resources";

/**
 * Resources page - Server Component (default).
 * Fetches data on the server, streams to client.
 */
export default async function ResourcesPage() {
  return (
    <main className="container py-8">
      <h1 className="text-3xl font-bold mb-8">Resources</h1>
      <Suspense fallback={<ResourceListSkeleton />}>
        <ResourceListLoader />
      </Suspense>
    </main>
  );
}

async function ResourceListLoader() {
  const resources = await getResources();
  return <ResourceList resources={resources} />;
}
```

### 3.3 Client Components

```typescript
// components/features/ResourceForm/ResourceForm.tsx

"use client";

import { useTransition } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { createResourceSchema, type CreateResourceInput } from "@/lib/schemas";
import { createResource } from "@/lib/actions/resources";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

/**
 * Form for creating a new resource.
 * Client component for interactivity.
 *
 * @component
 */
export function ResourceForm() {
  const [isPending, startTransition] = useTransition();

  const form = useForm<CreateResourceInput>({
    resolver: zodResolver(createResourceSchema),
    defaultValues: {
      name: "",
      description: "",
    },
  });

  function onSubmit(data: CreateResourceInput) {
    startTransition(async () => {
      const result = await createResource(data);
      if (result.success) {
        form.reset();
      }
    });
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <Input
        {...form.register("name")}
        placeholder="Resource name"
        disabled={isPending}
      />
      {form.formState.errors.name && (
        <p className="text-sm text-destructive">
          {form.formState.errors.name.message}
        </p>
      )}
      <Button type="submit" disabled={isPending}>
        {isPending ? "Creating..." : "Create Resource"}
      </Button>
    </form>
  );
}
```

---

## 4. Server Actions

```typescript
// lib/actions/resources.ts

"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { createResourceSchema } from "@/lib/schemas";
import { db } from "@/lib/db";
import { auth } from "@/lib/auth";

/**
 * Server action to create a new resource.
 *
 * @param data - The resource creation data
 * @returns Result object with success status
 */
export async function createResource(
  data: z.infer<typeof createResourceSchema>
) {
  const session = await auth();

  if (!session?.user) {
    return { success: false, error: "Unauthorized" };
  }

  const validated = createResourceSchema.safeParse(data);

  if (!validated.success) {
    return {
      success: false,
      error: "Validation failed",
      fieldErrors: validated.error.flatten().fieldErrors,
    };
  }

  try {
    await db.resource.create({
      data: {
        ...validated.data,
        userId: session.user.id,
      },
    });

    revalidatePath("/resources");
    return { success: true };
  } catch (error) {
    return { success: false, error: "Failed to create resource" };
  }
}

/**
 * Server action to delete a resource.
 */
export async function deleteResource(id: string) {
  const session = await auth();

  if (!session?.user) {
    throw new Error("Unauthorized");
  }

  await db.resource.delete({
    where: { id, userId: session.user.id },
  });

  revalidatePath("/resources");
  redirect("/resources");
}
```

---

## 5. API Routes

```typescript
// app/api/resources/route.ts

import { NextResponse, type NextRequest } from "next/server";
import { z } from "zod";
import { auth } from "@/lib/auth";
import { db } from "@/lib/db";

const createResourceSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(1000).optional(),
});

/**
 * POST /api/resources - Create a new resource.
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const session = await auth();

    if (!session?.user) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    const body = await request.json();
    const validated = createResourceSchema.safeParse(body);

    if (!validated.success) {
      return NextResponse.json(
        { error: "Validation failed", details: validated.error.flatten() },
        { status: 400 }
      );
    }

    const resource = await db.resource.create({
      data: {
        ...validated.data,
        userId: session.user.id,
      },
    });

    return NextResponse.json(resource, { status: 201 });
  } catch (error) {
    console.error("Failed to create resource:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

/**
 * GET /api/resources - List resources with pagination.
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  try {
    const session = await auth();

    if (!session?.user) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const limit = Math.min(
      Math.max(Number(searchParams.get("limit")) || 20, 1),
      100
    );
    const offset = Math.max(Number(searchParams.get("offset")) || 0, 0);

    const resources = await db.resource.findMany({
      where: { userId: session.user.id },
      take: limit,
      skip: offset,
      orderBy: { createdAt: "desc" },
    });

    return NextResponse.json(resources);
  } catch (error) {
    console.error("Failed to list resources:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

---

## 6. Custom Hooks

```typescript
// lib/hooks/useResources.ts

"use client";

import useSWR from "swr";
import type { Resource } from "@/lib/types";

/**
 * Hook for fetching resources with SWR.
 *
 * @param options - Query options
 * @returns SWR response with resources
 *
 * @example
 * const { resources, isLoading, error } = useResources({ limit: 10 });
 */
export function useResources(options?: { limit?: number; offset?: number }) {
  const params = new URLSearchParams();
  if (options?.limit) params.set("limit", String(options.limit));
  if (options?.offset) params.set("offset", String(options.offset));

  const { data, error, isLoading, mutate } = useSWR<Resource[]>(
    `/api/resources?${params.toString()}`
  );

  return {
    resources: data ?? [],
    isLoading,
    error,
    mutate,
  };
}
```

---

## 7. Layout Patterns

### 7.1 Root Layout

<!-- 
SKILL AGENT INSTRUCTION: ${FONT_IMPORTS}
Ask the user: "Is this a personal project or an L3Harris project?"
- If personal project → Use distinctive fonts (Playfair Display, IBM Plex Sans, JetBrains Mono)
- If L3Harris project → Use corporate fonts (Inter, IBM Plex Mono)
-->

```typescript
// app/layout.tsx
import type { Metadata } from "next";
${FONT_IMPORTS}
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "App Name",
    template: "%s | App Name",
  },
  description: "App description",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html 
      lang="en" 
      suppressHydrationWarning
      className={${FONT_VARIABLES}}
    >
      <body className="font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

<!-- 
SKILL AGENT: Replace ${FONT_IMPORTS} and ${FONT_VARIABLES} based on project type:

FOR PERSONAL PROJECTS (tailwind-shadcn.md):
```typescript
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
```
${FONT_VARIABLES} = `${playfair.variable} ${ibmPlex.variable} ${jetbrains.variable}`

FOR L3HARRIS PROJECTS (tailwind-l3harris.md):
```typescript
import { Inter } from "next/font/google";
import localFont from "next/font/local";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

// IBM Plex Mono for code (load from Google Fonts or local)
const ibmPlexMono = localFont({
  src: "../fonts/IBMPlexMono-Regular.woff2",
  variable: "--font-mono",
  display: "swap",
});
```
${FONT_VARIABLES} = `${inter.variable} ${ibmPlexMono.variable}`
-->

### 7.2 Dashboard Layout

```typescript
// app/(dashboard)/layout.tsx

import { Sidebar } from "@/components/layouts/Sidebar";
import { Header } from "@/components/layouts/Header";
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();

  if (!session?.user) {
    redirect("/login");
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header user={session.user} />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
```

---

## 8. Error Handling

### 8.1 Error Boundary

```typescript
// app/error.tsx

"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="text-muted-foreground">
        An error occurred while processing your request.
      </p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
```

### 8.2 Not Found Page

```typescript
// app/not-found.tsx

import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
      <h2 className="text-2xl font-bold">Not Found</h2>
      <p className="text-muted-foreground">
        The page you're looking for doesn't exist.
      </p>
      <Button asChild>
        <Link href="/">Go home</Link>
      </Button>
    </div>
  );
}
```

---

## 9. Loading States

```typescript
// app/(dashboard)/resources/loading.tsx

import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    </div>
  );
}
```

---

## 10. Metadata

```typescript
// app/(dashboard)/resources/page.tsx

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Resources",
  description: "Manage your resources",
};

export default async function ResourcesPage() {
  // ...
}
```

Dynamic metadata:

```typescript
// app/(dashboard)/resources/[id]/page.tsx

import type { Metadata } from "next";
import { getResource } from "@/lib/api/resources";

type Props = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const resource = await getResource(id);

  return {
    title: resource.name,
    description: resource.description,
  };
}
```

---

## 11. Anti-Patterns to Avoid

These patterns indicate inexperience and **MUST NOT** appear in code:

### 11.1 Using `useEffect` for Derived State

```tsx
// ❌ MUST NOT: Effect for synchronous computation
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(`${firstName} ${lastName}`);
}, [firstName, lastName]);

// ✅ MUST: Compute during render
const fullName = `${firstName} ${lastName}`;
// Or useMemo for expensive computations
const fullName = useMemo(() => computeExpensive(firstName, lastName), [firstName, lastName]);
```

### 11.2 Missing Dependency Arrays

```tsx
// ❌ MUST NOT: Missing or incorrect dependencies
useEffect(() => {
  fetchUser(userId);
}, []); // userId not in deps!

// ✅ MUST: Include all dependencies
useEffect(() => {
  fetchUser(userId);
}, [userId]);
```

### 11.3 Prop Drilling Through Many Layers

```tsx
// ❌ SHOULD NOT: Passing props through 5+ components
<A user={user}><B user={user}><C user={user}><D user={user}><E user={user}/></D></C></B></A>

// ✅ SHOULD: Use context or composition
const UserContext = createContext<User | null>(null);
// Or component composition
<Layout><UserProfile /></Layout>
```

### 11.4 Inline Object/Array Props

```tsx
// ❌ SHOULD NOT: Creates new reference every render
<Child style={{ color: 'red' }} items={[1, 2, 3]} />

// ✅ SHOULD: Stable references
const style = useMemo(() => ({ color: 'red' }), []);
const items = useMemo(() => [1, 2, 3], []);
<Child style={style} items={items} />
```

### 11.5 Not Using Server Components

```tsx
// ❌ SHOULD NOT: Client component for static content (Next.js 14+)
'use client';
export function StaticList({ items }) {
  return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
}

// ✅ SHOULD: Server component by default
export function StaticList({ items }) {
  return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
}
```

### 11.6 Fetching in `useEffect` (Next.js)

```tsx
// ❌ SHOULD NOT: Client-side fetch when server fetch works
'use client';
function ResourcePage({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => { fetch(`/api/${id}`).then(r => r.json()).then(setData); }, [id]);
}

// ✅ SHOULD: Server component with direct data access
async function ResourcePage({ params }) {
  const data = await getResource(params.id);
  return <ResourceView data={data} />;
}
```

### 11.7 State for Form Inputs (Uncontrolled)

```tsx
// ❌ SHOULD NOT: Controlled when uncontrolled suffices
const [name, setName] = useState('');
<input value={name} onChange={e => setName(e.target.value)} />
<button onClick={() => submit(name)}>Submit</button>

// ✅ SHOULD: Uncontrolled with FormData
<form action={submitAction}>
  <input name="name" />
  <button type="submit">Submit</button>
</form>
```

### 11.8 Mutating State Directly

```tsx
// ❌ MUST NOT: Direct mutation
const [items, setItems] = useState([1, 2, 3]);
items.push(4); // Mutation!
setItems(items);

// ✅ MUST: Immutable updates
setItems([...items, 4]);
// Or with immer
setItems(draft => { draft.push(4); });
```

### 11.9 Missing Keys or Using Index as Key

```tsx
// ❌ MUST NOT: Index as key for dynamic lists
{items.map((item, index) => <Item key={index} {...item} />)}

// ✅ MUST: Stable unique identifiers
{items.map(item => <Item key={item.id} {...item} />)}
```

### 11.10 Business Logic in Components

```tsx
// ❌ SHOULD NOT: Complex logic mixed with UI
function OrderForm() {
  const calculateTotal = () => { /* 50 lines of business logic */ };
  const validateOrder = () => { /* 30 lines */ };
  return <form>...</form>;
}

// ✅ SHOULD: Separate concerns
// lib/orders/calculateTotal.ts
// lib/orders/validateOrder.ts
function OrderForm() {
  const total = calculateTotal(items);
  const errors = validateOrder(order);
  return <form>...</form>;
}
```

> **Reference**: See `react-antipatterns.md` for detailed explanations and detection patterns.
