"""
dns-trace CLI

Usage:
    python cli.py google.com
    python cli.py google.com A
    python cli.py google.com MX
    python cli.py --reverse 8.8.8.8
    python cli.py google.com --no-verbose

Examples:
    $ python cli.py google.com
    [hop 1] Querying 198.41.0.4 (root) for google.com ... 14ms → referral
    [hop 2] Querying 192.5.6.30 (TLD) for google.com ... 38ms → referral
    [hop 3] Querying 216.239.32.10 (auth) for google.com ... 22ms → answer

    Resolved google.com A in 3 hops, 74ms
    142.250.80.46  TTL=300s
"""

import argparse
import sys
import time

from resolver.iterative import IterativeResolver, NXDomainError, ResolutionError
from dns.records import TYPE_A, TYPE_NS, TYPE_MX, TYPE_AAAA, TYPE_CNAME


QTYPE_MAP = {
    "A":     TYPE_A,
    "NS":    TYPE_NS,
    "MX":    TYPE_MX,
    "AAAA":  TYPE_AAAA,
    "CNAME": TYPE_CNAME,
}


def reverse_lookup(ip: str) -> str:
    """
    Perform a reverse DNS lookup for an IP address.

    Steps:
    1. Reverse the octets of the IP: "8.8.8.8" → "8.8.8.8"
       More precisely: "1.2.3.4" → "4.3.2.1.in-addr.arpa"
    2. Query for a PTR record on that domain
    3. Return the PTR name

    TODO: implement this using IterativeResolver
    """
    raise NotImplementedError("You need to implement reverse_lookup()")


def main():
    parser = argparse.ArgumentParser(
        description="dns-trace: iterative DNS resolver from scratch"
    )
    parser.add_argument("domain", help="Domain name to resolve")
    parser.add_argument(
        "qtype", nargs="?", default="A",
        choices=QTYPE_MAP.keys(),
        help="Record type to query (default: A)"
    )
    parser.add_argument(
        "--reverse", action="store_true",
        help="Perform reverse lookup (domain arg is treated as IP)"
    )
    parser.add_argument(
        "--no-verbose", action="store_true",
        help="Suppress hop-by-hop output"
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Disable caching"
    )

    args = parser.parse_args()

    resolver = IterativeResolver(verbose=not args.no_verbose)

    start = time.time()
    try:
        if args.reverse:
            result = reverse_lookup(args.domain)
            elapsed = (time.time() - start) * 1000
            print(f"\n{args.domain} → {result}  ({elapsed:.0f}ms)")
        else:
            qtype = QTYPE_MAP[args.qtype]
            records = resolver.resolve(args.domain, qtype)
            elapsed = (time.time() - start) * 1000
            hops = len(resolver.hops)

            print(f"\nResolved {args.domain} {args.qtype} "
                  f"in {hops} hop{'s' if hops != 1 else ''}, {elapsed:.0f}ms")
            for r in records:
                print(f"  {r.parsed_rdata}  TTL={r.ttl}s")

    except NXDomainError:
        print(f"\nNXDOMAIN: {args.domain} does not exist", file=sys.stderr)
        sys.exit(1)
    except ResolutionError as e:
        print(f"\nResolution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
