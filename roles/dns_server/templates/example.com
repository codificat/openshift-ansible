; {{ dns_domain }} external view
@		IN SOA	dns.{{ dns_domain }}. hostmaster.{{ dns_domain }}. (
				2015062401 ; serial
				60         ; refresh (1 minute)
				15         ; retry (15 seconds)
				1800       ; expire (30 minutes)
				10         ; minimum (10 seconds)
				)
			NS	dns.{{ dns_domain }}.
			MX	10 mail.{{ dns_domain }}.

$TTL 600	; 10 minutes

dns		IN A    10.34.92.209

ose3-master	IN A	10.34.92.210
ose3-node1	IN A	10.34.92.211
ose3-node2	IN A	10.34.92.212

; This is where the router(s) run
*.apps		IN CNAME	ose3-node2
