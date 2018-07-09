# Face Detection Module

## Configuration
Open ```/modules/camCollectionPoint/config/collectionPoint.conf``` in your favorite text editor and configure to your needs:

Property|Description
--- | ---
`use_ids_camera`| if your using an IDS camera set use_ids_camera to True.  If this is set to false then opencv will just grab the first camera device it finds.
`primary_target`| this should be set to "closest", in the future more target modes may be added
`closest_threshold`| closest threshold is the amount larger a face must appear to become the primary target while under "closest" mode
`capture_width`| camera width to capture. you may need to mess with this to fit your camera and area.  Also this setting will affect frame speed and tracker.  Too low you cant recognize a face, distance is limited.  Too high the frame speed will drop and throw off the object tracking, and dectection time may suffer and api hits will go up.
`capture_height`| camera image height to capture.  see notes for capture_width about the impact this setting has on the overall system.
`target_face_width`| is the width we target for sending to ML for detection.  This is the ideal size and larger will be scaled down and smaller will be scaled up
 `min_face_width`, `min_face_height`| these settings are used for tuning the range.  This is the min size of a face object.  So if the face is way in the background and below the sizes outlined we ignore them.
|`face_pixel_buffer`| number of pixels added around the detected face, helps with detecting accuracy in cases where the face is clipped at the edges
`horizontal_velocity_buffer`, `vertical_velocity_buffer`| velocity is used to check whether trackers are the same face, in percent of pixels/second (higher velocity, less certain of exact face location due to frame rates)
`use_velocity`| boolean to describe whether to track the velocity of objects and use this velocity to avoid creating duplicate trackers. Useful when the frame rate is low and objects are moving quickly.
`collection_threshold`| how many seconds to wait between collection events, smooths out noise and random variability at the cost of speed of detection
`show_video_stream`| This will toggle on a opencv window to show you what the camera is seeing.  There is overhead to running this so expect the system to respond a bit slower when this is set to true.
`min_nearest_neighbors`| This helps you tune the face object detection phase. So if your picking up too maybe false faces turn it up.  Not picking up faces turn the number down.  default is 7
`show_blobs`| Toggles the camera 'blob' event. The blob event sends the entire camera capture image with bounding boxes from the object detection applied. Image is sent with data type and image as a base64 jpeg string. 
`compression_factor`\*|
`pixel_clock`\* |

\* We had to tune these settings to help make this solution work over a usb extender.  If camera is directly connected to compute device then this settings can be moved up.  [See reference.](https://en.ids-imaging.com/tl_files/downloads/techtip/TechTip_PixelClock_EN.pdf "IDS Tech Tip - Pixel Clock")

