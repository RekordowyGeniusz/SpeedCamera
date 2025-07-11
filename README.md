Here are listed some additional information about the project.

This program was used for a scaled-down version of a speed camera.
The device itself was composed of a Raspberry Pi 5 and two ArduCam B0386 cameras for video capture.
A racing car was used during testing to simulate real-world conditions.

The first camera detects when a car enters measurement section on a road and when the car leaves this section capturing timestamps of both events. By this method it is easy to calculate the velocity of the vehicle.
The second camera captures the license plate number of a vehicle by utilizing a specifically trained yolo model and EasyOCR library for reading text on the license plate. 
If the car exceeded the speed limit then an image of the vehicle is captured and stored and a .txt file is created with data connected to the vehicle itself (e.g. the velocity that the vehicle was traveling at, license plate number, etc.). 

Also for easier UX, an overlay was created which allows changing crucial parameters (like the coordinates on the window which correspond to the measurement track start and it's end etc.) without the need to manually change the code.

Feedback about the code and logic would be well recieved!
