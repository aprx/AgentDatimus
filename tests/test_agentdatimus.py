#from datetime import datetime
import pytest

from agentdatimus import AgentDatimus
from configparser import MissingSectionHeaderError, NoSectionError, NoOptionError


def test_missing_file(tmp_path):
    """
    The configuration file does not exists
    """
    with pytest.raises(FileNotFoundError):
        AgentDatimus(f'{tmp_path}/nonexistant.ini')

def test_missing_agent_section(tmp_path):
    """
    Missing required configuration
    """
    with pytest.raises(MissingSectionHeaderError):
        conf_file = tmp_path / "agent.ini"
        conf_file.write_text("""
        default_value=2
        """)
        AgentDatimus(conf_file)
    with pytest.raises(NoSectionError):
        conf_file = tmp_path / "agent.ini"
        conf_file.write_text("""
        [smthelse]
        default_value=2
        """)
        AgentDatimus(conf_file)

def test_missing_metrics(tmp_path):
    """
    Missing metrics configuration file.
    """
    with pytest.raises(NoOptionError):
        conf_file = tmp_path / "agent.ini"
        conf_file.write_text("""
        [Agent]
        default_value=2
        """)
        AgentDatimus(conf_file)
