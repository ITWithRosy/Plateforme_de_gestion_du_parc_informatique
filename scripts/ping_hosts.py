#!/usr/bin/env python3
import subprocess
import sys

# Liste des IPs  des equipements
HOSTS = ["192.168.1.1", "192.168.10.5", "192.168.10.11"]

echecs = 0
for host in HOSTS:
    res = subprocess.run(["ping", "-c", "1", "-W", "2", host], stdout=subprocess.DEVNULL)
    if res.returncode != 0:
        print(f"ALERTE : Équipement inatteignable -> {host}")
        echecs += 1

if echecs == 0:
    print("Tous les équipements répondent au ping.")
    sys.exit(0)
else:
    sys.exit(1)
