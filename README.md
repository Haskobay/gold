```markdown
live-youtube-xml

Ne yapar
- channels.txt içindeki kanalları kontrol eder.
- Canlı yayın varsa media.xml dosyasını günceller. Her <media> öğesi şu formatta olur:
  <media>
    <title>Kanal başlığı veya video başlığı</title>
    <thumb>https://img.youtube.com/vi/<VIDEO_ID>/0.jpg</thumb>
    <type>youtube</type>
    <src><VIDEO_ID></src>
  </media>

Kurulum (manuel)
1) Repo'na bu dosyaları ekle (veya klonladıysan root dizine kaydet):
   - scripts/fetch_live_to_repo.py
   - channels.txt
   - .github/workflows/update_live_xml.yml
   - README.md

2) Git komutları (örnek):
   mkdir -p scripts
   # dosyaları uygun yere kaydet
   git add .
   git commit -m "Add live YouTube fetch script and workflow"
   git push origin main

3) Repo Settings > Secrets > Actions içine YOUTUBE_API_KEY adlı secret ekle:
   - Bu, YouTube Data API v3 için alınmış API Key olmalı.
   - Nasıl alınır: https://console.cloud.google.com/ → APIs & Services → Library → YouTube Data API v3 → Enable → Credentials → Create API key

4) Workflow:
   - Cron: '0 */12 * * *' (her 12 saatte bir) olarak ayarlı.
   - İlk testi elle başlatmak için Actions → ilgili workflow'u seçip "Run workflow" ile tetikleyebilirsin.

Notlar
- Daha doğru sonuç için channels.txt içine doğrudan channelId (UC... ile başlayan) koy.
- YouTube Data API kota limitleri vardır; çok fazla kanal veya sık tetikleme kota tüketir.
- Eğer istersen media.xml'e kanal başlığı, video url veya başlangıç zamanı gibi ek alanlar ekleyebilirim.
```
