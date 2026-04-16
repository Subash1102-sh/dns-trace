"""
DNS Question and Resource Record (answer) structures.

QUESTION section wire format:
    QNAME   — variable length, label-encoded domain name
    QTYPE   — 2 bytes, record type (A=1, NS=2, CNAME=5, MX=15, AAAA=28)
    QCLASS  — 2 bytes, always 1 (IN = Internet)

RESOURCE RECORD wire format (answers, authority, additional):
    NAME    — variable length, label-encoded (may use pointer compression)
    TYPE    — 2 bytes
    CLASS   — 2 bytes
    TTL     — 4 bytes, seconds this record can be cached
    RDLENGTH— 2 bytes, length of RDATA
    RDATA   — variable, the actual data (IP address, nameserver name, etc.)

Label encoding for domain names:
    "google.com" is encoded as:
        \x06 g o o g l e \x03 c o m \x00
    Each label is prefixed by its length byte.
    The name ends with a zero byte (\x00).

Pointer compression (the hard part):
    If the top 2 bits of a length byte are 11 (i.e. byte & 0xC0 == 0xC0),
    it's NOT a length — it's a pointer.
    The offset = ((byte & 0x3F) << 8) | next_byte
    Jump to that offset in the full message and read the name from there.
    This is why parse_name() needs the full message buffer, not just a slice.
"""

import struct
from dataclasses import dataclass
from typing import Optional


# Record type constants
TYPE_A     = 1
TYPE_NS    = 2
TYPE_CNAME = 5
TYPE_MX    = 15
TYPE_AAAA  = 28
TYPE_PTR   = 12

TYPE_NAMES = {
    1: "A", 2: "NS", 5: "CNAME", 12: "PTR", 15: "MX", 28: "AAAA"
}

CLASS_IN = 1  # Internet class — always this


def encode_name(domain: str) -> bytes:
    """
    Encode a domain name into DNS label format.

    Example: "google.com" → b'\x06google\x03com\x00'

    Steps:
    1. Split domain by '.'
    2. For each label: encode length as 1 byte, then the label bytes
    3. Append \x00 to terminate

    Edge case: if domain ends with '.', strip it first.

    TODO: implement this
    """
    raise NotImplementedError("You need to implement encode_name()")


def parse_name(data: bytes, offset: int) -> tuple[str, int]:
    """
    Parse a label-encoded domain name from a DNS message.

    Returns (name_string, new_offset) where new_offset is the byte
    position AFTER the name in the original data (not after a pointer target).

    This is the hardest function in the project. Handle three cases:

    Case 1 — normal label:
        byte = data[offset]
        if byte == 0: end of name, return ('', offset+1)
        if (byte & 0xC0) == 0: it's a length byte
            read `byte` characters starting at offset+1
            recurse/continue from offset + 1 + byte

    Case 2 — pointer compression:
        if (byte & 0xC0) == 0xC0:
            offset2 = ((byte & 0x3F) << 8) | data[offset+1]
            follow the pointer: parse_name(data, offset2)
            IMPORTANT: return original offset+2, not the pointer target offset
            (the message continues after the 2-byte pointer, not after the target)

    Case 3 — zero byte:
        end of name

    Hint: build a list of labels, join with '.', return (name, final_offset)

    TODO: implement this
    """
    # labels = []
    # visited = offset
    #
    # while True:
    #     byte = data[offset]
    #
    #     if byte == 0:
    #         offset += 1
    #         break
    #
    #     elif (byte & 0xC0) == 0xC0:
    #         # pointer compression
    #         pointer = ((byte & 0x3F) << 8) | data[offset + 1]
    #         name, _ = parse_name(data, pointer)
    #         labels.append(name)
    #         offset += 2
    #         break
    #
    #     else:
    #         # normal label
    #         length = byte
    #         offset += 1
    #         label = data[offset:offset + length].decode()
    #         labels.append(label)
    #         offset += length
    #
    # return '.'.join(labels), offset


@dataclass
class DNSQuestion:
    name: str
    qtype: int = TYPE_A
    qclass: int = CLASS_IN

    def pack(self) -> bytes:
        """
        Pack into wire format: encoded name + 2-byte QTYPE + 2-byte QCLASS

        TODO: implement this
        """
        raise NotImplementedError("You need to implement DNSQuestion.pack()")

    @classmethod
    def unpack(cls, data: bytes, offset: int) -> tuple["DNSQuestion", int]:
        """
        Parse a question from data starting at offset.
        Returns (DNSQuestion, new_offset).

        TODO: implement this
        """
        raise NotImplementedError("You need to implement DNSQuestion.unpack()")


@dataclass
class DNSRecord:
    name: str
    rtype: int
    rclass: int
    ttl: int
    rdata: bytes          # raw rdata bytes
    parsed_rdata: str = ""  # human-readable: IP string, nameserver name, etc.

    @classmethod
    def unpack(cls, data: bytes, offset: int) -> tuple["DNSRecord", int]:
        """
        Parse a resource record from data starting at offset.
        Returns (DNSRecord, new_offset).

        Steps:
        1. parse_name(data, offset) → (name, offset)
        2. struct.unpack('!HHIH', data[offset:offset+10])
           → type(H), class(H), ttl(I=4bytes), rdlength(H)
           offset += 10
        3. rdata = data[offset:offset+rdlength], offset += rdlength
        4. parse parsed_rdata based on rtype:
               TYPE_A:     socket.inet_ntoa(rdata) → "x.x.x.x"
               TYPE_NS:    parse_name(data, offset-rdlength)[0] → nameserver
               TYPE_CNAME: parse_name(data, offset-rdlength)[0] → cname
               TYPE_AAAA:  socket.inet_ntop(AF_INET6, rdata) → IPv6 string
        5. Return (DNSRecord(...), offset)

        TODO: implement this
        """
        raise NotImplementedError("You need to implement DNSRecord.unpack()")

    def __repr__(self):
        type_name = TYPE_NAMES.get(self.rtype, str(self.rtype))
        return f"DNSRecord({self.name} {type_name} {self.parsed_rdata} TTL={self.ttl})"


# def encode_name(domain: str) -> bytes:
#     if domain.endswith('.'):
#         domain = domain[:-1]
#     result = b''
#     for label in domain.split('.'):
#         encoded = label.encode()
#         result += bytes([len(encoded)]) + encoded
#     result += b'\x00'
#     return result