#include <windows.h>
#include <opencv2/opencv.hpp>
#include <vector>
#include <string>
#include <unordered_map>
#include <random>
#include <thread>
#include <chrono>
#include <filesystem>
#include "nn/autobackend.h"
#include <opencv2/opencv.hpp>
#include "utils/augment.h"
#include "constants.h"
#include "utils/common.h"
#include <wingdi.h>


// Global variables
HDC hdcScreen;
int screenWidth, screenHeight;

cv::Scalar generateRandomColor(int numChannels) {
    if (numChannels < 1 || numChannels > 3) {
        throw std::invalid_argument("Invalid number of channels. Must be between 1 and 3.");
    }

    std::random_device rd; 
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dis(0, 255);

    cv::Scalar color;
    for (int i = 0; i < numChannels; i++) {
        color[i] = dis(gen); // for each channel separately generate value
    }

    return color;
}

std::vector<cv::Scalar> generateRandomColors(int class_names_num, int numChannels) {
    std::vector<cv::Scalar> colors;
    for (int i = 0; i < class_names_num; i++) {
        cv::Scalar color = generateRandomColor(numChannels);
        colors.push_back(color);
    }
    return colors;
}

// Function to initialize screen drawing context
void initializeScreenDrawing() {
    hdcScreen = GetDC(NULL);
    screenWidth = GetSystemMetrics(SM_CXSCREEN);
    screenHeight = GetSystemMetrics(SM_CYSCREEN);
}

// Function to draw a rectangle on the screen
void drawRectangle(const cv::Rect_<float>& bbox, const cv::Scalar& color) {
    HPEN hPen = CreatePen(PS_SOLID, 2, RGB(color[2], color[1], color[0]));
    HPEN hOldPen = (HPEN)SelectObject(hdcScreen, hPen);
    
    // Set the brush to NULL_BRUSH to avoid filling the rectangle
    HBRUSH hBrush = (HBRUSH)GetStockObject(NULL_BRUSH);
    HBRUSH hOldBrush = (HBRUSH)SelectObject(hdcScreen, hBrush);

    // Draw the rectangle
    Rectangle(hdcScreen, 
        static_cast<int>(bbox.x), 
        static_cast<int>(bbox.y), 
        static_cast<int>(bbox.x + bbox.width), 
        static_cast<int>(bbox.y + bbox.height));

    SelectObject(hdcScreen, hOldBrush);
    SelectObject(hdcScreen, hOldPen);
    DeleteObject(hPen);
}

// Function to draw text on the screen
void drawText(const std::string& text, const cv::Point& position, const cv::Scalar& color) {
    SetTextColor(hdcScreen, RGB(color[2], color[1], color[0]));
    SetBkMode(hdcScreen, TRANSPARENT);
    TextOutA(hdcScreen, position.x, position.y, text.c_str(), text.length());
}

// Function to draw a circle on the screen
void drawCircle(const cv::Point& center, int radius, const cv::Scalar& color) {
    HBRUSH hBrush = CreateSolidBrush(RGB(color[2], color[1], color[0]));
    HBRUSH hOldBrush = (HBRUSH)SelectObject(hdcScreen, hBrush);
    
    Ellipse(hdcScreen, center.x - radius, center.y - radius, center.x + radius, center.y + radius);
    
    SelectObject(hdcScreen, hOldBrush);
    DeleteObject(hBrush);
}

// Function to get screen scaling factor
float getScreenScalingFactor() {

    SetProcessDPIAware(); //true
    HDC screen = GetDC(NULL);
    double hPixelsPerInch = GetDeviceCaps(screen,LOGPIXELSX); 
    double vPixelsPerInch = GetDeviceCaps(screen,LOGPIXELSY);
    ReleaseDC(NULL, screen);
    float scaleFactor = ((hPixelsPerInch + vPixelsPerInch) * 0.5)/96;
    return scaleFactor;
}

