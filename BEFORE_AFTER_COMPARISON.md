# Before & After: Container Cleanup Fixes

## SSH Container - run() Method

### ❌ BEFORE (Resource Leak)
```python
def run(self):
    client = None
    try:
        client = docker.from_env()
        # ... SSH server setup and channel handling ...
        self._bridge_channel(channel)
    except Exception as exc:
        logger.warning('SSHContainer error: %s', exc)
    finally:
        self._cleanup()
        # ❌ Docker client NEVER closed - resource leak!
```

### ✅ AFTER (Fixed)
```python
def run(self):
    client = None
    try:
        client = docker.from_env()
        # ... SSH server setup and channel handling ...
        self._bridge_channel(channel)
    except Exception as exc:
        logger.warning('SSHContainer error: %s', exc)
    finally:
        self._cleanup()
        if client:
            try:
                logger.debug("Closing docker client %s", client)
                client.close()  # ✓ Now properly closed
            except Exception as close_err:
                logger.debug('Error closing docker client: %s', close_err)
```

## SSH Container - _cleanup() Method

### ❌ BEFORE (Silent Errors)
```python
def _cleanup(self):
    if self.transport:
        try:
            self.transport.close()
        except Exception:
            pass
    if self.container:
        try:
            logger.info('Stopping SSH container %s', self.container.id[:12])
            self.container.stop()
            self.container.remove()
        except Exception as exc:
            logger.debug('Error stopping SSH container: %s', exc)  # ❌ DEBUG level - invisible!
    try:
        self.source.close()
    except Exception:
        pass
```

### ✅ AFTER (Visible Errors)
```python
def _cleanup(self):
    if self.transport:
        try:
            self.transport.close()
        except Exception:
            pass
    if self.container:
        try:
            logger.info('Stopping SSH container %s', self.container.id[:12])
            self.container.stop()
            logger.info('Removing SSH container %s', self.container.id[:12])  # ✓ Added explicit log
            self.container.remove()
        except Exception as exc:
            logger.warning('Error stopping/removing SSH container %s: %s',  # ✓ WARNING level
                          self.container.id[:12], exc)
    try:
        self.source.close()
    except Exception:
        pass
```

## Telnet Container - Same Pattern

The Telnet container (`telnet_container.py`) had **identical issues** and received the **same fixes**:

1. **Added client closure** in `run()` method's finally block
2. **Upgraded error logging** from DEBUG to WARNING in `_cleanup()`
3. **Added explicit "Removing" log message**

## Regular Container Class - Improved Safety

### ❌ BEFORE
```python
def _stop_and_remove(self):
    logger.debug(str(self.container.logs()))
    logger.info('Stopping: %s', self.container)
    self.container.stop()  # ❌ No error handling
    logger.info('Removing: %s', self.container)
    self.container.remove()  # ❌ No error handling
```

### ✅ AFTER
```python
def _stop_and_remove(self):
    logger.debug(str(self.container.logs()))
    logger.info('Stopping: %s', self.container)
    try:
        self.container.stop()
        logger.info('Removing: %s', self.container)
        self.container.remove()
    except Exception as exc:  # ✓ Now catches and logs errors
        logger.warning('Error stopping/removing container %s: %s',
                      self.container.id[:12], exc)
```

## Impact Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Docker client closure** | ❌ Never closed | ✓ Closed in finally |
| **Error visibility** | ❌ DEBUG level only | ✓ WARNING level |
| **Cleanup status** | ❌ Unclear | ✓ Explicit "Removing" logs |
| **Error handling** | ❌ Silent failures | ✓ Logged and visible |
| **Container accumulation** | ❌ Hundreds per run | ✓ Proper cleanup |

## Log Output Comparison

### ❌ BEFORE (Missing errors)
```
container:111 INFO - Stopping SSH container a1b2c3d4
container:111 INFO - Stopping SSH container a1b2c3d4
# ❌ No "Removing" message!
# ❌ No error messages (if cleanup fails)
```

### ✅ AFTER (Complete visibility)
```
container:111 INFO - Stopping SSH container a1b2c3d4
container:111 INFO - Removing SSH container a1b2c3d4
container:109 DEBUG - Closing docker client <docker.client.DockerClient object at 0x...>
# ✓ Shows removal happening
# ✓ Shows client cleanup
# ✓ If errors occur: WARNING - Error stopping/removing SSH container a1b2c3d4: ...
```

## What Changed

### Files Changed: 3
1. `src/ssh_container.py` - 14 lines added/modified
2. `src/telnet_container.py` - 14 lines added/modified  
3. `src/container.py` - 7 lines added/modified

### Core Pattern Applied
```python
# Always ensure resources are closed in finally blocks
if resource:
    try:
        resource.close()
    except Exception as err:
        logger.debug('Error closing resource: %s', err)
```

### Error Handling Pattern
```python
# Log failures at appropriate level (not DEBUG)
try:
    container.stop()
    container.remove()
except Exception as exc:
    logger.warning('Error: %s', exc)  # Visible in normal logs
```
