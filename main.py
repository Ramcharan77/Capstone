import os
import re
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
width , height=1920,1080
folderPath="Capstone_Review final"
def rename_png_files(folder_path):
    # Get a list of PNG files in the folder
    png_files = [file for file in os.listdir(folder_path) if file.endswith('.png')]
    # Sort the PNG files
    png_files.sort()

    # Rename the files with sequential numbers
    for index, old_name in enumerate(png_files, start=1):
        new_name = f"{index}.png"
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} -> {new_name}")
rename_png_files(folderPath)
#camera
cap=cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)
#img list
pattern = r"(\d+)"  # Regular expression pattern to extract numeric part
pathImages = sorted(os.listdir(folderPath), key=lambda x: int(re.findall(pattern, x)[0]))
#print(pathImages)
#var
imgno=0
hs , ws =int(120*1) ,int(180*1)
gestureThreshold=300
buttonPressed=False
buttoncounter=0
buttondelay=15
annotations=[[]]
annotationNo=0
annotationstart=False
#hand dectector
det=HandDetector(detectionCon=0.8,maxHands=1)
while True:
    #images
    success , img=cap.read()
    img=cv2.flip(img,1)
    pathFullimage=os.path.join(folderPath,pathImages[imgno])
    imgcurr=cv2.imread(pathFullimage)
    hands,img=det.findHands(img)
    cv2.line(img,(0,gestureThreshold),(width,gestureThreshold),(0,255,0),10)
    print(annotationNo)
    if hands and buttonPressed is False:
        hand=hands[0]
        fingers=det.fingersUp(hand)
        cx,cy=hand['center']
        lmList=hand['lmList']
        #constrain values for easier drawing
        xVal=int(np.interp(lmList[8][0],[width//2,width],[0,width]))
        yVal =int(np.interp(lmList[8][1], [100,height], [0, height]))
        indexFinger=xVal,yVal
        #print(fingers)
        if cy<=gestureThreshold:#if hand is at the height is at face
            annotationstart = False
            #g-1 left
            if fingers==[1,0,0,0,0]:
                annotationstart = False
                print("left")
                if imgno>0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNo = 0
                    imgno-=1
            #g-2 right
            if fingers==[0,0,0,0,0]:
                annotationstart = False
                print("right")
                if imgno<len(pathImages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNo = 0
                    imgno+=1
            if fingers == [1, 1, 0, 0, 1]:
                    files = os.listdir(folderPath)
                    for file in files:
                        file_path = os.path.join(folderPath, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    print("All files in the folder have been deleted.")
                    break

        #g-3 -show pointer
        if fingers==[0,1,1,0,0]:
            cv2.circle(imgcurr,indexFinger,12,(0,0,255),cv2.FILLED)
            annotationstart = False
        # g-4 -draw pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationstart is False:
                annotationstart=True
                annotationNo+=1
                annotations.append([])
            cv2.circle(imgcurr, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNo].append(indexFinger)
        else:
            annotationstart=False
        #g-5 -erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNo>=0:
                    annotations.pop(-1)
                    annotationNo-=1
                    buttonPressed=True
    else:
        annotationstart = False
    #button pressed iterations
    if buttonPressed:
        buttoncounter+=1
        if buttoncounter>buttondelay:
            buttoncounter=0
            buttonPressed=False
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j!=0:
                cv2.line(imgcurr,annotations[i][j-1],annotations[i][j],(0,0,200),10)
    #adding  webcam in the site
    imgsmall=cv2.resize(img,(ws,hs))
    h,w,_=imgcurr.shape
    #imgcurr[hs:hs*2,w-ws:w]=imgsmall
    #imgcurr[h - hs:h, w - ws:w] = imgsmall
    # Resize imgsmall to a smaller size
    imgsmall_resized = cv2.resize(imgsmall, (ws, hs))

    # Create a black canvas to place the resized imgsmall
    canvas = np.zeros((imgcurr.shape[0], ws, 3), dtype=np.uint8)

    # Place the resized imgsmall on the canvas
    canvas[:imgsmall_resized.shape[0], :imgsmall_resized.shape[1]] = imgsmall_resized

    # Concatenate the canvas with imgcurr to create the final combined image
    img_combined = cv2.hconcat([imgcurr, canvas])
    cv2.imshow("slides", img_combined)
    #cv2.imshow("Image",img)
    key=cv2.waitKey(1)