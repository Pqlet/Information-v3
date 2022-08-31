import numpy as np
from scipy.special import ndtr
from .dependent_norm import multivariate_normal_from_MI

def normal_to_uniform(X):
    """
    Гауссов случайный вектор с единичными дисперсиями в равномерное
    распределение на [0; 1]^dim.
    
    Параметры
    ---------
    X : array
        Выборка из многомерного нормального распределения размерности (N,dim)
    """

    return ndtr(X)


def normal_to_segment(X, min_length):
    """
    Гауссов случайный вектор с единичными дисперсиями в координаты концов отрезка.
    Координаты концов распределены равномерно с учётом необходимости сохранения порядка.
    
    Параметры
    ---------
    X : array
        Выборка из многомерного нормального распределения размерности (N,2)
    min_length : float
        Минимальная длина отрезка.
    """

    assert len(X.shape) == 2
    assert X.shape[1] == 2
    assert min_length < 1.0
    n_samples = X.shape[0]

    # Получение равномерно распределённых сэмплов.
    coords = normal_to_uniform(X)

    # Первое число - координата левого конца.
    # Она должна быть распределена линейно от нуля до 1.0 - min_length
    coords[:,0] = (1.0 - min_length) * (1.0 - np.sqrt(1.0 - coords[:,0]))

    # Последнее число - координата правого конца.
    # При фиксированной первой координате она должна быть распределена
    # равномерно от координаты левого конца плюс min_length до 1.
    coords[:,1] *= 1.0 - coords[:,0] - min_length
    coords[:,1] += coords[:,0] + min_length

    return coords


def normal_to_rectangle_coords(X, min_width=0.0, max_width=1.0, min_height=0.0, max_height=1.0):
    """
    Гауссов случайный вектор с единичными дисперсиями в координаты точек прямоугольника.
    Координаты точек распределены равномерно с учётом необходимости сохранения порядка.
    
    Параметры
    ---------
    X : array
        Выборка из многомерного нормального распределения размерности (N,4)
    min_width : float
        Минимальная ширина прямоугольника.
    max_width : float
        Максимальная ширина прямоугольника.
    min_height : float
        Минимальная высота прямоугольника.
    max_height : float
        Максимальная высота прямоугольника.
    """

    assert len(X.shape) == 2
    assert X.shape[1] == 4

    coords = np.zeros_like(X)
    coords[:,0:2] = normal_to_segment(X[:,0:2], min_width / max_width) * max_width
    coords[:,2:4] = normal_to_segment(X[:,2:4], min_height / max_height) * max_height

    return coords


def rectangle_coords_to_rectangles(coords, img_width, img_height):
    """
    Координаты углов прямоугольников в изображения прямоугольников.
    
    Параметры
    ---------
    coords : array
        Выборка координат прямоугольников размерности (N,4)
    img_width : float
        Ширина изображения.
    img_height : float
        Высота изображения.
    """

    assert len(coords.shape) == 2
    assert coords.shape[1] == 4
    n_samples = coords.shape[0]

    # Непосредственная генерация прямоугольников.
    images = np.zeros((n_samples, img_width, img_height))
    for sample_index in range(n_samples):
        # Преобразование должно быть хотя бы кусочно-гладким.
        # Для этого каждый пиксель закрашиваем настолько, сколько в нём закрыто площади.
        floor_coords = np.floor(coords[sample_index]).astype(int)

        # Не самый оптимальный способ. Стоит переделать хотя бы заливку.
        for x_index in range(floor_coords[0], floor_coords[1] + 1):
            for y_index in range(floor_coords[2], floor_coords[3] + 1):
                dx = min(coords[sample_index][1], x_index + 1) - max(coords[sample_index][0], x_index)
                dy = min(coords[sample_index][3], y_index + 1) - max(coords[sample_index][2], y_index)

                images[sample_index][x_index][y_index] = dx * dy

    return images