"""
DNS Message — the full packet.

A DNS message has 5 sections:
    Header      — always 12 bytes (DNSHeader)
    Question    — QDCOUNT entries (DNSQuestion)
    Answer      — ANCOUNT entries (DNSRecord)
    Authority   — NSCOUNT entries (DNSRecord) — referrals to other nameservers
    Additional  — ARCOUNT entries (DNSRecord) — extra helpful records (glue)

For building queries: we only need Header + Question.
For parsing responses: we need all 5 sections.

The Authority section is critical for iterative resolution —
when a root server doesn't know the answer, it puts the
next nameserver to ask in the Authority section, and often
puts that nameserver's IP in the Additional section (glue records).
"""

import struct
from dataclasses import dataclass, field
from typing import List

from dns.header import DNSHeader
from dns.records import DNSQuestion, DNSRecord, TYPE_A


@dataclass
class DNSMessage:
    header: DNSHeader = field(default_factory=DNSHeader)
    questions: List[DNSQuestion] = field(default_factory=list)
    answers: List[DNSRecord] = field(default_factory=list)
    authority: List[DNSRecord] = field(default_factory=list)
    additional: List[DNSRecord] = field(default_factory=list)

    @classmethod
    def build_query(cls, domain: str, qtype: int = TYPE_A) -> "DNSMessage":
        """
        Build a DNS query message for the given domain and record type.

        Steps:
        1. Create a DNSHeader with qr=0 (query), rd=1, qdcount=1
        2. Create a DNSQuestion with the domain and qtype
        3. Return a DNSMessage with header + question

        TODO: implement this
        """
        raise NotImplementedError("You need to implement build_query()")

    def pack(self) -> bytes:
        """
        Serialize the full message to bytes.

        For a query: header.pack() + question.pack() for each question.
        We don't pack answers/authority/additional for outgoing queries.

        TODO: implement this
        """
        raise NotImplementedError("You need to implement pack()")

    @classmethod
    def unpack(cls, data: bytes) -> "DNSMessage":
        """
        Parse a full DNS response from raw bytes.

        Steps:
        1. DNSHeader.unpack(data) → header
        2. Parse header.qdcount questions starting at offset 12
        3. Parse header.ancount answer records
        4. Parse header.nscount authority records
        5. Parse header.arcount additional records
        6. Each parse call returns (record, new_offset) — chain the offsets

        TODO: implement this
        """
        raise NotImplementedError("You need to implement unpack()")

    def get_answer_ips(self) -> list:
        """Return list of IP strings from A records in the answer section."""
        from dns.records import TYPE_A
        return [r.parsed_rdata for r in self.answers if r.rtype == TYPE_A]

    def get_ns_names(self) -> list:
        """Return nameserver names from the authority section (NS records)."""
        from dns.records import TYPE_NS
        return [r.parsed_rdata for r in self.authority if r.rtype == TYPE_NS]

    def get_glue_ips(self) -> dict:
        """
        Return a dict of {nameserver_name: ip} from the additional section.
        These are 'glue records' — IPs for the nameservers in authority section.
        Without glue, you'd have to do a separate lookup for the NS's IP.
        """
        from dns.records import TYPE_A
        glue = {}
        for r in self.additional:
            if r.rtype == TYPE_A:
                glue[r.name] = r.parsed_rdata
        return glue
