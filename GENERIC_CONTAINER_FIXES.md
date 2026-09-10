# Generic Container Class Fixes

## Problem Identified
The generic `Container` class (used for httpd, telnet, and other services) was failing silently when Docker API timeouts occurred:

```
Error in container thread: UnixHTTPConnectionPool(host='localhost', port=None): 
Read timed out. (read timeout=60)
```

This suggests the Docker daemon was overwhelmed by hundreds of accumulated containers.

## Root Causes

### 1. Docker API Timeouts Not Handled
When Docker API calls timeout, the container cleanup fails silently. This is especially bad when the Docker daemon is under heavy load from accumulated containers.

### 2. Cleanup Error Logging at DEBUG Level (Fixed in Previous Commit)
Errors during cleanup after exceptions were logged at DEBUG level, making them invisible:
```python
# Before (Line 100)
except Exception as cleanup_err:
    logger.debug('Error during cleanup: %s', cleanup_err)  # DEBUG level
```

### 3. Logs Call Could Fail
The `.logs()` call on a container can itself timeout or fail, preventing the entire cleanup:
```python
# Before
logger.debug(str(self.container.logs()))  # Could fail here, preventing cleanup
```

## Solutions Applied

### Fix 1: Add Timeout to stop() Calls
```python
# Before
self.container.stop()

# After
self.container.stop(timeout=10)  # 10-second timeout
```
**Why**: Prevents hanging indefinitely if Docker daemon is slow.

### Fix 2: Use force=True on remove()
```python
# Before
self.container.remove()

# After
self.container.remove(force=True)  # Force removal even if stop times out
```
**Why**: Ensures container is removed even if graceful stop fails.

### Fix 3: Wrap Logs Call in Try/Except
```python
# Before
logger.debug(str(self.container.logs()))  # Could crash

# After
try:
    logger.debug(str(self.container.logs()))
except Exception as log_err:
    logger.debug('Error reading container logs: %s', log_err)
```
**Why**: Don't let logging failure prevent cleanup.

### Fix 4: Upgrade Error Logging to WARNING
```python
# Before (Line 100)
except Exception as cleanup_err:
    logger.debug('Error during cleanup: %s', cleanup_err)

# After
except Exception as cleanup_err:
    logger.warning('Error during cleanup after error: %s', cleanup_err)
```
**Why**: Cleanup failures are important and should be visible.

### Fix 5: Add Context Logging
Added container ID and context to cleanup operations:
```python
# Before
logger.info('Stopping: %s', self.container)

# After  
logger.info('Stopping: %s', self.container)  # Shows full container object
logger.debug('Successfully removed container %s', self.container.id[:12])
```
**Why**: Easier to track which containers failed and succeeded.

### Fix 6: Improve Error Context in Exception Handler
```python
# Before
logger.info('Error in container thread: %s', err)
if hasattr(self, 'container') and self.container:
    try:
        self._stop_and_remove()
    except Exception as cleanup_err:
        logger.debug('Error during cleanup: %s', cleanup_err)

# After
logger.info('Error in container thread: %s', err)
if hasattr(self, 'container') and self.container:
    try:
        logger.info('Attempting cleanup after error for container %s',
                   self.container.id[:12])
        self._stop_and_remove()
    except Exception as cleanup_err:
        logger.warning('Error during cleanup after error: %s', cleanup_err)
```
**Why**: Shows when cleanup is attempted after errors and captures all failures.

## Files Modified
- `src/container.py` - Improved error handling and timeout parameters
- `src/ssh_container.py` - Added timeout and force parameters
- `src/telnet_container.py` - Added timeout and force parameters

## Impact

### Before
```
container:94 WARNING - Error in container thread: UnixHTTPConnectionPool(...) Read timed out
[container fails to clean up, remains running indefinitely]
```

### After
```
container:111 INFO - Stopping: <Container: 204a2fe963d3>
container:111 INFO - Removing: <Container: 204a2fe963d3>
container:109 DEBUG - Successfully removed container 204a2fe963d3
[or if it fails:]
container:117 WARNING - Error stopping/removing container 204a2fe963d3: [error details]
```

## Benefits

1. **Timeout Prevention**: Won't hang waiting for unresponsive Docker daemon
2. **Force Removal**: Containers are removed even if graceful stop fails
3. **Better Visibility**: All cleanup operations and failures visible in logs
4. **Robustness**: Logs call failure doesn't prevent cleanup
5. **Traceability**: Container IDs in all log messages for debugging

## Testing Recommendations

1. **Monitor timeout messages**: Watch for any "Read timed out" errors
2. **Verify removals**: Check that both "Stopping" AND "Removing" messages appear
3. **Track success**: Look for "Successfully removed container" messages
4. **No accumulation**: Verify container count stays stable over 48+ hours
5. **Docker health**: Monitor if "Read timed out" messages appear (may need more resources)

## Future Improvements

1. Consider adding exponential backoff for retries if cleanup fails
2. Add metrics/counters for failed cleanup attempts
3. Consider setting `auto_remove=True` when creating containers as additional safety
4. Monitor Docker daemon health if timeouts persist
