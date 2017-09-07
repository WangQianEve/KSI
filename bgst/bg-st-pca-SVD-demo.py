import moviepy.editor as mpe
# from IPython.display import display
from glob import glob
import sys, os
import numpy as np
import scipy
import matplotlib.pyplot as plt
plt.imshow(img)
plt.show()
MAX_ITERS = 3
TOL = 1.0e-8
name = "background1"
video = mpe.VideoFileClip("background1.avi")
# HELPER
def create_data_matrix_from_video(clip, k=5, scale=50):
    tu=[scipy.misc.imresize(rgb2gray(clip.get_frame(i/float(k))).astype(int),
                      scale).flatten() for i in range(k * int(clip.duration))]
    return np.vstack(tu).T


def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])


def plt_images(M, A, E, index_array, dims, filename=None):
    f = plt.figure(figsize=(15, 10))
    r = len(index_array)
    pics = r * 3
    for k, i in enumerate(index_array):
        for j, mat in enumerate([M, A, E]):
            sp = f.add_subplot(r, 3, 3*k + j + 1)
            sp.axis('Off')
            pixels = mat[:,i]
            if isinstance(pixels, scipy.sparse.csr_matrix):
                pixels = pixels.todense()
            plt.imshow(np.reshape(pixels, dims), cmap='gray')
    return f


def plots(ims, dims, figsize=(15,20), rows=1, interp=False, titles=None):
    if type(ims[0]) is np.ndarray:
        ims = np.array(ims)
    f = plt.figure(figsize=figsize)
    for i in range(len(ims)):
        sp = f.add_subplot(rows, len(ims)//rows, i+1)
        sp.axis('Off')
        plt.imshow(np.reshape(ims[i], dims), cmap="gray")

def first_time():
    M = create_data_matrix_from_video(video, 100, scale)
    # plt.imshow(np.reshape(M[:,140], dims), cmap='gray');
#    np.save("M-wall.npy", M)
    return M

def second_time():
    return np.load("low_res_surveillance_matrix.npy")

# PCA
from scipy import sparse
from sklearn.utils.extmath import randomized_svd
import fbpca

def converged(Z, d_norm):
    err = np.linalg.norm(Z, 'fro') / d_norm
    print('error: ', err)
    return err < TOL


def shrink(M, tau):
    S = np.abs(M) - tau
    return np.multiply(np.sign(M),np.where(S>0, S, 0))


def _svd(M, rank):
    return fbpca.pca(M, k=min(rank, np.min(M.shape)), raw=True)


def norm_op(M): return _svd(M, 1)[1][0]


def svd_reconstruct(M, rank, min_sv):
    u, s, v = _svd(M, rank)
    s -= min_sv
    nnz = (s > 0).sum()
    return np.mat(u[:,:nnz]) * np.mat(np.diag(s[:nnz])) * np.mat(v[:nnz]), nnz

def plots(ims, dims, figsize=(15,20), rows=1, interp=False, titles=None):
    if type(ims[0]) is np.ndarray:
        ims = np.array(ims)
    f = plt.figure(figsize=figsize)
    for i in range(len(ims)):
        sp = f.add_subplot(rows, len(ims)//rows, i+1)
        sp.axis('Off')
        plt.imshow(np.reshape(ims[i], dims), cmap="gray")

def pcp(X, maxiter=10, k=10): # refactored
    m, n = X.shape
    trans = m<n
    if trans: X = X.T; m, n = X.shape

    lamda = 1/np.sqrt(m)
    op_norm = norm_op(X)
    Y = np.copy(X) / max(op_norm, np.linalg.norm( X, np.inf) / lamda)
    mu = k*1.25/op_norm; mu_bar = mu * 1e7; rho = k * 1.5

    d_norm = np.linalg.norm(X, 'fro')
    L = np.zeros_like(X); sv = 1

    examples = []

    for i in range(maxiter):
        print("rank sv:", sv)
        X2 = X + Y/mu

        # update estimate of Sparse Matrix by "shrinking/truncating": original - low-rank
        S = shrink(X2 - L, lamda/mu)

        # update estimate of Low-rank Matrix by doing truncated SVD of rank sv & reconstructing.
        # count of singular values > 1/mu is returned as svp
        L, svp = svd_reconstruct(X2 - S, sv, 1/mu)

        # If svp < sv, you are already calculating enough singular values.
        # If not, add 20% (in this case 240) to sv
        sv = int(svp + (1 if svp < sv else round(0.05*n)))

        # residual
        Z = X - L - S
        Y += mu*Z; mu *= rho

        examples.extend([S[140,:], L[140,:]])

        if m > mu_bar: m = mu_bar
        if converged(Z, d_norm): break

    if trans: L=L.T; S=S.T
    return L, S, examples

from imutils.video import WebcamVideoStream

scale = 100   # Adjust scale to change resolution of image
dims = (int(480 * (scale/100.0)), int(640 * (scale/100.0)))
M=first_time()
#M=second_time()
#realtime()
m, n = M.shape
L, S, examples =  pcp(M, maxiter=5, k=10)
np.save("low_rank_"+name+".npy",np.mean(L, axis=1))
# plots(examples, dims, rows=5)
# t=np.array(S[:,440].T)[0]
# t+=127.5
# t=t.astype(np.uint8)
# ret,thresh1 = cv2.threshold(t,200,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
# thresh1=np.reshape(thresh1, dims)
# plt.imshow(thresh1,cmap="gray")
# 
# gray=scipy.misc.imresize(rgb2gray(frame0).astype(int),scale).flatten()
# ne=np.mat(u).I*np.mat(gray).T
# lne=ne
# hne=ne
# for i in range(30,):
#     lne[i]=0
# 
# ll=np.mat(u)*np.mat(lne)
# thresh1=np.reshape(ll, dims)
# plt.imshow(thresh1,cmap="gray")
# 
# a=1
