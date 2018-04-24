import pytest
from nat_fixture import config, nat44_31_simple_stand_namespaces
# from aw import AutomationWorkstation, Namespace
# from vcgnat.vcgnat31 import vcgnat
from time import sleep



def test_operational_logging_based_on_set_level_errors(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']

    # STEP 2

    nat.clear_syslog_file()
    nat.log_syslog.debugging()
    nat.log_syslog.errors()
    assert 'log syslog errors' in nat.show_running_config()
    sleep(5)
    # STEP 3

    syslog = nat.get_syslog_file()
    assert 'VTY: command: "log syslog errors" MATCH OK' in syslog
    assert 'VTY: #011ARG0: "errors"' in syslog


def test_operational_logging_based_on_set_level_informational(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']

    # STEP 2

    nat.clear_syslog_file()
    nat.log_syslog.debugging()
    nat.log_syslog.informational()
    assert 'log syslog informational' in nat.show_running_config()

    # STEP 3

    syslog = nat.get_syslog_file()
    assert 'VTY: command: "log syslog informational" MATCH OK' in syslog
    assert 'VTY: #011ARG0: "informational"' in syslog


def test_operational_logging_based_on_set_level_debugging(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    nat = nat44_31_simple_stand_namespaces['nat']

    # STEP 2

    nat.clear_syslog_file()
    nat.log_syslog.debugging()
    nat.log_syslog.debugging()
    assert 'log syslog' in nat.show_running_config()

    nat.show_nat_counters()
    nat.get_cpu()
    nat.show_nat_mapping()
    nat.show_nat_pcp()
    nat.show_nat_counters_overall()

    # STEP 3

    syslog = nat.get_syslog_file()
    assert 'VTY: command: "log syslog debugging" MATCH OK' in syslog
    assert 'VTY: #011ARG0: "debugging"' in syslog

    assert 'VTY: command: "show nat counters" MATCH OK' in syslog
    assert 'VTY: command: "show cpu" MATCH OK' in syslog
    assert 'VTY: command: "show nat mapping" MATCH OK' in syslog
    assert 'VTY: command: "show nat pcp" MATCH OK' in syslog
    assert 'VTY: command: "show nat counters overall" MATCH OK' in syslog


def test_operational_logging_based_on_set_level_warnings(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']

    # STEP 2

    nat.clear_syslog_file()
    nat.log_syslog.debugging()
    nat.log_syslog.warnings()
    assert 'log syslog warnings' in nat.show_running_config()

    # STEP 3

    syslog = nat.get_syslog_file()
    assert 'VTY: command: "log syslog warnings" MATCH OK' in syslog
    assert 'VTY: #011ARG0: "warnings"' in syslog


def test_operational_logging_on_side_server(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    nat = nat44_31_simple_stand_namespaces['nat']
    config = nat44_31_simple_stand_namespaces['config']

    # STEP 2

    nat.log_server(config['aw']['management_ip'], 514)
    assert 'log server {} {}'.format(config['aw']['management_ip'], 514) in nat.show_running_config()
    nat.log_syslog.debugging()

    inside.clear_syslog_file()
    nat.clear_syslog_file()

    # random commands for logging
    nat.show_nat_counters()
    nat.get_cpu()
    nat.show_nat_mapping()
    nat.show_nat_pcp()
    nat.show_nat_counters_overall()

    # STEP 3

    nat_log_list = nat.get_list_by_syslog_file()
    server_log_list = inside.get_syslog_file().splitlines()

    nat_log = nat.get_syslog_file()
    server_log = inside.get_syslog_file()

    assert 'VTY: command: "show nat counters" MATCH OK' in nat_log
    assert 'VTY: command: "show cpu" MATCH OK' in nat_log
    assert 'VTY: command: "show nat mapping" MATCH OK' in nat_log
    assert 'VTY: command: "show nat pcp" MATCH OK' in nat_log
    assert 'VTY: command: "show nat counters overall" MATCH OK' in nat_log

    assert 'VTY: command: "show nat counters" MATCH OK' in server_log
    assert 'VTY: command: "show cpu" MATCH OK' in server_log
    assert 'VTY: command: "show nat mapping" MATCH OK' in server_log
    assert 'VTY: command: "show nat pcp" MATCH OK' in server_log
    assert 'VTY: command: "show nat counters overall" MATCH OK' in server_log

    check = True
    for log in nat_log_list:
        if log not in server_log_list:
            check = False

    assert check
