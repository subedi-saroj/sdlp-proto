
originalImage = imread('1920x20000-1bit-inverted.bmp');  
newSize = [6840, 1920];
resizedImage = imresize(originalImage, newSize);

imwrite(resizedImage, '1_1920x6840.bmp'); 
%%
% Specify the input BMP file and output PNG file
inputFileName = '1.bmp';  % Replace with your input BMP file name
outputFileName = '1.png';  % Replace with your desired output PNG file name

% Read the BMP image
imageData = imread(inputFileName);

% Write the image data to a new PNG file
imwrite(imageData, outputFileName);

%%
clear all;
clc;
%modifying the image
im = imread('1_1920x6840.bmp');
for i = 5794:6840
    for j = 1:1920
        im(i,j) = 0;
    end
end
for i = 1:20
    for j = 1:1920
        im(i,j) = 1;
    end
end
for i = 6820:6840
    for j = 1:1920
        im(i,j) = 1;
    end
end
imshow(im);
imwrite(im, '1_1920x6840_modified.bmp'); 
