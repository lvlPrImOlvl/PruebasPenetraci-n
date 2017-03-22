#!/usr/bin/python
# -*- coding: utf-8 -*-
# Jonathan Soto JImenez
# Sniffer de trafico entrante y saliente
# Modo de uso: python sniffer.py <ip>
# Ejemplo de uso y salida:

import socket, sys
from struct import *
 
# Creacion del socket
try:
    s = socket.socket( socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))  
except socket.error , msg:
    print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 
# Recibiremos pquetes y los desempquetaremos para analizar cada parte importante
while True:
    packet = s.recvfrom(65565)
     
    # Obtenemos el pquete 
    packet = packet[0]
     
    # Tomamos los primeros 20 caracteres del paquete
    ip_header = packet[0:20]
     
    # Los desempaquetamos
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    
    # Obtrenemos los datos que queremos
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
     
    iph_length = ihl * 4
     
    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8]);
    d_addr = socket.inet_ntoa(iph[9]);
     
    print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
     
    tcp_header = packet[iph_length:iph_length+20]
     
    tcph = unpack('!HHLLBBHHH' , tcp_header)
     
    source_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
    window1 = tcph[5]
    window2 = tcph[6]    
    window3 = tcph[7]
     
    print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length) + ' Window1 : ' + str(window1) +' Window2 : ' + str(window2) +' Window3 : ' + str(window3)
     
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size
     
    #get data from the packet
    data = packet[h_size:]
     
    print 'Data : ' + data
    print