# Reset ufw to default settings (optional, removes all existing rules)
sudo ufw --force reset

# Set default policies - deny incoming, allow outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow TCP port 80 (HTTP)
sudo ufw allow 80/tcp

# Allow TCP port 443 (HTTPS)
sudo ufw allow 443/tcp

# Enable the firewall
sudo ufw enable

# Check the status
sudo ufw status verbose

# list rules with numbers
sudo ufw status numbered

# By port
sudo ufw delete allow 80/tcp

# Or by rule number
sudo ufw delete [number]

# Probably don't want to do this
sudo ufw disable
