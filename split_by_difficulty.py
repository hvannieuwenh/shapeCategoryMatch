import numpy as np
from utils import *

shape_set = 2
path_src = f'./shapes_{shape_set}/'
SC = np.loadtxt(path_src + 'SC.txt', dtype='f', delimiter=',')
D = distance_matrix(SC, SC)

N_categories = 2
N_stim = SC.shape[0]

diffs = split_diff(SC, N_categories)
cat_ranges = category_ranges(N_stim, N_categories)

path_dest = f'./stimuli/pack_shapes_{shape_set}/'

prototype_IDs = category_prototypes(D, cat_ranges)

for i, p in enumerate(prototype_IDs) :
    copy_shape(p, 0, i+1, path_src, path_dest)

for i, r in enumerate(cat_ranges):
    prototype_ID = prototype_IDs[i] + 1
    for ex in r[::2]:
        shape_ID = ex + 1
        diff_level = diffs[ex] + 1
        category_ID = i + 1

        dir_dest = path_dest + f'cat_{category_ID}/' + f'diff_{diff_level}/'

        if shape_ID != prototype_ID :
            copy_shape(shape_ID, diff_level, category_ID, path_src, dir_dest)
        