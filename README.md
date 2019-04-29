# videocr

<img width="300" alt="screenshot" src="https://user-images.githubusercontent.com/10210967/56873658-3b76dd00-6a34-11e9-95c6-cd6edc721f58.png">

<img width="300" alt="screenshot" src="https://user-images.githubusercontent.com/10210967/56873659-3b76dd00-6a34-11e9-97aa-2c3e96fe3a97.png">

<img width="300" alt="screenshot" src="https://user-images.githubusercontent.com/10210967/56873660-3b76dd00-6a34-11e9-90dc-20cd9613ebb1.png">

```
import videocr

print(videocr.get_subtitles('video.avi', lang='HanS'))

```

Output:

``` 
0
00:00:00,000 --> 00:00:02,711
-谢谢 … 你 好 -谢谢
Thank you...Hi. Thanks.

1
00:00:02,794 --> 00:00:04,879
喝 点 什么 ?
What can I get you?

2
00:00:05,046  --> 00:00:12,554
休闲 时 光 …
For relaxing times, make it...

3
00:00:12,804 --> 00:00:14,723
三 得 利 时 光
Bartender, Bob Suntory time.

4
00:00:16,474 --> 00:00:19,144
Un, I'll have a vodka tonic.

5
00:00:19,394 --> 00:00:20,687
谢谢
Laughs Thanks.

```
