import cv2
import time 
import numpy as np
import requests
import socket
import pyttsx3

text_speech = pyttsx3.init()
PORT = 8080
# socket thing 
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(3)
print("Waiting for connections...")
client_socket, client_address = server_socket.accept()
print("Connection accepted from", client_address)

# loading the yolo model
# dnn stands for deep neural netwrok  
net =cv2.dnn.readNet("C:/Users/Shreyash/Desktop/smart-white-cane/test/yolov3.cfg","C:/Users/Shreyash/Desktop/smart-white-cane/test/yolov3.weights") 
classes=[]


# open the coco.names file to read the name of different objects we can identify 

with open("C:/Users/Shreyash/Desktop/smart-white-cane/test/coco.names","r") as f:
    classes =[line.strip() for line in f.readlines()]

# get names of the layers of dnn 
layer_names = net.getLayerNames()
# we get the output layers from all the layers of the dnn 
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
# this output layers will provide the final detection 


url = "http://192.168.43.1:8080/video"

cap=cv2.VideoCapture(url);
while(True):
    bol ,frame= cap.read()
    if  frame is not None:
        img = frame
        height, width, channels = img.shape

        # the object detection part starts here 
        # we cannot give the image directly to the model we need to convert it to blob first 

        # converting the image to blob 

        # the parameters 
        # /////////////////////////////////
        # search the parameters and add the meaning here in the blobFromImage
        # ////////////////////////////////
        # we also convert the bgr(std for cv2 ) img from rgb this is done using the True param 
        # this blob will store blob for each channel rgb 

        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        # now the image is ready to be processed by the yolo algorithm 

        # giving the input to the model 
        net.setInput(blob)
        # forward the final results to the output layer
        # this outs object contians all the information 
        # so the object has already been detected and it is there 

        outputs=net.forward(output_layers)

        # arrays to store the infomration about objects detected so far 
        class_ids = []
        confidences = []
        boxes = []
        # recive message from socket
        message = client_socket.recv(1024).decode().split()
        # print(message)
        dist=message[0]
        lat=message[1]
        lang=message[2]
        print("https://www.google.com/maps/@"+lat+","+lang+",10.6z?entry=ttu")
        # now we need to show the info on the screen 
        for output in outputs:
            # getting the detection out of the output 
            for detection in output:
                # detection[0] : center x 
                # detection[1] : center y
                # detection[2] : width of the image 
                # detection[3] : height of image 
                scores=detection[5:]
        # seach about this method 
        # /////////////////////// 
                # we select which detection has max confidence
                class_id=np.argmax(scores)
        # //////////////////////
                # we will extract the detected object cofidiance 
                confidence=scores[class_id]
                if confidence>0.5:
                    # object detected 
                    # need to do this cause we croped the image when we converted it to the blob and we need to draw the rectangles on the orginal image 

                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)  

                    # rectangle cordinates extrat 
                    # top left x      
                    x = int(center_x - w / 2)
                    # top left y
                    y = int(center_y - h / 2)     
                    # putting the retriverd infomration into the array data strcutures 
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # no mark speration 
        # this is a dnn function to remove repeated dtection works on threeshold that we provide it 
        # that way remove the noise 
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        # indexes=boxes
        # 0.5 : score threeshold
        # 0.4 : nms_threshold 
        # getting the font for putting the label on the image 
        font = cv2.FONT_HERSHEY_PLAIN

        # now we need to loop on the collected data in the array and for only thoses which are in index above 
        for i in range(len(boxes)):
            # take only those i which are in the index 
            if i in indexes:
            # if True:
                # extract the top-left-x and top-left-y
                # extract the width 
                # extract the height 

                x, y, w, h = boxes[i]
                # label is in the classes array defined at top 
                # we have stored id of the class in to which current object belongs to in the class ids array 
                label = str(classes[class_ids[i]])
                
                print(label+" is at distance " + dist + " cm ")
                text_speech.say(label+" is at distance " + dist + " cm ")
                text_speech.runAndWait()
                # //////////////////////////
                # check how this rectangle function works 
                # /////////////////////////
                cv2.rectangle(img, (x, y), (x + w, y + h), (0,255,0), 2)
                # ///////////////////////////
                # put text on the reactangles 
                # check how this works also 
                # //////////////////////////
                cv2.putText(img, label, (x, y + 30), font, 3, (0,255,0), 3)
        cv2.imshow("frame",img)
    
        q=cv2.waitKey(1)
        if q== ord('q'):
            break

cv2.destroyAllWindows()
client_socket.close()
server_socket.close()