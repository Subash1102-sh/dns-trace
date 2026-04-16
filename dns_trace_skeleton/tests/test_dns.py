"""
Tests for DNS Trace.

Run with: pytest tests/ -v

These tests are your checkpoints. Each one tells you exactly
what you need to make work. Implement them one by one.
"""

import pytest
import struct


class TestDNSHeader:

    def test_pack_produces_12_bytes(self):
        """A packed header must always be exactly 12 bytes."""
        from dns.header import DNSHeader
        h = DNSHeader(id=1234)
        assert len(h.pack()) == 12

    def test_pack_unpack_roundtrip(self):
        """pack() then unpack() must give back the same values."""
        from dns.header import DNSHeader
        original = DNSHeader(id=42, qr=0, rd=1, qdcount=1)
        raw = original.pack()
        parsed = DNSHeader.unpack(raw)
        assert parsed.id == 42
        assert parsed.qr == 0
        assert parsed.rd == 1
        assert parsed.qdcount == 1

    def test_qr_flag_bit(self):
        """QR flag must be in bit 15 of the flags field."""
        from dns.header import DNSHeader
        h = DNSHeader(id=1, qr=1, qdcount=0)
        raw = h.pack()
        _, flags = struct.unpack('!HH', raw[:4])
        assert (flags >> 15) & 0x1 == 1

    def test_tc_flag_bit(self):
        """TC (truncation) flag must be in bit 9."""
        from dns.header import DNSHeader
        h = DNSHeader(id=1, tc=1, qdcount=0)
        raw = h.pack()
        _, flags = struct.unpack('!HH', raw[:4])
        assert (flags >> 9) & 0x1 == 1

    def test_rcode_nxdomain(self):
        """RCODE=3 must round-trip correctly."""
        from dns.header import DNSHeader
        h = DNSHeader(id=1, qr=1, rcode=3, qdcount=0)
        parsed = DNSHeader.unpack(h.pack())
        assert parsed.rcode == 3


class TestEncoding:

    def test_encode_simple_domain(self):
        """google.com → \\x06google\\x03com\\x00"""
        from dns.records import encode_name
        result = encode_name("google.com")
        assert result == b'\x06google\x03com\x00'

    def test_encode_subdomain(self):
        """www.google.com → \\x03www\\x06google\\x03com\\x00"""
        from dns.records import encode_name
        result = encode_name("www.google.com")
        assert result == b'\x03www\x06google\x03com\x00'

    def test_encode_single_label(self):
        """Single label like 'com' → \\x03com\\x00"""
        from dns.records import encode_name
        result = encode_name("com")
        assert result == b'\x03com\x00'

    def test_parse_name_simple(self):
        """Parse a simple label-encoded name."""
        from dns.records import parse_name
        data = b'\x06google\x03com\x00' + b'\x00' * 10
        name, offset = parse_name(data, 0)
        assert name == "google.com"
        assert offset == 12  # 1+6+1+3+1 = 12

    def test_parse_name_with_pointer(self):
        """
        Pointer compression: name at offset 12 uses pointer to offset 0.
        data = b'\\x06google\\x03com\\x00' + b'\\xc0\\x00'
                offset 0-11 = "google.com"
                offset 12-13 = pointer to offset 0
        """
        from dns.records import parse_name
        data = b'\x06google\x03com\x00\xc0\x00'
        name, offset = parse_name(data, 12)
        assert name == "google.com"
        assert offset == 14  # pointer is 2 bytes, so offset advances by 2


class TestDNSMessage:

    def test_build_query_packs_cleanly(self):
        """A query message must pack without errors."""
        from dns.message import DNSMessage
        msg = DNSMessage.build_query("google.com")
        raw = msg.pack()
        assert len(raw) > 12  # header + at least some question bytes

    def test_query_id_in_header(self):
        """The packed query must have a non-zero ID in the first 2 bytes."""
        from dns.message import DNSMessage
        msg = DNSMessage.build_query("google.com")
        raw = msg.pack()
        msg_id = struct.unpack('!H', raw[:2])[0]
        assert msg_id != 0

    def test_unpack_real_response(self):
        """
        Parse a real captured DNS response for google.com A.
        This is a pre-captured binary response — no network needed.

        The response contains:
          - 1 question
          - 1 answer: A record 142.250.80.46
        """
        from dns.message import DNSMessage
        # Real DNS response for google.com A (captured)
        raw = bytes([
            0x00, 0x01,  # ID=1
            0x81, 0x80,  # QR=1 RD=1 RA=1 (standard response)
            0x00, 0x01,  # QDCOUNT=1
            0x00, 0x01,  # ANCOUNT=1
            0x00, 0x00,  # NSCOUNT=0
            0x00, 0x00,  # ARCOUNT=0
            # Question: google.com A IN
            0x06, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65,  # \x06google
            0x03, 0x63, 0x6f, 0x6d, 0x00,               # \x03com\x00
            0x00, 0x01,  # QTYPE=A
            0x00, 0x01,  # QCLASS=IN
            # Answer: pointer to google.com, A, IN, TTL=300, 4 bytes, IP
            0xc0, 0x0c,  # pointer to offset 12 (google.com)
            0x00, 0x01,  # TYPE=A
            0x00, 0x01,  # CLASS=IN
            0x00, 0x00, 0x01, 0x2c,  # TTL=300
            0x00, 0x04,  # RDLENGTH=4
            0x8e, 0xfa, 0x50, 0x2e,  # 142.250.80.46
        ])
        msg = DNSMessage.unpack(raw)
        assert msg.header.ancount == 1
        assert len(msg.answers) == 1
        assert msg.answers[0].parsed_rdata == "142.250.80.46"
        assert msg.answers[0].ttl == 300


class TestCache:

    def test_put_and_get(self):
        """Cached record should be retrievable before TTL expires."""
        from resolver.cache import DNSCache
        from dns.records import DNSRecord, TYPE_A
        cache = DNSCache()
        record = DNSRecord("google.com", TYPE_A, 1, 300, b'', "142.250.80.46")
        cache.put("google.com", TYPE_A, [record])
        result = cache.get("google.com", TYPE_A)
        assert result is not None
        assert result[0].parsed_rdata == "142.250.80.46"

    def test_miss_returns_none(self):
        """Cache miss must return None."""
        from resolver.cache import DNSCache
        from dns.records import TYPE_A
        cache = DNSCache()
        assert cache.get("missing.com", TYPE_A) is None

    def test_expired_returns_none(self):
        """Expired record must return None."""
        import time
        from resolver.cache import DNSCache
        from dns.records import DNSRecord, TYPE_A

        cache = DNSCache()
        # Create a record with TTL=0 — expires immediately
        record = DNSRecord("google.com", TYPE_A, 1, 0, b'', "1.2.3.4")
        cache.put("google.com", TYPE_A, [record])
        time.sleep(0.1)
        assert cache.get("google.com", TYPE_A) is None
