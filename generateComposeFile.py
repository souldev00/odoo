#!/usr/bin/env python3
# encoding: utf-8

# generateComposeFile.py :
# AUTHOR: J.F.Gratton, Infra (jeanfrancois.gratton.partner@decathlon.com)
# DATE: 2022.10.19
# DESC: YAML compose file generator
# CURRENT VERSION: 4

# version   author      date        desc
# -------   ------      ----        ----
# 4         jfgratton   2022.11.09  http[s]_proxy are no longer ignored
# 3         jfgratton   2022.10.26  Completely trashed previous version to revert to the initial goal.
# 2         jfgratton   2022.10.24  added docker context files.
# 1         jfgratton   2022.10.19  initial version.


import argparse, os, sys, time

CAP_CPU=0.85
CAP_MEM=0.75
RESERV=0.50

# Timestamped backup of the current YAML file
def backupCurrentYamlFile():
    tstamp = time.strftime('%Y-%b-%d_%H:%M:%S')

    if os.path.exists('docker-backups') == False:
        os.mkdir('docker-backups')

    if os.path.exists('composeFile.yml'):
        os.rename('composeFile.yml', 'docker-backups/composeFile.yml.'+tstamp)

# All variables (be it a CLI parameter or the default values) get inserted in the YAML file here.
def injectVariables(cpulimit, cpureserve, memorylimit, memoryreserve):
    original = open('composeFile.yml', 'rt')
    wholefile = original.read()
    wholefile = wholefile.replace('___CPUCAP___', str(cpulimit))
    wholefile = wholefile.replace('___CPURESERV___', str(cpureserve))
    wholefile = wholefile.replace('___MEMORYCAP___', str(memorylimit))
    wholefile = wholefile.replace('___MEMORYRESERVATION___', str(memoryreserve))
    original.close()

    final = open('composeFile.yml', 'wt')
    final.write(wholefile)
    final.close()

# This is where we write the actual YAML file
def writeNewYamlFile():
    with open('composeFile.yml', 'w') as yf:
        yf.write("""\
services:
  db:
    image: postgres:12
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

  odoo:
    image: odoo:14
    depends_on:
      - db
    environment:
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
      - HTTP_PORT=${HTTP_PORT}
    volumes:
      - odoo-data:/var/lib/odoo
    ports:
      - 8069:8069
    deploy:
      resources:
        limits:
          cpus: '___CPUCAP___'
        reservations:
          cpus: '___CPURESERV___'

  nginx:
    image: nginx:latest
    ports:
      - 80:80
    volumes:
      - ./docker/etc/nginx/nginx.conf:/etc/nginx/nginx.conf
      - odoo-data:/var/lib/odoo
    depends_on:
      - odoo

volumes:
  odoo-data:
  odoo-db-data:

""")
        yf.close()

# Main method, entry point
def main(args):
    cpucount = os.cpu_count()
    system_memory = int(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024 ** 2))

    if cpucount == None:
        print("Unable to determine the number of CPUs. Aborting.")
        sys.exit(0)
    if args.cpulim == None:
        cpulimit = cpucount * CAP_CPU
    else:
        cpulimit = args.cpulim
    if args.cpures == None:
        cpureserve = cpucount * RESERV
    else:
        cpureserve = args.cpures
    if args.memlim == None:
        memorylimit = int(system_memory * CAP_MEM)
    else:
        memorylimit = args.memlim
    if args.memres == None:
        memoryreserve = int(system_memory * RESERV)
    else:
        memoryreserve = args.memres


    backupCurrentYamlFile()
    writeNewYamlFile()
    injectVariables(cpulimit, cpureserve, memorylimit, memoryreserve)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cpulim', '-c', help='Maximum number of allocated CPUs', nargs=1)
    parser.add_argument('--cpures', '-r', help='Minimum number of allocated CPUs', nargs=1)
    parser.add_argument('--memlim', '-m', help='Maximum allocated RAM, in MB', nargs=1)
    parser.add_argument('--memres', '-e', help='Minimum allocated RAM, in MB', nargs=1)
    args = parser.parse_args()

    main(args)