// Modified function to draw detection results directly on the screen
void drawDetectionResults(const std::vector<YoloResults>& results, const std::vector<cv::Scalar>& colors, const std::unordered_map<int, std::string>& names, float scalingFactor) {
    for (const auto& res : results) {
        cv::Rect_<int> bbox(res.bbox);
        drawRectangle(bbox, colors[res.class_idx]); 

        // Draw label
        std::string label = names.at(res.class_idx) + " " + std::to_string(res.conf);
        drawText(label, cv::Point(bbox.x, bbox.y - 5), colors[res.class_idx]);

        // Draw keypoints if available
        if (!res.keypoints.empty()) {
            for (size_t i = 0; i < res.keypoints.size(); i += 3) {
                int x = static_cast<int>(res.keypoints[i]);
                int y = static_cast<int>(res.keypoints[i + 1]);
                float conf = res.keypoints[i + 2];
                if (conf > 0.5) {
                    drawCircle(cv::Point(x, y), 3, cv::Scalar(0, 255, 0));
                }
            }
        }
    
        // Calculate the center of the bounding box
        int centerX = static_cast<int>((bbox.x + bbox.width / 2));
        int centerY = static_cast<int>((bbox.y + bbox.height / 2));

    }
}

std::string get_class_name(int class_idx, const std::unordered_map<int, std::string>& names) {
    auto it = names.find(class_idx);
    if (it != names.end()) {
        return it->second;
    } else {
        std::cerr << "Warning: class_idx not found in names for class_idx = " << class_idx << std::endl;
        // Then convert it to a string anyway
        return std::to_string(class_idx);
    }
}

// Function to simulate mouse click
void simulateMouseClick(int x, int y) {

    // Set the cursor position to the specified coordinates and perform the click
    SetCursorPos(x, y);
    mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0);
    mouse_event(MOUSEEVENTF_LEFTUP, x, y, 0, 0);
}

// Function to simulate keyboard input
void simulateKeyboardInput(const std::string& text) {
    for (char c : text) {
        SHORT vkey = VkKeyScan(c);
        UINT scanCode = MapVirtualKey(vkey & 0xff, 0);
        keybd_event(vkey & 0xff, scanCode, 0, 0);
        keybd_event(vkey & 0xff, scanCode, KEYEVENTF_KEYUP, 0);
    }
}

void clickButton(const std::vector<YoloResults>& detected_elements, const int& class_index = 0) {

    for (const auto& element : detected_elements) {
        if (element.class_idx == class_index) {

            // Calculate the center of the bounding box
            int centerX = static_cast<int>((element.bbox.x + element.bbox.width / 2));
            int centerY = static_cast<int>((element.bbox.y + element.bbox.height / 2));            

            simulateMouseClick(centerX, centerY); 
            std::cout << "Clicked " << element.class_idx << std::endl;
            return;
        }
    }
}

void clickInput(const std::vector<YoloResults>& detected_elements, const int& class_index, const std::string& text) {
    for (const auto& element : detected_elements) {
        if (element.class_idx == class_index) {

            // Calculate the center of the bounding box
            int centerX = static_cast<int>((element.bbox.x + element.bbox.width / 2));
            int centerY = static_cast<int>((element.bbox.y + element.bbox.height / 2));   

            simulateMouseClick(centerX, centerY);
            std::this_thread::sleep_for(std::chrono::seconds(2));

            simulateKeyboardInput(text);
            std::this_thread::sleep_for(std::chrono::seconds(2));

            return;
        }
    }
}

void clickSecurity(const std::vector<YoloResults>& detected_elements) {
    for (const auto& element : detected_elements) {
        if (element.class_idx == 17) { //securityinput

        // Calculate the center of the bounding box
        int centerX = static_cast<int>((element.bbox.x + element.bbox.width / 2));
        int centerY = static_cast<int>((element.bbox.y + element.bbox.height / 2));   

        simulateMouseClick(centerX, centerY);
        std::cout << "Clicked drop down" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(2));

        simulateMouseClick(centerX, centerY + 40);
        std::cout << "Clicked option" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(2));

        return;
        }
    }
}


