Simple L3VPN between two routers, can be achieved by using BGP or static routing for the underlay instead of IS-IS.


Notes:

1. You can use ipv6 unicast to send BGP route for srv6 node prefix..
But to get bgpd to do recursive lookup for BGP prefix SID next-hop, you need to tell FRR/bgpd to disable-connected-check for the neighbor.
Doesn't matter if next-hop is global or link-local, frr/linux does not do recursive lookup in BGP for the locator otherwise.
Using a static route for the srv6 node prefix also works.

2. Even for single-hop, FRR uses encap and not encap.red mode in kernel. i.e. a redundant SRH is added (segments left = 0 from beginning). Not sure how to enable encap.red header.

