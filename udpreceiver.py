import cv2

cap = cv2.VideoCapture("udp://@0.0.0.0:11111")

while(True):
    # Capture frame-by-framestreamon
    ret, frame = cap.read()
    # Our operations on the frame come here

    # Display the resulting frame
    cv2.imshow('ff',frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
