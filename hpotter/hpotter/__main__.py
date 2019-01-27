from hpotter.env import logger, shell_container
import hpotter.plugins
import importlib
import signal

def shutdown_servers(signum, frame):
    plugins_dict = hpotter.plugins.__dict__
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Stopping ' + plugin_name)
        plugin.stop_server()

    if shell_container:
        logger.info('Stopping shell container')
        shell_container.stop()
        logger.info('Removing shell container')
        shell_container.remove()
    exit()

if "__main__" == __name__:
    signal.signal(signal.SIGINT, shutdown_servers)

    plugins_dict = hpotter.plugins.__dict__
    for plugin_name in plugins_dict['__all__']:
        importlib.import_module('hpotter.plugins.' + plugin_name)
        plugin = plugins_dict[plugin_name]
        logger.info('Starting ' + plugin_name)
        plugin.start_server()
