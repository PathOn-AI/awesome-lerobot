import cv2
import platform

def test_640x480_compatibility():
    """Test if camera can be set to 640x480 resolution"""
    
    print("=== Testing 640x480 Resolution Compatibility ===\n")
    
    # Test all available cameras for 640x480 support
    available_cameras = []
    for i in range(10):
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            available_cameras.append(i)
            camera.release()
        else:
            camera.release()
    
    print(f"Available cameras: {available_cameras}\n")
    
    for camera_idx in available_cameras:
        print(f"--- Testing Camera {camera_idx} ---")
        
        # Test different backends for macOS
        backends_to_test = []
        if platform.system() == "Darwin":
            backends_to_test = [
                ("CAP_AVFOUNDATION", cv2.CAP_AVFOUNDATION),
                ("CAP_ANY", cv2.CAP_ANY)
            ]
        else:
            backends_to_test = [("CAP_ANY", cv2.CAP_ANY)]
        
        for backend_name, backend in backends_to_test:
            print(f"  Testing with {backend_name}:")
            
            camera = cv2.VideoCapture(camera_idx, backend)
            
            if not camera.isOpened():
                print(f"    ❌ Cannot open with {backend_name}")
                continue
            
            # Get current settings
            original_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            original_fps = camera.get(cv2.CAP_PROP_FPS)
            
            print(f"    📐 Default: {original_width}x{original_height} @ {original_fps:.2f} FPS")
            
            # Try to set 640x480
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Check what we got
            actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = camera.get(cv2.CAP_PROP_FPS)
            
            if actual_width == 640 and actual_height == 480:
                print(f"    ✅ SUCCESS! 640x480 @ {actual_fps:.2f} FPS")
                print(f"    🎯 Camera {camera_idx} with {backend_name} supports 640x480!")
                
                # Test if we can actually capture a frame
                ret, frame = camera.read()
                if ret and frame is not None:
                    print(f"    📷 Frame capture test: SUCCESS (shape: {frame.shape})")
                else:
                    print(f"    ❌ Frame capture test: FAILED")
                    
            else:
                print(f"    ❌ FAILED: Got {actual_width}x{actual_height} instead of 640x480")
            
            camera.release()
        
        print()

def test_manual_camera_settings():
    """Test manual camera settings that might help"""
    
    print("=== Manual Camera Settings Test ===\n")
    
    camera = cv2.VideoCapture(0)  # Use first camera
    
    if not camera.isOpened():
        print("❌ Cannot open camera 0")
        return
    
    print("Testing manual property settings...")
    
    # Properties that might affect resolution support
    properties_to_test = [
        ("AUTO_EXPOSURE", cv2.CAP_PROP_AUTO_EXPOSURE, [0, 1, 0.25, 0.75]),
        ("EXPOSURE", cv2.CAP_PROP_EXPOSURE, [-5, -3, -1]),
        ("GAIN", cv2.CAP_PROP_GAIN, [0, 1, 2]),
        ("BRIGHTNESS", cv2.CAP_PROP_BRIGHTNESS, [0, 0.5, 1]),
        ("CONTRAST", cv2.CAP_PROP_CONTRAST, [0, 0.5, 1]),
    ]
    
    # Get original values
    original_settings = {}
    for prop_name, prop_id, _ in properties_to_test:
        original_settings[prop_name] = camera.get(prop_id)
        print(f"Original {prop_name}: {original_settings[prop_name]}")
    
    print("\nTesting combinations...")
    
    # Try different property combinations
    test_combinations = [
        {"AUTO_EXPOSURE": 0},  # Manual exposure
        {"AUTO_EXPOSURE": 1},  # Auto exposure
        {"AUTO_EXPOSURE": 0, "EXPOSURE": -3},  # Manual exposure with specific value
        {"GAIN": 0, "BRIGHTNESS": 0.5},  # Lower gain, medium brightness
    ]
    
    for i, settings in enumerate(test_combinations):
        print(f"\n--- Test {i+1}: {settings} ---")
        
        # Apply settings
        for prop_name, value in settings.items():
            prop_id = next(pid for pname, pid, _ in properties_to_test if pname == prop_name)
            camera.set(prop_id, value)
        
        # Try to set 640x480
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        # Check result
        actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = camera.get(cv2.CAP_PROP_FPS)
        
        if actual_width == 640 and actual_height == 480:
            print(f"✅ SUCCESS with settings: {settings}")
            print(f"   Resolution: {actual_width}x{actual_height} @ {actual_fps:.2f} FPS")
        else:
            print(f"❌ Failed: Got {actual_width}x{actual_height}")
    
    camera.release()

def check_camera_formats():
    """Check supported camera formats"""
    
    print("=== Checking Camera Formats ===\n")
    
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Cannot open camera")
        return
    
    # Common formats to test
    formats = [
        ("MJPG", cv2.VideoWriter_fourcc(*'MJPG')),
        ("YUYV", cv2.VideoWriter_fourcc(*'YUYV')),
        ("YUY2", cv2.VideoWriter_fourcc(*'YUY2')),
        ("H264", cv2.VideoWriter_fourcc(*'H264')),
    ]
    
    print("Testing different video formats...")
    
    for format_name, fourcc in formats:
        print(f"\n--- Testing {format_name} format ---")
        
        # Set format
        camera.set(cv2.CAP_PROP_FOURCC, fourcc)
        
        # Try 640x480
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = camera.get(cv2.CAP_PROP_FPS)
        
        if actual_width == 640 and actual_height == 480:
            print(f"✅ {format_name}: 640x480 @ {actual_fps:.2f} FPS - WORKS!")
        else:
            print(f"❌ {format_name}: Got {actual_width}x{actual_height}")
    
    camera.release()

# Initialize camera

def list_available_cameras():
    """
    Find all available cameras
    """
    print("=== Available Cameras ===")
    available_cameras = []
    
    for i in range(10):  # Check first 10 camera indices
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            available_cameras.append(i)
            print(f"Camera {i}: Available")
            camera.release()
        else:
            camera.release()
    
    if not available_cameras:
        print("No cameras found")
    
    return available_cameras

cameras = list_available_cameras()

for camera_idx in cameras:
    camera = cv2.VideoCapture(0)  # Use 0 for default camera

    if camera.isOpened():
        print(f"Camera {camera_idx} is available")
        # Check the three properties
        actual_fps = camera.get(cv2.CAP_PROP_FPS)
        actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        # Display the values
        print(f"FPS: {actual_fps}")
        print(f"Width: {int(actual_width)}")
        print(f"Height: {int(actual_height)}")
        print(f"Resolution: {int(actual_width)}x{int(actual_height)}")
        
        camera.release()
    else:
        print("Could not open camera")

test_640x480_compatibility()
print("-" * 60)
test_manual_camera_settings()
print("-" * 60)
check_camera_formats()