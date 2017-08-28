import bluetooth
import os
import subprocess
import json

mypath="/bluetooth"

try: 
    os.makedirs(mypath)
except OSError:
    if not os.path.isdir(mypath):
        raise
os.chdir(mypath)

service_uuid = "00001101-0000-1000-8000-00805F9B34FB"

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

server_sock.bind(("",bluetooth.PORT_ANY))
server_sock.listen(1)

bluetooth.advertise_service(server_sock, "PerkyBlue", service_id = service_uuid,
                     service_classes=[bluetooth.SERIAL_PORT_CLASS],
                     profiles=[bluetooth.SERIAL_PORT_PROFILE])

print("awaiting RFCOMM connection on channel:1")

client_sock, address = server_sock.accept()
print "Accepted connection from ",address

try:
    while True:
       data = client_sock.recv(1024).strip()
       if len(data) == 0: 
		break
       else:
		print("received [%s]" % data)
		cmdlist=data.split(":")
		print cmdlist, type(cmdlist[0])
		if (cmdlist[0] == "GETFILE"):
			proc = subprocess.Popen(['obexftp','-b',address[0],'-c', '/PHONE_MEMORY/bluetooth','-g',cmdlist[1],'-o','/bluetooth' ], stdout=subprocess.PIPE)
			for line in proc.stdout.readlines():
    				print line.rstrip()
            		client_sock.sendall(json.dumps({"typeinfo": "result","value":"ok"}));
		elif (cmdlist[0] == "SENDFILE"):
			#proc = subprocess.Popen(['obexftp','-b',address[0],'-c', '/PHONE_MEMORY/bluetooth','-p',cmdlist[1],'-o','/PHONE_MEMORY/bluetooth' ], stdout=subprocess.PIPE)
			proc = subprocess.Popen(['ussp-push','--dev','hci0','--debug',address[0]+'@12',cmdlist[1], '/PHONE_MEMORY/bluetooth/'+cmdlist[1] ], stdout=subprocess.PIPE)

			for line in proc.stdout.readlines():
    				print line.rstrip()
            		client_sock.sendall(json.dumps({"typeinfo": "result","value":"ok"}));
		elif (cmdlist[0] == "LISTFILE"):
			onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
			filearray=""
            		for e in onlyfiles:
				filearray=filearray+'{"name":"'+str(e)+'"},'
			filearray=filearray[0:-1]
			filejson='{"typeinfo": "listfile","filename":['+filearray+']}'
			print filejson
			print(json.dumps(filejson));
            		client_sock.sendall(filejson)
except IOError:
    pass

print("disconnected")

client_sock.close()
server_sock.close()

print("all done")

