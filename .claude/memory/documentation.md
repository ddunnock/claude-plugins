# Documentation Standards

> **Applies to**: All project documentation  
> **Framework**: Diátaxis + Sphinx with Furo theme  
> **Parent**: `constitution.md`

---

## 1. Diátaxis Framework

All documentation **MUST** follow the Diátaxis framework, which organizes content into four distinct quadrants based on user needs:

```
                    PRACTICAL                         THEORETICAL
              ┌─────────────────────┬─────────────────────┐
              │                     │                     │
   LEARNING   │     TUTORIALS       │    EXPLANATION      │
              │   (Learning-        │   (Understanding-   │
              │    oriented)        │    oriented)        │
              │                     │                     │
              ├─────────────────────┼─────────────────────┤
              │                     │                     │
   WORKING    │    HOW-TO GUIDES    │    REFERENCE        │
              │   (Task-oriented)   │   (Information-     │
              │                     │    oriented)        │
              │                     │                     │
              └─────────────────────┴─────────────────────┘
```

### 1.1 Quadrant Definitions

| Quadrant | Purpose | User State | Content Style |
|----------|---------|------------|---------------|
| **Tutorials** | Learning by doing | Newcomer, studying | Step-by-step, hand-holding |
| **How-To Guides** | Solving specific problems | Practitioner, working | Goal-oriented, practical |
| **Reference** | Looking up information | Practitioner, working | Accurate, complete, structured |
| **Explanation** | Understanding concepts | Learner or practitioner, studying | Discursive, contextual |

### 1.2 Content Rules

**Tutorials MUST:**
- Start from zero assumptions
- Provide repeatable, working examples
- Focus on learning, not completeness
- Have a clear beginning and end

**How-To Guides MUST:**
- Assume competence
- Focus on achieving a specific goal
- Be flexible (not rigid step-by-step)
- Address real-world scenarios

**Reference MUST:**
- Be comprehensive and accurate
- Follow consistent structure
- Be kept in sync with code
- Avoid explanation or tutorial content

**Explanation MUST:**
- Provide context and background
- Connect concepts together
- Discuss alternatives and trade-offs
- Help readers understand "why"

### 1.3 Anti-Patterns

**MUST NOT** mix quadrants in a single document:

```markdown
<!-- ❌ Bad: Tutorial mixed with Reference -->
# Getting Started

First, install the package:
pip install mypackage

## API Reference

### mypackage.Client
class Client(host: str, port: int = 8080)
...
```

```markdown
<!-- ✅ Good: Separate documents -->
<!-- tutorials/getting-started.md -->
# Getting Started
First, install the package...

<!-- reference/api.md -->
# API Reference
## mypackage.Client
...
```

---

## 2. Documentation Structure

### 2.1 Directory Layout

```
docs/
├── conf.py                     # Sphinx configuration
├── index.md                    # Documentation home
├── tutorials/                  # Learning-oriented
│   ├── index.md
│   ├── getting-started.md
│   ├── first-project.md
│   └── advanced-features.md
├── how-to/                     # Task-oriented
│   ├── index.md
│   ├── installation.md
│   ├── configuration.md
│   ├── deployment.md
│   └── troubleshooting.md
├── reference/                  # Information-oriented
│   ├── index.md
│   ├── api/
│   │   ├── index.md
│   │   ├── client.md
│   │   └── models.md
│   ├── cli.md
│   ├── configuration.md
│   └── changelog.md
├── explanation/                # Understanding-oriented
│   ├── index.md
│   ├── architecture.md
│   ├── design-decisions.md
│   └── concepts.md
├── _static/                    # Static assets
│   ├── css/
│   │   └── custom.css
│   └── images/
└── _templates/                 # Custom templates
```

### 2.2 Index Page Structure

```markdown
<!-- docs/index.md -->
# Project Name

Brief project description and value proposition.

## Quick Links

::::{grid} 2
:gutter: 3

:::{grid-item-card} 🎓 Tutorials
:link: tutorials/index
:link-type: doc

Learn the basics with hands-on tutorials.
:::

:::{grid-item-card} 📖 How-To Guides
:link: how-to/index
:link-type: doc

Step-by-step guides for common tasks.
:::

:::{grid-item-card} 📚 Reference
:link: reference/index
:link-type: doc

Technical reference and API documentation.
:::

:::{grid-item-card} 💡 Explanation
:link: explanation/index
:link-type: doc

Background concepts and architecture.
:::
::::

## Installation

\`\`\`bash
pip install project-name
\`\`\`

## Quick Example

\`\`\`python
from project_name import Client

client = Client()
result = client.do_something()
\`\`\`
```

---

## 3. Sphinx Configuration

### 3.1 Project Setup

