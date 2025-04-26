
import streamlit as st
import pickle
import numpy as np
import pandas as pd

st.set_page_config(page_title="Apartment Price Prediction", layout="centered")

@st.cache_resource
def load_model():
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model

model = load_model()



st.title("Daire Fiyat Tahmin Uygulaması")
st.write("\nBu uygulama ile daire özelliklerine göre tahmini fiyatı öğrenebilirsiniz.")

# Kullanıcıdan veri alma
st.header("Daire Özelliklerini Seçin:")

rooms = st.slider("Oda Sayısı", 1, 10, 3)
floor = st.number_input("Bulunduğu Kat", min_value=0, max_value=100, value=3)
floorCount = st.number_input("Bina Kat Sayısı", min_value=1, max_value=100, value=10)
latitude = st.number_input("Enlem (Latitude)", value=52.2297)
longitude = st.number_input("Boylam (Longitude)", value=21.0122)
poiCount = st.number_input("Yakındaki POI (İlgi Noktası) Sayısı", min_value=0, max_value=500, value=20)

st.subheader("Okul, Klinik, Postane, Restoran vb. Mesafeleri (metre cinsinden)")
schoolDistance = st.slider("Okul Mesafesi", 0, 5000, 500)
clinicDistance = st.slider("Klinik Mesafesi", 0, 5000, 800)
postOfficeDistance = st.slider("Postane Mesafesi", 0, 5000, 600)
kindergartenDistance = st.slider("Anaokulu Mesafesi", 0, 5000, 400)
restaurantDistance = st.slider("Restoran Mesafesi", 0, 5000, 300)
collegeDistance = st.slider("Üniversite Mesafesi", 0, 5000, 1500)
pharmacyDistance = st.slider("Eczane Mesafesi", 0, 5000, 500)

hasParkingSpace = st.checkbox("Otopark Var mı?")
hasBalcony = st.checkbox("Balkon Var mı?")
hasElevator = st.checkbox("Asansör Var mı?")
hasSecurity = st.checkbox("Güvenlik Var mı?")
hasStorageRoom = st.checkbox("Depo Alanı Var mı?")

squareMeters_capped = st.number_input("Metrekare (m²)", min_value=20, max_value=500, value=100)
centreDistance_winsorized = st.number_input("Merkeze Uzaklık (metre)", min_value=0, max_value=50000, value=5000)

type_mapping = {
    'Daire': 0,
    'Stüdyo Daire': 1,
    'Villa': 2,
    'Çatı Katı Daire': 3
}
type_choice = st.selectbox("Ev Tipi", list(type_mapping.keys()), help="Evin türünü seçin: Daire, Stüdyo, Villa veya Çatı Katı Daire.")
type_encoded = type_mapping[type_choice]

# Kullanıcı dostu Konum Tipi seçimi
location_mapping = {
    'Şehir Merkezi': 0,
    'Popüler Semt': 1,
    'Sessiz Yerleşim Alanı': 2,
    'Sanayi Bölgesi': 3,
    'Kırsal Alan': 4,
    'Diğer': 5
}
location_choice = st.selectbox("Konum Tipi", list(location_mapping.keys()), help="Evin konumunu seçin: Şehir merkezi, semt, kırsal vb.")
location_cluster = location_mapping[location_choice]


age = st.slider("Bina Yaşı", 0, 100, 10)

city = st.selectbox("Şehir", [
    'bydgoszcz', 'czestochowa', 'gdansk', 'gdynia', 'katowice', 'krakow', 
    'lodz', 'lublin', 'poznan', 'radom', 'rzeszow', 'szczecin', 'warszawa', 'wroclaw'
])
ownership = st.selectbox("Mülkiyet Tipi", ['cooperative', 'udział'])

# Özellikleri uygun sıraya göre ayarla
city_columns = ['city_bydgoszcz', 'city_czestochowa', 'city_gdansk', 'city_gdynia',
                'city_katowice', 'city_krakow', 'city_lodz', 'city_lublin', 'city_poznan',
                'city_radom', 'city_rzeszow', 'city_szczecin', 'city_warszawa', 'city_wroclaw']

ownership_columns = ['ownership_cooperative', 'ownership_udziaÅ']

city_values = [1 if city in col else 0 for col in city_columns]
ownership_values = [1 if (ownership == 'cooperative' and 'cooperative' in col) or 
                    (ownership == 'udział' and 'udziaÅ' in col) else 0 for col in ownership_columns]

features = [
    rooms, floor, floorCount, latitude, longitude, poiCount,
    schoolDistance, clinicDistance, postOfficeDistance, kindergartenDistance,
    restaurantDistance, collegeDistance, pharmacyDistance,
    int(hasParkingSpace), int(hasBalcony), int(hasElevator), int(hasSecurity), int(hasStorageRoom),
    squareMeters_capped, centreDistance_winsorized,
    location_cluster, type_encoded, age
] + city_values + ownership_values

features = np.array(features).reshape(1, -1)

if st.button("Fiyatı Tahmin Et"):
    prediction = model.predict(features)
    tahmini_fiyat = np.expm1(prediction[0])
    st.success(f"Tahmini Fiyat: {int(tahmini_fiyat):,} TL")
