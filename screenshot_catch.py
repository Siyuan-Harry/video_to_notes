# 每隔30秒钟截一张图
# filename: save_screenshots.py

import cv2
import os

# Function to ensure the output directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

video_folder_path = 'cs224n_videos'
video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]

# Read the video frame by frame
for video_file in video_files:
    
    # Open the video file
    vc = cv2.VideoCapture(f"video_folder_path/{video_file}")

    # Check if the video was opened successfully
    if not vc.isOpened():
        print("Error: Could not open video.")
        exit()

    # Get the frames per second (fps) of the video
    fps = vc.get(cv2.CAP_PROP_FPS)

    # Calculate the number of frames to skip to take a screenshot every 30 seconds
    frame_interval = int(fps * 30)
    
    # Directory where screenshots will be saved
    output_directory = f'notes/screenshots/{video_file[:-4]}'
    ensure_dir(output_directory)
    
    # Frame counter
    frame_count = 0
    # Screenshot counter
    screenshot_count = 1
    while True:
        ret, frame = vc.read()
        if not ret:
            break

        # If the current frame is at the specified interval, save it as an image
        if frame_count % frame_interval == 0:
            # Construct image file path
            image_path = os.path.join(output_directory, f'Screenshot{screenshot_count}.jpg')
            # Save the image
            cv2.imwrite(image_path, frame)
            # Print information about the saved screenshot
            print(f"Screenshot{screenshot_count} saved at frame {frame_count}")
            screenshot_count += 1

        frame_count += 1

    # Release the video capture object
    vc.release()
    print('')
print("All screenshots have been saved.")