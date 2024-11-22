import numpy as np
import imageio.v3 as iio
import moviepy.editor as mp
import pyloudnorm as pyln
from pydub import AudioSegment

################Video analysis####################################

# sRGB luminance(Y) values
rY = 0.212655
gY = 0.715158
bY = 0.072187

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

# inverse of sRGB "gamma" function (approx 2.2)
def inv_gam_sRGB(ic):
    c = ic / 255.0
    if c <= 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055)**2.4

# gray value ("brightness")
def gray(r, g, b):
    return rY * inv_gam_sRGB(r) + gY * inv_gam_sRGB(g) + bY * inv_gam_sRGB(b)


# computing visual intensity of all frames by summarizing the
# absolute value of the three color values for each pixel
#
# then calculating normed difference of brightness between two frames
# the difference is summed over all selected pixels

def computeIntensityAndNormedDiff(f1, f2):
    total_intensity = 0
    total_normed_diff = 0
    for i in range(0, height, ph):
        for j in range(0, width, pl):
            r1, g1, b1 = f1[i][j][:3]
            r2, g2, b2 = f2[i][j][:3]
            
            brightness1 = gray(r1, g1, b1)
            brightness2 = gray(r2, g2, b2)
            
            # Compute intensity for the first frame
            total_intensity += brightness1
            
            # Compute normalized difference between the two frames
            if brightness1 != 0:
                normed_diff = abs((brightness2 - brightness1) / brightness1)
                total_normed_diff += normed_diff
    
    return total_intensity, total_normed_diff


# creating matrices
# calculations of normedDiffData starting on the second frame,
# hence subtracting 1 on index
intensity = np.zeros(int(totalUsed - 1))
normedDiffData = np.zeros(int(totalUsed - 1))

# update the loop to call this function
for i in range(len(normedDiffData)):
    intensity[i], normedDiffData[i] = computeIntensityAndNormedDiff(frames[i * pvid], frames[(i + 1) * pvid])


################Sound analysis####################################

def calculate_loudness_over_time(audio_file, window_duration=60.0):
    # Load audio file
    audio = AudioSegment.from_file(audio_file, format="wav")
    
    # Convert to numpy array and normalize to range [-1, 1]
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
    fs = audio.frame_rate
    
    # Calculate window size in samples
    window_size = int(window_duration * fs)
    
    # Stereo audio needs to be reshaped as a 2D numpy array with shape (N, 2)
    # If the audio is mono, we can simply use `np.newaxis` to create a 2D array
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
    else:
        samples = samples.reshape(-1, 1)
    
    # Meter initialization
    meter = pyln.Meter(fs)
    
    # Calculate loudness for each window
    loudness_values = []
    for window_start in range(0, len(samples), window_size):
        window_end = window_start + window_size
        window_samples = samples[window_start:window_end]
        
        # Ensure the window is complete; this avoids processing incomplete windows
        if window_samples.shape[0] < window_size:
            break 
        
        # Get short-term loudness
        loudness = meter.integrated_loudness(window_samples)
        loudness_values.append(loudness)
    
    return loudness_values

# extracting audio from video file (mp4)
# and saving it as a wav file
video = mp.VideoFileClip(fileName)

video.audio.write_audiofile("clip.wav")

# calls the program above
loudness_values = calculate_loudness_over_time("clip.wav")

################Final Calculations####################################

# total length rounded downwards
total_minutes = int(duration // 60)

# creating matrices for intensity and change
# including an extra minute to accommodate data
# that exceed a whole number of minutes
intensity_video_matrix = np.zeros(total_minutes + 1)
sum_normedDiffData = np.zeros(total_minutes + 1)

# number of computed frames per minute
framesPerMinute = len(normedDiffData) / total_minutes

# visual input intensity
for i in range(len(intensity)):
    t = int(i // framesPerMinute)
    intensity_video_matrix[t] += intensity[i]

# change in visual input with normalization
for i in range(len(normedDiffData)):
    t = int(i // framesPerMinute)
    sum_normedDiffData[t] += normedDiffData[i]

min_length = min(len(intensity_video_matrix), len(sum_normedDiffData), len(loudness_values))

# printing
print("Mean visual intensity in video:")
for i in range(min_length):
    print(intensity_video_matrix[i])
print()
print("Sum of normalized differences in the movie:")
for i in range(min_length):
    print(sum_normedDiffData[i])
print()
print("Loudness values:")
for i in range(min_length):
    print(loudness_values[i])

# writing to file
out_file = open(outputName, "w")

for i in range(min_length):
    out_file.write(str(intensity_video_matrix[i]) + "   " + str(sum_normedDiffData[i]) + "   "
                   + str(loudness_values[i]) + "   \n")

out_file.close()
