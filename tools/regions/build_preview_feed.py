#!/usr/bin/env python3
"""India Regions PREVIEW (26 Nov 2026) – writes editions/in-regions/news.json from the hand-written stories below.

Regions: Uttar Pradesh · Delhi · Mumbai · Maharashtra · Chennai · Odisha.
Every summary is in our own words, with the source name + link (same rules as the other editions).
`sec` = region keys used by the chips on /in-regions/. Mumbai stories are also tagged 'maharashtra'.
`t` empty = the source did not show a time, so the card shows only the date.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "editions", "in-regions", "news.json")

C = {"up": "--c-gov", "delhi": "--c-city", "mumbai": "--c-city", "maharashtra": "--c-gov", "chennai": "--c-biz", "odisha": "--c-gov"}

def S(sec, loc, cat, h, p, src, url, pub, t="", lbl="fact", stat="", statl=""):
    d = pub[8:10] + "." + pub[5:7] + "." + pub[0:4]
    return {"h": h, "p": p, "cat": cat, "loc": loc, "sec": sec, "src": src, "url": url, "pub": pub, "d": d, "t": t,
            "lbl": lbl, "stat": stat, "statl": statl, "lang": "en", "st": "IN", "pic": "logo", "col": C[sec[0]]}

STORIES = [
 # ---------------- Uttar Pradesh ----------------
 S(["up"], "Lucknow", "Uttar Pradesh · Politics",
   "SP releases its 2027 manifesto on Constitution Day",
   "Samajwadi Party chief Akhilesh Yadav released the party's manifesto for the 2027 Uttar Pradesh Assembly election in Lucknow on Thursday. "
   "Called 'PDA Ka Prannpatra', it was prepared under former chief secretary Alok Ranjan and puts the Constitution, democracy and reservation at the centre. "
   "Senior leaders including Azam Khan and Dimple Yadav were present, ANI reports.",
   "ANI", "https://www.aninews.in/news/national/politics/akhilesh-yadav-to-release-samajwadi-partys-pda-ka-prannpatra-in-lucknow-for-2027-up-polls20261126163132/",
   "2026-11-26T16:31+05:30", "16:31", "fact", "2027", "UP Assembly polls"),
 S(["up"], "Lucknow", "Uttar Pradesh · Politics",
   "Kharge leads Congress 'Samvidhan Raksha March' in Lucknow",
   "Congress held a march to protect the Constitution in Lucknow on Constitution Day. Party president Mallikarjun Kharge told workers "
   "that the BJP government in the state is afraid of Rahul Gandhi and the Congress, and said the party will keep marching whenever it can, ANI reports.",
   "ANI", "https://menafn.com/1112025548/Congress-Holds-Samvidhan-Raksha-March-In-Lucknow-On-Constitution-Day",
   "2026-11-26T13:00+05:30", "", "claim", "26 Nov", "Constitution Day"),
 S(["up"], "Lucknow", "Uttar Pradesh · Politics",
   "Owaisi backs Chandrashekhar Azad as CM face at Lucknow rally",
   "At a rally of the Samajik Parivartan Morcha in Lucknow, AIMIM chief Asaduddin Owaisi said Chief Minister Yogi Adityanath's days are numbered "
   "and projected Azad Samaj Party leader Chandrashekhar Azad as the front's chief minister face for 2027, Outlook's live updates report.",
   "Outlook India", "https://www.outlookindia.com/national/breaking-news-india-world-live-updates-26-11-mumbai-attacks-up-elections-2027-akhilesh-yadav-bjp-congress-november-26",
   "2026-11-26T12:00+05:30", "", "claim", "2027", "UP race heats up"),
 S(["up"], "Varanasi", "Uttar Pradesh · Varanasi",
   "Varanasi ghats glow for Dev Deepawali",
   "The Kashi Vishwanath Dham and the ghats along the Ganga in Varanasi were lit with earthen lamps and decorations for Dev Deepawali, "
   "and large crowds of devotees gathered by the river on Tuesday evening, according to TNI's headlines.",
   "TNI (enewsinsight)", "https://enewsinsight.com/tni-morning-news-headlines-november-25-2026/",
   "2026-11-25T11:10+05:30", "", "fact", "Ganga", "ghats lit with diyas"),

 # ---------------- Delhi ----------------
 S(["delhi"], "New Delhi", "Delhi · Air quality",
   "Delhi's air stays 'poor' – AQI 226 on Thursday morning",
   "Delhi's citywide air quality index was 226 at 7 am on Thursday, still in the 'poor' band, with three stations in the 'very poor' range, "
   "according to CPCB data. Forecasters see no quick improvement, Business Standard reports.",
   "Business Standard", "https://business-standard.com/india-news/delhi-s-poor-air-streak-continues-aqi-at-226-no-immediate-relief-in-sight-126112600052_1.html",
   "2026-11-26T08:00+05:30", "", "fact", "226", "AQI · poor"),
 S(["delhi"], "New Delhi", "Delhi · Weather",
   "Coldest morning of the season as smog streak hits 11 days",
   "Delhi recorded its coldest morning of the season on Wednesday, while the 24-hour average AQI of 220 kept the city in the 'poor' category for the 11th day running. "
   "Anand Vihar was the worst spot at 357, and vehicle exhaust was the top pollution source, PTI reports.",
   "The Federal (PTI)", "https://thefederal.com/category/states/north/delhi/delhi-aqi-in-poor-category-for-11th-consecutive-day-set-to-worsen-264094",
   "2026-11-25T19:00+05:30", "", "fact", "11 days", "of poor air in a row"),
 S(["delhi"], "New Delhi", "Delhi · Health",
   "Two new government hospitals to open next year, says CM",
   "Chief Minister Rekha Gupta reviewed ongoing hospital and health projects on Wednesday and asked officials to finish them on time without cutting quality. "
   "Two new hospitals are due to open in Delhi next year, The Statesman reports.",
   "The Statesman", "https://www.thestatesman.com/cities/delhi/delhi-cm-reviews-healthcare-infra-expansion-stresses-timely-completion-of-projects-1503667003.html",
   "2026-11-25T21:56+05:30", "21:56", "fact", "2", "new hospitals in 2027"),
 S(["delhi"], "Shalimar Bagh", "Delhi · Jobs & skills",
   "8-acre skill centre planned in Shalimar Bagh",
   "The Delhi government will build an eight-acre skill development centre in Shalimar Bagh to train young people and women in new technologies "
   "and industry skills, Chief Minister Rekha Gupta announced.",
   "BozokMedia", "https://www.bozokmedia.com/en/national/2026/11/25/delhi-government-to-establish-skill-centre-for-youth-and-women-cm-rekha-gupta-426365/",
   "2026-11-25T01:24+05:30", "", "fact", "8 acres", "for youth & women"),
 S(["delhi"], "Pragati Maidan", "Delhi · Events",
   "Trade fair at Bharat Mandapam ends on Friday",
   "The 45th India International Trade Fair at Bharat Mandapam, Pragati Maidan, runs until 27 November – Friday is the last day for visitors, India TV notes.",
   "India TV", "https://www.indiatvnews.com/topic/delhi-",
   "2026-11-26T09:00+05:30", "", "fact", "27 Nov", "last day of IITF"),

 # ---------------- Mumbai ----------------
 S(["mumbai", "maharashtra"], "Mumbai", "Mumbai · 26/11",
   "Mumbai remembers 26/11 victims, 18 years on",
   "India marked the 18th anniversary of the 2008 Mumbai terror attacks, in which 166 people were killed. President Droupadi Murmu, "
   "Chief Minister Devendra Fadnavis and other leaders paid tribute to the victims and the security personnel who died, The Sentinel reports.",
   "The Sentinel", "https://www.sentinelassam.com/breakingnews/2611-mumbai-terror-attacks-india-marks-18th-anniversary-president-murmu-and-leaders-pay-tribute",
   "2026-11-26T10:20+05:30", "", "fact", "166", "lives lost in 2008"),
 S(["mumbai", "maharashtra"], "Mumbai", "Mumbai · Development",
   "Fadnavis plans 'Third and Fourth Mumbai', eyes $100 bn in infra",
   "Speaking at the Third World Mayors' Forum in Mumbai, Chief Minister Devendra Fadnavis said Maharashtra wants about $100 billion of infrastructure "
   "investment in five years and outlined plans for new 'Third' and 'Fourth Mumbai' growth centres, more transport and education hubs, Free Press Journal reports.",
   "Free Press Journal", "https://freepressjournal.in/mumbai/maharashtra-eyes-100-billion-infrastructure-investment-in-5-years-fadnavis-unveils-plans-for-3rd-4th-mumbai-mumbai-news",
   "2026-11-25T20:00+05:30", "", "claim", "$100 bn", "infra goal, 5 years"),
 S(["mumbai"], "Mumbai", "Mumbai · Civic",
   "BJP tells BMC to drop plan to hand open spaces to private firms",
   "The BJP has ruled out giving Mumbai's public open spaces to private operators and asked the BMC to withdraw its 2023 draft policy on the issue, Free Press Journal reports.",
   "Free Press Journal", "https://www.freepressjournal.in/mumbai",
   "2026-11-25T21:56+05:30", "21:56", "fact", "2023", "draft policy to go"),
 S(["mumbai"], "Borivali", "Mumbai · Local trains",
   "Train guard attacked at Borivali after asking man to leave ladies' coach",
   "A passenger hit a train guard on the head with a mobile phone at Borivali after the guard told him off for sleeping in the ladies' compartment, "
   "days after a stabbing during a fight on another local, News18 Lokmat reports.",
   "News18 Lokmat (Marathi)", "https://news18marathi.com/maharashtra/mumbai-local-passenger-attacks-train-guard-with-mobile-phone-borivali-station-1839950.html",
   "2026-11-24T09:40+05:30", "09:40", "fact", "Borivali", "Western line"),
 S(["mumbai"], "Kalyan", "Mumbai region · Traffic",
   "Road near Vitthalwadi station shut until 20 March",
   "A road near Vitthalwadi station in Kalyan–Dombivli is closed from 21 November 2026 to 20 March 2027 for construction work, and heavy vehicles face entry limits. "
   "Commuters should plan other routes, Free Press Journal reports.",
   "Free Press Journal", "https://www.freepressjournal.in/mumbai",
   "2026-11-25T22:44+05:30", "22:44", "fact", "4 months", "road closure"),

 # ---------------- Maharashtra ----------------
 S(["maharashtra"], "Mumbai", "Maharashtra · Drought",
   "310 of 358 talukas now drought-hit; farmers to get 5 kg grain",
   "After the latest additions, 310 of Maharashtra's 358 talukas – about 86.5% of the state – are officially drought-affected. "
   "Revenue Minister Chandrashekhar Bawankule said farmers in these talukas will get 5 kg of foodgrains on request. Marathwada and Vidarbha are hit hardest, ANI reports.",
   "ANI", "https://aninews.in/news/national/politics/maharashtra-cabinet-announces-drought-relief-measures-5-kg-foodgrains-for-farmers-on-demand-maharashtra-minister-chandrashekhar-bawankule20261125191106/",
   "2026-11-25T19:11+05:30", "19:11", "fact", "310", "of 358 talukas"),
 S(["maharashtra"], "Solapur", "Maharashtra · Water",
   "Every new bridge must store water underneath; fodder camps cleared",
   "Maharashtra has made it compulsory to build a check dam or weir with every new bridge over rivers and streams, so at least a metre of water stays below. "
   "Fodder camps for livestock were also approved, first in Solapur and Dharashiv districts, PTI reports.",
   "ThePrint (PTI)", "https://theprint.in/india/every-new-bridge-in-maharashtra-to-have-check-dam-underneath/3109090/",
   "2026-11-25T18:34+05:30", "", "fact", "1 m", "of water under each bridge"),
 S(["maharashtra"], "Pune", "Maharashtra · Pune",
   "Supriya Sule asks CM to step in on Pune crime",
   "NCP (SP) MP Supriya Sule called Pune's law and order alarming after a man was attacked with a machete and a gun outside the Shivajinagar court, "
   "and urged Chief Minister Fadnavis to intervene, citing central data that ranks Pune first in the state for crime, IANS reports.",
   "The Hawk (IANS)", "https://www.thehawk.in/news/states-and-uts/maharashtra/punes-law-and-order-alarming-cm-fadnavis-must-intervene-supriya-sule",
   "2026-11-25T21:12+05:30", "21:12", "claim", "Pune", "court-premises attack"),

 # ---------------- Chennai ----------------
 S(["chennai"], "Kovalam", "Chennai · Investment",
   "Tamil Nadu signs 78 deals worth ₹58,214 crore",
   "At the second VETTRI investment conclave near Kovalam on Wednesday, the state signed 78 agreements worth ₹58,214 crore that could create 65,786 jobs. "
   "Chief Minister Vijay also laid foundation stones for 15 projects worth ₹7,925 crore, DT Next reports.",
   "DT Next", "https://www.dtnext.in/news/tamilnadu/cm-vijay-presides-over-rs-58214-crore-investment-conclave-78-mous-signed",
   "2026-11-25T20:00+05:30", "", "fact", "₹58,214 cr", "78 MoUs"),
 S(["chennai"], "Chennai", "Chennai · Gold rate",
   "Gold falls ₹2,360 a sovereign in Chennai",
   "22-carat gold in Chennai fell by ₹2,360 per sovereign on Wednesday to ₹91,360 (₹11,420 a gram), reversing two days of gains, DT Next reports.",
   "DT Next", "https://www.dtnext.in/news/chennai/chennai-gold-price-falls-by-rs-2360-on-november-25-2026-check-todays-gold-silver-rate",
   "2026-11-25T04:49+05:30", "", "fact", "₹91,360", "per sovereign"),
 S(["chennai"], "Chennai", "Chennai · Fuel",
   "Petrol ₹107.77, diesel ₹99.55 – no change",
   "Fuel prices in Chennai were unchanged on Wednesday: petrol at ₹107.77 a litre and diesel at ₹99.55, DT Next reports.",
   "DT Next", "https://www.dtnext.in/news/business/check-out-petrol-and-diesel-prices-in-chennai-on-november-25-2026",
   "2026-11-25T07:57+05:30", "07:57", "fact", "₹107.77", "petrol / litre"),
 S(["chennai"], "Chennai", "Chennai · Civic",
   "Corporation finds 265 illegal hoardings, removes 90",
   "The Greater Chennai Corporation found 265 hoardings without licences across the city and has pulled down 90 so far, DT Next reports.",
   "DT Next", "https://www.dtnext.in/news/chennai",
   "2026-11-26T08:00+05:30", "", "fact", "265", "unlicensed hoardings"),

 # ---------------- Odisha ----------------
 S(["odisha"], "Bhubaneswar", "Odisha · Jobs",
   "CM Majhi wants one exam for similar government posts",
   "Chief Minister Mohan Charan Majhi suggested a single recruitment exam for posts in different departments that need the same qualifications, "
   "plus a fixed yearly hiring calendar and quick results, in talks with the central task force on exam reforms in Bhubaneswar, Pragativadi reports.",
   "Pragativadi", "https://pragativadi.com/odisha-cm-proposes-single-exam-for-similar-roles-recruitment-reform/",
   "2026-11-25T18:00+05:30", "", "fact", "1 exam", "for similar posts"),
 S(["odisha"], "Cuttack", "Odisha · Cuttack",
   "₹24,000 cr semiconductor hub and Mahanadi riverfront announced",
   "CM Majhi announced a ₹24,000 crore semiconductor hub and a ₹210 crore Mahanadi riverfront project for the Cuttack area, OMMCOM News reports.",
   "OMMCOM News", "https://ommcomnews.com/",
   "2026-11-25T17:00+05:30", "", "fact", "₹24K cr", "semiconductor hub"),
 S(["odisha"], "Cuttack", "Odisha · Fire",
   "Eight parked buses gutted by fire in Cuttack",
   "Eight parked buses were destroyed by a fire in Cuttack on Wednesday. No one was hurt, OMMCOM News and Odisharay report.",
   "OMMCOM News", "https://ommcomnews.com/",
   "2026-11-25T12:00+05:30", "", "fact", "8", "buses burnt, no injuries"),
 S(["odisha"], "Redhakhol", "Odisha · Wildlife",
   "Farmer killed by elephant while guarding paddy",
   "A farmer was trampled to death by an elephant while guarding his paddy field at Khamanmunda village under Redhakhol in Sambalpur district, OMMCOM News reports.",
   "OMMCOM News", "https://ommcomnews.com/",
   "2026-11-25T10:00+05:30", "", "fact", "Redhakhol", "human–elephant conflict"),
 S(["odisha"], "Bhubaneswar", "Odisha · Weather",
   "Nights to get 3–5 degrees colder",
   "Winter is setting in across interior Odisha, and night temperatures are likely to drop by 3 to 5 degrees over the next two to three days, local outlets report.",
   "Odisharay", "https://odisharay.com/cold-intensifies-in-interior-odisha/",
   "2026-11-25T09:00+05:30", "", "forecast", "−3 to −5°", "at night"),
 S(["odisha"], "Bhubaneswar", "Odisha · Sports",
   "Kalinga Stadium hosts first BIMSTEC U-23 athletics meet",
   "The first BIMSTEC Under-23 Athletics Championships are on at Kalinga Stadium in Bhubaneswar from 25 to 27 November, with four athletes from Odisha competing, OdishaBytes reports.",
   "OdishaBytes", "https://odishabytes.com/",
   "2026-11-25T08:00+05:30", "", "fact", "25–27 Nov", "Kalinga Stadium"),
]


def main():
    STORIES.sort(key=lambda s: s["pub"], reverse=True)
    data = {"date": "26.11.2026", "updated": "2026-11-26T18:00+05:30", "version": 1, "edition": "in-regions",
            "tz": "Asia/Kolkata", "preview": True, "stories": STORIES}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    by = {}
    for s in STORIES:
        for k in s["sec"]:
            by[k] = by.get(k, 0) + 1
    print(len(STORIES), "stories", by)


if __name__ == "__main__":
    main()
