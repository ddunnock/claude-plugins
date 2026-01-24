# Documentation Standards

> **Applies to**: All project documentation
> **Framework**: Diataxis + Sphinx with Furo theme
> **Parent**: `constitution.md`

---

## 1. Diataxis Framework

All documentation **MUST** follow the Diataxis framework, which organizes content into four distinct quadrants based on user needs:

```
                    PRACTICAL                         THEORETICAL
              +---------------------+---------------------+
              |                     |                     |
   LEARNING   |     TUTORIALS       |    EXPLANATION      |
              |   (Learning-        |   (Understanding-   |
              |    oriented)        |    oriented)        |
              |                     |                     |
              +---------------------+---------------------+
              |                     |                     |
   WORKING    |    HOW-TO GUIDES    |    REFERENCE        |
              |   (Task-oriented)   |   (Information-     |
              |                     |    oriented)        |
              |                     |                     |
              +---------------------+---------------------+
```

### 1.1 Quadrant Definitions

| Quadrant          | Purpose                   | User State                        | Content Style                  |
|-------------------|---------------------------|-----------------------------------|--------------------------------|
| **Tutorials**     | Learning by doing         | Newcomer, studying                | Step-by-step, hand-holding     |
| **How-To Guides** | Solving specific problems | Practitioner, working             | Goal-oriented, practical       |
| **Reference**     | Looking up information    | Practitioner, working             | Accurate, complete, structured |
| **Explanation**   | Understanding concepts    | Learner or practitioner, studying | Discursive, contextual         |

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
<!-- Bad: Tutorial mixed with Reference -->
# Getting Started

First, install the package:
pip install knowledge-mcp

## API Reference

### knowledge_mcp.search
def search(query: str, n_results: int = 5) -> list[dict]
...
```

```markdown
<!-- Good: Separate documents -->
<!-- tutorials/getting-started.md -->
# Getting Started
First, install the package...

<!-- reference/api.md -->
# API Reference
## knowledge_mcp.search
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
│   └── first-search.md
├── how-to/                     # Task-oriented
│   ├── index.md
│   ├── installation.md
│   ├── ingest-documents.md
│   └── configure-qdrant.md
├── reference/                  # Information-oriented
│   ├── index.md
│   ├── api/
│   │   ├── index.md
│   │   ├── search.md
│   │   └── ingest.md
│   ├── cli.md
│   └── configuration.md
├── explanation/                # Understanding-oriented
│   ├── index.md
│   ├── architecture.md
│   ├── chunking-strategies.md
│   └── embedding-models.md
├── _static/                    # Static assets
│   └── css/
│       └── custom.css
└── _templates/                 # Custom templates
```

---

## 3. Sphinx Configuration

### 3.1 Project Setup

```bash
# Install dependencies with Poetry
poetry add --group docs sphinx furo myst-parser sphinx-design sphinx-copybutton sphinx-autobuild
```

### 3.2 conf.py

```python
# docs/conf.py
"""Sphinx configuration for Knowledge MCP documentation."""

import os
import sys
from datetime import datetime

# Add source to path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
project = "Knowledge MCP"
copyright = f"{datetime.now().year}, David Dunnock"
author = "David Dunnock"
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
    "qdrant": ("https://qdrant.github.io/qdrant/redoc/", None),
}

# -- Options for copybutton --------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |> "
copybutton_prompt_is_regexp = True
```

---

## 4. Build and Deploy

### 4.1 Local Build

```bash
# Build HTML documentation
cd docs
sphinx-build -b html . _build/html

# Serve locally for preview
python -m http.server -d _build/html 8000

# Auto-rebuild on changes
sphinx-autobuild docs docs/_build/html --open-browser
```

### 4.2 pyproject.toml Integration

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
```

---

## 5. Documentation Templates

### 5.1 Tutorial Template

````markdown
# Tutorial Title

{.tutorial-badge}

## What You'll Learn

By the end of this tutorial, you will:

- Learning objective 1
- Learning objective 2
- Learning objective 3

## Prerequisites

Before starting, ensure you have:

- [ ] Knowledge MCP installed
- [ ] Qdrant Cloud account configured

## Step 1: First Step

Explanation of what we're doing and why.

```python
# Code example
from knowledge_mcp import search

results = search("systems engineering")
```

You should see:

```
[{'content': '...', 'score': 0.95}]
```

## Summary

In this tutorial, you learned how to:

- Summary point 1
- Summary point 2

## Next Steps

- [Next Tutorial](next-tutorial.md)
- [Related How-To Guide](../how-to/related.md)
````

### 5.2 How-To Guide Template

````markdown
# How to [Accomplish Task]

{.howto-badge}

This guide shows you how to [accomplish specific task].

## Prerequisites

- Requirement 1
- Requirement 2

## Steps

### 1. First Action

```bash
command to run
```

### 2. Second Action

```python
code example
```

### 3. Verify

Confirm the task completed successfully:

```bash
verification command
```

## Troubleshooting

### Common Issue 1

Solution for issue 1.

## See Also

- [Related Reference](../reference/related.md)
````

### 5.3 Reference Template

````markdown
# Component Reference

{.reference-badge}

## Overview

Brief description of the component.

## API

### Function: search

```python
def search(
    query: str,
    n_results: int = 5,
    document_type: str | None = None,
) -> list[dict[str, Any]]
```

**Parameters:**

| Parameter       | Type                  | Default  | Description                 |
|-----------------|-----------------------|----------|-----------------------------|
| `query`         | `str`                 | Required | Search query text           |
| `n_results`     | `int`                 | `5`      | Number of results to return |
| `document_type` | `str\| None`          | `None`   | Filter by document type     |

**Returns:**

- `list[dict]`: List of search results with content and scores

**Raises:**

- `ValueError`: When query is empty

**Example:**

```python
from knowledge_mcp import search

results = search("IEEE 15288 process", n_results=10)
for result in results:
    print(f"{result['score']:.2f}: {result['content'][:100]}")
```
````

---

## 6. Quality Checklist

### 6.1 Before Publishing

- [ ] Content is in the correct Diataxis quadrant
- [ ] No quadrant mixing within a document
- [ ] All code examples are tested and working
- [ ] Cross-references are valid
- [ ] Spelling and grammar checked
- [ ] Build completes without warnings (`-W` flag)

### 6.2 Periodic Review

- [ ] API documentation matches current code
- [ ] Tutorials work with latest version
- [ ] How-to guides address current user needs
- [ ] Explanations reflect current architecture