import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
import time
import requests
import io
import json

# Load the trained model
model = tf.keras.models.load_model('cotton_disease_model.h5')
with open('class_names.json', 'r') as f:
    class_names = json.load(f)

# Disease information database
disease_info = {
    'Aphids': {
        'sprinkle': True,
        'advice_en': 'Use insecticidal soap or neem oil. Introduce natural predators like ladybugs.',
        'advice_hi': 'कीटनाशक साबुन या नीम का तेल उपयोग करें। लेडीबग जैसे प्राकृतिक शिकारियों को पेश करें।',
        'pesticide_en': 'Imidacloprid, Acetamiprid, or Thiamethoxam',
        'pesticide_hi': 'इमिडाक्लोप्रिड, एसिटामिप्रिड, या थायमेथोक्सम'
    },
    'Army worm': {
        'sprinkle': True,
        'advice_en': 'Handpick worms or use biological controls like Bacillus thuringiensis (Bt).',
        'advice_hi': 'हाथ से इल्लियों को उठाएं या बैसिलस थुरिंजिएन्सिस (Bt) जैसे जैविक नियंत्रण का उपयोग करें।',
        'pesticide_en': 'Chlorantraniliprole, Spinosad, or Emamectin benzoate',
        'pesticide_hi': 'क्लोरान्ट्रानिलिप्रोल, स्पिनोसैड, या इमामेक्टिन बेंजोएट'
    },
    'Bacterial blight': {
        'sprinkle': True,
        'advice_en': 'Remove infected plants. Use copper-based bactericides and practice crop rotation.',
        'advice_hi': 'संक्रमित पौधों को हटा दें। तांबा-आधारित जीवाणुनाशक का उपयोग करें और फसल चक्रण का अभ्यास करें।',
        'pesticide_en': 'Copper oxychloride, Streptomycin, or Kasugamycin',
        'pesticide_hi': 'कॉपर ऑक्सीक्लोराइड, स्ट्रेप्टोमाइसिन, या कासुगामाइसिन'
    },
    'Cotton Boll Rot': {
        'sprinkle': True,
        'advice_en': 'Improve air circulation. Avoid overhead irrigation. Apply fungicides during flowering.',
        'advice_hi': 'हवा के संचार में सुधार करें। ऊपरी सिंचाई से बचें। फूल आने के दौरान कवकनाशी लगाएं।',
        'pesticide_en': 'Carbendazim, Mancozeb, or Propiconazole',
        'pesticide_hi': 'कार्बेन्डाजिम, मैंकोजेब, या प्रोपिकोनाजोल'
    },
    'Green Cotton Boll': {
        'sprinkle': False,
        'advice_en': 'No treatment needed. Maintain good agricultural practices.',
        'advice_hi': 'किसी उपचार की आवश्यकता नहीं है। अच्छी कृषि पद्धतियों को बनाए रखें।',
        'pesticide_en': 'None required',
        'pesticide_hi': 'आवश्यकता नहीं'
    },
    'Healthy': {
        'sprinkle': False,
        'advice_en': 'No treatment needed. Continue with regular monitoring and good agricultural practices.',
        'advice_hi': 'किसी उपचार की आवश्यकता नहीं है। नियमित निगरानी और अच्छी कृषि पद्धतियों को जारी रखें।',
        'pesticide_en': 'None required',
        'pesticide_hi': 'आवश्यकता नहीं'
    },
    'Powdery mildew': {
        'sprinkle': True,
        'advice_en': 'Improve air circulation. Apply sulfur-based or systemic fungicides.',
        'advice_hi': 'हवा के संचार में सुधार करें। गंधक-आधारित या प्रणालीगत कवकनाशी लगाएं।',
        'pesticide_en': 'Sulfur, Myclobutanil, or Tebuconazole',
        'pesticide_hi': 'सल्फर, माइक्लोब्यूटानिल, या टेबुकोनाजोल'
    },
    'Target spot': {
        'sprinkle': True,
        'advice_en': 'Remove infected leaves. Apply fungicides and practice crop rotation.',
        'advice_hi': 'संक्रमित पत्तियों को हटा दें। कवकनाशी लगाएं और फसल चक्रण का अभ्यास करें।',
        'pesticide_en': 'Chlorothalonil, Azoxystrobin, or Pyraclostrobin',
        'pesticide_hi': 'क्लोरोथैलोनिल, एज़ोक्सिस्ट्रोबिन, या पाइराक्लोस्ट्रोबिन'
    }
}

def preprocess_image(image):
    """Preprocess image for model prediction"""
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

def predict_disease(image):
    """Predict disease from image"""
    processed_image = preprocess_image(image)
    predictions = model.predict(processed_image, verbose=0)
    predicted_class_idx = np.argmax(predictions[0])
    predicted_class = class_names[predicted_class_idx]
    confidence = round(100 * np.max(predictions[0]), 2)
    return predicted_class, confidence

def capture_and_predict():
    """Capture image from camera and predict disease"""
    # Initialize camera (for Raspberry Pi camera module)
    camera = cv2.VideoCapture(0)
    
    # Set camera resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Camera initialized. Press 'c' to capture, 'q' to quit.")
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to capture image")
            break
            
        # Display the frame
        cv2.imshow('Cotton Disease Detection - Press c to capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Predict disease
            predicted_class, confidence = predict_disease(pil_image)
            
            # Get disease information
            disease_data = disease_info.get(predicted_class, {})
            
            # Prepare result
            result = {
                'disease': predicted_class,
                'confidence': confidence,
                'sprinkle': disease_data.get('sprinkle', False),
                'advice_en': disease_data.get('advice_en', ''),
                'advice_hi': disease_data.get('advice_hi', ''),
                'pesticide_en': disease_data.get('pesticide_en', ''),
                'pesticide_hi': disease_data.get('pesticide_hi', ''),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"Predicted: {predicted_class} ({confidence}%)")
            print(f"Sprinkle: {'Yes' if result['sprinkle'] else 'No'}")
            
            # Send to Streamlit server (if running)
            try:
                response = requests.post('http://localhost:8502/api/prediction', json=result)
                if response.status_code == 200:
                    print("Result sent to Streamlit UI")
            except:
                print("Streamlit server not available")
            
        elif key == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_predict()
