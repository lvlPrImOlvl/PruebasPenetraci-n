#Jonathan Soto Jimenez
#Script que busca host vivos dentro de un rango a traves de hping3
#Modo de uso:
#python NetworkSweep.py
#Pedira IP, inicio y fin.
# Ejemplo de salida
# Ingresa la IP: 192.168.100.10
# Ingresa el numero de comienzo de la subred: 15
# Ingresa el numero en el que deseas acabar el escaneo: 20
# [*] El escaneo se esta realizando desde 192.168.100.15 hasta 192.168.100.20
# 192.168.100.15 esta activo
# [*] El escaneo ha durado 0:00:11.593122

#Importamos las bibliotecas necesarias
#Limpiar pantalla
import os
#Comprobar que la ip introducida es correcta sintaticamente
import socket
#Para salir del programa en caso de errores
import sys
#Para tomar el tiempo de la ejecucion del programa
from datetime import datetime
#Al iniciar limpiamos pantalla
os.system('clear')

#Mientras que no ingrese una ip valida, no saldra del ciclo
while(1):
    ip = raw_input("Ingresa la IP: ")
    try:
        socket.inet_aton(ip)
        break
    except Exception as e:
        os.system('clear')
        print "Ingrese una ip valida"

#Dividimos la ip
ipDividida = ip.split('.')
 
while(1):
    #Obtenemos inicio y fin
    try:
        red = ipDividida[0]+'.'+ipDividida[1]+'.'+ipDividida[2]+'.'
        comienzo = int(raw_input("Ingresa el numero de comienzo de la subred: "))
        fin = int(raw_input("Ingresa el numero en el que deseas acabar el escaneo: "))

        # Comprobacion de rango
        if (comienzo >= 1 and fin <= 255 and comienzo<fin):
            break
        else:
            print "Ingrese un rango de [INICIO-FINAL] 1-255 y el valor inicial no puede ser mayor al final"
    except:
        print "[!] Error en el procesamiento de la IP"
        sys.exit(1)

# Tomamos el tiempo inicial
tiempoInicio = datetime.now()

# Empezamos el escaneo
# Por cada ip que se genere de la base [ejemplo -> 192.168.100] y del rango de inicio a fin [ejemplo 1-250]
# Se realizara un hping3, si devuelve algo relacionado a TTL, es que el host esta vivo.
# Si no, mandamos la salida a null
print "[*] El escaneo se esta realizando desde" , red + str(comienzo) , "hasta" , red + str(fin)
for subred in range(comienzo, fin + 1):
    direccion = red + str(subred)
    response = os.popen("hping3 -1 -c 2 "+direccion + " 2> /dev/null")
    for line in response.readlines():
        if ("ttl" in line.lower()):
            print direccion,"esta activo"
            break

# Obtenemos tiempo final            
tiempoFinal = datetime.now()
tiempo = tiempoFinal - tiempoInicio
print "[*] El escaneo ha durado",tiempo
