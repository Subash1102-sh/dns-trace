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


## Test status

| Test | Status |
|------|--------|
| `TestDNSHeader::test_pack_produces_12_bytes` | ✅ Passing |
| `TestDNSHeader::test_qr_flag_bit` | ✅ Passing |
| `TestDNSHeader::test_tc_flag_bit` | ✅ Passing |
| `TestDNSHeader::test_pack_unpack_roundtrip` | 🔄 In progress |
| `TestDNSHeader::test_rcode_nxdomain` | 🔄 In progress |
| `TestEncoding::test_encode_simple_domain` | 🔄 In progress |
| `TestEncoding::test_encode_subdomain` | 🔄 In progress |
| `TestEncoding::test_encode_single_label` | 🔄 In progress |
| `TestEncoding::test_parse_name_simple` | 🔄 In progress |
| `TestEncoding::test_parse_name_with_pointer` | 🔄 In progress |
| `TestDNSMessage::test_build_query_packs_cleanly` | 🔄 In progress |
| `TestDNSMessage::test_query_id_in_header` | 🔄 In progress |
| `TestDNSMessage::test_unpack_real_response` | 🔄 In progress |
| `TestCache::test_put_and_get` | 🔄 In progress |
| `TestCache::test_miss_returns_none` | 🔄 In progress |
| `TestCache::test_expired_returns_none` | 🔄 In progress |

---

## Why build this?

DNS is the foundation of every network connection. Most developers use libraries that hide what actually happens. This project builds the resolver from scratch — parsing RFC 1035 binary wire format, manually decoding bit-packed headers, following the root → TLD → authoritative delegation chain, and handling pointer compression — to deeply understand how DNS actually works at the protocol level.

