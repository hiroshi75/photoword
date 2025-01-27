from PIL import Image
import io

def test_image_loading():
    """Test that we can properly load and process the test image."""
    print("Testing image loading...")
    
    try:
        # Read and verify the test image
        with open('test_image/test1_restaurant.jpg', 'rb') as f:
            image_data = f.read()
            
        # Try to open the image with PIL
        img = Image.open(io.BytesIO(image_data))
        print(f'Success!')
        print(f'Image format: {img.format}')
        print(f'Image size: {img.size}')
        print(f'Image mode: {img.mode}')
        return True
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

if __name__ == "__main__":
    test_image_loading()
