import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Smart Cotton Doctor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2e7d32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #388e3c;
        margin-bottom: 1rem;
    }
    .result-card {
        background-color: #f1f8e9;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #4caf50;
    }
    .disease-card {
        background-color: #ffebee;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #f44336;
    }
    .healthy-card {
        background-color: #e8f5e8;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #4caf50;
    }
    .sprinkle-yes {
        color: #f44336;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .sprinkle-no {
        color: #4caf50;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Disease information database (same as in camera script)
disease_info = {
    'Aphids': {
        'sprinkle': True,
        'advice_en': 'Small sap-sucking insects that weaken plants. They cause curling and yellowing of leaves.',
        'advice_hi': 'छोटे कीट जो पौधों का रस चूसते हैं और पौधों को कमजोर करते हैं। वे पत्तियों के मुड़ने और पीले पड़ने का कारण बनते हैं।',
        'pesticide_en': 'Imidacloprid, Acetamiprid, or Thiamethoxam',
        'pesticide_hi': 'इमिडाक्लोप्रिड, एसिटामिप्रिड, या थायमेथोक्सम',
        'severity': 'Moderate'
    },
    'Army worm': {
        'sprinkle': True,
        'advice_en': 'Caterpillars that feed on leaves and can defoliate plants completely.',
        'advice_hi': 'इल्लियाँ जो पत्तियों को खाती हैं और पौधों को पूरी तरह से पत्तीविहीन कर सकती हैं।',
        'pesticide_en': 'Chlorantraniliprole, Spinosad, or Emamectin benzoate',
        'pesticide_hi': 'क्लोरान्ट्रानिलिप्रोल, स्पिनोसैड, या इमामेक्टिन बेंजोएट',
        'severity': 'High'
    },
    'Bacterial blight': {
        'sprinkle': True,
        'advice_en': 'Bacterial disease causing water-soaked lesions that turn brown and angular leaf spots.',
        'advice_hi': 'जीवाणु जनित रोग जो पानी से भरे घाव पैदा करता है जो भूरे हो जाते हैं और कोणीय पत्ती के धब्बे पैदा करते हैं।',
        'pesticide_en': 'Copper oxychloride, Streptomycin, or Kasugamycin',
        'pesticide_hi': 'कॉपर ऑक्सीक्लोराइड, स्ट्रेप्टोमाइसिन, या कासुगामाइसिन',
        'severity': 'High'
    },
    'Cotton Boll Rot': {
        'sprinkle': True,
        'advice_en': 'Fungal disease causing bolls to rot and turn black. Favored by humid conditions.',
        'advice_hi': 'फफूंदी जनित रोग जो टिंडों को सड़ने और काला करने का कारण बनता है। आर्द्र परिस्थितियों में फलता-फूलता है।',
        'pesticide_en': 'Carbendazim, Mancozeb, or Propiconazole',
        'pesticide_hi': 'कार्बेन्डाजिम, मैंकोजेब, या प्रोपिकोनाजोल',
        'severity': 'Moderate'
    },
    'Green Cotton Boll': {
        'sprinkle': False,
        'advice_en': 'Healthy cotton boll in development stage. No treatment needed.',
        'advice_hi': 'विकास के चरण में स्वस्थ कपास की टिंडी। किसी उपचार की आवश्यकता नहीं है।',
        'pesticide_en': 'None required',
        'pesticide_hi': 'आवश्यकता नहीं',
        'severity': 'None'
    },
    'Healthy': {
        'sprinkle': False,
        'advice_en': 'Healthy cotton plant with no signs of disease. Continue good practices.',
        'advice_hi': 'स्वस्थ कपास का पौधा जिसमें रोग के कोई लक्षण नहीं हैं। अच्छी प्रथाएं जारी रखें।',
        'pesticide_en': 'None required',
        'pesticide_hi': 'आवश्यकता नहीं',
        'severity': 'None'
    },
    'Powdery mildew': {
        'sprinkle': True,
        'advice_en': 'Fungal disease appearing as white powdery spots on leaves and stems.',
        'advice_hi': 'फफूंदी जनित रोग जो पत्तियों और तनों पर सफेद पाउडर जैसे धब्बे के रूप में दिखाई देता है।',
        'pesticide_en': 'Sulfur, Myclobutanil, or Tebuconazole',
        'pesticide_hi': 'सल्फर, माइक्लोब्यूटानिल, या टेबुकोनाजोल',
        'severity': 'Moderate'
    },
    'Target spot': {
        'sprinkle': True,
        'advice_en': 'Fungal disease causing target-like spots with concentric rings on leaves.',
        'advice_hi': 'फफूंदी जनित रोग जो पत्तियों पर निशाने जैसे धब्बे पैदा करता है जिनमें संकेंद्रित वलय होते हैं।',
        'pesticide_en': 'Chlorothalonil, Azoxystrobin, or Pyraclostrobin',
        'pesticide_hi': 'क्लोरोथैलोनिल, एज़ोक्सिस्ट्रोबिन, या पाइराक्लोस्ट्रोबिन',
        'severity': 'Moderate'
    }
}

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = []
if 'current_prediction' not in st.session_state:
    st.session_state.current_prediction = None

# API endpoint for receiving predictions
@st.experimental_memo
def receive_prediction(prediction_data):
    """Receive prediction from Raspberry Pi"""
    st.session_state.current_prediction = prediction_data
    st.session_state.predictions.append(prediction_data)
    return {"status": "success"}

# Main app
def main():
    st.markdown('<h1 class="main-header">🌿 Smart Cotton Doctor</h1>', unsafe_allow_html=True)
    st.markdown('### Real-time Cotton Disease Detection & Recommendation System')
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Live Detection", "History", "Disease Information"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="sub-header">Live Camera Feed</div>', unsafe_allow_html=True)
            
            # Placeholder for camera feed
            camera_placeholder = st.empty()
            camera_placeholder.info("Waiting for Raspberry Pi camera connection...")
            
            # Capture button
            if st.button("📷 Capture & Analyze", use_container_width=True):
                # This would trigger the Raspberry Pi to capture an image
                st.info("Sending capture command to Raspberry Pi...")
                # In a real implementation, you'd send a command to the Pi here
        
        with col2:
            st.markdown('<div class="sub-header">Analysis Results</div>', unsafe_allow_html=True)
            
            if st.session_state.current_prediction:
                prediction = st.session_state.current_prediction
                disease_data = disease_info.get(prediction['disease'], {})
                
                if disease_data.get('sprinkle', False):
                    st.markdown(f'<div class="disease-card">', unsafe_allow_html=True)
                    st.error("🚨 DISEASE DETECTED")
                else:
                    st.markdown(f'<div class="healthy-card">', unsafe_allow_html=True)
                    st.success("✅ PLANT IS HEALTHY")
                
                st.metric("Detected Disease", prediction['disease'])
                st.metric("Confidence Level", f"{prediction['confidence']}%")
                
                if disease_data.get('sprinkle', False):
                    st.markdown(f'<p class="sprinkle-yes">🔴 SPRINKLE: YES</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="sprinkle-no">🟢 SPRINKLE: NO</p>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Advice section
                st.markdown("### 🌱 Farmer Advice")
                
                col_advice1, col_advice2 = st.columns(2)
                
                with col_advice1:
                    st.markdown("**English**")
                    st.info(disease_data.get('advice_en', ''))
                    if disease_data.get('sprinkle', False):
                        st.warning(f"**Recommended Pesticide:** {disease_data.get('pesticide_en', '')}")
                
                with col_advice2:
                    st.markdown("**Hindi**")
                    st.info(disease_data.get('advice_hi', ''))
                    if disease_data.get('sprinkle', False):
                        st.warning(f"**सुझाया गया कीटनाशक:** {disease_data.get('pesticide_hi', '')}")
                
                # Severity and timestamp
                st.caption(f"Severity: {disease_data.get('severity', 'Unknown')} • Detected at: {prediction.get('timestamp', '')}")
            else:
                st.info("No analysis results yet. Capture an image to begin.")
    
    with tab2:
        st.markdown('<div class="sub-header">Detection History</div>', unsafe_allow_html=True)
        
        if st.session_state.predictions:
            # Convert to DataFrame for display
            history_df = pd.DataFrame(st.session_state.predictions)
            
            # Add sprinkle recommendation
            history_df['Sprinkle'] = history_df['disease'].apply(
                lambda x: 'Yes' if disease_info.get(x, {}).get('sprinkle', False) else 'No'
            )
            
            # Display table
            st.dataframe(
                history_df[['timestamp', 'disease', 'confidence', 'Sprinkle']],
                use_container_width=True
            )
            
            # Download button
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="Download History as CSV",
                data=csv,
                file_name="cotton_disease_history.csv",
                mime="text/csv"
            )
        else:
            st.info("No detection history available yet.")
    
    with tab3:
        st.markdown('<div class="sub-header">Cotton Disease Information</div>', unsafe_allow_html=True)
        
        selected_disease = st.selectbox(
            "Select a disease to learn more:",
            list(disease_info.keys())
        )
        
        if selected_disease:
            info = disease_info[selected_disease]
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown("**English Information**")
                st.write(f"**Disease:** {selected_disease}")
                st.write(f"**Sprinkle Recommended:** {'Yes' if info['sprinkle'] else 'No'}")
                st.write(f"**Severity:** {info.get('severity', 'Unknown')}")
                st.write("**Advice:**")
                st.info(info['advice_en'])
                if info['sprinkle']:
                    st.write("**Recommended Pesticides:**")
                    st.warning(info['pesticide_en'])
            
            with col_info2:
                st.markdown("**Hindi Information**")
                st.write(f"**रोग:** {selected_disease}")
                st.write(f"**छिड़काव सिफारिश:** {'हाँ' if info['sprinkle'] else 'नहीं'}")
                st.write(f"**गंभीरता:** {info.get('severity', 'अज्ञात')}")
                st.write("**सलाह:**")
                st.info(info['advice_hi'])
                if info['sprinkle']:
                    st.write("**सुझाया गया कीटनाशक:**")
                    st.warning(info['pesticide_hi'])

# Run the app
if __name__ == "__main__":
    main()
