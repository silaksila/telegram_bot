import cv2
import numpy as np
import math
import pytesseract
import re


def find_sudoku_grid(img_file_path, reserve=20):
    """Find sudoku grid on image and return cropped"""
    # TODO
    img = cv2.imread(img_file_path)
    grey_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(grey_scale, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # img = cv2.adaptiveThreshold(
    #     img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
    cv2.imshow("a", img)
    cv2.waitKey(0)
    return img


def get_num_from_img(img):
    custom_config = r'--oem 3 --psm 11'
    s= pytesseract.image_to_string(img, config=custom_config)
    return s

img = find_sudoku_grid("img.png")
s = get_num_from_img(img)
print(s)