# Flush existing rules (optional, but recommended for a clean start)
sudo nft flush ruleset

# Create a new table for filtering
sudo nft add table inet filter

# Create a base chain for input traffic
sudo nft add chain inet filter input { type filter hook input priority 0 \; policy drop \; }

# Create a base chain for forward traffic (if you're routing)
sudo nft add chain inet filter forward { type filter hook forward priority 0 \; policy drop \; }

# Create a base chain for output traffic
sudo nft add chain inet filter output { type filter hook output priority 0 \; policy accept \; }

# Allow loopback traffic
sudo nft add rule inet filter input iif lo accept

# Allow established and related connections
sudo nft add rule inet filter input ct state established,related accept

# Allow TCP port 80 (HTTP)
sudo nft add rule inet filter input tcp dport 80 accept

# Allow TCP port 443 (HTTPS)
sudo nft add rule inet filter input tcp dport 443 accept

# Optional: Allow ping (ICMP)
sudo nft add rule inet filter input icmp type echo-request accept
sudo nft add rule inet filter input icmpv6 type echo-request accept
