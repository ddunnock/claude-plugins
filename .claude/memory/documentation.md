# Documentation Standards

> **Applies to**: All project documentation in Knowledge MCP
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

| Quadrant          | Purpose                   | User State                        | Content Style                  |
|-------------------|---------------------------|-----------------------------------|--------------------------------|
| **Tutorials**     | Learning by doing         | Newcomer, studying                | Step-by-step, hand-holding     |
| **How-To Guides** | Solving specific problems | Practitioner, working             | Goal-oriented, practical       |
| **Reference**     | Looking up information    | Practitioner, working             | Accurate, complete, structured |
| **Explanation**   | Understanding concepts    | Learner or practitioner, studying | Discursive, contextual         |

### 1.2 Anti-Patterns

**MUST NOT** mix quadrants in a single document. Keep tutorials, how-to guides, reference, and explanation in separate files.

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
│   └── first-search.md
├── how-to/                     # Task-oriented
│   ├── index.md
│   ├── installation.md
│   ├── ingest-documents.md
│   ├── configure-qdrant.md
│   └── troubleshooting.md
├── reference/                  # Information-oriented
│   ├── index.md
│   ├── api/
│   │   ├── index.md
│   │   └── tools.md
│   ├── configuration.md
│   └── changelog.md
├── explanation/                # Understanding-oriented
│   ├── index.md
│   ├── architecture.md
│   ├── chunking-strategies.md
│   └── hybrid-search.md
└── _static/
    └── css/
        └── custom.css
```

---

## 3. Sphinx Configuration

### 3.1 conf.py

```python
# docs/conf.py
"""Sphinx configuration for Knowledge MCP documentation."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
project = "Knowledge MCP"
copyright = f"{datetime.now().year}, David Dunnock"
author = "David Dunnock"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = ["_build"]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2563eb",
        "color-brand-content": "#2563eb",
    },
}

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
}
autodoc_typehints = "description"

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
```

---

## 4. Build and Deploy

### 4.1 Local Build

```bash
# Build HTML documentation
cd docs
poetry run sphinx-build -b html . _build/html

# Serve locally
python -m http.server -d _build/html 8000

# Auto-rebuild on changes
poetry run sphinx-autobuild docs docs/_build/html --open-browser
```

### 4.2 GitHub Actions

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths:
      - "docs/**"
      - "src/**"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry
      - run: poetry install --with docs
      - run: cd docs && poetry run sphinx-build -b html . _build/html -W
      - uses: actions/upload-pages-artifact@v3
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
    steps:
      - uses: actions/deploy-pages@v4
```

---

## 5. Documentation Templates

### 5.1 Tutorial Template

```markdown
# Tutorial: [Title]

## What You'll Learn

By the end of this tutorial, you will:

- Learning objective 1
- Learning objective 2

## Prerequisites

- [ ] Python 3.11+ installed
- [ ] Poetry installed

## Step 1: [First Step]

[Explanation and code]

## Step 2: [Second Step]

[Explanation and code]

## Summary

In this tutorial, you learned:

- Summary point 1
- Summary point 2

## Next Steps

- [Link to next tutorial]
```

### 5.2 How-To Template

````markdown
# How to [Accomplish Task]

This guide shows you how to [task].

## Prerequisites

- Requirement 1
- Requirement 2

## Steps

### 1. [Action]

```bash
command
```

### 2. [Action]

```python
code
```

## Troubleshooting

### Issue 1

Solution.
````

### 5.3 Reference Template

````markdown
# [Component] Reference

## Overview

Brief description.

## API

### `function_name(param1, param2)`

Description.

**Parameters:**

| Parameter   | Type  | Default  | Description |
|-------------|-------|----------|-------------|
| `param1`    | `str` | Required | Description |

**Returns:**
- `ReturnType`: Description

**Example:**

```python
result = function_name("value")
```
````

---

## 6. Required Documents

| Document        | Location            | Update Frequency        |
|-----------------|---------------------|-------------------------|
| README.md       | Root                | On feature changes      |
| CHANGELOG.md    | Root                | Every release           |
| Getting Started | `docs/tutorials/`   | On major changes        |
| Installation    | `docs/how-to/`      | On dependency changes   |
| API Reference   | `docs/reference/`   | On API changes          |
| Architecture    | `docs/explanation/` | On architecture changes |

---

## 7. Quality Checklist

### Before Publishing

- [ ] Content is in correct Diátaxis quadrant
- [ ] No quadrant mixing
- [ ] Code examples are tested
- [ ] Cross-references are valid
- [ ] Build completes without warnings