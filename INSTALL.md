# Installation Guide

## Prerequisites
- **Python**: 3.8 or higher
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (Recommended) or pip

## 🚀 Quick Start (Using uv)

`uv` is an extremely fast Python package installer and resolver.

```bash
# 1. Create a virtual environment
uv venv

# 2. Activate the environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 3. Install dependencies
uv pip install -r requirements.txt
```

## 🐢 Standard Install (Using pip)

If you prefer standard pip:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate
source .venv/bin/activate

# 3. Install
pip install -r requirements.txt
```

## 🛠 Troubleshooting
- **FPDF Error**: If you see `ImportError: No module named 'fpdf'`, ensure you installed specific dependencies:
  ```bash
  uv pip install fpdf
  ```
- **Plotting Issues**: If standard chinese/indian fonts don't render, the code defaults to English labels.
