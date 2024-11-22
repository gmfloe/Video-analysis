import numpy as np
import imageio.v3 as iio
import moviepy.editor as mp
from scipy.io.wavfile import read
from scipy.stats import pearsonr

################Video analysis####################################

# resolution
# if ph = n, only the nth pixel is used in calculations
# ph: heigth, pl: length
ph = 20
pl = 20

# number of skipped frames
# pvid = n means that we use every nth image
pvid = 30

# input
fileName = 'name.mp4'

# output
outputName = "output_name.txt"

# importing video
frames = iio.imread(fileName, plugin='pyav')

# frames per second
fps = iio.immeta(fileName, plugin='pyav')['fps']

# number of frames
totalFrames = len(frames)

# number of used frames
totalUsed = totalFrames / pvid

# duration of video
duration = totalFrames / fps

# measuring size and counting nr of colours
height = len(frames[0])
width = len(frames[0][0])
color = len(frames[0][0][0])


# calculating total normed difference between two frames
# with normalisation as percentage change from first image
def norm_move(f1,f2):
    tot = 0
    for i in range(0,height,ph):
        for j in range(0,width,pl):
            for k in range(color):
                if f1[i][j][k]!=0:
                    norm_move = abs((int(f2[i][j][k])-int(f1[i][j][k]))/int(f1[i][j][k]))
                tot += norm_move
    return tot

# creating matrix
# calculations of norm_move starting on the second frame,
# hence subtracting 1 on index
norm_move_data = np.zeros(int(totalUsed-1))

for i in range(len(norm_move_data)):
    norm_move_data[i] = norm_move(frames[i*pvid],frames[(i+1)*pvid])
    


################Sound analysis####################################


# getting sound from video file (mp4)
# and saving this in wav-format
video = mp.VideoFileClip(fileName)
video.audio.write_audiofile(r"klipp.wav")

# reading file
data_read = read("klipp.wav")

# sampling frequency
samp_fr = data_read[0]

# getting data
data = data_read[1]

# total time
time_audio = len(data) / samp_fr

#creating matrixes for each of the two channels
ch1 = np.zeros(len(data))
ch2 = np.zeros(len(data))

# copying values
for i in range(len(data)):
    ch1[i] = data[i][0]
    ch2[i] = data[i][1]

# selecting the least time video/audio
# there might be a small difference between these
time = min(duration,time_audio)

# rounding downwards to nearest integer
nr_sec = int(time)
nr_min = int(nr_sec/60)

# creating matrix
sound_level = np.zeros(nr_min+1)
sum_norm_move_data = np.zeros(nr_min+1)

framesPrMin = len(norm_move_data)/nr_min

# calculating sums of normed movement
for i in range(len(norm_move_data)):
    t = int(i//framesPrMin)
    sum_norm_move_data[t] += norm_move_data[i]

# calculating sound levels
# only channel one is used here
for i in range(len(data)):
    t = int(i//samp_fr)
    t_min = int(t/60)
    sound_level[t_min] += abs(ch1[i])

# writing to file
out_file = open(outputName,"w")

for i in range(len(sum_norm_move_data)):
    out_file.write(str(sum_norm_move_data[i])+"   "+str(sound_level[i])+"\n")

out_file.close()


