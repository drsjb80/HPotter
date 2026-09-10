# Testing Guide: Container Cleanup Verification

## Overview
This guide helps you verify that the container cleanup fixes are working correctly over several days.

## What To Watch For

### ✅ Signs the Fix is Working
- **Log messages show cleanup**: Both "Stopping" and "Removing" messages appear for each connection
- **Container count stable**: Total container count stays roughly the same, doesn't grow continuously
- **No WARNING messages**: Cleanup should succeed without errors
- **Cleanup happens immediately**: Containers removed within seconds of connection end

### ❌ Signs Something is Still Wrong
- **Only "Stopping" messages**: If you see "Stopping" but no "Removing", cleanup is failing
- **WARNING messages**: Errors like "Error stopping/removing container" mean cleanup failed
- **Containers accumulate**: Total count grows continuously over hours/days
- **Long-lived containers**: Containers older than a few seconds that shouldn't exist

## Setup for Multi-Day Testing

### Terminal 1: Run the Application
```bash
cd /home/beaty/src/HPotter
source venv/bin/activate

# Optional: Set debug loglevel to see more details
python3 -m src --loglevel debug | tee hpotter_run.log
```

### Terminal 2: Monitor Containers
```bash
cd /home/beaty/src/HPotter

# Monitor every 30 seconds (change number to adjust frequency)
./monitor_containers.sh 30

# Or monitor every 60 seconds
./monitor_containers.sh 60
```

### Terminal 3: Send Test Connections (optional)
```bash
# SSH connections (if configured)
for i in {1..5}; do
  timeout 2 ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no localhost:22
  sleep 1
done

# Telnet connections (if configured)  
for i in {1..5}; do
  timeout 2 telnet localhost 23
  sleep 1
done

# HTTP connections (if configured)
for i in {1..5}; do
  timeout 2 curl http://localhost:80/ 2>/dev/null
  sleep 1
done
```

## What to Log/Track

### Daily Checklist
- [ ] **Log file size**: Check `hpotter_run.log` size and review for errors
- [ ] **Container count**: Use `docker ps -a -q | wc -l` to get total
- [ ] **No accumulation**: Verify count is stable, not growing
- [ ] **Cleanup messages**: Grep for "Removing" in logs: `grep "Removing" hpotter_run.log | wc -l`
- [ ] **Error check**: Look for WARNING messages: `grep "WARNING" hpotter_run.log`

### Useful Commands

**Get current container counts:**
```bash
echo "Total containers: $(docker ps -a -q | wc -l)"
echo "Running: $(docker ps -q | wc -l)"
echo "Stopped: $(docker ps -a --filter 'status=exited' -q | wc -l)"
echo "HPotter sleep containers: $(docker ps -a --filter 'command=sleep infinity' -q | wc -l)"
```

**Watch logs in real-time:**
```bash
tail -f hpotter_run.log | grep -E "Stopping|Removing|WARNING|ERROR"
```

**Count cleanup messages per hour:**
```bash
# Every 30 minutes, count how many containers were removed
watch -n 1800 'echo "Containers removed: $(grep Removing hpotter_run.log | wc -l)"'
```

**Identify old containers:**
```bash
# Show containers older than 1 hour
docker ps -a --format "{{.ID}}: {{.CreatedAt}} - {{.Image}} - {{.Command}}"
```

## Expected Behavior

### First Hour
- Expect to see containers being created and removed frequently
- Log should show matching "Stopping" and "Removing" messages
- Container count might fluctuate but generally stable

### After 8+ Hours
- Container count should be in the **same ballpark** as after first hour
- Not 2x, 3x, or 10x larger
- **Old containers should NOT exist** (should have been cleaned up)

### After 24+ Hours
- Container count should be **roughly stable** (may vary by ±10 containers)
- No containers older than a few minutes should exist
- Log should show steady cleanup happening

## Troubleshooting

### If containers keep accumulating:
1. Check for WARNING messages in logs
2. Verify the fix was applied: `git diff HEAD~1 src/ssh_container.py`
3. Look for specific error patterns: `grep "Error stopping" hpotter_run.log`

### If you see only "Stopping" without "Removing":
1. This means cleanup is partially failing
2. Check logs for WARNING messages immediately after "Stopping"
3. May indicate docker client connection issues

### If containers accumulate but logs look fine:
1. The logs might be missing errors (check logging config)
2. Docker daemon might have issues: `docker system df`
3. Containers might be in a stuck state: `docker inspect <container_id>`

## When to Declare Success

After **48+ hours** of continuous operation:
- ✅ Container count stable (not continuously growing)
- ✅ Both "Stopping" and "Removing" messages in logs
- ✅ No WARNING messages about cleanup failures
- ✅ No containers older than expected connection lifetimes

## Cleanup if Issues Found

If you find issues and need to start fresh:
```bash
# Stop the application (Ctrl+C in terminal 1)

# Remove all HPotter containers
docker ps -a --filter "command=sleep infinity" -q | xargs docker rm -f

# Remove all stopped containers (if safe)
docker container prune -f

# Verify clean slate
docker ps -a -q | wc -l  # Should be low number

# Restart application
python3 -m src
```

## Success Metrics

Create a simple summary file to track:

```bash
# Run this each day
cat >> test_summary.txt << EOF
Date: $(date)
Total containers: $(docker ps -a -q | wc -l)
Cleanup messages: $(grep -c "Removing" hpotter_run.log)
Errors: $(grep -c "WARNING" hpotter_run.log)
Log size: $(du -h hpotter_run.log | cut -f1)
---
EOF
```

## Duration Recommendation

Test for at least:
- **Minimum**: 24 hours
- **Recommended**: 48-72 hours
- **Ideal**: Full week to catch any patterns

This allows time to see if containers accumulate and to confirm cleanup is consistent.