```bash
# Install dependencies
pip install sphinx furo myst-parser sphinx-design sphinx-copybutton

# Or with Poetry
poetry add --group docs sphinx furo myst-parser sphinx-design sphinx-copybutton
```

### 3.2 conf.py

```python
# docs/conf.py
"""Sphinx configuration for project documentation."""

import os
import sys
from datetime import datetime

# Add source to path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
project = "Project Name"
copyright = f"{datetime.now().year}, Author Name"
author = "Author Name"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    # Core
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    
    # Markdown support
    "myst_parser",
    
    # UI enhancements
    "sphinx_design",
    "sphinx_copybutton",
]

# Markdown configuration
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
myst_enable_extensions = [
    "colon_fence",      # ::: directive syntax
    "deflist",          # Definition lists
    "fieldlist",        # Field lists
    "tasklist",         # Task lists with checkboxes
    "attrs_inline",     # Inline attributes
    "attrs_block",      # Block attributes
]
myst_heading_anchors = 3

# Templates and static files
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# Furo theme options
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2563eb",
        "color-brand-content": "#2563eb",
    },
    "dark_css_variables": {
        "color-brand-primary": "#60a5fa",
        "color-brand-content": "#60a5fa",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/org/repo",
    "source_branch": "main",
    "source_directory": "docs/",
}

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}

# -- Options for copybutton --------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |> "
copybutton_prompt_is_regexp = True
```

### 3.3 Custom CSS

```css
/* docs/_static/css/custom.css */

/* Diátaxis quadrant styling */
.tutorial-badge::before {
  content: "🎓 Tutorial";
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.howto-badge::before {
  content: "📖 How-To";
  background: #dcfce7;
  color: #166534;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.reference-badge::before {
  content: "📚 Reference";
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.explanation-badge::before {
  content: "💡 Explanation";
  background: #f3e8ff;
  color: #6b21a8;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Code block enhancements */
.highlight {
  border-radius: 0.5rem;
}

/* Admonition styling */
.admonition {
  border-radius: 0.5rem;
}
```

---

## 4. Writing Markdown for Sphinx

### 4.1 File Header Template

```markdown
<!-- tutorials/getting-started.md -->
---
myst:
  html_meta:
    "description lang=en": "Learn how to get started with Project Name"
    "keywords": "tutorial, getting started, beginner"
---

# Getting Started

{.tutorial-badge}

This tutorial will guide you through...
```

### 4.2 Admonitions

```markdown
:::{note}
This is a note admonition.
:::

:::{tip}
This is a tip admonition.
:::

:::{warning}
This is a warning admonition.
:::

:::{danger}
This is a danger admonition.
:::

:::{seealso}
- [Related Guide](../how-to/related.md)
- [API Reference](../reference/api/index.md)
:::
```

### 4.3 Code Blocks

```markdown
\`\`\`python
# Python code with syntax highlighting
from project_name import Client

client = Client(host="localhost")
\`\`\`

\`\`\`{code-block} python
:caption: client.py
:linenos:
:emphasize-lines: 3,4

from project_name import Client

client = Client(host="localhost")
result = client.query("example")
\`\`\`
```

### 4.4 Cross-References

```markdown
<!-- Link to another document -->
See the [Installation Guide](../how-to/installation.md) for details.

<!-- Link to a specific section -->
See [Configuration Options](../reference/configuration.md#options) for all settings.

<!-- Link to API docs (autodoc) -->
See {py:class}`project_name.Client` for the full API.

<!-- Link to external docs (intersphinx) -->
Uses {py:class}`python:pathlib.Path` for file handling.
```

### 4.5 API Documentation

```markdown
<!-- reference/api/client.md -->
# Client API

{.reference-badge}

## Overview

The Client class provides the main interface for interacting with the service.

## API Reference

\`\`\`{eval-rst}
.. automodule:: project_name.client
   :members:
   :undoc-members:
   :show-inheritance:
\`\`\`

## Examples

\`\`\`python
from project_name import Client

# Basic usage
client = Client()
result = client.query("example")

# With configuration
client = Client(host="custom.host", timeout=30)
\`\`\`
```

---

## 5. Build and Deploy

### 5.1 Local Build

```bash
# Build HTML documentation
cd docs
sphinx-build -b html . _build/html

# Or using make
make html

# Serve locally for preview
python -m http.server -d _build/html 8000
```

### 5.2 GitHub Actions Workflow

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths:
      - "docs/**"
      - "src/**"
      - ".github/workflows/docs.yml"
  pull_request:
    paths:
      - "docs/**"
      - "src/**"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install --with docs
      
      - name: Build documentation
        run: |
          cd docs
          poetry run sphinx-build -b html . _build/html -W --keep-going
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/_build/html

  deploy:
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    
    permissions:
      pages: write
      id-token: write
    
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 5.3 GitHub Pages Configuration

