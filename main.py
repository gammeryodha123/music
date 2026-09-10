from flask import Flask, request, jsonify, render_template_string, Response
import os, urllib.parse, requests, time
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

search_cache = {}
stream_cache = {}

PIPED_SERVERS = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.privacydev.net",
    "https://pipedapi.moomoo.me",
    "https://pipedapi.drgns.space",
    "https://pipedapi.syncpundit.io",
    "https://pipedapi.adminforge.de",
]

TRENDING = [
    {"url":"https://www.youtube.com/watch?v=TO-_3tck2tg","title":"BONES","thumbnail":"https://i.ytimg.com/vi/TO-_3tck2tg/hqdefault.jpg","channel":"IMAGINE DRAGONS"},
    {"url":"https://www.youtube.com/watch?v=7wtfhZwyrcc","title":"BELIEVER","thumbnail":"https://i.ytimg.com/vi/7wtfhZwyrcc/hqdefault.jpg","channel":"IMAGINE DRAGONS"},
    {"url":"https://www.youtube.com/watch?v=60ItHLz5WEA","title":"FADED","thumbnail":"https://i.ytimg.com/vi/60ItHLz5WEA/hqdefault.jpg","channel":"ALAN WALKER"},
    {"url":"https://www.youtube.com/watch?v=JGwWNGJdvx8","title":"SHAPE OF YOU","thumbnail":"https://i.ytimg.com/vi/JGwWNGJdvx8/hqdefault.jpg","channel":"ED SHEERAN"},
]

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>YODHA</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#1DB954">
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="/icon-192">
<link rel="icon" href="/icon-192">
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore-compat.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial;font-weight:800}
body{background:#000;color:#fff;min-height:100vh}
#loginScreen{position:fixed;inset:0;background:#000;z-index:9999;display:flex;align-items:center;justify-content:center}
.card{background:#181818;padding:32px;border-radius:24px;width:92%;max-width:380px;text-align:center}
.card h1{font-size:44px;letter-spacing:6px;color:#1DB954}
.card input{width:100%;padding:14px;margin:7px 0;border-radius:30px;border:1px solid #333;background:#222;color:#fff;outline:none}
.btn{width:100%;padding:14px;border-radius:30px;border:none;font-weight:800;cursor:pointer;margin:5px 0}
.btn-green{background:#1DB954;color:#000}.btn-dark{background:#2a2a2a;color:#fff}.btn-white{background:#fff;color:#000}
.header{padding:18px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:#000;z-index:10}
.header h2{font-size:30px;letter-spacing:6px;color:#1DB954}
.searchWrap{padding:0 16px 10px;position:sticky;top:60px;background:#000;z-index:9}
.searchBox{display:flex;align-items:center;gap:10px;background:#242424;border-radius:30px;padding:12px 18px}
.searchBox input{flex:1;background:transparent;border:none;color:#fff;outline:none}
.tabs{display:flex;gap:8px;padding:12px 16px;overflow-x:auto}
.tab{padding:8px 18px;border-radius:20px;background:#222;color:#aaa;border:none;white-space:nowrap;cursor:pointer}
.tab.active{background:#1DB954;color:#000}
.main{padding:0 10px 300px}
.sectionTitle{padding:16px 10px 8px;font-size:15px;letter-spacing:2px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 6px}
.cardSong{background:#181818;border-radius:12px;padding:10px;cursor:pointer}
.cardSong img{width:100%;aspect-ratio:1;border-radius:8px;object-fit:cover}
.cardSong b{display:block;font-size:11px;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.listSong{display:flex;align-items:center;gap:12px;padding:12px 10px;border-radius:10px;cursor:pointer}
.listSong img{width:52px;height:52px;border-radius:6px}
.player{position:fixed;bottom:0;left:0;right:0;background:#181818;border-top:1px solid #333;padding:12px 14px;z-index:100;display:none;border-radius:20px 20px 0 0}
.pTop{display:flex;align-items:center;gap:12px}
.pTop img{width:56px;height:56px;border-radius:8px}
.progress{width:100%;height:4px;background:#333;border-radius:2px;margin:10px 0;overflow:hidden;cursor:pointer}
.progress div{height:100%;background:#1DB954;width:0%}
.controls{display:flex;justify-content:space-between;margin-top:6px;align-items:center}
.ctrlCenter{display:flex;gap:18px;align-items:center}
.ctrlCenter button{background:none;border:none;color:#fff;font-size:22px;cursor:pointer}
.playBig{width:46px!important;height:46px!important;background:#fff!important;color:#000!important;border-radius:50%!important}
#installBanner{display:none;position:fixed;top:70px;left:12px;right:12px;background:#1DB954;color:#000;padding:12px 16px;border-radius:12px;z-index:50;font-weight:900;justify-content:space-between;align-items:center}
#lyricsBox{max-height:120px;overflow:auto;background:#000;border-radius:10px;padding:12px;margin-top:10px;display:none;font-size:11px}
</style>
</head>
<body>
<div id="installBanner"><span>INSTALL YODHA</span><button onclick="installPWA()" style="background:#000;color:#fff;border:none;padding:8px 14px;border-radius:20px">INSTALL</button></div>
<div id="loginScreen"><div class="card">
<h1>YODHA</h1><p style="color:#666;font-size:11px;margin-bottom:18px">PWA + 6 SERVERS</p>
<input id="email" placeholder="EMAIL"><input id="password" type="password" placeholder="PASSWORD">
<button class="btn btn-green" onclick="login()">LOGIN</button>
<button class="btn btn-dark" onclick="signup()">CREATE ACCOUNT</button>
<button class="btn btn-white" onclick="googleLogin()">GOOGLE</button>
<p id="msg" style="color:red;font-size:11px;margin-top:8px"></p>
</div></div>
<div class="header"><h2>YODHA</h2><button onclick="auth.signOut()" style="background:#222;color:#fff;border:none;padding:8px 14px;border-radius:20px">LOGOUT</button></div>
<div class="searchWrap"><div class="searchBox"><input id="q" placeholder="SEARCH..." onkeypress="if(event.key=='Enter')doSearch()"><button onclick="doSearch()" style="background:#1DB954;border:none;padding:7px 14px;border-radius:20px">GO</button></div></div>
<div class="tabs">
<button class="tab active" id="tab-home" onclick="showTab('home')">HOME</button>
<button class="tab" id="tab-search" onclick="showTab('search')">SEARCH</button>
<button class="tab" id="tab-queue" onclick="showTab('queue')">QUEUE <span id="qCount"></span></button>
<button class="tab" id="tab-liked" onclick="showTab('liked')">LIKED</button>
</div>
<div class="main">
<div id="homeTab"><div class="sectionTitle">TRENDING TODAY</div><div class="grid" id="trendingGrid"></div><div id="forYouList"></div></div>
<div id="searchTab" style="display:none"><div id="searchList"></div></div>
<div id="queueTab" style="display:none"><div id="queueList"></div></div>
<div id="likedTab" style="display:none"><div id="likedList"></div></div>
</div>
<div class="player" id="playerBox">
<div class="pTop"><img id="pImg"><div><b id="pTitle"></b><br><small id="pArtist" style="color:#aaa"></small><br><small id="status" style="color:#1DB954"></small></div></div>
<div class="progress" onclick="seek(event)"><div id="progressBar"></div></div>
<div class="controls"><button onclick="toggleShuffle()" id="shufBtn">SHUF</button><div class="ctrlCenter"><button onclick="prev()">PREV</button><button onclick="togglePlay()" id="playBtn" class="playBig">PLAY</button><button onclick="next()">NEXT</button></div><button onclick="toggleRepeat()" id="repBtn">REP</button></div>
<div id="lyricsBox"></div>
<audio id="audio"></audio>
</div>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt',(e)=>{e.preventDefault();deferredPrompt=e;document.getElementById('installBanner').style.display='flex';});
function installPWA(){if(deferredPrompt){deferredPrompt.prompt();}}
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js');}
const firebaseConfig={apiKey:"AIzaSyArZJxJ6N4YHh8-0fbyH8c-MQ1V3jzbP9k",authDomain:"python-music-app-67.firebaseapp.com",projectId:"python-music-app-67"};
firebase.initializeApp(firebaseConfig);
const auth=firebase.auth(), db=firebase.firestore();
let currentList=[], currentIndex=0, currentSong=null, userData={recent:[],liked:[]}, allSongs=[], queue=[], isShuffle=false, isRepeat=false;
const audio=document.getElementById('audio');
const trending = __TRENDING__;
auth.onAuthStateChanged(async u=>{
 if(u){loginScreen.style.display='none';
  let s=await db.collection('users').doc(u.uid).get(); if(s.exists) userData=s.data(); else {userData={recent:[],liked:[]}; await db.collection('users').doc(u.uid).set(userData);}
  renderAll();
 }else loginScreen.style.display='flex';
});
function renderTrending(){
 trendingGrid.innerHTML=trending.map((s,i)=>`<div class="cardSong" onclick="playAtTrending(${i})"><img src="${s.thumbnail}"><b>${s.title}</b></div>`).join('');
 forYouList.innerHTML=trending.map((s,i)=>`<div class="listSong" onclick="playAtTrending(${i})"><img src="${s.thumbnail}"><div><b>${s.title}</b><br><small>${s.channel}</small></div></div>`).join('');
}
function renderAll(){renderTrending();renderQueue();renderLiked();}
async function login(){try{await auth.signInWithEmailAndPassword(email.value,password.value)}catch(e){msg.innerText=e.message}}
async function signup(){try{await auth.createUserWithEmailAndPassword(email.value,password.value)}catch(e){msg.innerText=e.message}}
async function googleLogin(){try{await auth.signInWithPopup(new firebase.auth.GoogleAuthProvider())}catch(e){msg.innerText=e.message}}
function showTab(t){document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));document.getElementById('tab-'+t).classList.add('active');homeTab.style.display=t=='home'?'block':'none';searchTab.style.display=t=='search'?'block':'none';queueTab.style.display=t=='queue'?'block':'none';likedTab.style.display=t=='liked'?'block':'none';}
async function save(){if(auth.currentUser) await db.collection('users').doc(auth.currentUser.uid).set(userData);}
function addToQueue(s){queue.push(s);renderQueue();}
function renderQueue(){qCount.innerText=queue.length?`(${queue.length})`:'';queueList.innerHTML=queue.length?queue.map((s,i)=>`<div class="listSong"><img src="${s.thumbnail}"><div><b>${s.title}</b></div></div>`).join(''):'QUEUE EMPTY';}
function renderLiked(){likedList.innerHTML=(userData.liked||[]).map((s,i)=>`<div class="listSong" onclick="playFrom('liked',${i})"><img src="${s.thumbnail}"><div><b>${s.title}</b></div></div>`).join('')||'NO LIKED';}
async function doSearch(){
 let qv=q.value.trim();if(!qv) return;showTab('search');searchList.innerHTML='SEARCHING...';
 let r=await fetch('/search?q='+encodeURIComponent(qv));let songs=await r.json();allSongs=songs;
 searchList.innerHTML=songs.map((s,i)=>`<div class="listSong" onclick="playAt(${i})"><img src="${s.thumbnail}"><div><b>${s.title}</b><br><small>${s.channel}</small></div></div>`).join('');
}
function playAtTrending(i){currentList=trending;currentIndex=i;play(currentList[i]);}
function playAt(i){currentList=allSongs;currentIndex=i;play(currentList[i]);}
function playFrom(l,i){currentList=userData[l];currentIndex=i;play(currentList[i]);}
async function play(song){
 currentSong=song;playerBox.style.display='block';pImg.src=song.thumbnail;pTitle.innerText=song.title;pArtist.innerText=song.channel;status.innerText='LOADING';playBtn.innerText='...';
 try{
  let res=await fetch('/stream?url='+encodeURIComponent(song.url));let data=await res.json();
  audio.src=data.url;await audio.play();status.innerText='PLAYING YODHA';playBtn.innerText='PAUSE';
 }catch(e){status.innerText='FAILED';}
}
function togglePlay(){if(audio.paused){audio.play();playBtn.innerText='PAUSE';}else{audio.pause();playBtn.innerText='PLAY';}}
function next(){if(queue.length>0){let n=queue.shift();renderQueue();play(n);return;}if(currentIndex<currentList.length-1){currentIndex++;}else{currentIndex=0;}play(currentList[currentIndex]);}
function prev(){if(currentIndex>0){currentIndex--;play(currentList[currentIndex]);}}
function toggleShuffle(){isShuffle=!isShuffle;}
function toggleRepeat(){isRepeat=!isRepeat;}
function seek(e){let rect=e.currentTarget.getBoundingClientRect();let x=e.clientX-rect.left;audio.currentTime=x/rect.width*audio.duration;}
audio.ontimeupdate=()=>{if(audio.duration) progressBar.style.width=(audio.currentTime/audio.duration*100)+'%';}
audio.onended=()=>{next();}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    html = HTML.replace("__TRENDING__", str(TRENDING))
    return render_template_string(html)

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "YODHA",
        "short_name": "YODHA",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#1DB954",
        "icons": [
            {"src": "/icon-192", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512", "sizes": "512x512", "type": "image/png"}
        ]
    })

@app.route("/sw.js")
def sw():
    js = "const CACHE='YODHA-V3';self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/','/manifest.json'])))});self.addEventListener('fetch',e=>{if(e.request.url.includes('/search')||e.request.url.includes('/stream')){return fetch(e.request);}e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});"
    return Response(js, mimetype='application/javascript')

@app.route("/icon-<int:size>")
def icon(size):
    if size not in [192, 512]:
        size = 192
    try:
        from PIL import Image, ImageDraw
        from io import BytesIO
        img = Image.new('RGB', (size, size), '#000000')
        draw = ImageDraw.Draw(img)
        draw.ellipse([size*0.08, size*0.08, size*0.92, size*0.92], fill='#1DB954')
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return Response(buf.getvalue(), mimetype='image/png')
    except Exception as ex:
        return Response(b"", mimetype='image/png')

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    q_lower = q.lower()
    if q_lower in search_cache:
        return jsonify(search_cache[q_lower])
    for server in PIPED_SERVERS:
        try:
            url = server + "/search?q=" + urllib.parse.quote(q) + "&filter=music_songs"
            r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                items = r.json().get('items', [])[:15]
                res = []
                for e in items:
                    u = e.get('url', '')
                    if 'v=' in u:
                        vid = u.split('v=')[-1].split('&')[0]
                    else:
                        vid = u.split('/')[-1].split('?')[0]
                    if len(vid) < 6:
                        continue
                    thumb = e.get('thumbnail')
                    if not thumb:
                        thumb = "https://i.ytimg.com/vi/" + vid + "/hqdefault.jpg"
                    res.append({
                        "url": "https://www.youtube.com/watch?v=" + vid,
                        "title": e.get('title', 'Unknown').upper(),
                        "thumbnail": thumb,
                        "channel": e.get('uploaderName', 'YouTube').upper()
                    })
                if len(res) > 0:
                    search_cache[q_lower] = res
                    return jsonify(res)
        except Exception:
            continue
    return jsonify(TRENDING[:3])

@app.route("/stream")
def stream():
    url = request.args.get("url", "")
    if "v=" in url:
        vid = url.split("v=")[-1].split("&")[0]
    else:
        vid = url.split("/")[-1].split("?")[0]
    if not vid:
        return jsonify({"error": "NO VID"}), 400
    if vid in stream_cache:
        if time.time() - stream_cache[vid]['t'] < 600:
            return jsonify({"url": stream_cache[vid]['url']})
    for server in PIPED_SERVERS:
        try:
            r = requests.get(server + "/streams/" + vid, timeout=6, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                j = r.json()
                aud = j.get('audioStreams', [])
                if len(aud) > 0:
                    best = sorted(aud, key=lambda x: x.get('bitrate', 0), reverse=True)[0]
                    best_url = best.get('url')
                    if best_url:
                        stream_cache[vid] = {'url': best_url, 't': time.time()}
                        return jsonify({"url": best_url})
                hls = j.get('hls')
                if hls:
                    stream_cache[vid] = {'url': hls, 't': time.time()}
                    return jsonify({"url": hls})
        except Exception:
            continue
    return jsonify({"error": "ALL BUSY"}), 500

@app.route("/stream2")
def stream2():
    url = request.args.get("url", "")
    if "v=" in url:
        vid = url.split("v=")[-1].split("&")[0]
    else:
        vid = url.split("/")[-1].split("?")[0]
    try:
        import yt_dlp
        ydl_opts = {'format': 'bestaudio', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("https://www.youtube.com/watch?v=" + vid, download=False)
            u = info.get('url')
            if u:
                stream_cache[vid] = {'url': u, 't': time.time()}
                return jsonify({"url": u})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "FAIL"}), 500

@app.route("/lyrics")
def lyrics_route():
    title = request.args.get("title", "")
    try:
        r = requests.get("https://lrclib.net/api/search?track_name=" + urllib.parse.quote(title), timeout=5)
        d = r.json()
        if d and d[0].get('plainLyrics'):
            return jsonify({"lyrics": d[0]['plainLyrics'][:6000]})
    except Exception:
        pass
    return jsonify({"lyrics": "NOT FOUND"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
