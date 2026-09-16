#!/usr/bin/env python3
import shutil
import sys

# Vérifie l'espace de la partition principale
total, used, free = shutil.disk_usage("/")
percent_used = (used / total) * 100

print(f"Utilisation disque actuelle : {percent_used:.2f}%")

if percent_used > 80:
    print("ATTENTION : Espace disque critique !")
    sys.exit(1)
else:
    sys.exit(0)
