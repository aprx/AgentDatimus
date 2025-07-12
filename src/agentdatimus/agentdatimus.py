#!/usr/bin/env python3

from argparse import ArgumentParser
import asyncio
from datetime import datetime
from configparser import ConfigParser
import sys

from prometheus_client import start_http_server, Gauge

from .weektimerangevalue import WeekTimeRangeValue

class AgentDatimus():

    def __init__(self, config_path):
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
        self.metrics[name] = data

    async def run(self):
        while True:
            now = datetime.now()
            for metric, data in self.metrics.items():
                for tr in data['timeranges']:
                    if tr.match(now):
                        data['gauge'].set(tr.value)
                        break
                else:
                    data['gauge'].set(0)
            end = datetime.now()
            print(f'computed {len(self.metrics)} in {end - now}')
            await asyncio.sleep(self.sleep_time)

def get_cl_parser():
    parser = ArgumentParser(description='AgentDatimus')
    parser.add_argument('-c', '--config', help="Path to agent.ini configuration",
                        default='conf/agent.ini')
    parser.add_argument('-l', '--listen-port', help="Prometheus scrapping port",
                        default=8000, type=int)
    return parser.parse_args()

def main():
    args = get_cl_parser()
    agent = AgentDatimus(args.config)
    start_http_server(args.listen_port)
    asyncio.run(agent.run())

if __name__ == "__main__":
    main()
