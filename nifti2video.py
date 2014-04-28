import numpy as np
import nibabel as nb
import mininumm as numm
import sys
import os

nifti_1 = sys.argv[1]
nifti_2 = sys.argv[2]
file_name = os.path.splitext(os.path.splitext(os.path.basename(nifti_1))[0])[0]
print file_name
if not os.path.exists('webm/'):
    os.mkdir("webm/")
#if not os.path.exists('mp4/'):
#    os.mkdir("mp4/")

data_1 = nb.load(nifti_1).get_data()
data_2 = nb.load(nifti_2).get_data()

brain = (data_1*200).astype("uint8")

skull = data_2.astype("uint8")
##create movie (color channels)
movie = np.asarray((brain+skull,skull,skull))
fps = 10

###rotate brain
movieT = movie.T
movieA = movieT[::-1,...]
#axial
movie_axial = np.fliplr(movieA)
numm.np2video(movie_axial,"webm/"+file_name+"_view1.webm",fps=fps)
#numm.np2video(movie_axial,"mp4/"+file_name+"_axial.mp4",fps=fps)

#coronal
movieC = movieA.swapaxes(0,1)
movie_coronal = np.flipud(movieC)
numm.np2video(movie_coronal,"webm/"+file_name+"_view2.webm",fps=fps)
#numm.np2video(movie_axial,"mp4/"+file_name+"_coronal.mp4",fps=fps)

#saggital
movieS = movieC.swapaxes(0,2)
movie_saggital = movieS[:,:,::-1,:]
numm.np2video(movie_saggital,"webm/"+file_name+"_view3.webm",fps=fps)
#numm.np2video(movie_axial,"mp4/"+file_name+"_saggital.mp4",fps=fps)
