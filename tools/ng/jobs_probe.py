import urllib.request, json, xml.etree.ElementTree as ET
U={"MyJobMag":"https://www.myjobmag.com/jobsxml.xml","MyJobMag rss":"https://www.myjobmag.com/feeds/jobs","Hot Nigerian Jobs":"https://www.hotnigerianjobs.com/feed/",
 "NGCareers":"https://ngcareers.com/feed","Jobgurus":"https://www.jobgurus.com.ng/feed","Nigerian Jobs Plus":"https://www.jobsinnigeria.careers/feed/",
 "Recruitment portal (NG)":"https://www.recruitmentportal.com.ng/feed/","Jobzilla":"https://www.jobzilla.ng/feed/","Graduate jobs NG":"https://graduatejobsng.com/feed/",
 "Google News recruitment":"https://news.google.com/rss/search?q=recruitment+Nigeria+when:3d&hl=en-NG&gl=NG&ceid=NG:en",
 "Google News job portal opens":"https://news.google.com/rss/search?q=%22recruitment+portal%22+Nigeria+when:7d&hl=en-NG&gl=NG&ceid=NG:en",
 "Open-Meteo":"https://api.open-meteo.com/v1/forecast?latitude=6.45&longitude=3.39&current=temperature_2m,weather_code&timezone=Africa/Lagos",
 "ER-API USD":"https://open.er-api.com/v6/latest/USD"}
out={}
for n,u in U.items():
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (compatible; Swipe2NewsBot/1.0)"}),timeout=25).read()
        try:
            root=ET.fromstring(r.lstrip()); it=list(root.iter('item'))+list(root.iter('{http://www.w3.org/2005/Atom}entry'))
            out[n]={'ok':True,'items':len(it),'first':[ (x.findtext('title') or '')[:90] for x in it[:3]]}
        except Exception:
            out[n]={'ok':True,'bytes':len(r),'head':r[:160].decode('utf-8','replace')}
    except Exception as e: out[n]={'ok':False,'err':str(e)[:100]}
json.dump(out,open('tools/ng/jobs-probe.json','w'),indent=1,ensure_ascii=False)
