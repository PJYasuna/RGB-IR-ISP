# ISP for RGB-IR sensor

## Introduction

The rapid adoption of RGB-IR sensors in the automotive industry has revolutionized both day and night vision capabilities. These sensors have proven to be highly effective in capturing images by combining traditional RGB (Red, Green, Blue) channels with infrared (IR) information. However, the existing Image Signal Processing (ISP) techniques used for other types of sensors are not optimized for RGB-IR sensors. This project aims to address this challenge by developing an improved image processing pipeline specifically tailored for RGB-IR sensors.

The primary goal of this project is to enhance and implement an image processing pipeline, with a specific focus on improving the demosaicing process for the given RGB-IR Color Filter Array (CFA). Additionally, color correction techniques will be applied to further refine the output. The desired outcome of the project is to generate high-quality, color-corrected RGB images along with interpolated IR images.

In the following sections of this report, we will delve into the methodology, implementation details, and results obtained through the development of the image processing pipeline for RGB-IR sensors.

## Preliminaries

### RGB-IR camera

Modern color cameras commonly incorporate a Color Filter Array (CFA) with a Bayer BGGR pattern. However, the sensitivity of the RGB channels allows them to capture both visible and infrared (IR) wavelengths, resulting in diminished quality of the final RGB image due to color distortion. Moreover, accurately measuring the intensity of IR light in captured images becomes challenging.

Traditionally, an IR cut filter was employed in daytime imaging to prevent IR light from reaching the sensor, while it was mechanically removed during nighttime to aid low-light imaging using IR light. However, the mechanical nature of this component leads to wear and tear, negatively impacting the longevity of camera systems.

To address these challenges in embedded camera systems, an RGB-IR camera has been developed. This camera utilizes a novel CFA design featuring dedicated pixels for capturing both visible and IR light. Consequently, it becomes possible to capture images in both visible and IR spectrums without requiring a mechanical switch, while also preventing color distortion. This article explores the operational principles of an RGB-IR camera, its advantages, and its suitability for various embedded vision applications, outperforming conventional cameras in these scenarios.

As mentioned before, the standard Bayer CFA comes with a BGGR pattern. The below image represents the pixels in the Bayer format.

But an RGB-IR camera comes with an additional set of pixels that are dedicated to allow only light in the IR spectrum to pass through them. Presence of these pixels facilitates multi-band imaging. Many sensor manufacturers have developed this new CFA that comes with a combination or R,G,B, and IR pixels as shown in the image below:

Having an RGB-IR filter alone is not enough to effectively use the imaging technique. It is important to choose the right camera components such as the sensor, lens, and ISP (Image Signal Processor) that support RGB-IR imaging.

### ISP

An ISP is an application processor used for digital image processing, specifically for converting RAW images from imaging sensors to RGB/YUV images for further processing or display. 

The proposed ISP pipeline includes the following modules: DPC (dead pixel correction), BLC (black level compensation), ANF (anti-aliasing noise filter), AWB (auto white balance gain control), CFA (color filter array interpolation), CNF (chroma noise filtering), CCM (color correction matrix), GAC (gamma correction), CSC (color space conversion), NLM (Non-Local Means denoising), BNF (bilateral noise filtering), NF (noise filter for luma and chroma), EE (edge enhancement), FCS (false color suppression), HSC (hue/saturation/control), and BCC (brightness/contrast control)

## Methodology

### Pipeline for the ISP

