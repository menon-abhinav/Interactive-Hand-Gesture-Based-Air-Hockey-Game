"""
Neon Air Hockey Game with Hand Gesture Controls

This Python script enables a real-time air hockey game using hand gesture recognition to control the paddles.
Players interact with the game by moving their hands in front of the camera to manipulate virtual paddles on the screen.
The game incorporates two power-ups:
1. 'Mid-Blocker' - Activated by making a fist with the thumb out. It creates a temporary barrier in the middle of the game field.
2. 'Goal-Blocker' - Activated by holding up the index, middle, and thumb fingers. It temporarily blocks the goal area.
Each power-up is active for 5 seconds. The game is played to a score of 3 points, with the first player reaching this score declared the winner.

Author: Abhinav Ajit Menon
Created: 05-02-2024
"""

import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time

# Initialize the camera and set its resolution
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Load images for background, game over screen, and game elements
imgBackground = cv2.imread("Resources/cv_background.png")
imgGameOver = cv2.imread("Resources/cv_gameOver.png")
imgBall = cv2.imread("Resources/puck.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("Resources/blue_mallet.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("Resources/purple_mallet.png", cv2.IMREAD_UNCHANGED)
imgPowerUp = cv2.imread("Resources/fist_powerUp.png", cv2.IMREAD_UNCHANGED)
goal_blocker_powerUp = cv2.imread("Resources/goal_blocker_powerUp.png", cv2.IMREAD_UNCHANGED)

# Set up the hand detector with a confidence threshold
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Initialize game variables
ballPos = [100, 145]
speedX = 15
speedY = 15
speedIncrease = 3  # How much speed increases when level increases
hits = 0
level = 1
levelThreshold = 5  # Number of hits required to increase the level
gameOver = False
score = [0, 0]  # Score for each player
game_score = [0, 0]
max_score = 3
startTime = time.time()
bestTime = 0
winMessage = ""
powerUp1Used = False
powerUp1StartTime = 0
powerUpDuration = 5  # Power-up duration in seconds
powerUp1Position = ""
powerUp2UsedLeft = False
powerUp2StartTimeLeft = 0
powerUp2UsedRight = False
powerUp2StartTimeRight = 0
game_score_flag = False

while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)

    # Detect hands and overlay the background image
    hands, img = detector.findHands(img, flipType=False)
    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

    # Calculate the current time
    currentTime = time.time() - startTime

    # Check for hands
    if hands:

        # Loop through each hand
        for hand in hands:

            # Calculate mallet positions: Extract hand bounding box, determine mallet dimensions,
            # adjust mallet center based on hand position, and constrain mallet movement within designated game areas.
            x, y, w, h = hand['bbox']
            h1, w1, _ = imgBat1.shape
            x1 = x + w1 // 2
            y1 = y - h1 // 2
            x1_left = np.clip(x1, 0, 600)
            x1_right = np.clip(x1, 600, 1200)
            y1 = np.clip(y1, 115, 660)

            # Check which fingers are up
            fingerUp = detector.fingersUp(hand)

            # Overlay the mallets on the hands with left hand
            if hand['type'] == "Left":
                img = cvzone.overlayPNG(img, imgBat1, (x1_left, y1))

                # Check if power-up1 is used
                if fingerUp == [0, 0, 0, 0, 0]:
                    powerUp1Used = True
                    powerUp1StartTime = currentTime
                    powerUp1Position = ballPos[0]

                # Check if power-up2 is used
                if fingerUp == [0, 1, 1, 0, 0]:
                    powerUp2UsedLeft = True
                    powerUp2StartTimeLeft = currentTime

                # Check if the ball hits the mallet
                if x1_left - w1 < ballPos[0] < x1_left + w1 and y1 - h1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] += 30
                    score[0] += 1
                    hits += 1

            # Check if the ball hits the mallet with the right hand
            if hand['type'] == "Right":
                img = cvzone.overlayPNG(img, imgBat2, (x1_right, y1))

                # Check if power-up1 is used
                if fingerUp == [0, 0, 0, 0, 0]:
                    powerUp1Used = True
                    powerUp1StartTime = currentTime
                    powerUp1Position = ballPos[0]

                # Check if power-up2 is used
                if fingerUp == [0, 1, 1, 0, 0]:
                    powerUp2UsedRight = True
                    powerUp2StartTimeRight = currentTime

                # Check if the ball hits the mallet
                if x1_right - w1 < ballPos[0] < x1_right + w1 and y1 - h1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] -= 30
                    score[1] += 1
                    hits += 1

    # Check if power-up1 is active
    if powerUp1Used and currentTime - powerUp1StartTime < powerUpDuration:
        img = cvzone.overlayPNG(img, imgPowerUp, [10, 0])
        if powerUp1Position >= 630:
            if ballPos[0] < 650:
                speedX = -speedX
                ballPos[0] += 30
        else:
            if ballPos[0] > 580:
                speedX = -speedX
                ballPos[0] -= 30

    # Check if power-up2 is active for left player
    if powerUp2UsedLeft and currentTime - powerUp2StartTimeLeft < powerUpDuration:
        img = cvzone.overlayPNG(img, goal_blocker_powerUp, [40, 225])
        if ballPos[0] < 70:
            speedX = -speedX
            ballPos[0] += 30

    # Check if power-up2 is active for right player
    if powerUp2UsedRight and currentTime - powerUp2StartTimeRight < powerUpDuration:
        img = cvzone.overlayPNG(img, goal_blocker_powerUp, [1190, 225])
        if ballPos[0] > 1160:
            speedX = -speedX
            ballPos[0] -= 30

    # Check if level should increase and increase the speed as the level goes up
    if hits >= levelThreshold:
        level += 1
        hits = 0
        speedX += np.sign(speedX) * speedIncrease
        speedY += np.sign(speedY) * speedIncrease

    cv2.putText(img, f'Level: {level}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)

    # Check for goal condition and update scores
    if 40 > ballPos[0] and not game_score_flag:
        game_score_flag = True
        game_score[1] += 1
        ballPos = [1100, 145]
        game_score_flag = False
        speedX = -15
        speedY = 15
        level = 1
    elif 1200 < ballPos[0] and not game_score_flag:
        game_score_flag = True
        game_score[0] += 1
        ballPos = [100, 145]
        game_score_flag = False
        speedX = 15
        speedY = 15
        level = 1

    # Check for game over condition
    if game_score[0] >= max_score or game_score[1] >= max_score:
        gameOver = True
        if game_score[0] >= max_score:
            winMessage = "BLUE PLAYER WINS!"
        else:
            winMessage = "PURPLE PLAYER WINS!"

    # Update the best time if current time is greater
    if not gameOver:

        if ballPos[1] >= 610 or ballPos[1] <= 135:
            speedY = -speedY

        if ballPos[0] < 70 and (280 > ballPos[1] or ballPos[1] > 530):
            speedX = -speedX
            ballPos[0] += 30

        if ballPos[0] > 1160 and (280 > ballPos[1] or ballPos[1] > 530):
            speedX = -speedX
            ballPos[0] -= 30

        # Update the best time if current time is greater
        if currentTime > bestTime:
            bestTime = currentTime

        cv2.putText(img, f'Time: {currentTime:.2f}', (1125, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
        ballPos[0] += speedX
        ballPos[1] += speedY
        img = cvzone.overlayPNG(img, imgBall, ballPos)
        cv2.putText(img, str(game_score[0]), (515, 62), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 5)
        cv2.putText(img, str(game_score[1]), (715, 62), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 5)

    # Display the game over screen
    else:
        img = imgGameOver
        cv2.putText(img, winMessage, (300, 350), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 5)
        cv2.putText(img, f'Blue  {game_score[0]} - {game_score[1]}  Purple', (475, 425), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, f'Best Time: {bestTime:.2f}', (500, 475), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    # Conditions to reset the game
    if key == ord('r'):
        startTime = time.time()
        game_score_flag = False
        level = 1
        hits = 0
        ballPos = [100, 145]
        speedX = 15
        speedY = 15
        gameOver = False
        score = [0, 0]
        game_score = [0, 0]
        imgGameOver = cv2.imread("Resources/cv_gameOver.png")
        powerUp1Used = False
        powerUp1StartTime = 0
        powerUp2UsedLeft = False
        powerUp2StartTimeLeft = 0
        powerUp2UsedRight = False
        powerUp2StartTimeRight = 0

    if key == ord('q'):
        break
