# Autoras:
Mariana Garcia T
Sara Mariana Pinzon

# LABORATORIO-3
El propósito del presente laboratorio se basa en adquirir una señal EMG mediante un sistema de adquisición realizado en una interfaz en tiempo real, guardar los datos de cada contracción hasta haber llegado a la fatiga del músculo bicep en un archivo txt, y utilizar este mismo archivo para el procesamiento de los datos y determinar su fatiga mediante la mediana que se presenta en cada ventana de contracción en su espectro de frecuencia por cada contracción. 

## Procesamiento de la señal

Para realizar el procesamiento del archivo txt que fue obtenido en el sistema de adquisición, se realizó un código aparte llamado **Labtres_spyder**.

[![lib.png](https://i.postimg.cc/L8qf3D1R/lib.png)](https://postimg.cc/MnSvWy5r)

Utilizando estas librerías es posible cumplir con dicho objetivo del laboratorio, donde *matplotlib* es funcional para realizar las gráficas deseadas. *numpy* para realizar cálculos matemáticos e implementación de arreglos dentro del código. *scipy.signal* para la implementación de los filtros correspondientes para limpiar la señal EMG adquirida del ruido al que pudo estar sometida. Finalmente, se utilizó *scipy.fftpack* la cual es una librería funcional para realizar los cálculos respectivos de la transformada rápida de Fourier FFT requerido para realizar en análisis espectral de cada contracción.
