#Soto Jimenez Jonathan

import socket
import sys
if len(sys.argv) != 2:
        sys.exit("python SMTPEnum.py <ip>")

ip= sys.argv[1]
comando = 'vrfy'

usuario=raw_input("Introduce un usuario para validar: ")
try:
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	conn.connect((ip,25))
	banner = conn.recv(1024)
	print banner

	if '220' in banner:
		conn.send(comando+' '+usuario+'\n')
		result = conn.recv(1024)
		print result
		if '252' in result:
			print 'Usuario valido: ' + usuario
		else:
			print 'Usuario invalido: ' + usuario 
	conn.close()
except socket.timeout:
	print 'Tiempo de respuesta agotado: '+ip
except socket.error:
print 'Tiempo de respuesta agotado: '+ip