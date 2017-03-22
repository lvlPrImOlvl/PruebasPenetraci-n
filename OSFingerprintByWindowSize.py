#!/usr/bin/python
# -*- coding: utf-8 -*-
# Jonathan Soto JImenez
# Script que realiza un OSFingerprinting a traves del window size obtenido por medio de un sniffer
# Modo de uso: python OSFingerprintByWindowSize.py <ip>
# Ejemplo de uso y salida:
#root@kali:~/Desktop# python OSFingerprintByWindowSize.py 192.168.100.14
#Tu Sistema operativo es un Windows
# Referencia de los Window Size
# https://www.howtogeek.com/104337/hacker-geek-os-fingerprinting-with-ttl-and-tcp-window-sizes/


# Se importan para poder salir del programa si existe algun error y para usar el comando ping
import sys, commands
# Se importa para poder utilizar el socket
import socket
# Se importa para poder utilizar unpack
from struct import *

# Si no se ha ingresado argumento, no se ejecuta el programa y muestra su modo de uso.
if len(sys.argv) != 2:
	print("Uso: OSFingerprintByWindowSize.py <ip>")
else:
	#Se intenta crear un INET y STREAMing socket
	try:
	    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
	except socket.error , msg:
	    print 'No se ha podido crear el socket -> Codigo de error: ' + str(msg[0]) + ' Mensaje ' + msg[1]
	    sys.exit()

	# Se utiliza el comando ping para generar trtafico en la red hacia la ip victima
	commands.getoutput("ping -c1"+ sys.argv[1])

	# Obtenemos la salida del socket y la guardamos en packet
	packet = s.recvfrom(65565)
	     
    # Se obtiene una cadena apartir del paquete
	packet = packet[0]

    # Tomamos los primeros 20 caracteres de la cabecera IP
	ip_header = packet[0:20]

    # Los desempaquetamos para obtener una representación en una string
	iph = unpack('!BBHHHBBH4s4s' , ip_header)
    
    # Obtenemos la versión
	version_ihl = iph[0]
	version = version_ihl >> 4
	# Obtenemos IHL
	ihl = version_ihl & 0xF
    
    # Obtenemos la longitud de la cabecera   IP
	iph_length = ihl * 4

	# Obtenemos la cabecera de TCP (es donde esta el window size)
	tcp_header = packet[iph_length:iph_length+20]
     
    # Desempaquetamos nuevamente
	tcph = unpack('!HHLLBBHHH' , tcp_header)

	# Obtenemos el campo deseado
	windowSize = tcph[6]    
    
	# Comparamos con los diferentes window size que hay
	if (windowSize == 4128):
		print("Tu Sistema operativo es un IOS 12.4 (Cisco Router)")
	elif (windowSize == 5720):
		print("Tu Sistema operativo es un Google linux")
	elif (windowSize == 5840):
		print("Tu Sistema operativo es un Linux (Kernel 2.4 y 2.6)")
	elif (windowSize == 8192):
		print("Tu Sistema operativo es un Windows")
	elif (windowSize == 65535):
		print("Tu Sistema operativo es un Windows XP o FreeBSD")
	else:
		print "No se ha encontrado tu sistema operativo"