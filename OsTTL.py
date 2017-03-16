#!/usr/bin/python
# -*- coding: utf-8 -*-
# Soto Jimenez Jonathan
# Script que muestra el sistema operativo de la IP que se ingresa
# Modo de uso python OsTTL.py <ip>
# Un ejemplo de salida:
# root@kali:~/Desktop# python ttl.py 192.168.100.100
# No se ha encontrado tu sistema operativo
# root@kali:~/Desktop# python ttl.py 192.168.100.3
# Tu Sistema operativo es un linux

import sys, commands, os

os.system('clear')

if len(sys.argv)!=2:
	print("Uso: python OsTTL.py <ip>")
	sys.exit(1)
else:
	ttl = commands.getoutput("\nping -c1 " + sys.argv[1] + "| grep \"ttl\" | cut -d \" \" -f6")

	if (ttl == 'ttl=60'):
		print("Tu Sistema operativo es un AIX, Irix, MacOS 2.0.x")
	elif (ttl == 'ttl=64'):
		print("Tu Sistema operativo es un linux")
	elif (ttl == 'ttl=127' or ttl == 'ttl=128'):
		print("Tu Sistema operativo es un Windows")
	elif (ttl == 'ttl=154'):
		print("Tu Sistema operativo es Cisco")
	elif (ttl == 'ttl=255'):
		print("Tu Sistema operativo es un Solaris")
	else:
		print "No se ha encontrado tu sistema operativo"

	