void processElements(const std::vector<YoloResults>& detected_elements, std::unordered_map<int, std::string>& names) {
    for (const auto& element : detected_elements) {
        
        std::string class_name = get_class_name(element.class_idx, names);
        

        std::cout << "Label: " << class_name << ", Confidence: " << element.conf << ", Coordinates: " 
                  << element.bbox.x << ", " << element.bbox.y << ", " 
                  << element.bbox.x + element.bbox.width << ", " << element.bbox.y + element.bbox.height << std::endl;

        if (element.class_idx == 4 ) { //devicetitle
            std::cout << "Detected device name" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(2));
            clickInput(detected_elements, 6, "Computer-test");
            std::this_thread::sleep_for(std::chrono::seconds(2));

        } else if (element.class_idx == 10) { //nametitle
            std::cout << "Detected nametitle" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(2));
            clickInput(detected_elements, 6, "icsadmin");

        } else if (element.class_idx == 12 || element.class_idx == 2) { //passwordtitle & confirmtitle
            std::cout << "Detected passwordtitle" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(2));
            clickInput(detected_elements, 6, "Nova5455!");

        } else if (element.class_idx == 18) { //securitytitle
            std::cout << "Detected securitytitle" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(2));
            clickSecurity(detected_elements);
            clickInput(detected_elements, 6, "ics");

        } else if (element.class_idx == 19) { //setuptitle
            std::cout << "Detected setuptitle" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(2));
            clickButton(detected_elements, 15); //schooltitle
            std::this_thread::sleep_for(std::chrono::seconds(2));

        } else if (element.class_idx == 21) { //workschooltitle
            for (const auto& sub_element : detected_elements) {
                if (sub_element.class_idx == 5) { //domainjoin
                    clickButton(detected_elements, 5); //domainjoin
                    std::this_thread::sleep_for(std::chrono::seconds(2));

                } else if (sub_element.class_idx == 20) { //signinoptions
                    clickButton(detected_elements, 20); //signinoptions
                    std::this_thread::sleep_for(std::chrono::seconds(2));
                }
            }
        }
    }
    clickButton(detected_elements);
}


// Main function
int main() {
    // Initialize screen drawing
    initializeScreenDrawing();

    // Get screen scaling factor
    float scalingFactor = getScreenScalingFactor();
    std::cout << "Screen scaling factor: " << scalingFactor << std::endl;

    // Model parameters
    const std::string& modelPath = "best.onnx";
    const std::string& onnx_provider = OnnxProviders::CPU;
    const std::string& onnx_logid = "yolov8_inference2";
    float mask_threshold = 0.5f;
    float conf_threshold = 0.30f;
    float iou_threshold = 0.45f;
    int conversion_code = cv::COLOR_BGR2RGB;

    // Initialize the model
    AutoBackendOnnx model(modelPath.c_str(), onnx_logid.c_str(), onnx_provider.c_str());
    std::vector<cv::Scalar> colors = generateRandomColors(model.getNc(), model.getCh());
    std::unordered_map<int, std::string> names = model.getNames();


    while (true) {
        // Create a Mat object representing the entire screen
        cv::Mat screenMat(screenHeight, screenWidth, CV_8UC4);
        
        // Capture the screen content
        HDC memDC = CreateCompatibleDC(hdcScreen);
        HBITMAP hBitmap = CreateCompatibleBitmap(hdcScreen, screenWidth, screenHeight);
        HBITMAP hOldBitmap = (HBITMAP)SelectObject(memDC, hBitmap);
        BitBlt(memDC, 0, 0, screenWidth, screenHeight, hdcScreen, 0, 0, SRCCOPY);
        GetBitmapBits(hBitmap, screenWidth * screenHeight * 4, screenMat.data);
        
        // Convert the screen capture to the format expected by your model
        cv::Mat processedMat;
        cv::cvtColor(screenMat, processedMat, conversion_code);

        // Perform object detection
        std::vector<YoloResults> objs = model.predict_once(processedMat, conf_threshold, iou_threshold, mask_threshold, conversion_code);

        // Draw the results directly on the screen
        drawDetectionResults(objs, colors, names, scalingFactor);

        processElements(objs, names);

        // Clean up
        SelectObject(memDC, hOldBitmap);
        DeleteObject(hBitmap);
        DeleteDC(memDC);

        // Handle exit condition
        if (GetAsyncKeyState(VK_ESCAPE) & 0x8000) {
            break;
        }

        // Add a small delay to control the frame rate
        std::this_thread::sleep_for(std::chrono::seconds(3));
    }

    // Cleanup
    ReleaseDC(NULL, hdcScreen);

    return 0;
}