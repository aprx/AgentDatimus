""" Main agentdatimus """

from argparse import ArgumentParser
import asyncio
from datetime import datetime
from configparser import ConfigParser, NoSectionError
import os

import logging

from prometheus_client import start_http_server, Gauge

from .weektimerangevalue import WeekTimeRangeValue

logger = logging.getLogger(__name__)

class AgentDatimus():
    """
    Load and Orchestrate metric to set.
    """
    def __init__(self, config_path):
        """
        Args:
         config_path (str): Path to agent.ini configuration file
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f'{config_path} does not exist')
        self.metrics = {}
        config = ConfigParser()
        config.read(config_path)

        self.load_agent_configuration(config)

        metric_files = config.get('Agent', 'metric_files')
        for metric_file in metric_files.split('\n'):
            if not os.path.exists(metric_file):
                raise FileNotFoundError(f'Could not find file {metric_file}')
            metric_conf = ConfigParser()
            metric_conf.read(metric_file)
            self.load_metric_file(metric_conf)

    def load_agent_configuration(self, config):
        """
          Load agentdate general configuration. From time betweens updates
          to metrics files
          Args :
              config (ConfigParser): valid config of Agent

        """
        if 'Agent' not in config.sections():
            raise NoSectionError('Missing agent section in agent configuration file')

        value = config.get('Agent', 'default_value', fallback=None)
        if value is not None:
            if not value.isdigit():
                raise ValueError('default_value in must be an integer')
            self.default_value = int(value)

        value = config.get('Agent', 'sleep_time', fallback=None)
        if value is not None:
            if not value.isdigit():
                raise ValueError('sleep time must be an integer')
            value = int(value)
            if value <= 0:
                raise ValueError('sleep time must be > 0')
            if value < 2:
                raise ValueError('Come on who needs this granularity ?')
            self.sleep_time = value


    def load_metric_file(self, configuration):
        """
        Load a metric configuration files:

        Args:
          configuration (ConfigParser): metrics configuration
        """
        default_value = None
        prefix = None
        value = configuration.get('Configuration', 'default_value',
                                  fallback=None)
        if value is not None:
            if not value.isdigit():
                raise ValueError('Configuration/default_value should be int')
            default_value = int(value)
        prefix = configuration.get('Configuration', 'prefix', fallback=None)

        if 'Metrics' not in configuration.sections():
            raise NoSectionError('Missing metric section in metric file')
        for field in configuration['Metrics']:
            timeranges = []
            name = field if prefix is None else f'{prefix}{field}'
            data = {
                'name': name,
                'gauge': Gauge(name, f'AgentDatimus {name}'),
            }
            if default_value is not None:
                data['default'] = default_value
            for line in configuration['Metrics'][field].split('\n'):
                line = line.strip()
                if not line:
                    continue
                timeranges.append(WeekTimeRangeValue.from_string(line))
            data['timeranges'] = timeranges
            self.add_metric(name, data)

    def add_metric(self, name, data):
        """
        Add a metric to the agent
        Args:
          name (str): Name of the metric
          data (dict): Configuration of the metric

        """
        self.metrics[name] = data

    def run_metric(self, metric, data, now):
        """
        Set the metric value according to now and data.
        """
        for tr in data['timeranges']:
            if tr.match(now):
                logger.debug('%s match timerange "%s", set to %s', metric, tr, tr.value)
                data['gauge'].set(tr.value)
                break
        else:
            value = data.get('default') if data.get('default') is not None else self.default_value
            logger.debug('No matching timerange set %s to default (%s)', metric, value)
            data['gauge'].set(value)

    async def run(self):
        """
        Run loop that get the current time and compute the current value
        to affect to each metric.
        """
        while True:
            now = datetime.now()
            for metric, data in self.metrics.items():
                self.run_metric(metric, data, now)
            end = datetime.now()
            logger.info('Computed %s metrics in %s', len(self.metrics), end - now)
            await asyncio.sleep(self.sleep_time)

def get_cl_parser():
    """
    Command line parser helper
    """
    parser = ArgumentParser(description='AgentDatimus')
    parser.add_argument('-c', '--config', help="Path to agent.ini configuration",
                        default='conf/agent.ini')
    parser.add_argument('-l', '--listen-port', help="Prometheus scrapping port",
                        default=8000, type=int)
    parser.add_argument('-d', '--debug', help="Debug flag", action="store_true",
                        default=False)
    return parser.parse_args()

def main():
    """
    entry point
    """
    args = get_cl_parser()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO
    )
    agent = AgentDatimus(args.config)
    start_http_server(args.listen_port)
    asyncio.run(agent.run())

if __name__ == "__main__":
    main()
