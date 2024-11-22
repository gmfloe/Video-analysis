# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 19:13:58 2023

@author: geirf
"""

import pandas as pd
import numpy as np


# reading data
df = pd.read_csv(r'C:\Users\geirf_a\OneDrive - Akershus fylkeskommune\Dokumenter\Python Scripts\Video\Making non-making AI\filename.csv')

navnUt = "outfile.txt"

# converting to numpy array
# each line in this array is of length 152
# and contains the following information:
# cell 0 - number of frame
# cell 1 - person index
# cells 2-101 - calculations regarding the 25 keypoints
# cells 102-151 - x- and y-coordinates of the 25 keypoints
data = df.to_numpy()

number_of_keypoints = 25
col_nr_x = 102
col_nr_y = col_nr_x + number_of_keypoints

# list of person ids
person_id = []

# list of indices
index_list = []

# adding unique person ids to the list
# also adding indices for first entries
for i in range(len(data)):
    if data[i,1] not in person_id:
        person_id.append(data[i,1])
        index_list.append(i)

index_list.append(len(data))

# finding total number of frames
tot_frames = 0

for i in range(len(data)):
    if data[i][0] > tot_frames:
        tot_frames = data[i][0]

# finding number of minutes
# there is one frame pr minute
# counting starts at 0

nr_min = tot_frames //60

# creates array that sums total of distances each minute
tot_dist_pr_min = np.zeros([int(nr_min+1),2])


sum_dist_pr_min = np.zeros([int(nr_min+1),2])

for i in range(len(person_id)):
    a = index_list[i]
    b = index_list[i+1]
    sum_dist = 0
    # number of keypoint-frames-occurences
    nr_kp_fr = 0
    sum_dist_pr_min_temp = np.zeros([int(nr_min+1),2])
    for j in range(number_of_keypoints):
        for k in range(a,b-1):
            x2 = data[k+1,col_nr_x+j]
            x1 = data[k,col_nr_x+j]
            y2 = data[k+1,col_nr_y+j]
            y1 = data[k,col_nr_y+j]
            test = True
            for element in [x1,x2,y1,y2]:
                if element == 0 or np.isnan(element):
                    test = False
            if test == True:
                del_x = x2-x1
                del_y = y2-y1
                dist = np.sqrt(del_x**2+del_y**2)
                sum_dist += dist
                nr_kp_fr +=1
                frame_nr = data[k+1][0]
                min_nr = frame_nr //60
                sum_dist_pr_min_temp[int(min_nr)][0] += dist
                sum_dist_pr_min_temp[int(min_nr)][1] += 1
                
    for x in range(int(nr_min)+1):
        if sum_dist_pr_min_temp[x][1]>5:
            sum_dist_pr_min[x][0] += sum_dist_pr_min_temp[x][0]
            sum_dist_pr_min[x][1] += sum_dist_pr_min_temp[x][1]
    

# skriver til fil
out_file = open(navnUt,"w")

for i in range(int(nr_min)+1):
    out_file.write(str(sum_dist_pr_min[i][0])+"   "+str(sum_dist_pr_min[i][1])+"\n")

out_file.close()






