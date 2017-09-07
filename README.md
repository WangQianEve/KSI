# KSI: device free version
## The idea
We want to use computer vision method to track the hand. There are two possible angles for cameras
1. cameras above the keyboard to track hands
2. cameras beside the keyboard to track any touches on the surface.

And two types of devices we can use:
1. depth cameras  
there're 60fps cameras costing [$110+](https://www.amazon.com/Razer-Stargazer-Depth-Sensing-Webcam-1080P/dp/B01GE9QM5M/ref=sr_1_3?ie=UTF8&qid=1501774854&sr=8-3&keywords=depth+camera)
2. RGB webcams

We tried **RGB webcams** on **top** first. So there're mainly 6 steps:
1. camera speed up
2. background subtraction
3. find index finger
4. determine track point (find fingertip)
5. depth calculation
6. integrating 

We are currently working on Step 6, while step 1 proved to be unnessesary and even have worse effect(details in later chapters).

## Step 1 : camera speed up
### SUMMARY
1. We used threaded method to get better speed when cameras and our algorithm works together. ([See reference](http://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/))
2. We tests the speed of two cameras working simultaneously, on the same USB bus, with different resolution. (see below the statistics)

[need update]()
320*240 182
640*480 60
display|average fps|std fps
--|--|--
0|892.3|6.5
1|460.3|9.4

## Step 2 : background subtraction
### SUMMARY
We spent a week trying different background subtraction algorithms:  
*(item checked means it has been tried, vice versa) *  
*(sorted by time that we tried it)*  
+ [x] opencv's MOG2
+ [x] opencv's KNN
+ [x] PCA-based dynamic
+ use PCA algorithm to find the moving object.
+ [x] PCA-based static
+ use PCA algorithm to get the matrix that represent the background, then subtract it from the current frame.
+ [x] simple background subtraction (SBS)  
+ use the difference of current frame and average of previously obtained background frames to find the hand.
+ [x] dynamic simple background subtraction(D-SBS)  
+ an improved version of SBS, we use background images under different lighting conditions, and for each pixel the threshold is multiples of std.
+ [x] brightness filter
+ use grayscale images to find the hand.
+ [x] skin color filter
+ use skin color's histogram to find the hand.
+ [x] 42 algorithms in [BGS library](https://github.com/andrewssobral/bgslibrary)(43 algorithms)

After thorough consideration, skin-color-filter proved to be the best algorithm for our task. (See below details about the exploring process)

Generally speaking, outcome of simple subtract and static PCA-based are similar in both quality and speed. But lights and shadows strongly effect the quality of images. D-SBS partly solve this problem, skin color filter thoroughly solved it . Other algorithms are too slow or not robust. So skin color filter is our final choice.

### TESTING
We recorded videos to compare different algorithm. But due to the laptop wasn't delivered in first days and other reasons, the testing videos are changing in the whole iteration period. But every comparison is based on a same video.

#### v1
+ background ([camera0](https://drive.google.com/open?id=0BxVGQBoQVFueMXVRamlnVWJPcXc) [camera1](https://drive.google.com/open?id=0BxVGQBoQVFueNGdJb3kzejhLVzQ) )  
pure background with people moving around causing the light and shadows change over time.
+ moving  ([camera0](https://drive.google.com/open?id=0BxVGQBoQVFueX05KaFFUZkxHSnM) [camera1](https://drive.google.com/open?id=0BxVGQBoQVFueaTdwUVdQZFFuWUE))   
The other is hands working on the keyboard(pointing and clicking) with different speed for 10s each.

[need update]()

### DETAILS
#### opencv's MOG2
+ effect: too many noise when patterns change, but it learns.
![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/mog2.png?raw=true)
+ speed: 62(single test, 101secs)
+ [code here](https://github.com/ubicomp-lab/KSI/blob/master/bg-st-opencv.py)

#### opencv's KNN
+ effect: less noise in background, but when hands in/out still big changes.
+ speed: perceptible lag
+ [code here](https://github.com/ubicomp-lab/KSI/blob/master/bg-st-demo.py)

#### opencv's other- to be tested
+ still can't use them with opencv3, need to be tested.
+ there are hand tracking videos using CNT seems good.
+ references:
    + http://docs.opencv.org/trunk/d1/d5c/classcv_1_1bgsegm_1_1BackgroundSubtractorGMG.html
    + https://github.com/opencv/opencv/blob/master/samples/python/digits_video.py

#### PCA-based Dynamic
+ references:
    + [basic algorithm](https://github.com/fastai/numerical-linear-algebra/blob/master/nbs/3.%20Background%20Removal%20with%20Robust%20PCA.ipynb)
    + [basic theory](https://plot.ly/ipython-notebooks/principal-component-analysis/)
    + [another basic SVD theory](http://blog.csdn.net/jyl1999xxxx/article/details/52982091)
+ description: uses frames from now to before to form a big matrix, and apply it to the basic algorithm.
  + effect: poor
![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/k360.png?raw=true)
  + speed: very slow
    + statistics here(720 frames requires almost 1 sec to do the math.)
  + [code here](https://github.com/ubicomp-lab/KSI/blob/master/bg-st-pca-single.py)

#### PCA-based Static
+ Method 1: uses SVD result matrix, U, S, V. Wrong in the end.
I was thinking about decompose the new image with vectors from U, and only keep first nnz coefficients. But the result is a mess, so this idea is probably wrong, because the original samples were calculated with elements from U, S, and V.
  + [code here](https://github.com/ubicomp-lab/KSI/blob/master/bg-st-pca-SVD-demo.py)
+ Method 2: uses background video to get the low_rank matrix. Calculate the average of low_rank, then subtract it from captured frame.
  + anticipates: similar to directly subtract the background? Yes, results are similar
  + speed: average:251.26fps; std:4.85
  + effect:
    + black&white video [camera0](https://drive.google.com/open?id=0BxVGQBoQVFueRUY2Ym1zbmxBZzQ)
    [camera1](https://drive.google.com/open?id=0BxVGQBoQVFuea21aU1h1OG01M00)
    + gray-scale video [camera0](https://drive.google.com/open?id=0BxVGQBoQVFueWnRKeTZQVWFPeDQ) [camera1](https://drive.google.com/open?id=0BxVGQBoQVFueczFndWFwbXVqTTQ)
    + pics:
  ![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/pca-ave-wall.png?raw=true)
  ![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/pca-ave-key.png?raw=true)
  + [code here](https://github.com/ubicomp-lab/KSI/blob/master/bg-st-pca-bg-ave.py)
+ Method 3: use many frames and their low_rank background. Find the frame that's most like captured frame, then subtract corresponding background from the captured frame.
  + concerns: a lot of calculation and since there are hands, we need many many samples. (maybe only background samples will work? it's more like decrease the noise)

#### (SBS) Simple Background Subtract
Subtract background image(mean) from captured image, do filtering.
Initially, we used subtraction on RGB images, and get the following result:
+ effect:
    + black&white video [camera0](https://drive.google.com/open?id=0BxVGQBoQVFueY2Y3d1QxQVdJVFk) [camera1](https://drive.google.com/open?id=0BxVGQBoQVFueS0gyQVdUOU1DTGM)
+ [code here](https://github.com/ubicomp-lab/KSI) but on commit with tag "try rgb subtraction first". bg-st-simple.py is to produce the outcome video, compare.py is to compare difference between RBG version and gray version's outcome. This is a screenshot when comparing:
![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/compare.png?raw=true)
(Window "frame" is RBG version subtract Gray version. Frame1 is RGB version, Frame0 is gray version)

Then we realize that subtraction on grayscale images could be faster, so results are as below:
+ effect:
    + black&white video [camera0](https://drive.google.com/open?id=0BxVGQBoQVFueNjVMTm52TGxsNWc)
    [camera1](https://drive.google.com/open?id=0BxVGQBoQVFueNGZUSzJUR3N2Qnc)
    + gray-scale video [camera0](https://drive.google.com/open?id=0BxVGQBoQVFuebnI4TjQ3QS11T28) [camera1](https://drive.google.com/open?id=0BxVGQBoQVFueWnhKLVVvTjkwWEk)
    + pics:
![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/simple-darkbg.png?raw=true)
![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/simple-lightbg.png?raw=true)
    + but when keyboard reflect much light, the result are strongly influenced, that's why we tried D-SBS(dynamic SBS) later.
+ speed: average: 253.31fps, std: 4.78, times=10
+ disadvantage: when background change, you have to manually resample it for 1~2 seconds.
+ [code here](https://github.com/ubicomp-lab/KSI/blob/master/bg-st-simple.py)

#### (D-SBS) Dynamic Simple Background Subtraction
After testing with PCA-BS and SBS, I find that lighting conditions effect result greatly. Initially, I thought of the following solutions:
+ use unreflective keyboards( put a mask maybe)

  ![](https://img.diytrade.com/cdimg/1448043/21126996/1/1304498124/Computer_keyboard_silica_dust_mask.jpg)
+ use another angle for cameras and detect any touch within certain area on keyboard instead of recognizing the whole hand.

But after discussion, we want our implementation working on any keyboard, so the first is out of consideration. The other angle requires user to use keyboard surface as trackpads, lifting up other fingers while touch with certain fingers. But currently, we want users to rest their fingers on the keyboard, and use index as pointer.

So, with Julian's advice, we have dynamic-SBS, which calculate threshold for each pixel separately. The threshold is 6 times standard deviation of background video.

+ speed:
+ effect: shadows are eliminated greatly(compare video: [D-SBS](https://drive.google.com/open?id=0BxVGQBoQVFueVDZ5M3RYckpfYms) [SBS](https://drive.google.com/open?id=0BxVGQBoQVFuea21aU1h1OG01M00))
however, when we use a new recorded video, with larger difference between light and shadows, part of skin are filtered out as well, while shadows under fingers remains.([video](https://drive.google.com/open?id=0BxVGQBoQVFueSmtOQXNBUUt2UGc))
+ [code here](https://github.com/ubicomp-lab/KSI/blob/master/bg-st-simple.py)

#### Brightness Filter (along with convex hull)
This method uses grayscale images, extract pixels above a threshold, filters small areas and find the big convex hull. Code refering to [Project Shubham](https://github.com/ShubhamCpp/Hand-Gesture-Detection). Speed were tested and shown below.

+ speed(below are tested with convex hull, speed without convex hull is higher than SBS) *To Be Modified*

frames per test|test times|average fps|std fps
--|--|--|--
500|10|134.6|6.86

+ effect: [video](https://drive.google.com/open?id=0BxVGQBoQVFuealVOUDNrZEZ2QlU)  
Hand detection part is quite good with dark background. But index location need more work.
![](https://github.com/ubicomp-lab/KSI/blob/master/testResult/skin.png?raw=true)
+ [code here](https://github.com/ubicomp-lab/KSI/blob/master/skin-color.py)

#### Skin Color Filter (SCF)
Though D-SBS eliminated some influence of shadows, however, under certain lighting conditions, much part of the hand are also filtered away. So we tried skin color filter:
+ Description
We use HSV to decrease influence of lighting. Use hist information to pick out skin part.
+ resources: http://www.benmeline.com/finger-tracking-with-opencv-and-python/
+ Sampling
For this algorithm, sampling for user's hand is important. We ask users to put several parts(inlude the darker skin and brighter skin and nails) of their hand at a certain place on keyboard sequentially.
+ speed: average 178.15 std 8.51 raw camera speed 43.80
+ effect: usable(though noise exists)
[video](https://drive.google.com/open?id=0BxVGQBoQVFueWDIzQUFzdXFWY0U)
+ code: [realtime version](https://github.com/ubicomp-lab/KSI/blob/master/skin-color-filter.py) [video version](https://github.com/ubicomp-lab/KSI/blob/master/v-skin-color-filter.py)

#### BGS library (43 algorithms)
We found a library implemented many algorithms.
+ resources:
  + a [paper](http://www.sciencedirect.com/science/article/pii/S1077314213002361) that compares different background subtraction algorithms
  + the [library](https://github.com/andrewssobral/bgslibrary) it used.
+ result:
most of the algorithms either are way too slow or have bad result. The code and comments are [here](https://github.com/ubicomp-lab/KSI/blob/master/BGS.py)

## Step 3 : Find the Index Finger
After background subtraction, we get an image where hands are white and background is black.
### DESCRIPTION
The algorithm of finding the index finger consists of 4 parts:
![]()
1. Basics: Find the contours of the image, and select the biggest area as valid. Then find the convex hull and center of the contour.
2. Get hand direction.
  + find the left/right endpoint of wrist-line and left/right edge of hand.
  + use the closer one to center as anchor and find the symmetric point on the edge of the other side.
  + add the two vectors to get the opposite of hand direction.
3. Use hand direction to find estimated thumb and index position on convex hull.
  + we scan all the edges on convex hull clockwise from leftmost point.
  + the first one who's longer than _thumb_l, and who's angle is smaller than _thumb_a is considered the thumb.
  + the first one who's longer than  _index_l, and who's angle is smaller than  _index_a is considered the index.
  + angle: we define vector from "center" to the testing point as "point direction". Angle refers to the angle of "point direction" and hand direction.

4. Confirm: Deal with situations where index is not on convex hull.
  + we noticed that middle fingers are sometime considered as index finger, especially when index finger moves closer to palm. So we decide to use ["convex approaximation"](http://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html) to help with this situation.
  + First get the approximation and the nearest point to estimated thumb and index on approximation's convex points, mark them as approx thumb and approx index.
    + here we experience two versions of definition of "convex point".
      1. use center point of hand
      2. use direction changes
  + then check points on approximation between approx thumb and approx index. If there're two concave in between, then those convex betweeen the concoaves are considered index.

### RESULT  
+ quality
+ speed

### Convex Approximation
Another idea is to find fingers directly from approximation. But considering the previous algorithm works out fine, so we didn't try this yet.
1. get convex hull of approximation
2. use concave to separate points into groups.
3. estimate the width of each group, and how many fingers there are likely.
4. find the second as index.

## Step 4: Determine Track Point
After we know the general position of index finger, we need to find a precise tracking point so that both cameras can track the same point and calculate depth. We tried 3 ways of doing that. We first crop a rectangle around the general index position. Then apply different algorithms on it to see which works best.

### Description
1. Box
2. Convex Hull
3. Edge detection

### QUALITY COMPARISON
#### pics (from up to low: camera0's x, camera0's y, camera1's x, camera1's y)
+ box
![box](https://github.com/ubicomp-lab/KSI/blob/master/testResult/plots/line-box.png?raw=true)
+ edge
![edge](https://github.com/ubicomp-lab/KSI/blob/master/testResult/plots/line-edge.png?raw=true)
+ conv
![conv](https://github.com/ubicomp-lab/KSI/blob/master/testResult/plots/line-conv.png?raw=true)

#### video
#### tables
+ length of routes

method | x0 | y0 | x1 | y1
--|--|--|--|--
box  | 4245 | 5984 | 3940 | 6067
edge | 4153 | 6553 | 4178 | 7347
conv | 4309 | 6612 | 3978 | 7284

+ average

method | x0 | y0 | x1 | y1
--|--|--|--|--
box  | 220.22927242  | 136.78680203  | 216.171929825 | 101.250877193 |
edge | 228.097292724 | 137.546531303 | 222.929824561 | 101.954385965 |
conv | 229.175972927 | 138.359560068 | 225.124561404 | 104.349122807 |

+ standard deviation

method | x0 | y0 | x1 | y1
--|--|--|--|--
box  | 27.9720501541 | 47.0161461458 | 27.0126075463 | 45.025044192 |
edge | 28.1405075516 | 47.4805592132 | 27.1805268588 | 46.4812320932 |
conv | 28.0231563304 | 47.5557931032 | 27.0359460569 | 45.7308971634 |

### SPEED COMPARISON

method | ave | std
--|--|--
box  | 0.000074422123307 | 0.000013260347968
edge | 0.000901667543981 | 0.000359573519302
conv | 0.000744257786477 | 0.000259432506332

## Step 5 : Depth Calculation

## Step 6: Speed up
contours and approx: .0010
palm: 0.00014
drawing: .0003
prlc: 0.0010
dep: 0.0003
## Usage
preprocess:
1 background subtraction
2 palm direction
3 fingers and p_fingers
4 
### TOMORROWOW

### NEXT STEPPS
