Descripción

En el presente repositorio se encuentran los códigos en Python pertinentes al sistema de adquisición de una señal EMG (electromiografía) mediante una interfaz, junto con el código (en el mismo lenguaje) donde a partir de procesamiento de señales es posible determinar la si el músculo alcanzó la fatiga después de una serie de contracciones en repetición.

# LABORATORIO-3
El propósito del presente laboratorio se basa en adquirir una señal EMG mediante un sistema de adquisición realizado en una interfaz en tiempo real, guardar los datos de cada contracción hasta haber llegado a la fatiga del músculo bicep en un archivo txt, y utilizar este mismo archivo para el procesamiento de los datos y determinar su fatiga mediante la mediana que se presenta en cada ventana de contracción en su espectro de frecuencia por cada contracción.  Alguna de las líneas de código estarán marcadas con negrita a lo largo de la redacción de este readme.


## Sistema de adquisición
Para la adquisición de los datos correspondientes a cada contracción se realizó un codigo en python el cual aplicará los filtros digitales tratados más adelante y conectara con el código de arduino que estará enlazado con el sensor conectado en el bíceps  junto a esto también se verán reflejados los datos tomados por el sensor y los datos filtrados por medio de una interfaz gráfica que la cual tendrá el acceso a la coneccion serial con el sensor para dar inicio a la toma de datos usando a cada una de las siguientes librerías 

	import sys
	from PyQt6 import uic
	from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout
	import serial.tools.list_ports
	import serial
	import threading
	from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

**Libreria "sys":** Funciona como la librería estándar de python.

**Libreria "Pyqt6.iuc":**usada para los elementos qt esto hace parte de la interfaz gráfica que mostrará la señal obtenida del sensor y la señal filtrada.

**Libreria "serial.tools.list_ports:"**Esta es la encargada de la comunicación  serial.

class Principal(QMainWindow):
    def __init__(self):
        super(Principal, self).__init__()
        uic.loadUi("ecginterfaz1.ui", self)
        self.puertos_disponibles()
        self.ser = None
        self.connect.clicked.connect(self.conectar)
        self.data_grabados = []  # Almacena los datos grabados

        # Configuración de la gráfica de la señal cruda
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.senalEMG.setLayout(layout)

        # Configuración de la gráfica de la señal filtrada
        self.figA = Figure()
        self.axA = self.figA.add_subplot(111)
        self.canvasA = FigureCanvas(self.figA)
        layoutA = QVBoxLayout()
        layoutA.addWidget(self.canvasA)
        self.senalFiltrada.setLayout(layoutA)

        # Parámetros del filtro
        self.fs = 1000.0  # Frecuencia de muestreo (Hz)
        self.fc_low = 50.0  # Frecuencia de corte inferior (Hz)
        self.fc_high= 150.0 #frecuencia de corte superior
        self.w_low = self.fc_low / (self.fs / 2)  # Normalizar frecuencia de corte inferior
        self.w_high = self.fc_high / (self.fs / 2) 
        self.b, self.a = butter(4,  [self.w_low, self.w_high], btype='band')  # Crear filtro Butterworth de orden 4

