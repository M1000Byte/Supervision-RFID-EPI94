from smartcard.System import readers
from smartcard.util import toHexString
from pylibftdi import BitBangDevice
from datetime import datetime
import requests
 # import csv (f.write fait la meme chose donc pas besoin sauf en cas de  manip complexe)
import time 
def enregistrer_acces(id_badge): 
    horodatage = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    with open('acces.csv','a') as f:
        f.write(f'{horodatage};{id_badge}\n')
    print(f'Accès enregistré pour le badge {id_badge} à {horodatage}')
def obtenir_uid(): 

    r = readers()
    if len(r) == 0:
        print('Aucun lecteur de carte détecté')
        return None

    try:
        connection = r[0].createConnection()
        connection.connect()
        get_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(get_uid)

        if sw1 == 0x90 and sw2 == 0x00:
            id_badge = toHexString(data)
            print(f'UID du badge est : {id_badge}')
            return id_badge
    except Exception as e:
        return None
    return None
def ouvrir_portail()   :
    try:
        with BitBangDevice() as dev:
            dev.direction = 0xFF    
    
            print("Activation de la porte 8")
            dev.port = 0x80  
    
            time.sleep(2)
    
            print("Fermeture...")
            dev.port = 0x00

    except Exception as e:
        print(f"Erreur de communication avec le portail: {e}")          

print('Lecture des badges en cours...')
while True:
    try:
        uid = obtenir_uid()
        if uid:
            enregistrer_acces(uid)
            ouvrir_portail()
            time.sleep(2)
    except Exception as e:
        pass
    time.sleep(0.5)