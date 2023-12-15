import shutil
import os
import functools
import copy

import numpy as np
from scipy.spatial import distance_matrix
import imageio.v3 as iio
import imageio.v2 as iiov2
from pygifsicle import optimize

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.animation as animation

def category_ranges(N_stim, N_categories):
    cat_bounds = np.linspace(0, N_stim, N_categories + 1, dtype='i') 
    cat_ranges = np.empty(N_categories, dtype=np.ndarray)
    for i in range(0, N_categories):
        cat_ranges[i] = np.arange(cat_bounds[i], cat_bounds[i+1])
    
    return cat_ranges

def category_prototypes(D, cat_ranges):
    N_categories = len(cat_ranges)
    avg_dist = avg_dist_to_other_categories(D, cat_ranges)

    prototype_IDs = np.empty(N_categories, dtype=int)
    for i, r in enumerate(cat_ranges):
        idx = np.where(avg_dist == np.max(avg_dist[r]))[0]
        assert idx in r, f'Prototype appears to not belong to category {i}'
        prototype_IDs[i] = idx
    
    return prototype_IDs

def avg_dist_to_other_categories(D, cat_ranges):
    N_stim = D.shape[0]
    avg_dists = np.zeros(N_stim)

    for i in range(0, N_stim):
        other_cat_ranges = [r for r in cat_ranges if i not in r]
        avg_dists[i] = np.mean(D[i, other_cat_ranges])

    return avg_dists

def split_diff(SC, N_categories):
    D = distance_matrix(SC, SC)

    N_stim = SC.shape[0]
    N_diff_levels = 5

    cat_ranges = category_ranges(N_stim, N_categories)

    avg_dists = avg_dist_to_other_categories(D, cat_ranges)

    diffs = np.zeros(N_stim, dtype='i')
    c = 0
    for r in cat_ranges:
        cat_avgd = avg_dists[r]
        idxs = cat_avgd.argsort()[::-1] # sort by maximum average distance across other categories 
        idxs_diff = np.array_split(idxs, N_diff_levels)
        for j, dj in enumerate(idxs_diff):
            diffs[dj + c] = j
        c += len(r) 

    return diffs 

def copy_shape(shape_ID, diff_level, category_ID, path_src, path_dest):
    os.makedirs(path_dest, exist_ok=True)
    files = os.listdir(path_dest)
    c = sum([".png" in f for f in files])

    file_src = path_src + f'shape_{shape_ID}.png'
    file_dest =  path_dest + f'ex_{category_ID}_{diff_level}_{c+1}.png'

    shutil.copy(file_src, file_dest)

def get_shape(S, ID):
    return S[0, ID][0]

def animate(frame, polygon):
    polygon.set_xy(frame)

    return polygon

def write_shape_gif(S, shape_ID, prototype_ID, diff_level, category_ID, path_dest, duration=4, fps=15):
    N_frames = int(np.ceil(duration * fps))

    if np.abs(shape_ID - prototype_ID) >= N_frames :
        sgn = np.sign(prototype_ID - shape_ID)

        shapes = np.array([get_shape(S, i) for i in range(shape_ID, prototype_ID + sgn, sgn)])
        idxs = np.round(np.linspace(0, shapes.shape[0] - 1, N_frames, dtype='int'))
        frames = shapes[idxs]
    else :
        sgn = np.sign(prototype_ID - shape_ID)
        shapes = [get_shape(S, i) for i in range(shape_ID, prototype_ID + sgn, sgn)]

        N_interpolated = N_frames - len(shapes)
        N_intervals = len(shapes) - 1
        N_interpolated_per_interval = int(np.ceil(N_interpolated / N_intervals))
       
        N_remaining = N_interpolated
        frames = []
        for i in range(N_intervals) :
            shape = shapes[i]
            next_shape = shapes[i + 1]

            weights = np.linspace(0, 1, num = min(N_interpolated_per_interval, N_remaining) + 2)
            weights = weights[1:-1]
            frames.append(shape)
            for w in weights : 
                interp_shape = (1-w)*shape + w*next_shape
                frames.append(interp_shape)
                N_remaining -= 1
        frames.append(shapes[-1])
    
    fig, ax = plt.subplots(figsize=(8,8))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ax.set_facecolor('black')

    p = Polygon(frames[0], color='white')
    ax.add_patch(p)

    ani = animation.FuncAnimation(
        fig=fig, 
        func=functools.partial(animate, polygon=p), 
        frames=frames, 
        interval=1/fps,
        repeat=False
    )

    os.makedirs(path_dest, exist_ok=True)
    files = os.listdir(path_dest)
    c = sum([".gif" in f for f in files])
    filename = path_dest + f'ex_{category_ID}_{diff_level}_{c+1}.gif'

    ani.save(filename=filename, writer = "imagemagick", fps=fps, extra_args=["-loop","1"])
    optimize(filename)