Se inicia con la creación de la clase principal la cual estará conectada a la interfaz gráfica por Pqt6. se continua con la inicialización de las ventanas en la interfaz, seguido a esto se procede con el llamado de los puestos disponibles para la comunicación serial, se asigna el botón de conexión para empezar con la comunicación serial mediante el puerto seleccionado. para luego almacenar los datos adquiridos por el sensor para de esta forma proceder con las gráficas de la señal obtenida y llamando a la que será la grafica de la señal filtrada mediante el diseño de los parametros del filtros para ser aplicados en la señal cruda, para esto se realizo la normalización de las frecuencias de corte y se dividen por la frecuencia de muestreo para de esta forma obtener un filtro pasabanda encargado de filtrar lo mejor posible la señal eliminando ruido y datos innecesarios 


	  def puertos_disponibles(self):
        p = serial.tools.list_ports.comports()
        for port in p:
            self.puertos.addItem(port.device)

    def conectar(self):
        estado = self.connect.text()
        self.stop_event_ser = threading.Event()
        if estado == "CONECTAR":
            com = self.puertos.currentText()
            try:
                self.ser = serial.Serial(com, 115200)  # Conexión a 115200 bps
                self.hilo_ser = threading.Thread(target=self.grabar_datos)
                self.hilo_ser.start()
                print("Puerto serial conectado")
                self.connect.setText("DESCONECTAR")
            except serial.SerialException as e:
                print("Error en el puerto serial: ", e)
        else:
            if self.ser:
                self.ser.close()
            self.stop_event_ser.set()
            self.hilo_ser.join()
            print("Puerto serial desconectado")
            self.connect.setText("CONECTAR")
            self.actualizar_grafica()  # Actualiza la gráfica al desconectar
            self.filtrar_senal()

    def grabar_datos(self):
        while not self.stop_event_ser.is_set():
            if self.ser is not None and self.ser.is_open:
                try:
                    data = self.ser.readline().decode('utf-8').strip()
                    if data.replace('.', '', 1).isdigit():  # Verificar que los datos son válidos
                        value = float(data)
                        self.data_grabados.append(value)
                        print(f"Valor recibido: {value}")
                except serial.SerialException as e:
                    print(f"Error al leer del puerto serial: {e}")
                    break
        self.guardar_datos()

    def guardar_datos(self):
        with open('emg_data.txt', 'w') as file:
            for valor in self.data_grabados:
                file.write(f"{valor}\n")
        print(f"Datos guardados, último valor: {valor}")

    def filtrar_senal(self):
        if len(self.data_grabados) > 0:
            # Aplicar el filtro Butterworth a los datos grabados
            filtered_data = filtfilt(self.b, self.a, self.data_grabados)

            # Crear el eje de tiempo en milisegundos
            tiempo = np.arange(len(filtered_data)) * (1000.0 / self.fs)

            # Actualizar gráfica de señal filtrada
            self.axA.clear()
            self.axA.plot(tiempo, filtered_data, label="Señal Filtrada")
            self.axA.set_xlabel("Tiempo (ms)")  # Eje X en milisegundos
            self.axA.set_ylabel("Amplitud (V)")  # Eje Y en voltios
            self.axA.grid(True)
            self.axA.legend()
            self.canvasA.draw()  
            print("Gráfica de señal filtrada dibujada")

    def actualizar_grafica(self):
        if len(self.data_grabados) > 0:
            # Crear el eje de tiempo en milisegundos
            tiempo = np.arange(len(self.data_grabados)) * (1000.0 / self.fs)

            # Actualizar gráfica de señal cruda
            self.ax.clear()
            self.ax.plot(tiempo, self.data_grabados, label="Señal Capturada")

            # Configuración de la gráfica
            self.ax.set_title('Señal EMG Capturada')
            self.ax.set_xlabel('Tiempo (ms)')  # Eje X en milisegundos
            self.ax.set_ylabel('Voltaje (V)')  # Eje Y en voltios
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()

Teniendo en cuenta lo anterior se inicia con la definición de cada una de las funciones las cuales estarán relacionadas con la conexión del puerto serial y la captura de de los datos provenientes del sensor. con esto en mente se inicia con:

- La funcion **puertos_diponibles**: Encargados de dar la visualización de los puertos disponibles en el computador.

- **conectar**: Este maneja la conexión y desconexión del puerto serial.

- **grabar_datos**: Captura los datos desde el puerto serial y los envía a un bucle para después de la desconexión mostrar los datos guardados por medio del uso de un hilo 
- **filtrar_senal**: Se inicia con la implementación del filtro Butterworth definido anteriormente para aplicar el filtrado a la señal y después mediante **self.canvasA.draw()** redibujar la señal filtrada en la interfaz mostrando la en un nuevo widget

