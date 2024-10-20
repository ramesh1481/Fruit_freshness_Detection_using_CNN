% Step 1: Load the trained model
% ------------------------------
load('train.mat','traninedNet.mat');  % Load the trained network saved as 'train.mat'

% Step 2: Test the model with a new image
% ---------------------------------------
% Specify the path to the test image
testImagePath = "Your image path";  % Update this path if necessary

% Load and resize the test image to match the network input size (224x224)
testImage = imread(testImagePath);
testImage = imresize(testImage, [224 224]);

% Classify the test image using the trained network
predictedLabel = classify(trainedNet, testImage);

% Display the predicted label
disp(['Predicted label for the test image: ', char(predictedLabel)]);

% Step 3: Visualize the test image and predicted label
% ----------------------------------------------------
imshow(testImage);  % Display the test image
title(['Predicted Label: ', char(predictedLabel)]);  % Show the predicted label as the image title
