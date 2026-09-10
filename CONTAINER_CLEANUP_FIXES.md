# Docker Container Cleanup Fixes

## Problem
HPotter was not cleaning up Docker containers after connections ended, resulting in hundreds of orphaned containers accumulating over time. Analysis showed 344 running containers from runs spanning 11 hours to 3 days ago.

## Root Cause
The SSH and Telnet container handlers had a resource leak:

1. **Missing Docker Client Closure**: Both `SSHContainer` and `TelnetContainer` create a Docker client in their `run()` method but never close it in a finally block. This leaves connections open and can prevent proper container cleanup.

2. **Silent Error Handling**: When `stop()` and `remove()` calls fail, errors were logged at DEBUG level only, making it impossible to diagnose cleanup failures in normal logs.

3. **Inconsistent Error Handling**: The regular `Container` class didn't catch exceptions from stop/remove calls, causing issues to propagate silently.

## Files Modified

### src/ssh_container.py
**Changes:**
- Added docker client closure in the finally block of `run()` method
- Improved `_cleanup()` method to:
  - Add explicit "Removing" log message
  - Upgrade error logging from DEBUG to WARNING level
  - Log container ID for better traceability

**Before:**
```python
def run(self):
    client = None
    try:
        client = docker.from_env()
        # ... container setup and operation ...
    except Exception as exc:
        logger.warning('SSHContainer error: %s', exc)
    finally:
        self._cleanup()  # client never closed!
```

**After:**
```python
def run(self):
    client = None
    try:
        client = docker.from_env()
        # ... container setup and operation ...
    except Exception as exc:
        logger.warning('SSHContainer error: %s', exc)
    finally:
        self._cleanup()
        if client:  # NOW properly closed
            try:
                logger.debug("Closing docker client %s", client)
                client.close()
            except Exception as close_err:
                logger.debug('Error closing docker client: %s', close_err)
```

### src/telnet_container.py
**Changes:**
- Added docker client closure in the finally block of `run()` method (same as SSH)
- Improved `_cleanup()` method with better error logging

### src/container.py
**Changes:**
- Added exception handling around stop/remove operations
- Improved error logging with container ID and WARNING level

## Impact

These fixes ensure:
1. Docker clients are properly closed after each connection, preventing resource leaks
2. Errors during container cleanup are visible in normal logs (WARNING level)
3. Containers are properly stopped and removed when connections end
4. Better debugging information if cleanup still fails

## Testing Recommendations

1. **Start the application** and verify it runs without errors
2. **Send test connections** to SSH and Telnet ports
3. **Monitor logs** to ensure you see "Stopping" and "Removing" messages
4. **Check docker ps** after connections close to verify containers are removed
5. **Run for extended period** to ensure no accumulation over time

## Future Considerations

- Consider adding metrics for failed cleanup attempts
- Implement periodic cleanup job for orphaned containers as safety net
- Add configuration option to set container TTL/auto-removal policy
- Consider using `auto_remove=True` in `client.containers.run()` as additional safety

## Cleanup of Existing Orphaned Containers

To remove all existing orphaned containers:
```bash
# Stop and remove all containers (CAUTION: only if no other containers needed)
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

# Or, remove only 'sleep infinity' containers (likely from HPotter):
docker ps -a --filter "command=sleep infinity" -q | xargs docker rm -f
```
