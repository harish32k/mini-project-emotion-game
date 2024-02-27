# Emotion based Dynamic Difficulty Adjusting Game

## Description

This game can record user emotions in real-time and modify the game's difficulty accordingly. The Emotion Adaptive Game operates by adapting to the emotional states of the player, with the difficulty level changing based on these emotions. For the game, a desktop-based space shooter game has been selected, where the player must shoot down enemy ships. Players who exhibit negative emotions are subjected to a penalty, resulting in an increase in game difficulty. 

## Implementation Details

- **Emotion Prediction**: Utilizes a deep learning model trained on a dataset of labelled facial expressions and their corresponding emotions to predict emotions in real-time during gameplay.
- **Integration**: A machine learning model has been integrated into the game, and the game and emotion predictor are run concurrently using threads. The emotion information obtained from the predictor is then used by the game to dynamically adjust the difficulty level.
- **Model Architecture**: Utilized a Convolutional Neural Network (CNN) model implemented using the Keras API in Tensorflow. The model consists of repeated combinations of Convolutional, Batch Normalization, and Max pooling layers, with an activation function of ReLU.

## Getting Started

1. Make sure that the computer has a working camera device for the image capture purpose.
2. Clone this repository to your local machine.
3. Run `startVideoCapture.py` to start both the video capture and the game.

## Paper Reference

Refer to the [paper](https://link.springer.com/chapter/10.1007/978-981-99-2058-7_22) for a detailed implementation of this game.
