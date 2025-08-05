# AgentDatimus

**AgentDatimus** generates Prometheus metrics based on a simple, time-based configuration file.
It's particularly useful for defining dynamic thresholds that change throughout the week, making your **Alertmanager** alerts more context-aware.

---

## Features

- Define Prometheus Gauge values by time slots during the week
- Configure default metric values outside defined periods
- Lightweight loop to update metrics regularly
- Simple INI-based configuration

---

## Configuration

### Agent Config (`agent.ini`)

```ini
[Agent]
default_value = 0
sleep_time = 30
metric_files = conf/config.ini
```


 - `default_value`: Value used when no time range matches.
 - `sleep_time`: Time interval (in seconds) between metric recomputations.
     The atomicity of the configuration being 1 minute, it's recommanded
     to stay between 30s to 60s.
 - `metric_files`: Path to the metrics definition file.

### Metrics config (`config.ini`)

Each metric is configured with one or more time slots and corresponding values:

```ini
[metrics]
metric_1 = fri 04:00;fri 05:00=8
            fri 09:00;fri 10:00=7
            fri 17:00;fri 18:00=3
            thu 16:00;thu 17:00=9
            sun 01:00;sun 02:00=7
```

Format :
```ini
<day start_time>;<day end_time>=<value>
```
Supported day values: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`.


It's also possible to add an optional `default_value` for all metrics in the configuration file and also add an optional `prefix` in a `Configuration` section that will prefix all metrics at once, as such :

```ini
[Configuration]
default_value=12
prefix=scope_1_

```

## Installation

```
$ git clone git@github.com:aprx/AgentDatimus.git
$ cd AgentDatimus
$ pip install .
$ agentdatimus -c /path/to/agent.ini

```
