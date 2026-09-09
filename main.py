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
    "https://pipedapi.leptos.dev",
    "https://pipedapi.ducks.party",
    "https://pipedapi.qdi.at",
    "https://pipedapi.r4fo.com",
    "https://api.piped.privacy.com.de",
]

TRENDING = [
    {"url":"https://www.youtube.com/watch?v=TO-_3tck2tg","title":"IMAGINE DRAGONS - BONES","thumbnail":"https://i.ytimg.com/vi/TO-_3tck2tg/hqdefault.jpg","channel":"IMAGINE DRAGONS"},
    {"url":"https://www.youtube.com/watch?v=7wtfhZwyrcc","title":"IMAGINE DRAGONS - BELIEVER","thumbnail":"https://i.ytimg.com/vi/7wtfhZwyrcc/hqdefault.jpg","channel":"IMAGINE DRAGONS"},
    {"url":"https://www.youtube.com/watch?v=60ItHLz5WEA","title":"ALAN WALKER - FADED","thumbnail":"https://i.ytimg.com/vi/60ItHLz5WEA/hqdefault.jpg","channel":"ALAN WALKER"},
    {"url":"https://www.youtube.com/watch?v=JGwWNGJdvx8","title":"ED SHEERAN - SHAPE OF YOU","thumbnail":"https://i.ytimg.com/vi/JGwWNGJdvx8/hqdefault.jpg","channel":"ED SHEERAN"},
    {"url":"https://www.youtube.com/watch?v=kJQP7kiw5Fk","title":"LUIS FONSI - DESPACITO","thumbnail":"https://i.ytimg.com/vi/kJQP7kiw5Fk/hqdefault.jpg","channel":"LUIS FONSI"},
]

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>YODHA</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#1DB954">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="YODHA">
<link rel="apple-touch-icon" href="/icon-192">
<link rel="icon" href="/icon-192">
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore-compat.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',Arial;text-transform:uppercase}
body{background:linear-gradient(180deg,#1a1a1a 0%,#000 100%);color:#fff;min-height:100vh}
#loginScreen{position:fixed;inset:0;background:#000;z-index:9999;display:flex;align-items:center;justify-content:center}
.card{background:#181818;padding:32px;border-radius:24px;width:92%;max-width:380px;text-align:center}
.card h1{font-size:44px;font-weight:900;letter-spacing:6px;color:#1DB954}
.card p{color:#666;font-size:11px;margin-bottom:18px}
.card input{width:100%;padding:14px;margin:7px 0;border-radius:30px;border:1px solid #333;background:#222;color:#fff;outline:none;text-transform:none}
.btn{width:100%;padding:14px;border-radius:30px;border:none;font-weight:800;cursor:pointer;margin:5px 0;letter-spacing:1px}
.btn-green{background:#1DB954;color:#000}.btn-dark{background:#2a2a2a;color:#fff}.btn-white{background:#fff;color:#000}
.header{padding:18px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:rgba(0,0,0,.9);backdrop-filter:blur(20px);z-index:10}
.header h2{font-size:30px;font-weight:900;letter-spacing:6px;color:#1DB954}
.searchWrap{padding:0 16px 10px;position:sticky;top:60px;z-index:9;background:linear-gradient(180deg,rgba(0,0,0,.9),transparent)}
.searchBox{display:flex;align-items:center;gap:10px;background:#242424;border-radius:30px;padding:12px 18px;border:1px solid #333}
.searchBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;text-transform:none}
.tabs{display:flex;gap:8px;padding:12px 16px;overflow-x:auto}
.tab{padding:8px 18px;border-radius:20px;background:#222;color:#aaa;border:none;font-weight:800;white-space:nowrap;cursor:pointer}
.tab.active{background:#1DB954;color:#000}
.main{padding:0 10px 300px}
.sectionTitle{padding:16px 10px 8px;font-size:15px;font-weight:900;letter-spacing:2px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 6px}
.cardSong{background:#181818;border-radius:12px;padding:10px;cursor:pointer}
.cardSong img{width:100%;aspect-ratio:1;border-radius:8px;object-fit:cover}
.cardSong b{display:block;font-size:11px;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cardSong small{color:#aaa;font-size:10px}
.listSong{display:flex;align-items:center;gap:12px;padding:12px 10px;border-radius:10px;cursor:pointer}
.listSong:hover{background:#1a1a1a}
.listSong img{width:52px;height:52px;border-radius:6px}
.addBtn{width:32px;height:32px;border-radius:50%;background:#2a2a2a;color:#fff;border:none}
.player{position:fixed;bottom:0;left:0;right:0;background:rgba(24,24,24,.97);backdrop-filter:blur(30px);border-top:1px solid #333;padding:12px 14px;z-index:100;display:none;border-radius:20px 20px 0 0}
.pTop{display:flex;align-items:center;gap:12px}
.pTop img{width:56px;height:56px;border-radius:8px}
.progress{width:100%;height:4px;background:#333;border-radius:2px;margin:10px 0;overflow:hidden;cursor:pointer}
.progress div{height:100%;background:#1DB954;width:0%}
.controls{display:flex;align-items:center;justify-content:space-between;margin-top:6px}
.ctrlCenter{display:flex;align-items:center;gap:18px}
.ctrlCenter button{background:none;border:none;color:#fff;font-size:22px;cursor:pointer}
.playBig{width:46px!important;height:46px!important;background:#fff!important;color:#000!important;border-radius:50%!important}
.iconBtn{background:none;border:none;color:#aaa;font-size:20px;cursor:pointer}
#lyricsBox{max-height:140px;overflow-y:auto;background:#000;border-radius:10px;padding:12px;margin-top:10px;display:none;white-space:pre-line;font-size:11px;color:#ccc;text-transform:none}
#installBanner{display:none;position:fixed;top:70px;left:12px;right:12px;background:#1DB954;color:#000;padding:12px 16px;border-radius:12px;z-index:50;font-weight:900;justify-content:space-between;align-items:center}
</style>
</head>
<body>
<div id="installBanner"><span>INSTALL YODHA</span><button onclick="installPWA()" style="background:#000;color:#fff;border:none;padding:8px 14px;border-radius:20px;font-weight:800">INSTALL</button><button onclick="installBanner.style.display='none'" style="background:none;border:none">X</button></div>
<div id="loginScreen"><div class="card">
<h1>YODHA</h1><p>YMP-PRO.ONRENDER.COM • PWA • 13 SERVERS</p>
<input id="email" placeholder="EMAIL"><input id="password" type="password" placeholder="PASSWORD">
<button class="btn btn-green" onclick="login()">LOGIN</button>
<button class="btn btn-dark" onclick="signup()">CREATE ACCOUNT</button>
<button class="btn btn-white" onclick="googleLogin()">CONTINUE WITH GOOGLE</button>
<button class="btn btn-dark" onclick="githubLogin()">CONTINUE WITH GITHUB</button>
<p id="msg" style="color:#ff5555;font-size:11px;margin-top:8px;text-transform:none"></p>
</div></div>
<div class="header"><h2>YODHA</h2><button onclick="auth.signOut()" style="background:#222;color:#fff;border:none;padding:8px 14px;border-radius:20px;font-size:11px;font-weight:800">LOGOUT</button></div>
<div class="searchWrap"><div class="searchBox"><input id="q" placeholder="SEARCH SONGS..." onkeypress="if(event.key=='Enter')doSearch()"><button onclick="doSearch()" style="background:#1DB954;border:none;color:#000;padding:7px 14px;border-radius:20px;font-weight:900">GO</button></div></div>
<div class="tabs">
<button class="tab active" id="tab-home" onclick="showTab('home')">HOME</button>
<button class="tab" id="tab-search" onclick="showTab('search')">SEARCH</button>
<button class="tab" id="tab-queue" onclick="showTab('queue')">QUEUE <span id="qCount"></span></button>
<button class="tab" id="tab-recent" onclick="showTab('recent')">RECENT</button>
<button class="tab" id="tab-liked" onclick="showTab('liked')">LIKED</button>
</div>
<div class="main">
<div id="homeTab"><div class="sectionTitle">TRENDING TODAY</div><div class="grid" id="trendingGrid"></div><div class="sectionTitle">MADE FOR YOU</div><div id="forYouList"></div></div>
<div id="searchTab" style="display:none"><div id="searchList"></div></div>
<div id="queueTab" style="display:none"><div id="queueList"></div></div>
<div id="recentTab" style="display:none"><div id="recentList"></div></div>
<div id="likedTab" style="display:none"><div id="likedList"></div></div>
</div>
<div class="player" id="playerBox">
<div class="pTop"><img id="pImg"><div class="pInfo"><b id="pTitle"></b><small id="pArtist" style="color:#aaa"></small><small id="status" style="color:#1DB954;display:block;font-size:10px"></small></div><button onclick="toggleLike()" id="likeBtn" class="iconBtn">🤍</button><button onclick="toggleLyrics()" class="iconBtn">📜</button></div>
<div class="progress" onclick="seek(event)"><div id="progressBar"></div></div>
<div class="controls"><button class="iconBtn" onclick="toggleShuffle()" id="shufBtn">🔀</button><div class="ctrlCenter"><button onclick="prev()">⏮</button><button onclick="togglePlay()" id="playBtn" class="playBig">▶</button><button onclick="next()">⏭</button></div><button class="iconBtn" onclick="toggleRepeat()" id="repBtn">🔁</button></div>
<div id="lyricsBox"></div>
<audio id="audio" style="display:none"></audio>
</div>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt',(e)=>{e.preventDefault();deferredPrompt=e;document.getElementById('installBanner').style.display='flex';});
function installPWA(){if(deferredPrompt){deferredPrompt.prompt();deferredPrompt.userChoice.then(()=>{deferredPrompt=null;installBanner.style.display='none';});}}
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js');}
const firebaseConfig={apiKey:"AIzaSyArZJxJ6N4YHh8-0fbyH8c-MQ1V3jzbP9k",authDomain:"python-music-app-67.firebaseapp.com",projectId:"python-music-app-67",storageBucket:"python-music-app-67.firebasestorage.app",messagingSenderId:"868162538798",appId:"1:868162538798:web:3312a15c372f24434cbebf"};
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
 trendingGrid.innerHTML=trending.map((s,i)=>`<div class="cardSong" onclick="playAtTrending(${i})"><img src="${s.thumbnail}"><b>${s.title}</b><small>${s.channel}</small></div>`).join('');
 forYouList.innerHTML=trending.map((s,i)=>`<div class="listSong" onclick="playAtTrending(${i})"><img src="${s.thumbnail}"><div class="info"><b>${s.title}</b><small>${s.channel}</small></div><button class="addBtn" onclick="event.stopPropagation();addToQueue(trending[${i}])">+</button></div>`).join('');
}
function renderAll(){renderTrending();renderQueue();renderRecent();renderLiked();}
async function login(){try{await auth.signInWithEmailAndPassword(email.value,password.value)}catch(e){msg.innerText=e.message}}
async function signup(){try{await auth.createUserWithEmailAndPassword(email.value,password.value)}catch(e){msg.innerText=e.message}}
async function googleLogin(){try{await auth.signInWithPopup(new firebase.auth.GoogleAuthProvider())}catch(e){msg.innerText=e.message}}
async function githubLogin(){try{await auth.signInWithPopup(new firebase.auth.GithubAuthProvider())}catch(e){msg.innerText=e.message}}
function showTab(t){document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));document.getElementById('tab-'+t).classList.add('active');homeTab.style.display=t=='home'?'block':'none';searchTab.style.display=t=='search'?'block':'none';queueTab.style.display=t=='queue'?'block':'none';recentTab.style.display=t=='recent'?'block':'none';likedTab.style.display=t=='liked'?'block':'none';}
async function save(){if(auth.currentUser) await db.collection('users').doc(auth.currentUser.uid).set(userData);}
function addToQueue(s){queue.push(s);renderQueue();}
function renderQueue(){qCount.innerText=queue.length?`(${queue.length})`:'';queueList.innerHTML=queue.length?queue.map((s,i)=>`<div class="listSong"><img src="${s.thumbnail}"><div class="info"><b>${s.title}</b><small>${s.channel}</small></div><button class="addBtn" onclick="queue.splice(${i},1);renderQueue()">X</button></div>`).join(''):'<p style="padding:30px;color:#555;text-align:center">QUEUE EMPTY</p>';}
function renderRecent(){recentList.innerHTML=(userData.recent||[]).map((s,i)=>`<div class="listSong" onclick="playFrom('recent',${i})"><img src="${s.thumbnail}"><div class="info"><b>${s.title}</b><small>${s.channel}</small></div></div>`).join('')||'<p style="padding:30px;color:#555;text-align:center">NO RECENT</p>';}
function renderLiked(){likedList.innerHTML=(userData.liked||[]).map((s,i)=>`<div class="listSong" onclick="playFrom('liked',${i})"><img src="${s.thumbnail}"><div class="info"><b>${s.title}</b><small>${s.channel}</small></div></div>`).join('')||'<p style="padding:30px;color:#555;text-align:center">NO LIKED YET</p>';if(currentSong) likeBtn.innerText=(userData.liked||[]).find(x=>x.url==currentSong.url)?'❤️':'🤍';}
async function doSearch(){
 let qv=q.value.trim();if(!qv) return;showTab('search');searchList.innerHTML='<p style="padding:20px;color:#888">SEARCHING '+qv.toUpperCase()+'...</p>';
 let r=await fetch('/search?q='+encodeURIComponent(qv));let songs=await r.json();allSongs=songs;
 searchList.innerHTML=songs.map((s,i)=>`<div class="listSong" onclick="playAt(${i})"><img src="${s.thumbnail}"><div class="info"><b>${s.title}</b><small>${s.channel}</small></div><button class="addBtn" onclick="event.stopPropagation();addToQueue(allSongs[${i}])">+</button></div>`).join('');
}
function playAtTrending(i){currentList=trending;currentIndex=i;play(currentList[i]);}
function playAt(i){currentList=allSongs;currentIndex=i;play(currentList[i]);}
function playFrom(l,i){currentList=userData[l];currentIndex=i;play(currentList[i]);}
async function play(song){
 currentSong=song;playerBox.style.display='block';pImg.src=song.thumbnail;pTitle.innerText=song.title;pArtist.innerText=song.channel;status.innerText='LOADING';playBtn.innerText='...';
 userData.recent=userData.recent.filter(s=>s.url!=song.url);userData.recent.unshift(song);userData.recent=userData.recent.slice(0,50);save();renderAll();
 try{
  let res=await fetch('/stream?url='+encodeURIComponent(song.url));let data=await res.json();
  if(data.error) throw data.error;
  audio.src=data.url;await audio.play();status.innerText='PLAYING • YODHA';playBtn.innerText='⏸';
 }catch(e){
  status.innerText='TRYING BACKUP...';
  try{let r2=await fetch('/stream2?url='+encodeURIComponent(song.url));let d2=await r2.json();if(d2.url){audio.src=d2.url;await audio.play();status.innerText='PLAYING • BACKUP';playBtn.innerText='⏸';return;}}catch{}
  status.innerText='FAILED';
 }
}
function togglePlay(){if(audio.paused){audio.play();playBtn.innerText='⏸';}else{audio.pause();playBtn.innerText='▶';}}
function next(){if(queue.length>0){let n=queue.shift();renderQueue();play(n);return;}if(isShuffle){currentIndex=Math.floor(Math.random()*currentList.length);}else if(currentIndex<currentList.length-1){currentIndex++;}else if(isRepeat){currentIndex=0;}else return;play(currentList[currentIndex]);}
function prev(){if(audio.currentTime>3){audio.currentTime=0;return;}if(currentIndex>0){currentIndex--;play(currentList[currentIndex]);}}
function toggleShuffle(){isShuffle=!isShuffle;shufBtn.style.color=isShuffle?'#1DB954':'#aaa';}
function toggleRepeat(){isRepeat=!isRepeat;repBtn.style.color=isRepeat?'#1DB954':'#aaa';}
async function toggleLike(){if(!currentSong) return;let ex=userData.liked.find(s=>s.url==currentSong.url);if(ex) userData.liked=userData.liked.filter(s=>s.url!=currentSong.url);else userData.liked.unshift(currentSong);await save();renderLiked();}
async function toggleLyrics(){if(lyricsBox.style.display=='block'){lyricsBox.style.display='none';return;}lyricsBox.style.display='block';lyricsBox.innerText='LOADING...';let r=await fetch('/lyrics?title='+encodeURIComponent(currentSong.title));let d=await r.json();lyricsBox.innerText=d.lyrics;}
audio.ontimeupdate=()=>{if(audio.duration) progressBar.style.width=(audio.currentTime/audio.duration*100)+'%';}
function seek(e){let rect=e.currentTarget.getBoundingClientRect();let x=e.clientX-rect.left;audio.currentTime=x/rect.width*audio.duration;}
audio.onended=()=>{next();}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    html = HTML_PAGE.replace("__TRENDING__", str(TRENDING))
    return render_template_string(html)

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "YODHA",
        "short_name": "YODHA",
        "description": "YODHA - MUSIC APP",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#1DB954",
        "icons": [
            {"src": "/icon-192", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/icon-512", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ]
    })

@app.route("/sw.js")
def sw():
    js = "const CACHE='YODHA-V2';const ASSETS=['/','/manifest.json','/icon-192','/icon-512'];self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)))});self.addEventListener('fetch',e=>{if(e.request.url.includes('/search')||e.request.url.includes('/stream')||e.request.url.includes('/lyrics')){return fetch(e.request);}e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{caches.open(CACHE).then(c=>{c.put(e.request,res.clone())});return res;}).catch(()=>caches.match('/'))));});"
    return Response(js, mimetype='application/javascript')

@app.route("/icon-<int:size>")
def icon(size):
    if size not in [192, 512]:
        size = 192
    try:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        img = Image.new('RGB', (size, size), '#000000')
        draw = ImageDraw.Draw(img)
        draw.ellipse([size*0.08, size*0.08, size*0.92, size*0.92], fill='#1DB954')
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(size*0.22))
        except:
            font = None
        text = "YODHA"
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((size - w) / 2, (size - h) / 2), text, fill='black', font=font)
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return Response(buf.getvalue(), mimetype='image/png')
    except Exception:
        return Response(requests.get(f"https://via.placeholder.com/{size}/1DB954/000000?text=YODHA").content, mimetype='image/png')

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
            url = f"{server}/search?q={urllib.parse.quote(q)}&filter=music_songs"
            r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                data = r.json()
                items = data.get('items', [])[:15]
                res = []
                for e in items:
                    u = e.get('url', '')
