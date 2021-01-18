from funciones import *
import folium
import os
import webbrowser

opciones = ["Top 10 de las estaciones mas visitas",
            "Analisis horario", "Consulta tipo pase",
            "Mostrar top veinte de las estaciones en el mapa",
            "Salir"]

opcion = 0
nombre_archivo = "prestamos_bici"
estaciones = None

while opcion != len(opciones):

    opcion = obtenerOpcion(opciones)

    if opcion == 1:
        if estaciones == None:
            estaciones = analizarEstaciones(nombre_archivo)

        arrayEstaciones,arrayVisitas = obtenerNEstaciones(estaciones,10)

        print("\nTop 10 estaciones:")

        for i in range(len(arrayEstaciones)):
            print("Estacion " + arrayEstaciones[i] + ": " + str(arrayVisitas[i]) + " visitas")

    elif opcion == 2:
        prestamos = analizarPrestamos(nombre_archivo)

        maximo = numpy.max(prestamos[0,:])
        minimo = numpy.min(prestamos[0,:])
        promedio = numpy.mean(prestamos[0,:])

        print("\nDuracion maxima:", maximo, "minutos")
        print("Duracion minima:", minimo, "minutos")
        print("Duracion promedio:", round(promedio, 2), "minutos")


        unique, counts = numpy.unique(prestamos[1,:], return_counts=True)
        prestamos_conteo = dict(zip(unique, counts))

        indices = numpy.argsort(counts)[:-4:-1]
        print("\nHoras a las que se inician mas prestamos")
        print("{:<10} {:<10}".format("Horario", "#Prestamos"))
        for indice in indices:
            hora = unique[indice]
            numero_prestamos = counts[indice]

            hora_str = "0"*int(hora < 9) + str(int(hora)) + ":00"
            print("{:<10} {:<10}".format(hora_str, numero_prestamos))

    elif opcion == 3:
        pass
    
    elif opcion == 4:

        if estaciones == None:
            estaciones = analizarEstaciones(nombre_archivo)
        centro = obtenerCentro(estaciones)
        zoom = round(obtenerZoom(centro, estaciones) * 490)

        mapa = folium.Map(location=centro, zoom_start = zoom)

        arrayEstaciones,arrayVisitas = obtenerNEstaciones(estaciones,20, destino= False)

        for i in range(len(arrayEstaciones)):
            ubicacion = estaciones[arrayEstaciones[i]]["ubicacion"]
            folium.Marker(ubicacion,popup = "Estacion #" +  arrayEstaciones[i] + "\nPrestamos:" + str(arrayVisitas[i])).add_to(mapa)
        
        path = os.getcwd()

        print("\nMapa desplegado!")
        print("Mapa disponible en: "+ path + "/mapa.html")

        mapa.save("mapa.html")
        webbrowser.open_new("file://"+path+"\\mapa.html")

print("Programa finalizado")