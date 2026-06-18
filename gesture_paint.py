import cv2
import mediapipe as mp
import numpy as np

def main():
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    mp_draw = mp.solutions.drawing_utils

    # Initialize Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Read first frame to get dimensions
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        return

    h, w, c = frame.shape

    # Create a black canvas for drawing. We will draw on this and overlay it.
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    # Drawing parameters
    draw_color = (0, 255, 0)  # Green color for drawing
    draw_thickness = 5
    eraser_thickness = 50

    # Variables to track previous position for smooth line drawing
    prev_x, prev_y = 0, 0
    is_drawing = False
    is_erasing = False

    print("--------------------------------------------------")
    # Printable instructions
    print("Gesture Drawing App is running!")
    print("Controls:")
    print("  - Index Finger Up: Draw")
    print("  - Index + Middle (or more) Fingers Up: Erase")
    print("  - Closed Fist / Hover: Don't draw or erase (hover mode)")
    print("  - Press 'c' on keyboard to Clear Canvas")
    print("  - Press 'q' on keyboard to Quit")
    print("--------------------------------------------------")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a natural mirror-view
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        # Draw existing canvas strokes on the live camera frame
        # Convert canvas to grayscale, threshold to create a mask, and merge
        gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY)
        
        # Merge canvas with frame: where canvas is not black, put canvas pixels
        foreground = cv2.bitwise_and(canvas, canvas, mask=thresh)
        background = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(thresh))
        combined_frame = cv2.add(foreground, background)

        mode_text = "Hovering"
        mode_color = (255, 255, 0) # Cyan/Yellow-ish

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw hand skeleton on the screen
                mp_draw.draw_landmarks(combined_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extract landmarks list
                landmarks = hand_landmarks.landmark
                
                # Get coordinates of Index finger tip and PIP joint
                # Coordinates are normalized (0 to 1), convert to pixel coordinates
                index_tip_x = int(landmarks[8].x * w)
                index_tip_y = int(landmarks[8].y * h)
                index_pip_y = int(landmarks[6].y * h)

                # Middle finger tip and PIP joint
                middle_tip_y = int(landmarks[12].y * h)
                middle_pip_y = int(landmarks[10].y * h)

                # Ring finger tip and PIP joint
                ring_tip_y = int(landmarks[16].y * h)
                ring_pip_y = int(landmarks[14].y * h)

                # Pinky finger tip and PIP joint
                pinky_tip_y = int(landmarks[20].y * h)
                pinky_pip_y = int(landmarks[18].y * h)

                # Thumb tip and joint (MCP)
                # Thumb is a bit trickier, but we can compare x coordinates or simplified y coordinate check
                thumb_tip_y = int(landmarks[4].y * h)
                thumb_ip_y = int(landmarks[3].y * h)

                # Count fingers up (y coordinates are 0 at top, so tip_y < pip_y means finger is up)
                index_up = index_tip_y < index_pip_y
                middle_up = middle_tip_y < middle_pip_y
                ring_up = ring_tip_y < ring_pip_y
                pinky_up = pinky_tip_y < pinky_pip_y
                
                # Check thumb up based on relative positions
                # For simplified logic, compare tip y with IP joint y
                thumb_up = thumb_tip_y < thumb_ip_y

                # Count total raised fingers (excluding thumb, or including thumb)
                fingers_up_count = sum([index_up, middle_up, ring_up, pinky_up])

                # Determine action based on fingers up count
                if fingers_up_count == 1 and index_up:
                    # Drawing mode (only index finger is up)
                    mode_text = "Drawing"
                    mode_color = (0, 255, 0)
                    
                    # Draw a circle indicator at index finger tip
                    cv2.circle(combined_frame, (index_tip_x, index_tip_y), draw_thickness, draw_color, cv2.FILLED)

                    if not is_drawing:
                        # First frame starting to draw
                        is_drawing = True
                        prev_x, prev_y = index_tip_x, index_tip_y
                    else:
                        # Draw line from previous position to current position for smoothness
                        cv2.line(canvas, (prev_x, prev_y), (index_tip_x, index_tip_y), draw_color, draw_thickness)
                        prev_x, prev_y = index_tip_x, index_tip_y
                    
                    is_erasing = False

                elif fingers_up_count >= 2:
                    # Eraser mode (2 or more fingers are up)
                    mode_text = "Erasing"
                    mode_color = (0, 0, 255)
                    
                    # Draw an eraser cursor (circle outlines) at the midpoint of index & middle or index tip
                    cv2.circle(combined_frame, (index_tip_x, index_tip_y), eraser_thickness, (0, 0, 255), 2)
                    
                    # Draw on the black canvas with black color to "erase"
                    cv2.circle(canvas, (index_tip_x, index_tip_y), eraser_thickness, (0, 0, 0), cv2.FILLED)
                    
                    is_drawing = False
                    is_erasing = True
                    prev_x, prev_y = index_tip_x, index_tip_y

                else:
                    # Hovering mode / closed hand
                    is_drawing = False
                    is_erasing = False
                    # Visual dot representing cursor
                    cv2.circle(combined_frame, (index_tip_x, index_tip_y), 5, (255, 255, 255), cv2.FILLED)

        else:
            # Hand not detected
            is_drawing = False
            is_erasing = False

        # Draw status panel at top-left
        cv2.rectangle(combined_frame, (10, 10), (280, 80), (40, 40, 40), cv2.FILLED)
        cv2.putText(combined_frame, f"Mode: {mode_text}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2)
        cv2.putText(combined_frame, "Press 'c' to Clear, 'q' to Quit", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Show Output
        cv2.imshow("Gesture Scribble Art", combined_frame)

        # Handle Keyboard Input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            # Clear Canvas
            canvas = np.zeros((h, w, 3), dtype=np.uint8)
            print("Canvas Cleared!")

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()
