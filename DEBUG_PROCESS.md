# Debugging: Docker Container Cleanup Issue

## Observation
Application not removing Docker containers - 344 containers running, dating back 3 days.

## Investigation Steps

### Step 1: Data Gathering
- **debug.log** (5.9MB): Contains application runtime logs
- **dpsa.txt** (docker ps -a): Shows 344 running containers with ages from 11 hours to 3 days
- Git status: Recent code changes to `.choices` and `README.md`

### Step 2: Log Analysis
Searched debug.log for cleanup-related messages:
```
container:111 INFO - Stopping: <Container: 204a2fe963d3>
container:113 INFO - Removing: <Container: 204a2fe963d3>
```

**Key Finding**: Logs show cleanup code IS being called ("Stopping" and "Removing" messages), but containers remain running.

**Conclusion**: Cleanup is being attempted but failing silently.

### Step 3: Code Review - Architecture

Examined the connection lifecycle as documented in CLAUDE.md:
1. **ListenThread** → accepts connection, submits Container to ThreadPoolExecutor
2. **Container** → runs in executor, calls `_stop_and_remove()` in finally block
3. **SSHContainer/TelnetContainer** → subclasses of Container with different protocols

### Step 4: Resource Management Pattern Analysis

Compared how docker clients are managed:

**In `container.py` (Regular HTTP/etc containers):**
```python
def run(self):
    client = None
    try:
        client = docker.from_env()
        # ... work ...
        self._stop_and_remove()
    finally:
        if client:
            client.close()  # ✓ Properly closed
```

**In `ssh_container.py` (SSH containers):**
```python
def run(self):
    client = None
    try:
        client = docker.from_env()
        # ... work ...
        self._bridge_channel(channel)
    finally:
        self._cleanup()  # ✗ client never closed!
```

**The Bug**: SSH and Telnet containers create a docker client but never close it!

### Step 5: Cascading Resource Leak Impact

1. Docker client created in `run()` → never closed
2. Same container class creates ANOTHER client in `_bridge_channel()` → that one IS closed
3. But the first client stays open → resource leak
4. When `_stop_and_remove()` tries to stop/remove container, docker connection issues occur
5. Errors logged at DEBUG level only (invisible by default)
6. Container cleanup fails silently
7. Orphaned containers accumulate

### Step 6: Error Visibility Issue

Additional finding in error handling:

**Original code:**
```python
def _cleanup(self):
    if self.container:
        try:
            self.container.stop()
            self.container.remove()
        except Exception as exc:
            logger.debug('Error stopping SSH container: %s', exc)  # DEBUG level!
```

Even when cleanup fails, errors are at DEBUG level, making them invisible in normal logs.

## Solution Applied

### Fix 1: Close Docker Clients Properly
Added docker client closure in finally block for both SSH and Telnet containers:

```python
finally:
    self._cleanup()
    if client:
        try:
            logger.debug("Closing docker client %s", client)
            client.close()
        except Exception as close_err:
            logger.debug('Error closing docker client: %s', close_err)
```

### Fix 2: Better Error Logging
Upgraded error logging for container cleanup from DEBUG to WARNING:

```python
except Exception as exc:
    logger.warning('Error stopping/removing SSH container %s: %s',
                  self.container.id[:12], exc)
```

### Fix 3: Explicit Status Logging
Added explicit "Removing" log message to match "Stopping" message for clarity.

## Files Changed
- `src/ssh_container.py` - Added client closure + improved logging
- `src/telnet_container.py` - Added client closure + improved logging  
- `src/container.py` - Improved error handling in stop/remove

## Verification Strategy

1. **Unit Testing**: Verify container cleanup in test environment
2. **Integration Testing**: Run honeypot for extended period, monitor logs
3. **Metrics**: Count containers before/after to verify cleanup working
4. **Log Monitoring**: Watch for any WARNING messages about cleanup failures

## Prevention of Similar Issues

Checklist for resource management in this codebase:
- [ ] All docker clients created with `docker.from_env()` must be closed in finally block
- [ ] All socket connections must be closed in finally block
- [ ] All threading.Event() cleanups must be signaled
- [ ] Important errors should be at WARNING+ level, not DEBUG
- [ ] Resource cleanup errors should be visible for debugging

## Key Lessons

1. **Resource Leaks Are Silent**: Files and connections that aren't explicitly closed might look fine in logs
2. **Parent Classes Matter**: When subclassing, ensure resource cleanup patterns are followed
3. **Log Levels Matter**: DEBUG-level errors are easy to miss in production logs
4. **Multiple Clients**: Creating multiple docker clients to the same daemon can cause issues if previous ones aren't closed
5. **Test Coverage**: Need explicit tests for container cleanup, not just creation
