"""
DNS Header — 12 bytes, always fixed.

Wire format (RFC 1035 Section 4.1.1):

     0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                       |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   OPCODE  |AA|TC|RD|RA|   Z    |   RCODE   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

Key flag bits (inside the 16-bit FLAGS field):
    QR     bit 15  — 0 = query, 1 = response
    OPCODE bits 11-14 — 0 = standard query
    AA     bit 10  — authoritative answer
    TC     bit 9   — truncated (response too big for UDP)
    RD     bit 8   — recursion desired (we set this to 1)
    RA     bit 7   — recursion available (server sets this)
    RCODE  bits 0-3 — 0=ok, 3=NXDOMAIN, 2=SERVFAIL
"""

import struct
import random
from dataclasses import dataclass, field


@dataclass
class DNSHeader:
    id: int = field(default_factory=lambda: random.randint(0, 65535))
    qr: int = 0          # 0=query, 1=response
    opcode: int = 0      # 0=standard
    aa: int = 0          # authoritative answer
    tc: int = 0          # truncated
    rd: int = 1          # recursion desired — always 1 for us
    ra: int = 0          # recursion available
    z: int = 0           # reserved, must be 0
    rcode: int = 0       # 0=NOERROR, 3=NXDOMAIN, 2=SERVFAIL
    qdcount: int = 1     # number of questions
    ancount: int = 0     # number of answers
    nscount: int = 0     # number of authority records
    arcount: int = 0     # number of additional records

    def pack(self) -> bytes:
        """
        Pack the header into 12 bytes of binary wire format.

        The FLAGS field packs all the bit fields into a single 16-bit integer.
        Use bitwise OR and left-shift (<<) to build it:

            flags = (self.qr << 15) | (self.opcode << 11) | (self.aa << 10) ...

        Then use struct.pack with format '!HHHHHH':
            '!' = network byte order (big-endian)
            'H' = unsigned short (2 bytes)
            Six H's = ID, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT

        TODO: implement this
        """

    def pack(self) -> bytes:
        flags = (
                (self.qr << 15) |
                (self.opcode << 11) |
                (self.aa << 10) |
                (self.tc << 9) |
                (self.rd << 8) |
                (self.ra << 7) |
                (self.z << 4) |
                (self.rcode)
        )
        return struct.pack('!HHHHHH',
                           self.id,
                           flags,
                           self.qdcount,
                           self.ancount,
                           self.nscount,
                           self.arcount
                           )

    # @classmethod
    # def unpack(cls, data: bytes) -> "DNSHeader":
    #     id_, flags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', data[:12])
    #     return cls(
    #         id=id_,
    #         qr=(flags >> 15) & 0x1,
    #         opcode=(flags >> 11) & 0xF,
    #         aa=(flags >> 10) & 0x1,
    #         tc=(flags >> 9) & 0x1,
    #         rd=(flags >> 8) & 0x1,
    #         ra=(flags >> 7) & 0x1,
    #         rcode=flags & 0xF,
    #         qdcount=qdcount,
    #         ancount=ancount,
    #         nscount=nscount,
    #         arcount=arcount,
    #     )

    def __repr__(self):
        return (
            f"DNSHeader(id={self.id}, qr={self.qr}, rcode={self.rcode}, "
            f"qdcount={self.qdcount}, ancount={self.ancount})"
        )
