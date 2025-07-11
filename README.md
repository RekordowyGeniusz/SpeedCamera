## 👋 Welcome!
Below you can find some additional information about the project.
<br>
## 🔎 **Project overview**
This program was used for a scaled-down version of a speed camera.<br>
The device itself was composed of a Raspberry Pi 5 and two ArduCam B0386 cameras for video capture.<br>
However it supports velocity measurement from video files.<br>
A racing car was used during testing to simulate real-world conditions.<br>
<br>
The first camera detects when a car enters measurement section of a road and when the car leaves this part of the road, capturing timestamps of both events. These timestamps are then used to calculate the velocity of the vehicle.<br>
The second camera captures the license plate number of a vehicle by utilizing a specifically trained yolo model and EasyOCR library for reading text on the license plate. <br>
If the car exceeded the speed limit then an image of the vehicle is captured and stored, additionally a .txt file is created with data connected to the vehicle itself (e.g. the velocity that the vehicle was traveling at, license plate number, etc.). <br>
<br>
To improve user experience, an overlay interface was created which allows changing crucial parameters (like the coordinates on the window which correspond to the measurement track start and it's end etc.) without the need to manually change the code.<br>
<br>
**Feedback** on the code and logic would be well received!<br>
<br>
## 📦 **Requirements**
Apart from requirements.txt file, it may be needed to install PyTorch and Cuda drivers.  <br>
<br>
## 📄 **License**
This project is licensed under the MIT License. See the LICENSE.md file for details.<br>
