import re
import numpy
from datetime import datetime, time, timedelta
from math import cos, sin, atan2, sqrt, radians, degrees, acos

PRESTAMOS_SMALL = "prestamos_bici_small"
PRESTAMOS = "prestamos_bici_small"


def analizarEstaciones(nombre_archivo):
    cache = dict()
    with open(nombre_archivo + ".csv", 'r') as f:
        for linea in f.readlines():
            linea = linea.split(";")

            codigos = linea[3:5]

            for idx in range(len(codigos)):
                codigo = codigos[idx]

                # Funcion de busqueda regex para extraer la longitud y latitud
                coords = re.findall(
                    r"'longitude': '(.*\..*)', 'latitude': '(.*\..*)',", linea[7 + idx])
                lon, lat = coords[0]
                lon, lat = float(lon), float(lat)

                if codigo not in cache.keys():
                    cache[codigo] = {"ubicacion": [lat, lon], "veces_origen": int(
                        idx == 0), "veces_destino": int(idx == 1)}
                else:
                    cache[codigo]["veces_origen"] += int(idx == 0)
                    cache[codigo]["veces_destino"] += int(idx == 1)

    return cache


def diferenciaEnMinutos(fecha1, fecha2):
    formato = "%Y-%m-%dT%H:%M:%S"

    fecha1 = datetime.strptime(fecha1, formato)
    fecha2 = datetime.strptime(fecha2, formato)

    diferencia = fecha2 - fecha1
    # Conversion manual a minutos debido a que diferencia es un objeto deltatime
    minutes = (diferencia.total_seconds() % 3600) // 60

    return minutes


def analizarPrestamos(nombre_archivo):

    formato = "%Y-%m-%dT%H:%M:%S"
    id_prestamos = []
    data = []
    duraciones = []
    with open(nombre_archivo + '.csv', 'r') as f:
        for linea in f.readlines():
            linea = linea.split(';')

            id_prestamo = linea[0]

            duracion = diferenciaEnMinutos(linea[1], linea[2])
            duraciones.append(duracion)
            HoraInicio = datetime.strptime(linea[1], formato).hour
            pase = 1 * int(linea[6] == "Monthly Pass") + 2 * int(linea[6]
                                                                 == "Flex Pass") + 3 * int(linea[6] == "Walk-up")
            # Se desconoce la cantidad de viajes, por eso se opta por almacenar en una lista
            data.append([duracion, HoraInicio, pase])
    cache = numpy.transpose(numpy.array(data))  # Y convertirlo a un array
    return cache

# Funciones adicionales


def menu(opciones):
    times = 6
    print()
    print("*"*times, "MENU", "*"*times)
    for i, opc in enumerate(opciones):
        print(i + 1, opc)
    print()


def obtenerOpcion(opciones):
    valido = False
    while not valido:
        menu(opciones)
        opcion = input("Seleccione una opcion: ")
        if opcion.isnumeric() and (int(opcion) > 0 and int(opcion) < len(opciones) + 1):
            return int(opcion)
        else:
            print("Porfavor ingrese un numero que este dentro de las opciones\n")


def obtenerCentro(estaciones):

    x = 0
    y = 0
    z = 0
    n = len(estaciones.keys())
    mean_lat, mean_lon = 0, 0

    for estacion in estaciones.keys():
        lat, lon = estaciones[estacion]["ubicacion"]
        if lat != 0 and lon != 0:
            lat, lon = radians(lat), radians(lon)

            x += cos(lat) * cos(lon)
            y += cos(lat) * sin(lon)
            z += sin(lat)
        else:
            n -= 1

    x = x / n
    y = y / n
    z = z / n
    mean_lon = atan2(y, x)
    hipotenusa = sqrt(x * x + y * y)
    mean_lat = atan2(z, hipotenusa)

    mean_lat, mean_lon = round(degrees(mean_lat), 5), round(degrees(mean_lon), 7)

    return mean_lat, mean_lon


def obtenerNEstaciones(estaciones, n, origen = True, destino = True):

    lstEstaciones = []
    lstVisitas = []

    for estacion in estaciones.keys():
        visitas = estaciones[estacion]["veces_origen"]  * int(origen) + estaciones[estacion]["veces_destino"] * int(destino)
        lstEstaciones.append(estacion)
        lstVisitas.append(visitas)

    indices = numpy.argsort(lstVisitas)[:-(n + 1):-1]
    arrayEstaciones = numpy.array(lstEstaciones)[indices]
    arrayVisitas = numpy.array(lstVisitas)[indices]

    return arrayEstaciones, arrayVisitas

def distancia(lat1, lon1, lat2, lon2):
    return acos(sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lon2 - lon1))

def obtenerZoom(centro, estaciones):
    centro_lat, centro_lon = centro
    centro_lat, centro_lon = radians(centro_lat), radians(centro_lon)

    disctancias = []
    for estacion in estaciones.keys():
        lat,lon = estaciones[estacion]["ubicacion"] 
        lat, lon = radians(lat), radians(lon)

        disctancias.append(distancia(lat, lon, centro_lat, centro_lon))

    return numpy.mean(disctancias)
