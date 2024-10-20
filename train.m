% Step 1: Load and Split the Dataset
% ------------------------------------
dataFolder = 'The folder of your dataset';  % Update with the path to your dataset
imds = imageDatastore(dataFolder, 'IncludeSubfolders', true, 'LabelSource', 'foldernames');

% Display the number of images per label
tbl = countEachLabel(imds);
disp(tbl);

% Resize the images to a fixed size (224x224) for the CNN
imds.ReadFcn = @(loc)imresize(imread(loc), [224, 224]);

% Split data into training and validation sets (80% training, 20% validation)
[imdsTrain, imdsValidation] = splitEachLabel(imds, 0.8, 'randomized');

% Step 2: Define a Custom Convolutional Neural Network (CNN) Architecture
% -----------------------------------------------------------------------
numClasses = numel(categories(imdsTrain.Labels));  % Automatically get the number of classes (12 in this case)

layers = [
    imageInputLayer([224 224 3], 'Name', 'input')  % Input layer for 224x224 RGB images
    
    convolution2dLayer(3, 32, 'Padding', 'same', 'Name', 'conv_1')  % Conv layer 1
    batchNormalizationLayer('Name', 'bn_1')  % Batch normalization layer
    reluLayer('Name', 'relu_1')  % ReLU activation
    
    maxPooling2dLayer(2, 'Stride', 2, 'Name', 'pool_1')  % Max pooling layer
    
    convolution2dLayer(3, 64, 'Padding', 'same', 'Name', 'conv_2')  % Conv layer 2
    batchNormalizationLayer('Name', 'bn_2')  % Batch normalization layer
    reluLayer('Name', 'relu_2')  % ReLU activation
    
    maxPooling2dLayer(2, 'Stride', 2, 'Name', 'pool_2')  % Max pooling layer
    
    convolution2dLayer(3, 128, 'Padding', 'same', 'Name', 'conv_3')  % Conv layer 3
    batchNormalizationLayer('Name', 'bn_3')  % Batch normalization layer
    reluLayer('Name', 'relu_3')  % ReLU activation
    
    maxPooling2dLayer(2, 'Stride', 2, 'Name', 'pool_3')  % Max pooling layer
    
    fullyConnectedLayer(512, 'Name', 'fc1')  % Fully connected layer 1
    reluLayer('Name', 'relu_fc1')  % ReLU activation
    
    fullyConnectedLayer(numClasses, 'Name', 'fc2')  % Fully connected layer 2 (for 12 classes)
    softmaxLayer('Name', 'softmax')  % Softmax activation for classification
    classificationLayer('Name', 'classoutput')  % Classification output layer
];

% Step 3: Set Up Training Options
% -------------------------------
options = trainingOptions('sgdm', ...
    'MiniBatchSize', 32, ...
    'MaxEpochs', 15, ...  % Adjust number of epochs as necessary
    'InitialLearnRate', 0.001, ...
    'ValidationData', imdsValidation, ...
    'ValidationFrequency', 5, ...
    'Verbose', false, ...
    'Plots', 'training-progress');  % Visualize training progress

% Step 4: Train the Network
% -------------------------
[trainedNet, trainInfo] = trainNetwork(imdsTrain, layers, options);

% Step 5: Evaluate the Trained Network
% ------------------------------------
% Classify the validation images using the trained network
predictedLabels = classify(trainedNet, imdsValidation);
trueLabels = imdsValidation.Labels;

% Calculate the validation accuracy
accuracy = mean(predictedLabels == trueLabels);
disp(['Validation Accuracy: ', num2str(accuracy * 100), '%']);

% Step 6: Test the Model with a New Image
% ---------------------------------------
% Load a test image (replace 'path_to_test_image.jpg' with an actual image path)
testImage = imread('Load your test image');
testImage = imresize(testImage, [224 224]);  % Resize to network input size
predictedLabel = classify(trainedNet, testImage);
disp(['Predicted label: ', char(predictedLabel)]);

% Step 7: Visualize the Confusion Matrix
% --------------------------------------
confMat = confusionmat(trueLabels, predictedLabels);
confusionchart(confMat);
