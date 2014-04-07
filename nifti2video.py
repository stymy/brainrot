import numpy as np
import nibabel as nb
import mininumm as numm
import sys
import os

nifti_file = sys.argv[1]
file_name = nifti_file.split('/')[4]
if not os.path.exists('webm/'):
    os.mkdir("webm/")
#if not os.path.exists('mp4/'):
#    os.mkdir("mp4/")
    
nifti = nb.load(nifti_file).get_data()
brain = nifti.astype("uint8")

##create movie (color channels)
movie = np.asarray((brain,brain,brain))
fps = 10

###rotate brain
movieT = movie.T
movieA = movieT[::-1,...]
#axial
movie_axial = np.fliplr(movieA)
numm.np2video(movie_axial,"webm/"+file_name+"_axial.webm",fps=fps)
#numm.np2video(movie_axial,"mp4/"+file_name+"_axial.mp4",fps=fps)

#coronal
movieC = movieA.swapaxes(0,1)
movie_coronal = np.flipud(movieC)
numm.np2video(movie_coronal,"webm/"+file_name+"_coronal.webm",fps=fps)
#numm.np2video(movie_axial,"mp4/"+file_name+"_coronal.mp4",fps=fps)

#saggital
movieS = movieC.swapaxes(0,2)
movie_saggital = movieS[:,:,::-1,:]
numm.np2video(movie_saggital,"webm/"+file_name+"_saggital.webm",fps=fps)
#numm.np2video(movie_axial,"mp4/"+file_name+"_saggital.mp4",fps=fps)
