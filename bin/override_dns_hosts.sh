#!/usr/bin/env bash

# Script to query Cloudflare DNS server 1.1.1.1 for the IP addresses of specified domains and update /etc/hosts

# List of domains to query and update /etc/hosts
# Todo: add other OVH API domains
domains=("eu.api.ovh.com")

# Function to query Cloudflare DNS server for the IP address of a domain
query_ip_address() {
    domain=$1
    # Query IP address for the domain from Cloudflare DNS server 1.1.1.1
    ip_address=$(dig @1.1.1.1 +short $domain)
    echo "$ip_address"
}

# Function to update /etc/hosts with the IP address of a domain
update_hosts() {
    domain=$1
    ip_address=$2
    # Check if IP address is obtained
    if [ -n "$ip_address" ]; then
        # Update /etc/hosts with the IP address
        sed -i "/ $domain /d" /etc/hosts
        echo "$ip_address $domain # [$(date +'%Y-%m-%d %H:%M:%S')] Automatically added by $0" >>/etc/hosts
        echo "Updated /etc/hosts with IP address: $ip_address for domain: $domain"
    else
        # Remove entry from /etc/hosts if IP address is not obtained
        sed -i "/ $domain/d" /etc/hosts
        echo "Removed entry for domain: $domain from /etc/hosts due to resolution failure"
    fi
}

# Loop through the list of domains, query Cloudflare DNS server for IP addresses, and update /etc/hosts
for domain in "${domains[@]}"; do
    ip_address=$(query_ip_address $domain)
    update_hosts $domain $ip_address
done

exit 0
