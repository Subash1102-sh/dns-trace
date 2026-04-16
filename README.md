---

## Setup

```bash
git clone https://github.com/Subash1102-sh/dns-trace.git
cd dns-trace
touch dns/__init__.py resolver/__init__.py tests/__init__.py
echo "import sys, os; sys.path.insert(0, os.path.dirname(__file__))" > conftest.py
pip install pytest
pytest tests/ -v
```

---

## Why build this?

DNS is the foundation of every network connection. Most developers use libraries that hide what actually happens. This project builds the resolver from scratch — parsing RFC 1035 binary wire format, manually decoding bit-packed headers, following the root → TLD → authoritative delegation chain, and handling pointer compression — to deeply understand how DNS actually works at the protocol level.

