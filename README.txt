This repository contains programs for video and sound analysis. The motivation and background for this Method of analysis will be found in an forthcoming paper.

## video analysis - SRGB-scale
Place the file "video analysis SRGB" in the same folder as the relevant mp4 file and enter its name in line 25. One may also ajust lines 17, 18 and 22 according to needed computational accuracy.

The program will calculate and Write to file Three different values accumulated each minute:
1. intensity of the video data using a SRGB scale.
2. normalized differences between frames
3. loudness values

## video analysis - non-SRGB-scale
Place the file "video analysis non-SRGB" in the same folder as the relevant mp4 file and enter its name in line 20. One may also ajust lines 12, 13 and 17 according to needed computational accuracy.

The program will calculate and Write to file two different values accumulated each minute:
1. normed movement data
2. sound level

## video analysis using OpenPose
The program calculating_changes.py contains an algorithm for calculating cumulative movement. The input required for this algoritm is csv-files produced according to the OpenPose JSON-file output developed here:

https://github.com/tca2/videodata-processing

The version of the files "concat_JSON_files" and "allprocesses_command" included in Our repository were used in Our own calculations. A few lines were changed to make the program work here.

After having run the programs "concat_JSON_files" and "allprocesses_command" on the OpenPose JSON-output, run "calculating changes" With the relevant filename given in line 13. The program calculates and Writes to file the cumulated distances for each minute. These are based on the locations of the 25 keypoints used in OpenPose.