def animate_noise(frame, noise):
    noise.set_array(frame)

    return noise

def write_noise_shape_gif(S, shape_ID, diff_level, category_ID, path_dest, duration=4, fps=15):
    N_frames = int(np.ceil(duration * fps))
    
    sz = (8,8)
    fig, ax = plt.subplots(figsize=sz)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ax.set_facecolor('black')

    shape = get_shape(S, shape_ID)
    p = Polygon(shape, color='white', zorder=0)
    ax.add_patch(p)

    row, col = sz[0]*100, sz[1]*100
    mean = 0
    var = 0.1
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(row,col))
    gauss = gauss.reshape(row,col)  
    
    frames = [np.zeros((row, col)) for i in range(N_frames)]
    thrs = np.linspace(-3*sigma, 1*sigma, N_frames)

    for (i,t) in enumerate(thrs) :
        D = np.copy(gauss)
        D[D < t] = np.nan
        frames[i] = D

    transp_cmp = copy.copy(plt.cm.get_cmap('gray')) 
    transp_cmp.set_bad(alpha=0)

    im = ax.imshow(frames[0], extent=(0,1,0,1), cmap=transp_cmp, zorder=10)

    ani = animation.FuncAnimation(
        fig=fig, 
        func=functools.partial(animate_noise, noise=im), 
        frames=frames, 
        interval=1/fps,
        repeat=False
    )

    os.makedirs(path_dest, exist_ok=True)
    files = os.listdir(path_dest)
    c = sum([".mp4" in f for f in files])
    filename = path_dest + f'ex_{category_ID}_{diff_level}_{c+1}.mp4'

    ani.save(filename=filename, writer = "ffmpeg", fps=fps)#, fps=fps, extra_args=["-loop","1"])
    plt.close()
    #optimize(filename)

def write_noise_gif(S, shape_ID, diff_level, category_ID, path_dest, duration=4, fps=15):
    N_frames = int(np.ceil(duration * fps))
    
    sz = (8,8)
    fig, ax = plt.subplots(figsize=sz)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ax.set_facecolor('black')

    shape = get_shape(S, shape_ID)
    p = Polygon(shape, color='white', zorder=0)
    ax.add_patch(p)

    row, col = sz[0]*100, sz[1]*100
    mean = 0
    var = 0.1
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(row,col))
    gauss = gauss.reshape(row,col)  
    
    frames = np.zeros((row, col) + (N_frames,))
    thrs = np.linspace(-3*sigma, 0.5*sigma, N_frames)

    for (i,t) in enumerate(thrs) :
        D = np.copy(gauss)
        D[D < t] = np.nan
        frames[:,:,i] = D

    transp_cmp = copy.copy(plt.cm.get_cmap('gray')) 
    transp_cmp.set_bad(alpha=0)

    im = ax.imshow(frames[:,:,0], extent=(0,1,0,1), cmap=transp_cmp, zorder=10)

    ani = animation.FuncAnimation(
        fig=fig, 
        func=functools.partial(animate_noise, noise=im), 
        frames=frames, 
        interval=1/fps,
        repeat=False
    )

    os.makedirs(path_dest, exist_ok=True)
    files = os.listdir(path_dest)
    c = sum([".gif" in f for f in files])
    filename = path_dest + f'ex_{category_ID}_{diff_level}_{c+1}.gif'

    ani.save(filename=filename, writer = "imagemagick", fps=fps, extra_args=["-loop","1"])
    optimize(filename)

def plot_shape(shape):
    sz = (8,8)
    fig, ax = plt.subplots(figsize=sz)

    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

    ax.set_facecolor('black')
    #ax.patch.set_alpha(0.0)

    p = Polygon(shape, color='white', zorder=0)
    ax.add_patch(p)

    row, col = sz[0]*100, sz[1]*100
    mean = 0
    var = 0.1
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(row,col))
    gauss = gauss.reshape(row,col)  
    
    gauss[gauss < -0.7] = np.nan
    my_cmap = copy.copy(plt.cm.get_cmap('gray')) # get a copy of the gray color map
    my_cmap.set_bad(alpha=0)

    plt.imshow(gauss, extent=(0,1,0,1), cmap=my_cmap, zorder=10)
                   
    plt.show()

