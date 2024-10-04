import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout
import serial.tools.list_ports
import serial
import threading
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.signal import butter, filtfilt
import numpy as np

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Principal()
    ventana.show()  # Mostrar la interfaz gráfica
    sys.exit(app.exec())
