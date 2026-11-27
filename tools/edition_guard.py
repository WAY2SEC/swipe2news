# Edition guard (owner, 27 Nov 2026): India and Nigeria readers each see only their own news.
#  - Decided on every visit by location (owner, 27 Nov 2026 18:24: "all Nigerians who installed so far get Nigeria news"):
#      * a phone on Nigerian time (Africa/Lagos) or, for other time zones, a Nigerian connection
#        (free country lookup get.geojs.io, cached 3 days) -> Nigeria, also devices that read the India app before;
#      * India time or any other country -> India.
#    (The 27 Nov 16:11 rule "earlier India readers in Nigeria stay India" was dropped; old "s2n.ed" locks are cleared.)
#  - India pages send Nigeria-locked readers to /ng/; Nigeria pages send everyone else to "/".
#  - Owner/admin sees both: open any page with ?admin=both (undo: ?admin=off).
# Used by index.html, ng/index.html, tools/build_previews.py (s/ pages, web/), tools/build_lang.py (en/, hi/)
# and tools/ng/build_previews_ng.py (ng/s/ share pages).


def snippet(page, ng_url="'/ng/'"):
    """page: 'in' (India pages), 'ng' (Nigeria app) or 'ngshare' (a Nigeria story's share page: Nigeria readers ->
    the app at that story, everyone else -> India). ng_url: JS expression for where a Nigeria reader goes."""
    return ("<script>/* S2N edition: India and Nigeria readers each see only their own news (owner 27 Nov 2026). "
            "Anyone in Nigeria gets Nigeria, everyone else India. Owner: ?admin=both (off: ?admin=off) – also gives this page its own home-screen app. */"
            "(function(){try{var P='" + page + "',ls=localStorage,q=new URLSearchParams(location.search),A='s2n.admin',E='s2n.ed';"
            "if(q.get('admin')==='both')ls.setItem(A,'1');if(q.get('admin')==='off')ls.removeItem(A);"
            "if(ls.getItem(A)==='1'){var mf=document.querySelector('link[rel=manifest]'),own='/owner/'+(P==='in'?'in':'ng')+'.webmanifest';if(mf)mf.href=own;else document.write('<link rel=manifest href='+own+'>');return;}"
            "if(/bot|crawl|spider|slurp|facebookexternalhit|WhatsApp|Twitterbot|TelegramBot|Lighthouse|Google-InspectionTool/i.test(navigator.userAgent))return;"
            "var go=function(c){var u=(P!=='ng'&&c==='NG')?" + ng_url + ":(P!=='in'&&c!=='NG')?'/':'';if(u){window.__s2nGo=1;location.replace(u);}};"
            "ls.removeItem(E);var ng=function(){go('NG');};"
            "var tz='';try{tz=Intl.DateTimeFormat().resolvedOptions().timeZone||'';}catch(e){}"
            "if(tz==='Africa/Lagos')return ng();if(tz==='Asia/Kolkata'||tz==='Asia/Calcutta')return go('IN');"
            "var g=(ls.getItem('s2n.geo')||'').split('|');if(g[0]&&Date.now()-(+g[1]||0)<3*864e5)return g[0]==='NG'?ng():go(g[0]);"
            "fetch('https://get.geojs.io/v1/ip/country.json').then(function(r){return r.json();}).then(function(j){var c=String(j.country||'').toUpperCase();"
            "if(c){ls.setItem('s2n.geo',c+'|'+Date.now());if(c==='NG')ng();else go(c);}}).catch(function(){if(P!=='in')location.replace('/');});"
            "}catch(e){}})();</script>")


if __name__ == "__main__":
    print(snippet("in"))
