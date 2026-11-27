# Edition guard (owner, 27 Nov 2026): India and Nigeria readers each see only their own news.
#  - A device is LOCKED to one edition (localStorage "s2n.ed"), decided once:
#      * it already used the India app before (any "w2s." key, e.g. Indians in Nigeria reading Telugu news;
#        "w2s.first.*" counts only if older than 26 Nov 2026) -> India, wherever it is;
#      * otherwise a phone on Nigerian time (Africa/Lagos) or, for other time zones, a Nigerian connection
#        (free country lookup get.geojs.io, cached 3 days) -> Nigeria (new readers/installs from 27 Nov 2026);
#      * India time or any other country -> India (not locked, so a later move to Nigeria still counts).
#  - India pages send Nigeria-locked readers to /ng/; Nigeria pages send everyone else to "/".
#  - Owner/admin sees both: open any page with ?admin=both (undo: ?admin=off).
# Used by index.html, ng/index.html, tools/build_previews.py (s/ pages, web/), tools/build_lang.py (en/, hi/)
# and tools/ng/build_previews_ng.py (ng/s/ share pages).


def snippet(page, ng_url="'/ng/'"):
    """page: 'in' (India pages), 'ng' (Nigeria app) or 'ngshare' (a Nigeria story's share page: Nigeria readers ->
    the app at that story, everyone else -> India). ng_url: JS expression for where a Nigeria reader goes."""
    return ("<script>/* S2N edition: India and Nigeria readers each see only their own news (owner 27 Nov 2026). "
            "Earlier India readers stay India; new readers in Nigeria get Nigeria. Admin: ?admin=both (off: ?admin=off). */"
            "(function(){try{var P='" + page + "',ls=localStorage,q=new URLSearchParams(location.search),A='s2n.admin',E='s2n.ed';"
            "if(q.get('admin')==='both')ls.setItem(A,'1');if(q.get('admin')==='off')ls.removeItem(A);if(ls.getItem(A)==='1')return;"
            "if(/bot|crawl|spider|slurp|facebookexternalhit|WhatsApp|Twitterbot|TelegramBot|Lighthouse|Google-InspectionTool/i.test(navigator.userAgent))return;"
            "var go=function(c){var u=(P!=='ng'&&c==='NG')?" + ng_url + ":(P!=='in'&&c!=='NG')?'/':'';if(u){window.__s2nGo=1;location.replace(u);}};"
            "var ed=ls.getItem(E);"
            "if(!ed){for(var i=0;i<ls.length;i++){var n=ls.key(i)||'';if(n.indexOf('w2s.')===0&&(n.indexOf('w2s.first.')!==0||(+ls.getItem(n)||0)<1795651200000)){ed='in';ls.setItem(E,'in');break;}}}"
            "if(ed)return go(ed==='ng'?'NG':'IN');"
            "var ng=function(){ls.setItem(E,'ng');go('NG');};"
            "var tz='';try{tz=Intl.DateTimeFormat().resolvedOptions().timeZone||'';}catch(e){}"
            "if(tz==='Africa/Lagos')return ng();if(tz==='Asia/Kolkata'||tz==='Asia/Calcutta')return go('IN');"
            "var g=(ls.getItem('s2n.geo')||'').split('|');if(g[0]&&Date.now()-(+g[1]||0)<3*864e5)return g[0]==='NG'?ng():go(g[0]);"
            "fetch('https://get.geojs.io/v1/ip/country.json').then(function(r){return r.json();}).then(function(j){var c=String(j.country||'').toUpperCase();"
            "if(c){ls.setItem('s2n.geo',c+'|'+Date.now());if(c==='NG')ng();else go(c);}}).catch(function(){if(P!=='in')location.replace('/');});"
            "}catch(e){}})();</script>")


if __name__ == "__main__":
    print(snippet("in"))
