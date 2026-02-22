"""Threads that manage data flow to/from containers.

This module implements bidirectional data proxying between clients and containers,
with configurable limits on data length and command count. Data is optionally
persisted to the database.
"""
import threading

from src import tables
from src.lazy_init import lazy_init
from src.logger import logger

class OneWayThread(threading.Thread):
    """Thread that proxies data in one direction between source and destination.

    Attributes:
        source: Source socket to read data from
        dest: Destination socket to write data to
        connection: Database connection record for this session
        container: Configuration dict for the honeypot container
        direction: Data flow direction ('request' or 'response')
        database: Database instance for persisting data
        length: Maximum bytes to transfer before stopping
        commands: Maximum number of commands (delimited lines) before stopping
        delimiters: Characters that delimit commands (default: newline, carriage return)
        shutdown_requested: Flag to signal thread shutdown
    """

    @lazy_init
    def __init__(self, source, dest, connection, container, direction, database):
        super().__init__()

        # Load configuration with direction-specific keys
        self.length = self.container.get(f'{self.direction}_length', 4096)
        self.commands = self.container.get(f'{self.direction}_commands', 10)
        self.delimiters = self.container.get(f'{self.direction}_delimiters', ['\n', '\r'])

        self.shutdown_requested = False

    def _read(self):
        """Read data from the source socket.

        Returns:
            Bytes read from the socket (up to 4096 bytes)
        """
        logger.debug('%s reading from: %s', self.direction, self.source)
        data = self.source.recv(4096)
        logger.debug('%s read: %s', self.direction, data)
        return data

    def _write(self, data):
        """Write data to the destination socket.

        Args:
            data: Bytes to send to the destination
        """
        logger.debug('%s sending to: %s', self.direction, self.dest)

        if self.direction == 'response':
            logger.debug('RADDR: %s', self.dest.getpeername())

        self.dest.sendall(data)

        logger.debug('%s sent: %s', self.direction, data)

    def _too_many_commands(self, data):
        """Check if the data contains too many commands.

        Commands are counted by looking for delimiter characters.
        Returns True if the command limit is exceeded.

        Args:
            data: Bytes to check for command delimiters

        Returns:
            True if command limit exceeded, False otherwise
        """
        if self.commands <= 0:
            return False

        sdata = str(data)
        # Count delimiters - use the maximum count across all delimiter types
        count = 0
        for delimiter in self.delimiters:
            count = max(count, sdata.count(delimiter))

        if count >= self.commands:
            logger.info('Command limit exceeded (%d >= %d), stopping', count, self.commands)
            return True

        return False

    def run(self):
        """Main thread execution loop - proxy data with limits.

        Reads data from source, writes to destination, and tracks total bytes.
        Stops when:
        - Connection closes
        - Length limit exceeded
        - Command limit exceeded
        - Shutdown requested
        - Exception occurs

        Optionally saves all transferred data to the database.
        """
        total = b''

        while True:
            try:
                data = self._read()
                if not data:
                    logger.debug('%s connection closed', self.direction)
                    break
                self._write(data)
            except Exception as exception:
                logger.debug('%s error: %s', self.direction, exception)
                break

            total += data

            # Check stopping conditions
            if self.shutdown_requested:
                logger.debug('%s shutdown requested', self.direction)
                break

            if self.length > 0 and len(total) >= self.length:
                logger.debug('%s length limit exceeded (%d >= %d)',
                           self.direction, len(total), self.length)
                break

            if self._too_many_commands(data):
                break

        # Save data to database if configured
        logger.debug('%s transfer complete: %d bytes (limit: %d)',
                    self.direction, len(total), self.length)

        save_key = f'{self.direction}_save'
        if self.container.get(save_key, False) and len(total) > 0:
            self.database.write(tables.Data(
                direction=self.direction,
                data=str(total),
                connection=self.connection
            ))

    def shutdown(self):
        """Request graceful shutdown of the data proxy thread.

        Called externally when HPotter is shutting down.
        Sets a flag that causes the main loop to terminate.
        """
        self.shutdown_requested = True