- **actualizar_grafica**: Con esto se realiza la correspondiente actualización de la señal con el fin de mostrar los datos guardados después de la desconexión del puerto serial 




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

Obteniendo así: 

*Señal con ventana Hanning aplicada para cada contracción*

[![hanning.png](https://i.postimg.cc/SKyKjzds/hanning.png)](https://postimg.cc/bZBPBrKc)

*Señal con ventana Hamming aplicada para cada contracción*

[![hamming.png](https://i.postimg.cc/zGNhSvpm/hamming.png)](https://postimg.cc/ykfW7Vwn)

### Aplicación de ventanas 

Para aplicar las ventanas primero que nada fue fundamental observar la señal EMG que está siendo filtrada, para así lograr colocar unos umbrales y así cada vez que superara ambos umbrales los contara como una contracción y se le aplicara a ella la ventana correspondiente.

Ejemplo del conteo de la contracción teniendo en cuenta los umbrales establecidos de acuerdo a lo observado por la señal filtrada. 

	def hanning_window(data, fs):
     windowed_signal = np.copy(data)
     umbral_inicio = 0.77
     umbral_fin = -0.77
     i = 0
	  while i < len(data):
         if data[i] > umbral_inicio:
             inicio_contraccion = i
             
             while i < len(data) and data[i] > umbral_fin:
                 i += 1
             
             fin_contraccion = i
             ancho_segmento = fin_contraccion - inicio_contraccion
             
             # Aplicar ventana de Hann
             segmento = data[inicio_contraccion:fin_contraccion]
             ventana_hann = windows.hann(ancho_segmento)
             segmento_windowed = segmento * ventana_hann
             ventanas.append(segmento_windowed)
             
             # Calcular FFT de la ventana
             N = ancho_segmento  # Número de puntos en la FFT para mayor resolución
             A = fft(segmento_windowed, N)
             freqs = np.fft.fftfreq(N, 1/fs)[:N // 2]  # Solo frecuencias positivas
             response = np.abs(A)[:N // 2]
             
             # Almacenar el tiempo promedio de la contracción para el eje X
             tiempo_promedio_contraccion = (inicio_contraccion + fin_contraccion) / 2 / fs
             tiempos_contracciones.append(tiempo_promedio_contraccion)
             
             # Calcular la frecuencia mediana y almacenar
             frecuencia_median = np.median(freqs)
             frecuencias_medianas.append(frecuencia_median)
             print(f'Contracción {len(frecuencias_medianas)}: Frecuencia mediana = {frecuencia_median:.2f} Hz')
             
             respuestas_fft.append(response)
             
             # Reemplazar el segmento original con el aplicado la ventana de Hann
             windowed_signal[inicio_contraccion:fin_contraccion] = segmento_windowed
         else:
             i += 1
     
     return windowed_signal, ventanas, respuestas_fft, tiempos_contracciones, frecuencias_medianas

Para que se relizara durante todo el tiempo de la toma de datos, se creó un vector el cual contuviera los datos de las ventanas aplicadas cad vez que hubiera una contracción llamado *ventanas*.

Para conocer el ancho del segmento, se utilizaron los contadores que se mencionaron al inicio que marcaban el inicio de la contracción una vez superado el umbral de 0.77 y el contador que marcaba el final de la contracción una vez superado el umbral de -0.77. 

Con el procedimiento realizado, las gráficas observadas y las ventanas aplicadas se puede determinar que a pesar de que al implementar la ventana hanning comienza a filtrar a partir desde el 0 mientras que la Hamming no, por esta razón se desea continuar con el procesamiento de la señal con la aplicación de las ventanas Hanning ya que provee un mayor suavizado a la señal EMG sin necesidad de perder información de mayor relevancia. 







