# coding=utf-8

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def image_labels_grid(n_row, n_col, image_data, fig_dims=(12,8), 
                      plot_style='seaborn-white', width_space=0.4, height_space=0.1,
                      save_fig=None):
    '''
    Plots random images with labels for a dataset with methods __len__ & __getitem__
    (Two values for each index: an image and its label)
    '''
    num_show = n_row * n_col
    assert len(image_data) >= num_show, 'Number of images should be more than n_row*n_col'
    show_indices = np.random.randint(low=0, high=len(image_data), 
                                         size=(n_row, n_col))
    plt.style.use(plot_style)    
    fig,ax = plt.subplots(n_row, n_col, sharex=False, sharey=False, squeeze=False, 
                          figsize=fig_dims)
    _ = [a.axis('off') for a in ax.ravel()]
    fig.subplots_adjust(hspace=height_space, wspace=width_space)
    for r in range(n_row):
        for c in range(n_col):
            img = image_data[show_indices[r,c]][0]
            if isinstance(img, (str,)):
                img = plt.imread(img)
            ax[r, c].imshow(img)
            ax[r, c].set_title('Label: ' + str(image_data[show_indices[r,c]][1]))
    if save_fig:
        plt.savefig(save_fig)
    plt.show()
    
    
def plot_learning_curve(history, metrics=['loss','accuracy'], train=True, val=True,
                        grid=(1,2), fig_shape=(12,4), plot_style='fivethirtyeight', 
                        save_to=None):
    '''
    Plots learning curves both for train and validation
    for a specified list of metrics[i]ics
    -------
    Params:
        history: either pd.DataFrame (columns as metrics) or dict (keys as columns)
        metrics: columns/keys without 'train'/'val' prefix to plot
        train: True if plot train metrics
        val: True if plot val metrics
    -------
    '''
    plt.style.use(plot_style)
    fig,ax = plt.subplots(grid[0], grid[1], sharex=False, sharey=False, figsize=fig_shape)
    for i in range(grid[0]*grid[1]):    
        row = i // grid[1]
        col = i % grid[1]
        if grid[0] > 1:
            pos = (row, col)
        else:
            pos = (col,)
        if i >= len(metrics):
            fig.delaxes(ax[pos])
            break
        ax[pos].set_title('{} curves'.format(metrics[i]))
        if train:
            ax[pos].plot(history['epoch'], history['train_{}'.format(metrics[i])], 'r--', label='train {}'.format(metrics[i]))
        if val:
            ax[pos].plot(history['epoch'], history['val_{}'.format(metrics[i])], 'b--', label='validation {}'.format(metrics[i]))
        ax[pos].set_xlabel('epoch')
        ax[pos].legend()
    fig.tight_layout()
    if save_to: 
        fig.savefig(save_to)
    else:
        fig.show()

    
def plot_image_pairs(pairs, grid, fig_shape=(15,7), save_fig=None, style='fivethirtyeight'):
    '''
    Plots pairs of images along 2 rows
    '''
    plt.style.use(style)
    fig,ax = plt.subplots(grid[0], grid[1], sharex=True, sharey=True, figsize=fig_shape)
    for i in range(grid[1]):
        ax[0, i].imshow(pairs[i, 0])
        ax[0, i].axis('off')
        ax[1, i].imshow(pairs[i, 1])
        ax[1, i].axis('off')
    if save_fig: 
        plt.savefig(save_fig)
    plt.show()

    
def plot_feature_importances(feature_names, feature_importances, 
                             orient='h', max_show=15, fig_shape=(8,6)):
    '''
    Plots feature importances
    '''
    feat_imp = pd.DataFrame(
        {'feature': feature_names,
         'importance': feature_importances})
    feat_imp.sort_values('importance', ascending=False, inplace=True)
    plt.figure(figsize=fig_shape)
    plt.title('Feature importances')
    sns.barplot(feat_imp['importance'].iloc[:max_show],
                feat_imp['feature'].iloc[:max_show],
                orient=orient)
    plt.show()

    
