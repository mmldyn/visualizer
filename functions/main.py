import base64
import io
import random
import requests
import numpy as np
import os
import json
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
# Import Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore


# --- Inisialisasi Server Flask ---
app = Flask(__name__)
CORS(app) # Izinkan koneksi dari browser

# --- Inisialisasi Firebase ---
# PENTING: Unduh file JSON "serviceAccountKey.json" dari Firebase Console
# dan letakkan di folder yang sama dengan file app.py ini.
try:
    # Ganti "path/to/your/serviceAccountKey.json" dengan path sebenarnya
    cred = credentials.Certificate("./serviceAccountKey.json") 
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Koneksi Firebase Berhasil!")
except FileNotFoundError:
    print("ERROR: File 'serviceAccountKey.json' tidak ditemukan.")
    print("Silakan unduh dari Firebase Console dan letakkan di folder yang sama.")
    db = None
except Exception as e:
    print(f"Koneksi Firebase Gagal: {e}")
    db = None

# === KODE ANALISIS ANDA (SUDAH DIOPTIMALKAN) ===
FEEDBACK_TEMPLATES = {
    "lighting": {
        "good": [
            "Tingkat pencahayaan (exposure) terlihat seimbang dan pas.",
            "Pencahayaan pada foto ini sangat baik, detail di area gelap dan terang terjaga.",
            "Exposure yang tepat membuat foto ini enak dilihat."
        ],
        "dark": [
            "Foto terlihat terlalu gelap (underexposed). Coba naikkan exposure.",
            "Detail penting mungkin hilang di area bayangan karena foto kurang cahaya.",
            "Secara keseluruhan foto ini terlalu gelap. Pertimbangkan untuk meningkatkan kecerahan."
        ],
        "bright": [
            "Foto terlihat terlalu terang (overexposed). Coba turunkan exposure.",
            "Beberapa area pada foto terlihat 'blow out' atau kehilangan detail karena terlalu terang.",
            "Hati-hati dengan cahaya berlebih, foto ini cenderung overexposed."
        ]
    },
    "color": {
        "match_warm": [
            "Bagus! Palet warna sudah sesuai dengan mood 'hangat' yang diminta brief.",
            "Atmosfer hangat berhasil ditangkap dengan sempurna melalui warna-warna ini.",
        ],
        "match_cool": [
            "Luar biasa! Tone warna dingin pada foto ini sesuai dengan mood 'dingin' dari brief.",
            "Palet warna yang sejuk ini berhasil menciptakan mood yang diinginkan.",
        ],
        "match_neutral": [
            "Warna pada foto ini terlihat natural dan seimbang, sesuai dengan brief mood 'netral'.",
            "Keseimbangan warna yang baik, tidak terlalu hangat ataupun dingin."
        ],
        "mismatch_warm_instead_of_cool": [
            "Brief meminta mood 'dingin', namun warnamu cenderung hangat. Coba sesuaikan White Balance.",
            "Warna foto ini lebih hangat dari yang diminta brief."
        ],
        "mismatch_cool_instead_of_warm": [
            "Brief meminta mood 'hangat', namun warnamu cenderung dingin. Coba sesuaikan White Balance.",
            "Terdeteksi tone warna yang dingin, padahal brief menginginkan suasana hangat."
        ]
    },
    "composition": {
        "good": [
            "Luar biasa! Subjek utama ditempatkan dengan baik di area Rule of Thirds.",
            "Penempatan elemen pada titik 'power points' membuat komposisi foto ini sangat menarik.",
        ],
        "standard": [
            "Penempatan subjek cenderung di tengah. Komposisinya aman namun standar.",
            "Komposisi sentral. Coba eksplorasi Rule of Thirds untuk hasil yang lebih dinamis.",
        ]
    }
}

def generate_random_brief():
    moods = ['hangat', 'dingin', 'netral']
    return {"mood": random.choice(moods)}

# Fungsi analisis (dengan tambahan 'title' untuk UI)
def analyze_lighting(image: Image.Image):
    grayscale_image = image.convert('L')
    histogram = grayscale_image.histogram()
    total_pixels = image.width * image.height
    dark_threshold, bright_threshold = 85, 170
    dark_pixels = sum(histogram[:dark_threshold])
    bright_pixels = sum(histogram[bright_threshold:])
    
    score, key, title = 85, "good", "Brightness match!"
    if (dark_pixels / total_pixels) > 0.5:
        score, key, title = 30, "dark", "Too Dark (Underexposed)"
    elif (bright_pixels / total_pixels) > 0.5:
        score, key, title = 35, "bright", "Too Bright (Overexposed)"
    feedback = random.choice(FEEDBACK_TEMPLATES["lighting"][key])
    return {"score": score, "title": title, "feedback": feedback}

def analyze_color(image: Image.Image, brief: dict):
    thumb = image.resize((100, 100), Image.Resampling.LANCZOS)
    warm_pixels, cool_pixels = 0, 0
    for r, g, b in thumb.getdata():
        if r > b: warm_pixels += (r - b)
        if b > r: cool_pixels += (b - r)

    mood_brief = brief.get("mood", "netral")
    score, key, title = 50, "match_neutral", "Neutral Tone"
    if mood_brief == 'hangat':
        if warm_pixels > cool_pixels * 1.5:
            score, key, title = 90, "match_warm", "Warm Tone Match!"
        else:
            score, key, title = 40, "mismatch_cool_instead_of_warm", "Warm Tone Mismatch"
    elif mood_brief == 'dingin':
        if cool_pixels > warm_pixels * 1.5:
            score, key, title = 90, "match_cool", "Cool Tone Match!"
        else:
            score, key, title = 40, "mismatch_warm_instead_of_cool", "Cool Tone Mismatch"
    feedback = random.choice(FEEDBACK_TEMPLATES["color"][key])
    return {"score": score, "title": title, "feedback": feedback, "brief": mood_brief}

