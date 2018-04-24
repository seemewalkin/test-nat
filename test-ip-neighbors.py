from nat_fixture import config, nat44_31_simple_stand_namespaces
import pytest
# from  aw import AutomationWorkstation, Namespace
from time import sleep
import re


def test_wrong_macs_of_neighbors(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']

    # STEP 1

    nat.__exec_conf_command__("interface if0\ndescription inside\nexit\ninterface if1\ndescription outside\nexit\n")

    # STEP
    wrong_mac1 = "00:1A:69:1B:E8:01"
    wrong_mac2 = "00:1A:69:7F:B2:01"
    wrong_mac_neighbor1 = "ip neighbor 192.168.10.200 interface if0 mac 0:1a:69:1b:e8:1"
    wrong_mac_neighbor2 = "ip neighbor 192.168.11.200 interface if1 mac 0:1a:69:7f:b2:1"

    nat.__exec_conf_command__("{}\n".format(wrong_mac_neighbor1))
    nat.__exec_conf_command__("{}\n".format(wrong_mac_neighbor2))

    # STEP 3

    assert wrong_mac_neighbor1 in nat.__exec_command__("show run\n")
    assert wrong_mac_neighbor2 in nat.__exec_command__("show run\n")

    pattern1 = "192.168.10.200\s+Permanent\s+if0\s+{}".format(wrong_mac1)
    pattern2 = "192.168.11.200\s+Permanent\s+if1\s+{}".format(wrong_mac2)

    # STEP 4

    ip_neighbor = nat.__exec_command__("show ip neighbor\n")
    assert 1 == len(re.findall(pattern1, ip_neighbor))
    assert 1 == len(re.findall(pattern2, ip_neighbor))

    # STEP 5

    assert "Lost: 1 (100.00%)" in inside.exec_command("nping --icmp -c 1 192.168.11.200")

    # STEP 6

    nat.__exec_conf_command__("no {}\n".format(wrong_mac_neighbor1))
    nat.__exec_conf_command__("no {}\n".format(wrong_mac_neighbor2))

    # STEP 7

    assert "Lost: 0 (0.00%)" in inside.exec_command("nping --icmp -c 1 192.168.11.200")
    ping = inside.get_invoke_shell()
    ping.send("{} nping --icmp -c 1000 192.168.11.200\n".format(inside.get_netns_command()))
    sleep(3)

    # STEP 8
    assert 2 == nat.__exec_command__("show ip neighbor\n").count("Reachable")

    # STEP 9

    ping.close()
    sleep(50)
    # STEP 10

    assert 2 == nat.__exec_command__("show ip neighbor\n").count("Stale")


def test_corrects_macs_of_neighbors(nat44_31_simple_stand_namespaces):
    aw = nat44_31_simple_stand_namespaces['aw']
    inside = aw.namespaces.get("inside")
    outside = aw.namespaces.get("outside")
    nat = nat44_31_simple_stand_namespaces['nat']

    # STEP 1

    nat.__exec_conf_command__("interface if0\ndescription inside\nexit\ninterface if1\ndescription outside\nexit\n")

    # STEP 2

    correct_mac1 = inside.get_mac()
    correct_mac2 = outside.get_mac()
    correct_neighbor1 = "ip neighbor 192.168.10.200 interface if0 mac {}".format(correct_mac1)
    correct_neighbor2 = "ip neighbor 192.168.11.200 interface if1 mac {}".format(correct_mac2)

    nat.__exec_conf_command__("{}\n".format(correct_neighbor1))
    nat.__exec_conf_command__("{}\n".format(correct_neighbor2))

    # STEP 3

    assert 2 == nat.__exec_command__("show run\n").count("ip neighbor")

    # STEP 4

    pattern1 = "192.168.10.200\s+Permanent\s+if0\s+{}".format(correct_mac1.upper())
    pattern2 = "192.168.11.200\s+Permanent\s+if1\s+{}".format(correct_mac2.upper())

    ip_neighbor = nat.__exec_command__("show ip neighbor\n")
    assert 1 == len(re.findall(pattern1, ip_neighbor))
    assert 1 == len(re.findall(pattern2, ip_neighbor))

    # STEP 5

    assert "Lost: 0 (0.00%)" in inside.exec_command("nping --icmp -c 1 192.168.11.200")

    # STEP 6

    wrong_mac = "00:1a:69:7f:b2:01"
    uncorrect_neighbor3 = "ip neighbor 192.168.11.201 interface if1 mac {}".format(wrong_mac)
    nat.__exec_conf_command__("{}\n".format(uncorrect_neighbor3))

    # STEP 7

    pattern3 = "192.168.11.201\s+Permanent\s+if1\s+{}".format(wrong_mac.upper())
    assert 1 == len(re.findall(pattern3, nat.__exec_command__("show ip neighbor\n")))

    # STEP 8

    nat.__exec_conf_command__("no {}\n".format(uncorrect_neighbor3))

    # STEP 9

    pattern4 = "192.168.11.201\s+Failed\s+if1\s+{}".format(wrong_mac.upper())

    # STEP 10

    assert "Lost: 0 (0.00%)" in inside.exec_command("nping --icmp -c 1 192.168.11.200")
