# -*- coding: utf-8 -*-
"""
PROCESAMIENTO DE SENAL EMG 

LABORATORIO 3

AUTORAS:
    
    MARIANA GARCIA T
    SARA MARIANA PINZON R
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter,lfilter,filtfilt,windows
from scipy.fftpack import fft, fftshift

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)  # Aplicar el filtro
    return y

def hanning_window(data, fs):
     windowed_signal = np.copy(data)
     umbral_inicio = 0.77
     umbral_fin = -0.77
     i = 0
     
     ventanas = []  # Para almacenar las ventanas aplicadas
     respuestas_fft = []  # Para almacenar las FFTs de las ventanas
     tiempos_contracciones = []  
     frecuencias_medianas = []  # Para almacenar las frecuencias medianas de cada ventana
     
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

def hamming_window(data):
    
    windowed_signal = np.copy(data) 
    umbral_inicio = 0.77
    umbral_fin = -0.77
    i=0
    
    
    
    while i<len(data):
        if data[i]>umbral_inicio:
            inicio_contraccion=i
                
            while i<len(data) and data[i]>umbral_fin:
                i+=1
            
            fin_contraccion=i
            
            ancho_segmento=fin_contraccion-inicio_contraccion
            
            segmento=data[inicio_contraccion:fin_contraccion]
            
            ventana = np.hamming(ancho_segmento)
            
            windowed_signal[inicio_contraccion:fin_contraccion]=segmento*ventana
            
        else:
            i+=1
            
    return windowed_signal



def main():
    
    emg=open('emg_data5.txt')
    emg_datas=emg.read()
    emg.close()
    
    emg_data = []  # Inicializar la lista vacía
    for valor in emg_datas.strip().split():
        emg_data.append(float(valor))  # Convertir cada valor a float y agregarlo a la lista

    
    fs = 1000.0
    lowcut = 50.0
    highcut = 450.0
    order=5


       # Filtrar la señal EMG
       
    emg_filtered = butter_bandpass_filter(emg_data, lowcut, highcut, fs, order)

     # Aplicar la ventanas
    emg_hanning, ventanas_hanning, respuestas_fft, tiempos_contracciones, frecuencias_medianas = hanning_window(emg_filtered, fs)
    emg_hamming = hamming_window(emg_filtered)

    # Crear el eje de tiempo basado en la cantidad de datos
    tiempo = np.arange(len(emg_data)) / fs
    
    
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
    
    # Gráfico se la senal con ventana Hanning 
    plt.figure(figsize=(12, 6))
    plt.plot(tiempo,emg_filtered, label='Señal EMG Filtrada', color='orange')
    plt.plot(tiempo, emg_hanning, label='Señal EMG con Ventana de Hanning', color='blue')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Señal EMG')
    plt.title('Comparación: Señal Filtrada vs. Ventana de Hanning')
    plt.legend()
    plt.grid()
    plt.show()
   
   # Gráfico de la señal con ventana Hamming
    plt.figure(figsize=(12, 6))
    plt.plot(tiempo, emg_filtered, label='Señal EMG Filtrada', color='orange')   
    plt.plot(tiempo, emg_hamming, label='Señal EMG con Ventana de Hamming', color='green')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Señal EMG con Ventana de Hamming')
    plt.title('Señal EMG con Ventana de Hamming')
    plt.grid()
    plt.legend()
    plt.show()
    
    # Graficar cada ventana
    for i, (response, freqs) in enumerate(zip(respuestas_fft, frecuencias_medianas)):
        plt.figure(figsize=(10, 5))
        plt.plot(response, label='FFT Contracción ' + str(i + 1))
        plt.title(f'FFT de la Contracción {i + 1}')
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Magnitud')
        plt.grid()
        plt.axvline(freqs, color='r', linestyle='--', label=f'Frecuencia Mediana: {freqs:.2f} Hz')
        plt.legend()
        plt.show()
    
if __name__ == "__main__":
    main()    