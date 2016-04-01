#!/usr/bin/env python
import argparse
import nmap
from snimpy.manager import Manager as M
from snimpy.manager import load
import csv


def read_hosts(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines


def scan(nm):
    devices = []
    for host in nm.all_hosts():
        device = {}
        device['name'] = host
        device['state'] = nm[host].state()

        for proto in nm[host].all_protocols():
            device['ssh'] = nm[host][proto][22]['state']

        snmp = have_snmp(str(host))
        if snmp:
            device['snmp'] = 'open'
        else:
            device['snmp'] = 'closed'

        devices.append(device)

    return devices


def have_snmp(host):
    load("SNMPv2-MIB")
    try:
        m = M(host=host, community="public", version=2)
        if m.sysName is not None:
            snmp = True
    except:
        snmp = False
    return snmp


def write_to_csv(devices, filename):
    filename = filename.split("/")[0].replace(".", "_") + ".csv"
    with open(filename, 'wb') as discover_file:
        fieldnames = ["name", "state", "snmp", "ssh"]
        writer = csv.DictWriter(discover_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(devices)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discover info of network' +
                                     'devices.')
    parser.add_argument('inputfile', help='file with hosts to scan')
    parser.add_argument('outputfile', help='csv file to write devices info')

    args = parser.parse_args()

    hosts_to_scan = read_hosts(args.inputfile)

    hosts_str = " ".join(hosts_to_scan)

    # Scan hosts
    nm = nmap.PortScanner()
    nm.scan(hosts_str, '22')

    devices = scan(nm)

    write_to_csv(devices, args.outputfile)
