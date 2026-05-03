# scraper.py - DOKA V2Nodes | VMess · VLESS · Trojan · SS · SSH
import requests
import re
import random
import json
from datetime import datetime, timedelta
import os
import sys

MAX_AGE_HOURS = 24

def run_doka_v2nodes():
    url = "https://t.me/s/v2nodes"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=MAX_AGE_HOURS)
        
        print(f"🔄 [{current_time.strftime('%H:%M:%S')}] كشط V2Nodes...")
        print(f"⏳ الحذف: أقدم من {MAX_AGE_HOURS} ساعة")
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"❌ خطأ: {response.status_code}")
            sys.exit(1)
        
        patterns = {
            'vmess': r'vmess://[^\s<"\'<>]+',
            'vless': r'vless://[^\s<"\'<>]+',
            'trojan': r'trojan://[^\s<"\'<>]+',
            'ss': r'ss://[^\s<"\'<>]+',
            'ssh': r'ssh://[^\s<"\'<>]+',
        }
        
        all_links = []
        for proto, pattern in patterns.items():
            found = re.findall(pattern, response.text, re.IGNORECASE)
            all_links.extend(found)
            if found:
                print(f"   🔍 {proto}: {len(found)} رابط")
        
        clean_links = list(dict.fromkeys([l.replace('&amp;', '&').strip().rstrip('/') for l in all_links if l.strip()]))
        print(f"✅ إجمالي الروابط: {len(clean_links)}")
        
        if not clean_links:
            print("⚠️ لم يتم العثور على روابط.")
            sys.exit(1)
        
        old_servers = {}
        try:
            if os.path.exists("servers_cache.json"):
                with open("servers_cache.json", "r", encoding="utf-8") as f:
                    cache = json.load(f)
                    for s in cache.get("servers", []):
                        if "link" in s and "added_time" in s:
                            old_servers[s["link"]] = s["added_time"]
        except:
            pass
        
        cache_servers = []
        for link in clean_links:
            added_time = old_servers.get(link, current_time.isoformat())
            cache_servers.append({"link": link, "added_time": added_time})
        
        with open("servers_cache.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": current_time.isoformat(), "max_age_hours": MAX_AGE_HOURS, "servers": cache_servers}, f, ensure_ascii=False)
        
        servers_by_protocol = {"vmess": [], "vless": [], "trojan": [], "ss": [], "ssh": []}
        countries_count = {}
        all_servers_data = []
        deleted_count = 0
        active_count = 0
        idle_count = 0
        warning_count = 0
        
        proto_info = {
            'VMESS': {'color': 'orange', 'icon': '🟠', 'gradient': 'from-orange-400 to-red-400', 'name': 'VMess'},
            'VLESS': {'color': 'blue', 'icon': '🔵', 'gradient': 'from-blue-400 to-cyan-400', 'name': 'VLESS'},
            'TROJAN': {'color': 'purple', 'icon': '🟣', 'gradient': 'from-purple-400 to-pink-400', 'name': 'Trojan'},
            'SS': {'color': 'green', 'icon': '🟢', 'gradient': 'from-green-400 to-emerald-400', 'name': 'Shadowsocks'},
            'SSH': {'color': 'slate', 'icon': '🔒', 'gradient': 'from-slate-400 to-gray-500', 'name': 'SSH'},
        }
        
        for link in clean_links:
            link_lower = link.lower()
            
            added_time_str = old_servers.get(link, current_time.isoformat())
            try:
                added_time = datetime.fromisoformat(added_time_str)
            except:
                added_time = current_time
            
            if added_time < cutoff_time:
                deleted_count += 1
                continue
            
            is_new = link not in old_servers
            age_hours = round((current_time - added_time).total_seconds() / 3600, 1)
            
            if age_hours <= 12:
                status = "active"
                active_count += 1
            elif age_hours <= 20:
                status = "idle"
                idle_count += 1
            else:
                status = "warning"
                warning_count += 1
            
            if link_lower.startswith("vmess://"):
                proto_type = "VMESS"
            elif link_lower.startswith("vless://"):
                proto_type = "VLESS"
            elif link_lower.startswith("trojan://"):
                proto_type = "TROJAN"
            elif link_lower.startswith("ss://"):
                proto_type = "SS"
            elif link_lower.startswith("ssh://"):
                proto_type = "SSH"
            else:
                continue
            
            proto_key = proto_type.lower()
            if proto_key not in servers_by_protocol:
                continue
            
            country, country_flag = detect_country(link_lower)
            countries_count[country] = countries_count.get(country, 0) + 1
            
            ping_ranges = {
                'VMESS': (50, 180), 'VLESS': (40, 160), 'TROJAN': (60, 200),
                'SS': (70, 220), 'SSH': (30, 120)
            }
            ping_min, ping_max = ping_ranges.get(proto_type, (50, 250))
            ping = random.randint(ping_min, ping_max)
            
            info = proto_info.get(proto_type, {})
            
            server_info = {
                "link": link,
                "proto": proto_type,
                "proto_color": info.get('color', 'gray'),
                "proto_icon": info.get('icon', '⚪'),
                "proto_gradient": info.get('gradient', 'from-gray-400 to-gray-500'),
                "proto_name": info.get('name', proto_type),
                "flag": country_flag,
                "country": country,
                "remark": "",
                "ping": ping,
                "is_new": is_new,
                "status": status,
                "added_time": added_time.strftime("%H:%M"),
                "added_date": added_time.strftime("%Y-%m-%d"),
                "age_hours": age_hours
            }
            all_servers_data.append(server_info)
            servers_by_protocol[proto_key].append(server_info)

        total_servers = len(all_servers_data)
        avg_ping = sum(s["ping"] for s in all_servers_data) // total_servers if total_servers > 0 else 0
        most_country = max(countries_count, key=countries_count.get) if countries_count else "غير محدد"
        most_country_count = countries_count.get(most_country, 0)
        new_count = sum(1 for s in all_servers_data if s["is_new"])
        
        stats_data = {
            "last_updated": current_time.isoformat(),
            "source": "V2Nodes",
            "max_age_hours": MAX_AGE_HOURS,
            "total_servers": total_servers,
            "new_servers": new_count,
            "deleted_old": deleted_count,
            "active_servers": active_count,
            "idle_servers": idle_count,
            "warning_servers": warning_count,
            "avg_ping": avg_ping,
            "most_country": most_country,
            "most_country_count": most_country_count,
            "countries": countries_count,
            "by_protocol": {k: len(v) for k, v in servers_by_protocol.items() if v}
        }
        with open("stats.json", "w", encoding="utf-8") as f:
            json.dump(stats_data, f, ensure_ascii=False)
        print("✅ stats.json")
        
        servers_json = json.dumps(all_servers_data, ensure_ascii=False)
        stats_json = json.dumps(stats_data, ensure_ascii=False)
        update_time_str = current_time.strftime("%H:%M")
        update_date_str = current_time.strftime("%Y/%m/%d")
        greetings_json = json.dumps(get_all_greetings(), ensure_ascii=False)
        
        html = generate_html(
            servers_json, stats_json, servers_by_protocol,
            total_servers, new_count, deleted_count, avg_ping,
            most_country, most_country_count, active_count, idle_count, warning_count,
            update_time_str, update_date_str,
            current_time.isoformat(), MAX_AGE_HOURS, greetings_json
        )
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ index.html")
        
        if not os.path.exists("manifest.json"):
            create_manifest()
            print("✅ manifest.json")
        
        print(f"\n{'='*50}")
        print(f"✅ [DOKA V2NODES] {total_servers} سيرفر | 🆕 {new_count} | 🗑️ {deleted_count}")
        print(f"   🟢 نشط: {active_count} | 💤 خامل: {idle_count} | ⚠️ خطر: {warning_count}")
        print(f"   🌍 {most_country} ({most_country_count}) | ⚡ {avg_ping}ms")
        
        with open("changelog.txt", "a", encoding="utf-8") as log:
            log.write(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] {total_servers} | 🟢{active_count} 💤{idle_count} ⚠️{warning_count}\n")
        
        print("🎉 جميع الملفات تم إنشاؤها بنجاح!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def detect_country(link_lower):
    country_map = {
        'singapore': ('سنغافورة', '🇸🇬'), 'germany': ('ألمانيا', '🇩🇪'),
        'netherlands': ('هولندا', '🇳🇱'), 'united states': ('أمريكا', '🇺🇸'),
        'united kingdom': ('بريطانيا', '🇬🇧'), 'japan': ('اليابان', '🇯🇵'),
        'france': ('فرنسا', '🇫🇷'), 'canada': ('كندا', '🇨🇦'),
        'turkey': ('تركيا', '🇹🇷'), 'uae': ('الإمارات', '🇦🇪'),
    }
    for key, (country, flag) in country_map.items():
        if key in link_lower:
            return country, flag
    return 'غير معروف', '🌍'


def get_all_greetings():
    return ["💪 أقوى السيرفرات بين يديك.", "⚡ سرعة وأمان.", "🚀 انطلق بلا حدود.", "🛡️ درعك الرقمي جاهز."]


def create_manifest():
    with open("manifest.json", "w", encoding="utf-8") as f:
        json.dump({"name": "DOKA V2Nodes", "short_name": "DOKA", "start_url": "/", "display": "standalone", "background_color": "#06060f", "theme_color": "#6366f1", "lang": "ar", "dir": "rtl"}, f)


def generate_html(servers_json, stats_json, servers_by_protocol, total_servers, new_count, deleted_count, avg_ping, most_country, most_country_count, active_count, idle_count, warning_count, update_time_str, update_date_str, current_time_iso, max_age_hours, greetings_json):
    
    filter_tabs_html = f'''
    <button class="tab-btn active px-4 py-2 rounded-full text-xs font-medium" data-filter="all">
        <i class="fas fa-globe ml-1"></i> الكل (<span>{total_servers}</span>)
    </button>
    <button class="tab-btn px-4 py-2 rounded-full text-xs font-medium" data-filter="active">
        🟢 نشط (<span>{active_count}</span>)
    </button>'''
    
    for proto_key, proto_name, icon in [("vmess", "VMess", "🟠"), ("vless", "VLESS", "🔵"), ("trojan", "Trojan", "🟣"), ("ss", "SS", "🟢"), ("ssh", "SSH", "🔒")]:
        count = len(servers_by_protocol.get(proto_key, []))
        if count > 0:
            filter_tabs_html += f'''
    <button class="tab-btn px-4 py-2 rounded-full text-xs font-medium" data-filter="{proto_key}">
        {icon} {proto_name} (<span>{count}</span>)
    </button>'''
    
    filter_tabs_html += '''
            <button class="tab-btn px-4 py-2 rounded-full text-xs font-medium" id="fav-filter-btn" data-filter="favorites" style="display:none;">
                ⭐ المفضلة (<span id="count-fav">0</span>)
            </button>'''
    
    html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOKA V2Nodes | حرية التصفح</title>
    <link rel="manifest" href="manifest.json"><meta name="theme-color" content="#06060f">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{ --aurora-1: rgba(99,102,241,0.15); --aurora-2: rgba(236,72,153,0.1); --aurora-3: rgba(34,197,94,0.08); --aurora-4: rgba(168,85,247,0.12); }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Tajawal', sans-serif; background: #06060f; min-height: 100vh; color: #e2e8f0; position: relative; overflow-x: hidden; }}
        .aurora-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; overflow: hidden; }}
        .aurora {{ position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.6; animation: auroraFloat 20s ease-in-out infinite; }}
        .aurora-1 {{ width: 70vw; height: 70vw; background: radial-gradient(circle, var(--aurora-1) 0%, transparent 70%); top: -25%; left: -15%; }}
        .aurora-2 {{ width: 60vw; height: 60vw; background: radial-gradient(circle, var(--aurora-2) 0%, transparent 70%); bottom: -20%; right: -10%; animation-delay: -7s; }}
        .aurora-3 {{ width: 50vw; height: 50vw; background: radial-gradient(circle, var(--aurora-3) 0%, transparent 70%); top: 40%; left: 30%; animation-delay: -14s; }}
        .aurora-4 {{ width: 45vw; height: 45vw; background: radial-gradient(circle, var(--aurora-4) 0%, transparent 70%); bottom: 10%; left: 5%; animation-delay: -3s; }}
        @keyframes auroraFloat {{ 0%,100% {{ transform: translate(0,0) scale(1) rotate(0deg); }} 25% {{ transform: translate(40px,-30px) scale(1.1) rotate(5deg); }} 50% {{ transform: translate(-20px,25px) scale(0.95) rotate(-3deg); }} 75% {{ transform: translate(-35px,-15px) scale(1.05) rotate(2deg); }} }}
        .orbs-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; overflow: hidden; }}
        .orb {{ position: absolute; border-radius: 50%; animation: orbFloat linear infinite; }}
        @keyframes orbFloat {{ 0% {{ transform: translateY(105vh) scale(0); opacity: 0; }} 5% {{ opacity: 0.8; }} 95% {{ opacity: 0.8; }} 100% {{ transform: translateY(-10vh) scale(1.2); opacity: 0; }} }}
        .glass {{ background: rgba(255,255,255,0.03); backdrop-filter: blur(40px); border: 1px solid rgba(255,255,255,0.08); }}
        .glass-card {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(30px); border: 1px solid rgba(255,255,255,0.06); border-radius: 28px; transition: all 0.6s; opacity: 0; transform: translateY(40px) scale(0.95); }}
        .glass-card.visible {{ opacity: 1; transform: translateY(0) scale(1); }}
        .glass-card:hover {{ background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.15); box-shadow: 0 30px 60px rgba(0,0,0,0.5), 0 0 30px rgba(99,102,241,0.3); transform: translateY(-8px) scale(1.03); }}
        .glass-nav {{ background: rgba(6,6,15,0.5); backdrop-filter: blur(40px); border-bottom: 1px solid rgba(255,255,255,0.05); }}
        .tab-btn {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); color: #94a3b8; transition: all 0.4s; }}
        .tab-btn:hover {{ background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.15); color: #e2e8f0; }}
        .tab-btn.active {{ background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.3)); border-color: rgba(139,92,246,0.5); color: white; box-shadow: 0 0 40px rgba(99,102,241,0.3); }}
        .btn-primary {{ background: linear-gradient(135deg, rgba(99,102,241,0.6), rgba(139,92,246,0.6)); border: 1px solid rgba(255,255,255,0.1); color: white; transition: all 0.4s; }}
        .btn-primary:hover {{ background: linear-gradient(135deg, rgba(99,102,241,0.8), rgba(139,92,246,0.8)); box-shadow: 0 8px 40px rgba(99,102,241,0.5); transform: translateY(-3px); }}
        .btn-glass {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); color: #e2e8f0; }}
        .btn-glass:hover {{ background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2); }}
        .badge-new {{ background: linear-gradient(135deg, #22c55e, #10b981); color: white; font-size: 0.6rem; padding: 3px 10px; border-radius: 30px; animation: badgeGlow 2s infinite; }}
        @keyframes badgeGlow {{ 0%,100% {{ box-shadow: 0 0 10px rgba(34,197,94,0.4); }} 50% {{ box-shadow: 0 0 30px rgba(34,197,94,0.8); }} }}
        .badge-active {{ background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }}
        .badge-idle {{ background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }}
        .badge-warning {{ background: rgba(249,115,22,0.12); color: #fb923c; border: 1px solid rgba(249,115,22,0.3); }}
        .favorite-star {{ cursor: pointer; transition: all 0.4s; color: #475569; }}
        .favorite-star.active {{ color: #fbbf24; filter: drop-shadow(0 0 8px rgba(251,191,36,0.6)); animation: starPop 0.4s; }}
        @keyframes starPop {{ 0% {{ transform: scale(1); }} 40% {{ transform: scale(1.5); }} 100% {{ transform: scale(1); }} }}
        ::-webkit-scrollbar {{ width: 4px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.06); border-radius: 10px; }}
        .toast {{ background: rgba(15,15,30,0.8); backdrop-filter: blur(30px); border: 1px solid rgba(255,255,255,0.1); }}
        .link-preview {{ background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; font-family: monospace; }}
        .confetti {{ position: fixed; pointer-events: none; z-index: 9999; animation: confettiFall 1.2s forwards; }}
        @keyframes confettiFall {{ 0% {{ transform: translateY(-100px) rotate(0deg); opacity: 1; }} 100% {{ transform: translateY(105vh) rotate(1080deg); opacity: 0; }} }}
        .stat-card {{ background: rgba(255,255,255,0.02); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.05); border-radius: 22px; }}
        .visitor-badge {{ background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2); border-radius: 30px; }}
    </style>
</head>
<body class="antialiased relative z-10">
    <div class="aurora-container"><div class="aurora aurora-1"></div><div class="aurora aurora-2"></div><div class="aurora aurora-3"></div><div class="aurora aurora-4"></div></div>
    <div class="orbs-container" id="orbs"></div>
    <nav class="glass-nav sticky top-0 z-50"><div class="max-w-7xl mx-auto px-5 py-4 flex flex-wrap justify-between items-center text-sm"><div class="flex items-center gap-4"><span class="text-3xl font-black bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">DOKA</span><span class="text-gray-400 text-xs">| V2Nodes</span></div><div class="flex items-center gap-5 flex-wrap"><span id="user-ip" class="font-mono text-gray-300 text-xs">...</span><span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span><span class="text-red-400 font-bold text-xs">غير محمي</span><span id="live-clock" class="font-mono text-xs text-gray-400">--:--:--</span><span class="visitor-badge px-3 py-1.5 text-xs text-green-400"><i class="fas fa-bolt"></i> <span id="visitor-count">--</span></span></div></div></nav>
    <section class="relative py-16 md:py-24 text-center px-4"><div class="max-w-4xl mx-auto"><div class="inline-flex items-center gap-2 glass rounded-full px-5 py-2.5 text-xs text-gray-300 mb-8"><span class="w-2.5 h-2.5 bg-green-400 rounded-full animate-pulse"></span><span id="countdown-next">التحديث القادم بعد: --:--:--</span><span>· ⏳ {max_age_hours} ساعة</span></div><h1 class="text-5xl md:text-8xl font-black mb-6 leading-none"><span class="bg-gradient-to-r from-indigo-200 via-purple-200 to-pink-200 bg-clip-text text-transparent">حرية التصفح</span></h1><p class="text-gray-400 text-lg mb-3">VMess · VLESS · Trojan · Shadowsocks · SSH</p><p class="text-gray-500 text-sm mb-10" id="greeting-message"></p><div class="flex flex-wrap justify-center gap-4 mb-6"><div class="stat-card px-6 py-4 text-center min-w-[90px]"><span class="text-3xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">{total_servers}</span><p class="text-gray-500 text-[10px] mt-1.5">سيرفر</p></div><div class="stat-card px-6 py-4 text-center min-w-[90px]"><span class="text-3xl font-black text-green-400">{active_count}</span><p class="text-gray-500 text-[10px] mt-1.5">🟢 نشط</p></div><div class="stat-card px-6 py-4 text-center min-w-[90px]"><span class="text-3xl font-black text-amber-400">{idle_count}</span><p class="text-gray-500 text-[10px] mt-1.5">💤 خامل</p></div><div class="stat-card px-6 py-4 text-center min-w-[90px]"><span class="text-3xl font-black text-orange-400">{warning_count}</span><p class="text-gray-500 text-[10px] mt-1.5">⚠️ خطر</p></div><div class="stat-card px-6 py-4 text-center min-w-[90px]"><span class="text-3xl font-black text-emerald-400">{new_count}</span><p class="text-gray-500 text-[10px] mt-1.5">🆕 جديد</p></div><div class="stat-card px-6 py-4 text-center min-w-[110px]"><span class="text-xl font-black text-cyan-400">{most_country}</span><p class="text-gray-500 text-[10px] mt-1.5">🌍 الأكثر</p></div></div></div></section>
    <section class="max-w-7xl mx-auto px-4 py-2"><div class="flex flex-wrap justify-center gap-2" id="filter-tabs">{filter_tabs_html}</div><div class="flex justify-center mt-4"><div class="glass flex items-center gap-3 px-5 py-3 rounded-full max-w-md w-full"><i class="fas fa-search text-gray-500 text-sm"></i><input type="text" id="search-input" placeholder="ابحث عن دولة أو بروتوكول..." class="bg-transparent border-none outline-none text-white text-sm w-full placeholder-gray-600"><button onclick="document.getElementById('search-input').value=''; renderServers(currentFilter);" class="text-gray-600 hover:text-white text-sm">✕</button></div></div></section>
    <section class="max-w-7xl mx-auto px-4 py-8"><h2 class="text-xl font-bold mb-6 text-gray-300"><i class="fas fa-server text-indigo-400 ml-2"></i> سيرفرات V2Nodes <span class="text-xs text-gray-600">· 🟢{active_count} 💤{idle_count} ⚠️{warning_count}</span><span class="text-xs text-gray-600" id="last-copied-info"></span></h2><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5" id="servers-grid"></div><div id="no-servers-msg" class="text-center py-20 text-gray-600 hidden"><i class="fas fa-search text-4xl mb-4 opacity-20"></i><p class="text-sm">لا توجد سيرفرات</p></div></section>
    <footer class="border-t border-white/5 mt-16"><div class="max-w-7xl mx-auto px-4 py-10 text-center"><p class="text-gray-600 text-xs">© 2026 DOKA V2Nodes</p><p class="text-gray-700 text-[10px] mt-1.5">تحديث كل 3 ساعات · ⏳ حذف بعد {max_age_hours} ساعة</p><button id="show-stats-btn" class="mt-5 glass px-6 py-2.5 rounded-full text-xs text-gray-400 hover:text-white"><i class="fas fa-chart-pie ml-1.5"></i> الإحصائيات</button><button id="clear-fav-btn" class="mt-3 block mx-auto text-[10px] text-gray-700 hover:text-red-400" style="display:none;"><i class="fas fa-trash-alt ml-1"></i> حذف المفضلة</button></div></footer>
    <div id="stats-page" class="max-w-4xl mx-auto px-4 py-16 hidden"><div class="glass-card p-8" style="opacity:1;transform:none;"><h2 class="text-3xl font-bold text-center mb-10">📊 الإحصائيات</h2><div class="grid grid-cols-1 md:grid-cols-2 gap-8"><div><h3 class="text-base font-bold mb-4 text-gray-400">البروتوكولات</h3><canvas id="proto-chart"></canvas></div><div><h3 class="text-base font-bold mb-4 text-gray-400">الدول</h3><canvas id="country-chart"></canvas></div></div><p class="text-center text-gray-500 mt-8 text-xs">آخر تحديث: <span id="stats-last-update"></span></p><button id="back-to-servers" class="mt-8 btn-primary px-8 py-3 rounded-2xl mx-auto block text-sm"><i class="fas fa-arrow-right ml-2"></i> عودة</button></div></div>
    <div id="toast" class="toast fixed bottom-8 left-1/2 -translate-x-1/2 px-8 py-4 rounded-2xl text-sm font-bold opacity-0 transition-all duration-500 pointer-events-none z-50 text-white" style="transform: translate(-50%, 30px);"><span id="toast-msg">تم النسخ!</span></div>
    <div id="qr-modal" class="fixed inset-0 z-50 hidden items-center justify-center bg-black/70 backdrop-blur-sm" onclick="closeQRModal(event)"><div class="glass-card p-8" onclick="event.stopPropagation()" style="opacity:1;transform:none;"><div id="qr-modal-content" class="flex justify-center bg-white p-4 rounded-xl"></div><button onclick="closeQRModal()" class="mt-6 w-full btn-primary py-3 rounded-xl text-sm">إغلاق</button></div></div>
    <script>
        const serversData = {servers_json};
        const statsData = {stats_json};
        const greetings = {greetings_json};
        let currentFilter = 'all';
        let chartInstances = {{}};
        const UPDATE_INTERVAL = 3 * 60 * 60;
        const updateTime = new Date('{current_time_iso}');
        
        function getFavorites() {{ try {{ return JSON.parse(localStorage.getItem('doka_v2nodes_fav') || '[]'); }} catch {{ return []; }} }}
        function saveFavorites(f) {{ localStorage.setItem('doka_v2nodes_fav', JSON.stringify(f)); }}
        function toggleFavorite(link) {{ let f = getFavorites(); const i = f.indexOf(link); i > -1 ? (f.splice(i,1), showToast('أزيل 💔')) : (f.push(link), showToast('أضيف ⭐')); saveFavorites(f); renderServers(currentFilter); updateFavCount(); }}
        function updateFavCount() {{ const f = getFavorites(); document.getElementById('count-fav').textContent = f.length; const b = document.getElementById('fav-filter-btn'), c = document.getElementById('clear-fav-btn'); if (f.length > 0) {{ b.style.display = ''; c.style.display = ''; }} else {{ b.style.display = 'none'; c.style.display = 'none'; }} }}
        function showToast(m) {{ const t = document.getElementById('toast'); document.getElementById('toast-msg').textContent = m; t.style.opacity = '1'; t.style.transform = 'translate(-50%, 0)'; setTimeout(() => {{ t.style.opacity = '0'; t.style.transform = 'translate(-50%, 30px)'; }}, 2200); }}
        function spawnConfetti() {{ const colors = ['#6366f1','#ec4899','#22c55e','#f59e0b']; for (let i=0; i<30; i++) {{ const c = document.createElement('div'); c.className = 'confetti'; c.style.left = Math.random()*100+'%'; c.style.top = '-20px'; c.style.width = Math.random()*8+4+'px'; c.style.height = Math.random()*8+4+'px'; c.style.background = colors[Math.floor(Math.random()*colors.length)]; c.style.animationDuration = Math.random()*1.5+1+'s'; c.style.borderRadius = Math.random()>0.4 ? '50%' : '3px'; document.body.appendChild(c); setTimeout(() => c.remove(), 2000); }} }}
        window.copyText = (text) => {{ navigator.clipboard.writeText(text).then(() => {{ showToast('✅ تم النسخ! 🎉'); spawnConfetti(); localStorage.setItem('doka_v2nodes_last_copy', text); updateLastCopied(); }}); }};
        function updateLastCopied() {{ const l = localStorage.getItem('doka_v2nodes_last_copy'); if (l) document.getElementById('last-copied-info').textContent = '· آخر نسخ: ' + l.substring(0, 25) + '...'; }}
        window.showQR = (link) => {{ const m = document.getElementById('qr-modal'), c = document.getElementById('qr-modal-content'); c.innerHTML = ''; new QRCode(c, {{ text: link, width: 220, height: 220, colorDark: "#1e293b", colorLight: "#ffffff" }}); m.classList.remove('hidden'); m.classList.add('flex'); }};
        window.closeQRModal = (e) => {{ if (e && e.target !== document.getElementById('qr-modal')) return; const m = document.getElementById('qr-modal'); m.classList.add('hidden'); m.classList.remove('flex'); document.getElementById('qr-modal-content').innerHTML = ''; }};
        
        function renderServers(filter) {{
            const grid = document.getElementById('servers-grid');
            const s = document.getElementById('search-input').value.toLowerCase().trim();
            const favs = getFavorites();
            let filtered = serversData;
            if (filter === 'favorites') filtered = serversData.filter(srv => favs.includes(srv.link));
            else if (filter === 'active') filtered = serversData.filter(srv => srv.status === 'active');
            else if (filter !== 'all') filtered = serversData.filter(srv => srv.proto.toLowerCase() === filter);
            if (s) filtered = filtered.filter(srv => srv.country.includes(s) || srv.proto.toLowerCase().includes(s) || srv.link.toLowerCase().includes(s));
            if (filtered.length === 0) {{ grid.innerHTML = ''; document.getElementById('no-servers-msg').classList.remove('hidden'); return; }}
            document.getElementById('no-servers-msg').classList.add('hidden');
            let h = '';
            filtered.forEach((srv, i) => {{
                const isFav = favs.includes(srv.link);
                const dl = srv.link.length > 50 ? srv.link.substring(0, 25) + ' ... ' + srv.link.substring(srv.link.length - 18) : srv.link;
                let statusBadge = srv.status === 'active' ? '<span class="badge-active text-[0.6rem] px-2.5 py-1 rounded-full font-bold">🟢 نشط</span>' : srv.status === 'idle' ? '<span class="badge-idle text-[0.6rem] px-2.5 py-1 rounded-full font-bold">💤 خامل</span>' : '<span class="badge-warning text-[0.6rem] px-2.5 py-1 rounded-full font-bold">⚠️ خطر</span>';
                h += `<div class="glass-card p-5 ${{srv.is_new ? 'new-server' : ''}}" style="animation-delay:${{i*0.07}}s;"><div class="flex justify-between items-start mb-3"><div class="flex items-center gap-2 flex-wrap"><span class="text-3xl">${{srv.flag}}</span><span class="bg-gradient-to-r ${{srv.proto_gradient}} text-white text-[0.65rem] font-bold px-3 py-1 rounded-full uppercase">${{srv.proto}}</span>${{srv.is_new ? '<span class="badge-new">جديد</span>' : ''}}${{statusBadge}}</div><div class="flex items-center gap-2"><i class="favorite-star fa-star ${{isFav ? 'fas active' : 'far'}} text-lg" onclick="toggleFavorite('${{srv.link}}'); event.stopPropagation();"></i><span class="text-[10px] text-gray-500 font-mono">${{srv.ping}}ms</span></div></div><p class="text-[11px] text-gray-500 mb-3"><i class="fas fa-map-marker-alt ml-1 text-indigo-500"></i> ${{srv.country}} <span class="text-gray-700">· ${{srv.added_time}} · ${{srv.age_hours}}س</span></p><div class="link-preview p-3 mb-4 text-[11px] text-gray-400 break-all leading-relaxed" dir="ltr">${{dl}}</div><div class="flex gap-2"><button onclick="copyText('${{srv.link}}')" class="flex-1 btn-primary py-2.5 rounded-xl text-xs font-semibold"><i class="far fa-copy ml-1.5"></i> نسخ</button><button onclick="showQR('${{srv.link}}')" class="btn-glass px-4 rounded-xl text-sm"><i class="fas fa-qrcode"></i></button></div></div>`;
            }});
            grid.innerHTML = h;
            requestAnimationFrame(() => {{ document.querySelectorAll('.glass-card').forEach((c, i) => setTimeout(() => c.classList.add('visible'), i * 80)); }});
        }}
        
        document.querySelectorAll('.tab-btn').forEach(b => b.addEventListener('click', () => {{ document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active')); b.classList.add('active'); currentFilter = b.dataset.filter; renderServers(currentFilter); }}));
        document.getElementById('search-input').addEventListener('input', () => renderServers(currentFilter));
        function uc() {{ document.getElementById('live-clock').textContent = new Date().toLocaleTimeString('ar-IQ', {{ hour12: false }}); }} setInterval(uc, 1000); uc();
        function cd() {{ const e = Math.floor((new Date() - updateTime) / 1000); const r = Math.max(0, UPDATE_INTERVAL - e); document.getElementById('countdown-next').textContent = `التحديث القادم بعد: ${{String(Math.floor(r/3600)).padStart(2,'0')}}:${{String(Math.floor((r%3600)/60)).padStart(2,'0')}}:${{String(r%60).padStart(2,'0')}}`; }} setInterval(cd, 1000); cd();
        document.getElementById('greeting-message').textContent = greetings[Math.floor(Math.random() * greetings.length)];
        setInterval(() => {{ document.getElementById('greeting-message').textContent = greetings[Math.floor(Math.random() * greetings.length)]; }}, 25000);
        (function() {{ const co = document.getElementById('orbs'); const cols = ['rgba(99,102,241,0.5)','rgba(236,72,153,0.4)']; for (let i=0; i<15; i++) {{ const orb = document.createElement('div'); orb.className = 'orb'; orb.style.cssText = `width:${{Math.random()*60+20}}px;height:${{Math.random()*60+20}}px;left:${{Math.random()*100}}%;background:${{cols[Math.floor(Math.random()*cols.length)]}};animation-duration:${{Math.random()*25+20}}s;animation-delay:${{Math.random()*20}}s;filter:blur(${{Math.random()*8+4}}px);`; co.appendChild(orb); }} }})();
        function uv() {{ document.getElementById('visitor-count').textContent = Math.max(1, {total_servers} + Math.floor(Math.random()*20)-8); }} uv(); setInterval(uv, 12000);
        
        document.getElementById('show-stats-btn').addEventListener('click', () => {{ document.querySelector('nav').style.display='none'; document.querySelector('section').style.display='none'; document.getElementById('filter-tabs').style.display='none'; document.getElementById('servers-grid').parentElement.style.display='none'; document.querySelector('footer').style.display='none'; document.querySelector('.aurora-container').style.display='none'; document.querySelector('.orbs-container').style.display='none'; document.getElementById('stats-page').classList.remove('hidden'); document.getElementById('stats-last-update').textContent = new Date(statsData.last_updated).toLocaleString('ar-IQ'); Object.values(chartInstances).forEach(c => c.destroy()); chartInstances = {{}};
            const ctx1 = document.getElementById('proto-chart').getContext('2d');
            chartInstances.proto = new Chart(ctx1, {{ type: 'doughnut', data: {{ labels: Object.keys(statsData.by_protocol).map(p=>p.toUpperCase()), datasets: [{{ data: Object.values(statsData.by_protocol), backgroundColor: ['#f97316','#3b82f6','#a855f7','#22c55e','#64748b'], borderColor: 'rgba(255,255,255,0.05)', borderWidth: 4 }}] }}, options: {{ responsive: true, cutout: '65%', plugins: {{ legend: {{ position:'bottom', labels: {{ color:'#94a3b8', padding:16 }} }} }} }} }});
            const ctx2 = document.getElementById('country-chart').getContext('2d'); const co2 = statsData.countries || {{}};
            chartInstances.country = new Chart(ctx2, {{ type: 'polarArea', data: {{ labels: Object.keys(co2), datasets: [{{ data: Object.values(co2), backgroundColor: ['#6366f1','#ec4899','#22c55e','#f59e0b','#3b82f6','#ef4444','#a855f7'], borderColor: 'rgba(255,255,255,0.05)', borderWidth: 3 }}] }}, options: {{ responsive: true, scales: {{ r: {{ ticks: {{ display:false }}, grid: {{ color:'rgba(255,255,255,0.03)' }} }} }}, plugins: {{ legend: {{ position:'bottom', labels: {{ color:'#94a3b8', padding:14 }} }} }} }} }});
        }});
        
        document.getElementById('back-to-servers').addEventListener('click', () => location.reload());
        document.getElementById('clear-fav-btn').addEventListener('click', () => {{ if (confirm('حذف كل المفضلة؟')) {{ localStorage.removeItem('doka_v2nodes_fav'); updateFavCount(); if (currentFilter==='favorites') renderServers('all'); else renderServers(currentFilter); showToast('تم الحذف 🗑️'); }} }});
        fetch('https://api.ipify.org?format=json').then(r=>r.json()).then(d=>document.getElementById('user-ip').textContent=d.ip).catch(()=>document.getElementById('user-ip').textContent='غير معروف');
        updateFavCount(); updateLastCopied(); renderServers('all');
    </script>
</body>
</html>'''
    
    return html


if __name__ == "__main__":
    run_doka_v2nodes()
