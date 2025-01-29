from numba import cuda

print("Numba CUDA dostępna:", cuda.is_available())
print("Numba widzi GPU:", cuda.gpus.lst if cuda.is_available() else "Brak dostępnych GPU")