1. Go to repository Settings → Pages
2. Set Source to "GitHub Actions"
3. The workflow will automatically deploy on push to main

### 5.4 pyproject.toml Integration

```toml
[tool.poetry.group.docs]
optional = true

[tool.poetry.group.docs.dependencies]
sphinx = "^7.2"
furo = "^2024.1"
myst-parser = "^2.0"
sphinx-design = "^0.5"
sphinx-copybutton = "^0.5"
sphinx-autobuild = "^2024.2"

[tool.poetry.scripts]
docs-serve = "sphinx_autobuild:main"
```

### 5.5 Development Server

```bash
# Auto-rebuild on changes
sphinx-autobuild docs docs/_build/html --open-browser

# Or with Poetry script
poetry run docs-serve docs docs/_build/html --open-browser
```

---

## 6. Documentation Templates

### 6.1 Tutorial Template

```markdown
---
myst:
  html_meta:
    "description lang=en": "Tutorial description"
---

# Tutorial Title

{.tutorial-badge}

## What You'll Learn

By the end of this tutorial, you will:

- Learning objective 1
- Learning objective 2
- Learning objective 3

## Prerequisites

Before starting, ensure you have:

- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Step 1: First Step

Explanation of what we're doing and why.

\`\`\`python
# Code example
\`\`\`

You should see:

\`\`\`
Expected output
\`\`\`

## Step 2: Second Step

...

## Summary

In this tutorial, you learned how to:

- Summary point 1
- Summary point 2

## Next Steps

- [Next Tutorial](next-tutorial.md)
- [Related How-To Guide](../how-to/related.md)
```

### 6.2 How-To Guide Template

```markdown
---
myst:
  html_meta:
    "description lang=en": "How to accomplish specific task"
---

# How to [Accomplish Task]

{.howto-badge}

This guide shows you how to [accomplish specific task].

## Prerequisites

- Requirement 1
- Requirement 2

## Steps

### 1. First Action

\`\`\`bash
command to run
\`\`\`

### 2. Second Action

\`\`\`python
code example
\`\`\`

### 3. Verify

Confirm the task completed successfully:

\`\`\`bash
verification command
\`\`\`

## Troubleshooting

### Common Issue 1

Solution for issue 1.

### Common Issue 2

Solution for issue 2.

## See Also

- [Related Reference](../reference/related.md)
- [Background Explanation](../explanation/related.md)
```

### 6.3 Reference Template

```markdown
---
myst:
  html_meta:
    "description lang=en": "Reference documentation for Component"
---

# Component Reference

{.reference-badge}

## Overview

Brief description of the component.

## API

### Class: ClassName

\`\`\`python
class ClassName(param1: str, param2: int = 10)
\`\`\`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param1` | `str` | Required | Description |
| `param2` | `int` | `10` | Description |

**Methods:**

#### `method_name(arg: str) -> Result`

Description of method.

**Parameters:**
- `arg`: Description

**Returns:**
- `Result`: Description

**Raises:**
- `ValueError`: When...

**Example:**

\`\`\`python
obj = ClassName("value")
result = obj.method_name("arg")
\`\`\`

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `option1` | `str` | `"default"` | Description |
| `option2` | `bool` | `true` | Description |
```

### 6.4 Explanation Template

```markdown
---
myst:
  html_meta:
    "description lang=en": "Understanding concept in depth"
---

# Understanding [Concept]

{.explanation-badge}

## Introduction

Context and background for why this concept matters.

## The Problem

What problem does this solve? Why was this approach chosen?

## How It Works

Detailed explanation of the concept, including:

- Key principles
- Underlying mechanisms
- Important considerations

## Trade-offs

### Advantages

- Advantage 1
- Advantage 2

### Limitations

- Limitation 1
- Limitation 2

## Alternatives

Other approaches and when you might choose them:

### Alternative 1

Description and use cases.

### Alternative 2

Description and use cases.

## Further Reading

- [External Resource 1](https://example.com)
- [External Resource 2](https://example.com)

## See Also

- [Related Tutorial](../tutorials/related.md)
- [Related Reference](../reference/related.md)
```

---

## 7. Quality Checklist

### 7.1 Before Publishing

- [ ] Content is in the correct Diátaxis quadrant
- [ ] No quadrant mixing within a document
- [ ] All code examples are tested and working
- [ ] Cross-references are valid
- [ ] Spelling and grammar checked
- [ ] Build completes without warnings (`-W` flag)

### 7.2 Periodic Review

- [ ] API documentation matches current code
- [ ] Tutorials work with latest version
- [ ] How-to guides address current user needs
- [ ] Explanations reflect current architecture
