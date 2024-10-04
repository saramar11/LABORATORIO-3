Descripción

En el presente repositorio se encuentran los códigos en Python pertinentes al sistema de adquisición de una señal EMG (electromiografía) mediante una interfaz, junto con el código (en el mismo lenguaje) donde a partir de procesamiento de señales es posible determinar la si el músculo alcanzó la fatiga después de una serie de contracciones en repetición.

# LABORATORIO-3
El propósito del presente laboratorio se basa en adquirir una señal EMG mediante un sistema de adquisición realizado en una interfaz en tiempo real, guardar los datos de cada contracción hasta haber llegado a la fatiga del músculo bicep en un archivo txt, y utilizar este mismo archivo para el procesamiento de los datos y determinar su fatiga mediante la mediana que se presenta en cada ventana de contracción en su espectro de frecuencia por cada contracción.  Alguna de las líneas de código estarán marcadas con negrita a lo largo de la redacción de este readme.


## Sistema de adquisición


## Procesamiento de la señal 

Para realizar el procesamiento del archivo txt que fue obtenido en el sistema de adquisición, se realizó un código aparte llamado **Labtres_spyder**.


	import matplotlib.pyplot as plt
	import numpy as np
	from scipy.signal import butter,lfilter, windows
	from scipy.fftpack import fft**



Utilizando estas librerías es posible cumplir con dicho objetivo del laboratorio, donde *matplotlib* es funcional para realizar las gráficas deseadas. *numpy* para realizar cálculos matemáticos e implementación de arreglos dentro del código. *scipy.signal* para la implementación de los filtros correspondientes para limpiar la señal EMG adquirida del ruido al que pudo estar sometida. Finalmente, se utilizó *scipy.fftpack* la cual es una librería funcional para realizar los cálculos respectivos de la transformada rápida de Fourier FFT requerido para realizar en análisis espectral de cada contracción.

## def main()

Este código fue organizado mediante funciones, donde la principal es la función llamada main (de la misma forma en como funciona en c + +) en la cual se pretende que sea la base principal del código y se haga el llamado de las demás funciones que sean necesarias a lo largo de él. Para cumplir con este propósito, se debe colocar las siguientes líneas al final del código:

	if __name__ == "__main__":
    main()    
Inicialmente en el main, se debe realizar la lectura del archivo txt que fue obtenido del sistema de adquisición.

	emg=open('emg_data5.txt')
    emg_datas=emg.read()
    emg.close()

    emg_data = []  # Inicializar la lista vacía
    for valor in emg_datas.strip().split():
        emg_data.append(float(valor))  # Convertir cada valor a float y agregarlo a la lista

 Mediante estas líneas lo que se está haciendo es reconocer al archivo llamado *emg_data5.txt* siendo este el archivo que contiene a los datos del EMG para que sea leído. Es importante que este archivo  se encuentre en la misma carpeta en la que está guardado el código de procesamiento de la señal de Python para que pueda ser reconocido. Se inicializar un vector llamado *emg_data[]* en donde se estarán guardando los datos de archivos pero el txt contiene los archivos en un formato string, sin embargo para realizar los cálculos pertinentes se necesita que los valores se encuentren en formato float, y se van almacenando en el vector mencionado al inicio.

 	fs = 1000.0
    lowcut = 50.0
    highcut = 450.0
    order = 5

Teniendo en cuenta a la bibliografía, para lograr filtrar una señal EMG se debe realizar un filtro BandPass, en otras palabras un filtro de frecuencias pasa altas con una frecuencia de corte en 50 Hz con un filtro pasa bajos con frecuencia de corte de 500 Hz. Esto con el fin de que la señal original recupere únicamente la señal que se encuentre entre este rango de frecuencias ya que según la bibliografía es donde se encuentra el canal de información de una señal de EMG. Se utiliza un valor menor a la frecuencia de corte superior para que pueda cumplir los parámetros de frecuencia natural del filtro con respecto a la señal. Debido a esto para cumplir con el teorema de nyquist, la frecuencia de muestreo debe ser 2 veces la frecuencia maxima que se esté tomando, es decir 500 Hz, por esta razón *fs=1000*.  Así mismo se estipulo que el orden del filtro fuera de 5 ya que con este se puede obtener una pendiente más pronunciada en las frecuencias de corte.

 
	# Filtrar la señal EMG
    emg_filtered = butter_bandpass_filter(emg_data, lowcut, highcut, fs, order)

Posterior a esto, se realiza el llamado a la definición del filtro tipo butterworth bandpass en la cual se toma en arreglo unidimensional que contiene a los valores de la señal EMG originales, junto con las frecuencias de corte, el orden del filtro y la frecuencia de muestreo y se envía a esta definición la cual se estará mencionando más adelante.

Una vez con la señal filtrada se procede a realizar el aventanamiento de cada contracción, con esto en el main se llama a la definición de *hanning_window* y * hamming_window* con el fin de poder graficarlas con respecto a la señal filtrada original observando la forma en la que se suaviza la señal usando estas diferentes técnicas. 

	 # Aplicar la ventanas
    emg_hanning, ventanas_hanning, respuestas_fft, tiempos_contracciones, frecuencias_medianas = hanning_window(emg_filtered, fs)
    emg_hamming = hamming_window(emg_filtered)

Finamente, para lograr graficar de debe realizar un vector que sea de tiempo el cual tenga la misma longitud de la señal filtrada para utilizarlo en el plot de las gráficas:

    # Crear el eje de tiempo basado en la cantidad de datos
    tiempo = np.arange(len(emg_data)) / fs

En esta parte final de la definición del main se procedió a hacer las gráficas pertinentes para el análisis de este procesamiento.

Inicialmente se muestra un subplot en el cual se encuentra la gráfica que contiene los datos originales del archivo txt de la señal que fue adquirida previamente en el código ya mencionado mediante el siguiente código.

 	#Gráfico de la senal original
    plt.subplot(2,1,1)
    plt.plot(tiempo, emg_data, label='Señal EMG Original')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Señal EMG')
    plt.title('Señal EMG Original')
    plt.grid()

    
    # Gráfico de la señal filtrada
    plt.subplot(2,1,2)
    plt.plot(tiempo, emg_filtered, label='Señal EMG Filtrada', color='orange')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Señal EMG Filtrada')
    plt.title('Señal EMG Filtrada')
    plt.grid()
    plt.tight_layout()
    plt.show()

Obteniendo así la siguiente imagen.

[![Senal-Originaly-Filtrada.png](https://i.postimg.cc/LszzFfX8/Senal-Originaly-Filtrada.png)](https://postimg.cc/SXxXWnCB)

Posterior a esto se grafican una superposición entre la señal filtrada con la señal con las ventanas hamming y hanning, esto con el fin de observar y comparar la forma en la que se suaviza la señal y cual conviene mas para lograr un balance entre pérdida de información con limpieza de señal.