For a comprehensive understanding of the fundamental modules involved in Image Signal Processing (ISP), the [document](https://github.com/cruxopen/openISP/tree/master/docs) provided serves as a valuable resource. It offers detailed insights into the essential components that constitute an ISP pipeline and their respective functionalities.

### Color Interpolation Method

#### Replacing R with B

The proposed method for RGB-NIR filter sampling utilizes a 5x5 matrix to extract B and R pixel information, which is then used to replace corresponding pixels that match the Bayer pattern pixel location. In order to convert the R pixels in the G/B row of the Bayer CFA, the B channel values within the 5x5 matrix are summed and averaged to determine the replacement value for the B pixel at the R location.

#### Replacing IR with R

To convert the IR pixels in the G/R row of the Bayer CFA, a two-step process is employed using both a positive oblique direction and a negative oblique direction for sampling. Within the 5x5 matrix, a 3x3 sub-matrix is used to convert the IRLeft-up and IRRight-down pixels from the surrounding positive oblique R pixels. Similarly, the IRRight-up and IRLeft-down pixels are converted from the surrounding negative oblique R pixels. 

Finally the RGB-IR pattern is converted to BGGR pattern.

### Extracting Interpolated IR Image

The objective of this step is to extract the interpolated IR image from the RGB-IR image using bilinear interpolation. It is important to note that for the IR image, only the IR channel information should be taken into consideration. To achieve this, the 4x4 matrix is divided into 2x2 sub-matrices, and within each sub-matrix, interpolation is performed for the pixels N1, N2, and N3 using the IR information.

For N1, the interpolation is calculated as follows:

$IR_{N1} = \frac{IR_{top} + IR_{tl} + IR_{left} + IR}{4}$

For N2, the interpolation is calculated as follows:

$IR_{N2} = \frac{IR_{top} + IR}{2}$

For N3, the interpolation is calculated as follows:

$IR_{N3} = \frac{IR_{left} + IR}{2}$

In summary, these equations describe the process of interpolating the IR values for the pixels N1, N2, and N3 within each 2x2 sub-matrix of the RGB-IR image. By considering only the IR channel information and applying bilinear interpolation, an interpolated IR image can be obtained, providing enhanced details specifically for the IR component.

## Implementation

### fast-open RGB-IR ISP

the code is in ./fast-openISP

The code is based on [hdr plus/fast open-ISP](https://github.com/QiuJueqin/fast-openISP). repository. A significant enhancement has been made by introducing a new module called Split and Interpolation (SI). This module is responsible for extracting the RGB image in the BGGR pattern and generating an interpolated IR image.

The subsequent module in the pipeline focuses on processing the RGB image to obtain a color-corrected RGB image that can be seamlessly integrated with the functionality of traditional ISP modules.

By incorporating the SI module, the code has been enhanced to effectively split and interpolate the RGB image data while ensuring compatibility with the existing ISP modules. This advancement contributes to the overall improvement of the image processing pipeline, allowing for more accurate and refined color correction of the RGB image.

### Usage

In ./fast-openISP directory

run

```
python demo.py
```

The ISP outputs will be saved to `./output` directory.

The only required package for pipeline execution is `numpy`. `opencv-python` and `scikit-image` are required only for data IO.

### Analysis

In the CCM (Color Correction Matrix) module, a new color correction matrix needs to be designed since the specific matrix values are not provided. This new matrix will be responsible for color correcting the given image. While the resulting color correction may not achieve perfection, every effort has been made to devise an effective matrix design that yields the best possible results.

The pipeline result shows that we can generate RGB correction image and interpolation IR image successfully from this RGB-IR ISP.

## Conclusion

In this project, we developed an image processing pipeline specifically designed for RGB-IR sensors, with a focus on improving the demosaicing process and color correction techniques. The objective was to enhance the image quality and accuracy of RGB images while generating interpolated IR images.

By incorporating the Split and Interpolation (SI) module into the existing codebase, we were able to extract RGB images in the BGGR pattern and generate interpolated IR images effectively. This advancement significantly improved the image processing pipeline, making it compatible with RGB-IR sensor.

The implementation of the color interpolation method successfully converted the RGB-IR pattern to the desired BGGR pattern, allowing for better integration with conventional ISP algorithms. The CCM module played a crucial role in color correction, although a new color correction matrix had to be designed since specific matrix values were not provided. Despite the absence of a perfect solution, The efforts in devising an effective matrix design yielded satisfactory results in color correcting the given images.

Overall, the developed image processing pipeline demonstrated its capability to generate high-quality, color-corrected RGB images and interpolated IR images. 

## Reference

[1] Park H.S. (2016) Architectural Analysis of a Baseline ISP Pipeline. In: Kyung CM. (eds) Theory and Applications of Smart Cameras. KAIST Research Series. Springer, Dordrecht.

[2] Y. -K. Lai, Y. -H. Huang and Y. -L. Lai, "Color Interpolation with Full Resolution for Hybrid RGB-IR CMOS Sensor," *2023 IEEE International Conference on Consumer Electronics (ICCE)*, Las Vegas, NV, USA, 2023, pp. 1-2, doi: 10.1109/ICCE56470.2023.10043554.
