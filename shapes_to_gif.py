import numpy as np
from scipy.spatial import distance_matrix
import scipy.io as io

from utils import *

shape_set = 3
path_src = f'./shapes_{shape_set}/'
SC = np.loadtxt(path_src + 'SC.txt', dtype='f', delimiter=',')
D = distance_matrix(SC, SC)

N_categories = 2
N_stim = SC.shape[0]

diffs = split_diff(SC, N_categories)
cat_ranges = category_ranges(N_stim, N_categories)

path_dest = f'./stimuli/pack_noise_shapes_{shape_set}/'

name_mat = 'shape_set360'
SHAPES = io.loadmat(path_src + 'shapes.mat')[name_mat]

for i, r in enumerate(cat_ranges):
    for ex in r[::2]:
        shape_ID = ex + 1
        diff_level = diffs[ex] + 1
        category_ID = i + 1

        dir_dest = path_dest + f'cat_{category_ID}/' + f'diff_{diff_level}/'
        
        write_noise_movie(SHAPES, shape_ID, diff_level, category_ID, dir_dest, fps=8, duration=5.5)
