# Modulo de funciones varias
import network, time
# Funcion para conectar a WiFi
def FconnectWiFi(ssid: str, pwd: str, timeout: int = 10, verbose:bool = False) -> str:
    '''
    Esta función permite conectar a la red de WiFi especificado los parámetros siguientes:

        ssid: str       SSID de la red WiFi
        pwd: str        Password de conexión a la red
        timeout: int    Cantidad de veces que reintenta la conexion
        verbose: bool   Si muestra errores y display de progreso de la conexion
        
        Devuelve un string con los datos de conexión
    '''
    try:
        wlan=network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            if verbose:
                print ('Connecting to ' + ssid, end=' -> ')
            wlan.active(True)
            time.sleep(1)
            wlan.connect(ssid, pwd)
            tout=0
            while not wlan.isconnected() and tout < timeout:
                if verbose:
                    print(str(timeout-tout), end=',')
                time.sleep(1)
                tout+=1
        if wlan.isconnected():
            if verbose:
                print("\nWi-Fi Conectado. IP: ", wlan.ifconfig()[0])
            return wlan.ifconfig()
        else:
            if verbose:
                print('\nTimeout !!!!!!. Falló la conexión de Wi-Fi.\n')
            return ''
    except:
        if verbose:
            print('\nFalló desconocido en la conexión de Wi-Fi.\n')
        return ''
    
