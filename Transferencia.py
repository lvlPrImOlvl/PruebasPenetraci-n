#Jonathan Soto Jimenez
#Script que realiza tranferencia de zona, si es posible
#Modo de uso: Uso: Transferencia.py <dominio>

import sys
import os
import subprocess

try:
    import dns.query
    import dns.resolver
    import dns.zone
except:
    print("El modulo de dnspython no esta instalado en el sistema, verifique y vuelva a intentar")
    sys.exit(1)

if len(sys.argv) != 2:
    sys.exit("python automatizacion.py dominio")

# Pasamos el argumento a la variable
dominio=sys.argv[1]

# Obtenemos el NS
ns = dns.resolver.query(dominio,"NS")
# Probaremos cada NS
for datos in ns:
    try:
        print("analizando "+str(datos)+"\n")
        command = "dig @"+str(datos)+ " axfr "+ dominio
        print subprocess.check_output(command,shell=True)
    except:
        print "Error en la transferencia de zona"

print "[+] Se ha acabado de analizar"