"""
Iterative DNS Resolver — the heart of DNS Trace.

This is what your project builds that most people's resolvers don't:
a real iterative resolver that walks the full chain from root servers
down to the authoritative nameserver, just like a real recursive resolver does.

The algorithm:

    def resolve(domain, qtype):
        nameserver = pick a root server IP   # start at the top
        while True:
            response = query(domain, qtype, nameserver)

            if response has answers:
                if answer is CNAME and qtype == A:
                    follow the CNAME (resolve the alias target instead)
                else:
                    return answers   # done

            elif response has authority NS records:
                # not an answer, but a referral — go deeper
                ns_names = response.get_ns_names()
                glue     = response.get_glue_ips()

                if glue has IP for ns_names[0]:
                    nameserver = glue[ns_names[0]]   # use glue record
                else:
                    nameserver = resolve(ns_names[0], A)[0].parsed_rdata  # resolve NS

            else:
                raise exception — no answer and no referral

ROOT SERVERS — the 13 root server clusters (we use their IPv4 addresses):
    These are hardcoded. Every DNS resolver in the world starts here.
"""

import socket
import time
from typing import List, Optional

from dns.message import DNSMessage
from dns.records import DNSRecord, TYPE_A, TYPE_NS, TYPE_CNAME
from resolver.cache import DNSCache


# The 13 root server IPs (one per letter, a through m)
ROOT_SERVERS = [
    "198.41.0.4",    # a.root-servers.net
    "199.9.14.201",  # b.root-servers.net
    "192.33.4.12",   # c.root-servers.net
    "199.7.91.13",   # d.root-servers.net
    "192.203.230.10",# e.root-servers.net
    "192.5.5.241",   # f.root-servers.net
    "192.112.36.4",  # g.root-servers.net
    "198.97.190.53", # h.root-servers.net
    "192.36.148.17", # i.root-servers.net
    "192.58.128.30", # j.root-servers.net
    "193.0.14.129",  # k.root-servers.net
    "199.7.83.42",   # l.root-servers.net
    "202.12.27.33",  # m.root-servers.net
]

DNS_PORT = 53
TIMEOUT  = 3      # seconds to wait for UDP response
MAX_HOPS = 20     # prevent infinite loops


class ResolutionError(Exception):
    """Raised when DNS resolution fails."""
    pass

class NXDomainError(ResolutionError):
    """Raised when domain does not exist (RCODE=3)."""
    pass


class IterativeResolver:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.cache   = DNSCache()
        self.hops    = []   # list of dicts recording each hop for display

    def query(self, domain: str, qtype: int, server_ip: str) -> DNSMessage:
        """
        Send a single DNS UDP query to server_ip:53 and return the parsed response.

        Steps:
        1. DNSMessage.build_query(domain, qtype)
        2. sock = socket.socket(AF_INET, SOCK_DGRAM)
        3. sock.settimeout(TIMEOUT)
        4. start = time.time()
        5. sock.sendto(query.pack(), (server_ip, DNS_PORT))
        6. data, _ = sock.recvfrom(4096)   # 4096 is safe max UDP DNS size
        7. rtt = (time.time() - start) * 1000  # milliseconds
        8. sock.close()
        9. return DNSMessage.unpack(data), rtt

        Handle socket.timeout → raise ResolutionError("Timeout querying {server_ip}")

        TODO: implement this
        """
        raise NotImplementedError("You need to implement query()")

    def resolve(self, domain: str, qtype: int = TYPE_A,
                start_server: Optional[str] = None) -> List[DNSRecord]:
        """
        Full iterative resolution from root to authoritative.

        Steps:
        1. Check cache first — if hit, return cached records
        2. Pick starting nameserver:
               start_server if provided, else ROOT_SERVERS[0]
        3. Loop up to MAX_HOPS times:
               a. Call self.query(domain, qtype, current_ns)
               b. Record the hop in self.hops
               c. Check response.header.rcode:
                    3 → raise NXDomainError
                    2 → raise ResolutionError("SERVFAIL")
               d. If response.answers:
                    handle CNAME chain (see below)
                    cache the records
                    return the records
               e. Elif response.authority has NS records:
                    get ns_names and glue
                    pick next nameserver IP (from glue or recursive resolve)
               f. Else: raise ResolutionError("No answer and no referral")
        4. raise ResolutionError("Max hops exceeded")

        CNAME handling:
            If answer is a CNAME record and qtype == TYPE_A:
                target = cname_record.parsed_rdata
                if self.verbose: print the CNAME chain
                return self.resolve(target, TYPE_A)  # follow the alias

        TODO: implement this
        """
        raise NotImplementedError("You need to implement resolve()")

    def _log_hop(self, server_ip: str, domain: str, response: DNSMessage,
                 rtt: float) -> None:
        """
        Record and optionally print a resolution hop.

        Store in self.hops:
            {"server": server_ip, "domain": domain, "rtt_ms": rtt,
             "answers": len(response.answers),
             "authority": len(response.authority)}

        If self.verbose: print a formatted line like:
            [hop 1] Querying 198.41.0.4 for google.com ... 12ms → referred to a.gtld-servers.net

        TODO: implement this
        """
        raise NotImplementedError("You need to implement _log_hop()")