def show_images(image_paths, n_row, n_col, fig_dims=(12,8), 
                plot_style='seaborn-white', spaces=(0.01,0.01),
                save_fig=None):
    '''
    Show images from the list of image_paths
    '''
    num_show = n_row * n_col
    assert len(image_paths) >= num_show, 'Number of images should be more than n_row*n_col'
    image_paths = np.random.choice(image_paths, size=(n_row, n_col))
    plt.style.use(plot_style)
    fig,ax = plt.subplots(n_row, n_col, sharex=False, sharey=False, squeeze=False, 
                          figsize=fig_dims)
    _ = [a.axis('off') for a in ax.ravel()]
    fig.subplots_adjust(hspace=spaces[1], wspace=spaces[0])
    for r in range(n_row):
        for c in range(n_col):
            img = image_paths[r,c]
            if isinstance(img, (str,)):
                img = plt.imread(img)
            ax[r, c].imshow(img)
    if save_fig:
        plt.savefig(save_fig)
    plt.show()
    

def histograms(data_dict, n_row, n_col, fig_dims=None, save_fig=None, xlims=[],
               **kwargs):
    '''
    Plot multiple histograms for a data_dict
    Where keys are titles and values are arrays
    '''
    assert isinstance(xlims, (tuple,list))
    if not fig_dims:
        fig_dims = (n_col * 4, n_row * 3)
    fig,axes = plt.subplots(n_row, n_col, squeeze=False, figsize=fig_dims)
    if len(data_dict) < n_row * n_col:
        _ = [a.axis('off') for a in axes.ravel()[len(data_dict) : ]]
    for c,(k,v) in enumerate(data_dict.items()):
        row_num,col_num = divmod(c, n_col)
        splot = sns.distplot(v, ax=axes[row_num, col_num], **kwargs)
        if len(xlims) > 0:
            assert len(xlims) == 2, 'xlims has to be list/tupe of 2 elements'
            splot.set_xlim(*xlims)
        axes[row_num, col_num].set_title(k)
    if save_fig:
        plt.savefig(save_fig)
    plt.tight_layout()
    plt.show()


def barplots(data_dict, n_row, n_col, horizontal=True, fig_dims=None, save_fig=None, **kwargs):
    '''
    Plot multiple histograms for a data_dict
    Where keys are titles and values are arrays
    '''
    if not fig_dims:
        fig_dims = (n_col * 4, n_row * 3)
    fig,axes = plt.subplots(n_row, n_col, squeeze=False, figsize=fig_dims)
    if len(data_dict) < n_row * n_col:
        _ = [a.axis('off') for a in axes.ravel()[len(data_dict) : ]]
    for c,(k,v) in enumerate(data_dict.items()):
        row_num,col_num = divmod(c, n_col)
        seq_types = (list,tuple,np.ndarray,pd.core.series.Series)
        if len(v) == 2 and isinstance(v[0], seq_types) and isinstance(v[1], seq_types):
            labs,cnts = v
        else:
            labs,cnts = np.unique(v, return_counts=True)
        if horizontal:
            sns.barplot(y=labs, x=cnts, ax=axes[row_num, col_num], **kwargs)
        else:
            sns.barplot(x=labs, y=cnts, ax=axes[row_num, col_num], **kwargs)
        axes[row_num, col_num].set_title(k)
    if save_fig:
        plt.savefig(save_fig)
    plt.tight_layout()
    plt.show()


def scatterplots(data_dict, n_row, n_col, 
                 fig_dims=None, save_fig=None, **kwargs):
    '''
    Plot multiple scatterplots for a data_dict
    Where keys are titles and values are tuples of 2 arrays (x and y)
    '''
    if not fig_dims:
        fig_dims = (n_col * 4, n_row * 3)
    fig,axes = plt.subplots(n_row, n_col, squeeze=False, figsize=fig_dims)
    if len(data_dict) < n_row * n_col:
        _ = [a.axis('off') for a in axes.ravel()[len(data_dict) : ]]
    for c,(k,v) in enumerate(data_dict.items()):
        row_num,col_num = divmod(c, n_col)
        x,y= v
        sns.scatterplot(y=y, x=x, ax=axes[row_num, col_num], **kwargs)
        axes[row_num, col_num].set_title(k)
    if save_fig:
        plt.savefig(save_fig)
    plt.tight_layout()
    plt.show()
