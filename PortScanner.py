#Jonathan Soto Jimenez
#Script que busca host vivos dentro de un rango a traves de hping3
#Modo de uso: Uso: PortScanner.py <ip> <puerto inicio> <puerto fin>
# Ejemplo de salida y modo de uso:
# root@kali:~/Desktop# python PortScanner.py 192.168.100.1 1 10
# [+] Conectando a  192.168.100.1  desde  1  a  10
# Port: 1 close
# Port: 2 close
# Port: 3 close
# Port: 4 close
# Port: 5 close
# Port: 6 close
# Port: 7 close
# Port: 8 close
# Port: 9 close
# Port: 10 close

import socket
import sys
import os

# Si no se han ingresado los argumentos necesarios no se iniciara el programa
if len(sys.argv) != 4:
    print ("[+] Uso: PortScanner.py <ip> <puerto inicio> <puerto fin>")
    sys.exit(1)
 
# Asignamos los argumentos a las variables
ip = sys.argv[1]
inicio = int(sys.argv[2])
fin = int(sys.argv[3])

# Checamos si la IP y el rango son correctos, si no, el programa se sale.
try:
    socket.inet_aton(ip)
    if (inicio <1 or fin>255 or inicio>fin):
    	raise Exception('Error en los argumentos')
except Exception as e:
    os.system('clear')
    print "Ingrese una ip y rango valido"
    sys.exit(1)

# Se crea la conexion y se prueba si un puerto esta abierto
print "[+] Conectando a ",ip," desde ",inicio," a ",fin
conexion = socket.socket()
for i in range(inicio, fin+1):
    try:
        conexion.connect( (ip, i) )
        print "Port: %s open" % i
    except:
        print "Port: %s close" % i

# Cerramos la conexion al finalizar
conexion.close()