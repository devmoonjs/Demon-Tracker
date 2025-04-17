require('dotenv').config();

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const axios = require('axios');

const app = express();
const PORT = 9000;

// ✅ Google Maps API Key 환경변수로 설정 (보안 강화)
const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

// ✅ CORS 설정
app.use(cors());
app.use(express.json());

// 🔹 장소명을 위도/경도로 변환하는 함수 (비동기 API 요청)
const geocodeLocation = async (location) => {
    if (!location) return null;

    try {
        // ✅ Google Geocoding API 요청
        const formattedAddress = `${location}, 서울, 대한민국`;
        console.log(`📍 변환 요청: ${formattedAddress}`);

        const response = await axios.get("https://maps.googleapis.com/maps/api/geocode/json", {
            params: {
                address: formattedAddress,
                key: GOOGLE_MAPS_API_KEY,
                region: "kr", // 한국 지역 우선 검색
                language: "ko" // 한국어 응답
            }
        });

        if (response.data.status === "OK") {
            const { lat, lng } = response.data.results[0].geometry.location;
            console.log(`✅ 변환 성공: ${location} → 위도: ${lat}, 경도: ${lng}`);
            return { lat, lng };
        } else {
            console.error(`❌ 변환 실패: ${location} (Google API 응답: ${response.data.status})`);
            return null;
        }
    } catch (error) {
        console.error(`❌ Geocoding API 오류: ${error.message}`);
        return null;
    }
};

// 🔹 가장 최신 CSV 파일 가져오기
const getLatestCSVFile = () => {
    const dataDir = path.join(__dirname, '..', 'data');
    const files = fs.readdirSync(dataDir).filter(file => file.endsWith('.csv'));
    if (files.length === 0) return null;

    // 날짜 기준 최신 파일 찾기 (내림차순 정렬)
    files.sort((a, b) => b.localeCompare(a));
    return files[0];
};

// 🔹 시위 데이터를 JSON 형태로 반환하는 API
app.get('/api/protest-data', async (req, res) => {
    const latestCSV = getLatestCSVFile();
    if (!latestCSV) {
        return res.status(404).json({ message: "❌ 시위 일정 CSV 파일이 없습니다." });
    }

    const protestData = [];
    const filePath = path.join(__dirname, '..', 'data', latestCSV);

    // ✅ CSV 파일을 읽어서 JSON 변환
    fs.createReadStream(filePath)
        .pipe(csv())
        .on('data', (row) => protestData.push(row))
        .on('end', async () => {
            console.log(`✅ ${latestCSV} 파일 로드 완료!`);

            // ✅ Google Maps API를 이용한 좌표 변환 (병렬 요청)
            const locationPromises = protestData.map(async (row) => {
                const firstWord = row["장소"].split(" ")[0]; // 첫 단어만 사용
                const coordinates = await geocodeLocation(firstWord);
                return {
                    ...row,
                    위도: coordinates ? coordinates.lat.toString() : "",
                    경도: coordinates ? coordinates.lng.toString() : ""
                };
            });

            const updatedProtests = await Promise.all(locationPromises);

            // ✅ 최종 JSON 응답
            res.json({
                date: latestCSV.slice(0, 6), // 파일명 앞 6자리(날짜) 전달
                protests: updatedProtests
            });
        });
});

// ✅ 서버 실행
app.listen(PORT, () => console.log(`✅ 서버 실행됨: http://localhost:${PORT}`));
