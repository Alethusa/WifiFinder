import csv
from flask import Flask, request, jsonify, render_template
from math import radians, cos, sin, sqrt, atan2
import chardet

app = Flask(__name__)

# 공공 와이파이 데이터를 담을 리스트
wifi_list = []

# CSV 파일 읽기
def load_wifi_data(file_path):
    global wifi_list
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        charenc = result['encoding']
    
    with open(file_path, 'r', encoding=charenc) as file:
        reader = csv.DictReader(file)
        for row in reader:
            wifi_list.append({
                'name': row['와이파이명'],
                'address': row['도로명주소'],
                'latitude': float(row['Y좌표']),
                'longitude': float(row['X좌표'])
            })

# 거리 계산 함수 (Haversine formula 사용)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # 지구의 반지름 (미터 단위)
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # 두 지점 간의 거리 (미터 단위)
    return distance

# 가까운 공공 와이파이 찾기
def find_nearest_wifi(latitude, longitude):
    nearest_wifi = []
    for wifi in wifi_list:
        distance = calculate_distance(latitude, longitude, wifi['latitude'], wifi['longitude'])
        nearest_wifi.append({
            'name': wifi['name'],
            'address': wifi['address'],
            'latitude': wifi['latitude'],  # 지도에 위치를 표시할 때 사용
            'longitude': wifi['longitude'],  # 지도에 위치를 표시할 때 사용
            'distance': distance
        })
    # 거리 순으로 정렬 (가까운 순서대로)
    nearest_wifi = sorted(nearest_wifi, key=lambda x: x['distance'])
    return nearest_wifi[:5]  # 가까운 5개 와이파이 정보 반환

# 위치 데이터를 수신하는 엔드포인트
@app.route('/location', methods=['POST'])
def location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    print(f"수신한 위도: {latitude}, 경도: {longitude}")

    # 가까운 공공 와이파이 정보 가져오기
    nearby_wifi = find_nearest_wifi(latitude, longitude)
    
    return jsonify(nearby_wifi)

@app.route('/')
def home():
    return render_template('index(2번 - csv파일 사용).html')

if __name__ == '__main__':
    # CSV 파일에서 공공 와이파이 데이터 로드
    load_wifi_data('공공와이파이.csv')
    app.run(debug=True)