def analyze_composition(image: Image.Image, user_choice: str):
    width, height = image.size
    third_w, third_h = width // 3, height // 3
    grayscale_array = np.array(image.convert('L'))
    try: # Menangani gambar yang mungkin lebih kecil dari grid 3x3
        grid_complexity = [np.std(grayscale_array[i*third_h:(i+1)*third_h, j*third_w:(j+1)*third_w]) for i in range(3) for j in range(3)]
        busiest_box_index = np.argmax(grid_complexity)
    except ValueError:
        busiest_box_index = 4 # Default ke tengah jika gambar terlalu kecil

    power_points = [0, 2, 6, 8]
    score, key, title = 65, "standard", "Standard Composition"
    is_rot = busiest_box_index in power_points

    if user_choice == "Rule of Thirds":
        if is_rot:
            score, key, title = 95, "good", "Rule of Thirds: Great!"
        else:
            score, key, title = 40, "standard", "Rule of Thirds: Not Detected"
    # Anda bisa tambahkan logika spesifik untuk Golden Section dan Symmetry di sini
    elif user_choice == "Symmetry":
        # Placeholder
        score, key, title = 70, "standard", "Symmetry Check"
    elif user_choice == "Golden Section":
         # Placeholder
        score, key, title = 70, "standard", "Golden Section Check"
    else: # Fallback jika pilihan tidak dikenal
        if is_rot:
             score, key, title = 90, "good", "Dynamic Composition!"
        else:
             score, key, title = 70, "standard", "Central Composition"

    feedback = random.choice(FEEDBACK_TEMPLATES["composition"][key])
    return {"score": score, "title": title, "feedback": feedback, "user_choice": user_choice}

# Fungsi utama analisis (input hanya base64)
def analyze_image_base64(image_data: str, composition_choice: str):
    if not image_data.startswith('data:image/'):
         return {"error": "Format input gambar tidak didukung. Harus Base64.", "details": "Input bukan Base64 yang dikenali."}
    try:
        header, encoded = image_data.split(',', 1)
        decoded_image = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(decoded_image)).convert("RGB")
    except Exception as e:
        return {"error": "Gagal mendekode gambar Base64.", "details": str(e)}

    brief = generate_random_brief()
    lighting_result = analyze_lighting(image)
    color_result = analyze_color(image, brief)
    composition_result = analyze_composition(image, composition_choice) 

    final_score = round(
        composition_result["score"] * 0.4 +
        lighting_result["score"] * 0.3 +
        color_result["score"] * 0.3
    )

    return {
        "success": True,
        "finalScore": final_score,
        "feedbackSummary": {
            "lighting": lighting_result,
            "color": color_result,
            "composition": composition_result
        }
    }

# --- API Endpoint untuk Menerima Gambar ---
@app.route('/process-image', methods=['POST'])
def handle_image_processing():
    if not db:
        return jsonify({"status": "error", "message": "Koneksi database Firestore gagal"}), 500

    try:
        data = request.json
        image_data = data.get('image') # base64 string
        composition = data.get('composition') # Pilihan user
        app_id = data.get('appId', 'default-app-id') # Ambil appId dari request
        user_id = data.get('userId', 'anonymous') # Ambil userId dari request

        if not image_data or not composition:
            return jsonify({'error': 'Data tidak lengkap (gambar atau komposisi)'}), 400

        # 1. Jalankan analisis Python Anda
        analysis_result = analyze_image_base64(image_data, composition)
        
        if not analysis_result.get("success"):
            # Jika analisis gagal, kirim error kembali ke browser
            return jsonify({"status": "error", "message": analysis_result.get("error", "Analisis gagal"), "details": analysis_result.get("details", "")}), 500
            
        # 2. Siapkan data untuk disimpan ke Firestore
        # Gunakan path yang sesuai dengan aturan keamanan
        # /artifacts/{appId}/users/{userId}/ai_feedback
        doc_ref = db.collection(f'artifacts/{app_id}/users/{user_id}/ai_feedback').document()
        
        data_to_save = {
            "originalImage": image_data, # Simpan gambar asli
            "compositionChoice": composition,
            "analysis": analysis_result["feedbackSummary"],
            "finalScore": analysis_result["finalScore"],
            "timestamp": firestore.SERVER_TIMESTAMP # Tambahkan timestamp
        }
        
        # 3. Simpan ke Firestore
        doc_ref.set(data_to_save)
        
        # 4. Kirim balasan sukses ke browser
        # Browser tidak perlu menunggu hasil, cukup konfirmasi bahwa data diterima
        return jsonify({"status": "success", "message": "Gambar diterima dan sedang diproses untuk disimpan."})

    except Exception as e:
        print(f"Error di server Flask: {e}")
        # Kirim error generik ke browser
        return jsonify({'error': "Terjadi kesalahan internal pada server."}), 500

# Ambil JSON dari environment variable
service_account_json_string = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

if not service_account_json_string:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT environment variable not set.")
    
service_account_info = json.loads(service_account_json_string)
cred = credentials.Certificate(service_account_info)

