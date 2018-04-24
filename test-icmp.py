from nat_fixture import config, nat44_31_simple_stand_namespaces
# from aw import AutomationWorkstation, Namespace
import pytest
from time import sleep


def test_icmp_dynamic_nat_echo_request_receive(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']

    # INSIDE

    inside.exec_command("ping 192.168.11.200 -c 5")
    sleep(3)

    # CHECK
    session_entries_count = nat.get_counters()["Session Entries"]
    assert session_entries_count == 1

    nat_translations_count = nat.get_counters_overall()["Translations"]
    assert nat_translations_count == 10
    sleep(60)

    session_entries_count = nat.get_counters()["Session Entries"]
    assert session_entries_count == 0


def test_icmp_hairpinning_nat_echo_request_receive(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']
    inside2_ip = "192.168.10.249"

    # NAT
    nat.nat_static_IP_to_IP(inside2_ip, "5.5.5.150")
    nat.nat_service_hairpinning()

    # INSIDE2

    inside2 = aw.create_namespace("inside2", "inside")
    inside2.add_ip(inside2_ip, "24")
    inside2.interface_up()
    inside2.exec_command("ip route add 5.5.5.0/24 via 192.168.10.1")

    # INSIDE
    inside.exec_command("ip route add 5.5.5.0/24 via 192.168.10.1")
    inside.exec_command("ping 5.5.5.150 -c 5")
    sleep(4)
    # CHECK

    session_entries_count = nat.get_counters()["Session Entries"]
    assert session_entries_count == 2

    nat_translations_count = nat.get_counters_overall()["Translations"]
    assert nat_translations_count == 20

    sleep(60)

    session_entries_count = nat.get_counters()["Session Entries"]
    assert session_entries_count == 0


def test_icmp_static_nat_echo_request_receive(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']
    external_ip = "5.5.5.150"

    # NAT

    nat.nat_static_IP_to_IP("192.168.10.200", external_ip)

    # INSIDE

    inside.exec_command("ping 192.168.11.200 -c 5")

    # CHECK

    session_entries_count = nat.get_counters()["Session Entries"]
    assert session_entries_count == 1

    # nat_translations_count = nat.get_counters_overall()["Translations"]
    # assert nat_translations_count == 20

    sessions_dict = nat.get_dict_session_entries()
    assert external_ip == sessions_dict[0]['external_ip']

    sleep(60)

    session_entries_count = nat.get_counters()["Session Entries"]
    assert session_entries_count == 0
