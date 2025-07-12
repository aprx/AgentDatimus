""" Main agentdatimus """

from argparse import ArgumentParser
import asyncio
from datetime import datetime
from configparser import ConfigParser

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
        self.metrics = {}
        config = ConfigParser()
        config.read(config_path)
        self.default_value = int(config['Agent']['default_value'])
        self.sleep_time = int(config['Agent']['sleep_time'])

        metric_files = config['Agent']['metric_files']
        for metric_file in metric_files.split('\n'):
            metric_conf = ConfigParser()
            metric_conf.read(metric_file)
            self.load_metric_file(metric_conf)

    def load_metric_file(self, configuration):
        """
        Load a metric configuration files:

        Args:
          configuration (ConfigParser): metrics configuration
        """
        for field in configuration['metrics']:
            timeranges = []
            data = {
                'name': field,
                'gauge': Gauge(field, f'AgentDatimus {field}'),
            }
            for line in configuration['metrics'][field].split('\n'):
                line = line.strip()
                if not line:
                    continue
                timeranges.append(WeekTimeRangeValue.from_string(line))
            data['timeranges'] = timeranges
            self.add_metric(field, data)

    def add_metric(self, name, data):
        """
        Add a metric to the agent
        Args:
          name (str): Name of the metric
          data (dict): Configuration of the metric

        """
        self.metrics[name] = data

    async def run(self):
        """
        run loop that set the metric when the
        current time match a configured timerange.
        """
        while True:
            now = datetime.now()
            for metric, data in self.metrics.items():
                for tr in data['timeranges']:
                    if tr.match(now):
                        logger.debug('%s match timerange "%s", set to %s', metric, tr, tr.value)
                        data['gauge'].set(tr.value)
                        break
                else:
                    logger.debug('No matching timerange set %s to default', metric)
                    data['gauge'].set(0)
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
    parser.add_argument('-d', '--debug', help="Debug ", action="store_true",
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
