# Daily record as summer intern in ubicomp-lab
Wang Qian (Evelyn)
## Week 1
*(record of this week is written up in week 3)*
#### description
I arrived on Monday, and meet Julian on Tuesday afternoon. Started working on Wednesday, set the working environment took some time. Then I tested threaded video stream.
#### summary
Efficiency is quite low for this week. Probably because of jet lag, I felt sleepy day and night. But Julian is nice and patient. He guided me how and why to record the working procedure and data well at weekend.

## Week 2
### Summary
I learned a lot about how to record a research process with document of good structure.
+ Content related: Ideas need to be written down clearly. Plans/summary can be the first part so that readers know what you're doing, and what has been done. If something failed, why it failed should be explained clearly.

And how to do research strictly:
+ Result at any stage of needs to be recorded as numbers or pictures, rather than vague description.
+ Find uniformed method to compare result of different method, this is more persuasive.

I thought about a new method of implementing KSI, placing the cameras beside the keyboard to detect any touch on keyboard. Talked with Julian several times, but he was skeptical about it, think we should stick to the original method. For this new method, users need to lift up other fingers while pointing, which may cause fatigue. So we agreed on implementing current idea first to see the result. Speed up next week!

#### Monday
+ Finished video version of PCA-based background subtraction
+ Finished real-time version of PCA-based background subtraction
+ Test the algorithm.
+ Write the first version of report(README.md).

#### Tuesday
+ Tried my way to speed up PCA-based background subtraction, but still it's slow.
+ Talk with Julian.
+ Tried Julian's idea about speeding up PCA-based background subtraction.
+ Re-organized report according to Julian's feedback.

#### Wednesday
+ Tried simple background subtraction
+ Finished speed test with both algorithm
+ Record videos for comparing outcome quality of algorithms, and tested, found a new problem.

#### Thursday
+ Re-record videos( I didn't fully understand the purpose for those videos. )
+ Modify algorithms to video version and did tests, and optimized algorithm.
+ Think about methods to solve reflecting problem, discuss with Julian.

#### Friday
+ Tried all the background subtraction algorithms from BGS library
+ Deal with my new DS-2019.

#### Weekend
+ Tried dynamic simple background subtraction with Julian's advice, partly solved problem of shadows.
+ Recorded new test videos on the new laptop.

## Week 3
### summary
After a few trials, I decide to use angle and length of edge to locate index. The process of finding the right parameter is tiring. And there are various hand gestures I need to consider. But gladly locating index finally works.

### Monday
+ recorded new video, find out that there still are situations D-SBS can't deal with.
+ tried skin color filter, good. Starting step3!
+ implemented convex hull and tried first idea of locating index

### Tuesday
+ optimized index locating
+ find situations where index is not on convex hull a problem.
+ discuss with Julian about solutions.

### Wednesday
+ speed test
+ meet Anind

### Thursday
+ correct index from middle

### Friday
+ set up the new laptop
+ video with Julian

## Week 4
### summary
Early in this week, I think my part was done. I begin to re-organize everything, clean up the code, and use depth calculation to test the finger tracking. After I improved depth calculation, the result is good.

### Monday
+ Start step 4, locating track point.
+ Tried hand direction method.
+ Tried box method for step 4.

### Tuesday
(feel sick)
+ Improve the two methods
+ Talk with Julian

### Wednesday
+ re-record the video
+ auto settings of cameras off
+ tried 2 other methods(edge detection and convex hull image) of step 4

### Thursday
+ test speed about all methods of step 4
+ reorganize the whole project
    + config tips: https://martin-thoma.com/configuration-files-in-python/

### Friday
+ deal with my lost credit card and student ID
+ try depth calculation
+ inspect step2-4
+ build prepare program for user study

### Weekend
+ improve depth calculation
+ update report
+ make depth calculation real-time

## Week 5
### summary
This week is full of unexpected problems!

First, camera setting's balance between speed and image quality is really hard to find. But I learned a lot about camera parameters, gain, white balance, exposure ...

Second, python's multithreading is really annoying. Something(probably GIL) makes multithreading a fake, and influence the speed of program in a strange way. Spent a lot of time locating the problem, at first I suspect it was garbage collection. So I went back to single thread version and realize that multithreading is actually making the program slower.

Lesson learned: test with each stage before working on next stage.

#### Monday
+ evaluate result after depth calculation, the height users need to lift up fingers is 1cm, acceptable.
+ use multithreading to speed up

#### Tuesday
+ find that when camera resolution is set low and camera speed is set high, the quality becomes bad, effecting skin color filter.
+ spend the whole afternoon adjusting parameters to find the balance of camera speed and quality.

#### Wednesday
+ when testing speed, find something wierd.
+ searching for reason and find out the bad effect of multithreading.
+ talk with Julian about whole architechture of the project and our goal.

## Future plan
2. jumps too much, do not change.

1. try click
2. ask about tab
3. try new angle
4. depth question and qian's plane
