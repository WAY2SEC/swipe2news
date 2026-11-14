MORNING DATA for the Morning Briefing utility strip: morning.json at the repo root. Real values only, each from a page retrieved in this run. Never estimate or copy an old value; if a value can't be found for TODAY (IST), leave that key out (the app hides the chip).

Shape (keep exactly; validate with json.load):
{"updated":"<ISO time IST>",
 "gold":{"place":"hyderabad","k22":<₹ per 1 gram, 22 carat, number>,"k24":<₹ per 1 gram, 24 carat, number>,"date":"<YYYY-MM-DD the page says the rate is for>","src":"<site name>","url":"<page url>"},
 "panch":{"date":"<today YYYY-MM-DD>","place":"Hyderabad",
   "tithi":{"te":"<e.g. శుక్ల పంచమి>","en":"<e.g. Shukla Panchami>","hi":"<e.g. शुक्ल पंचमी>"},"tithiEnd":"<HH:MM 24h IST>",
   "nak":{"te":"<e.g. పూర్వాషాఢ>","en":"<e.g. Purva Ashadha>","hi":"<e.g. पूर्वाषाढ़ा>"},"nakEnd":"<HH:MM>",
   "masa":{"te":"<e.g. కార్తీక మాసం>","en":"<e.g. Kartika>","hi":"<e.g. कार्तिक>"},
   "src":"<site name>","url":"<page url>"}}

GOLD: search "gold rate today Hyderabad 22 carat 24 carat <today's date>" (WebSearch, then WebFetch the best page). Use only a page that states TODAY's date for the rate (The Hans India daily "Gold and Silver rates today, <D> Nov in Hyderabad", BankBazaar, GoodReturns, 5paisa, ClearTax). Per 1 gram. If 10-gram prices are given, divide by 10. 22K must be below 24K.
PANCHANGAM: search "panchangam <today's date> Hyderabad tithi nakshatra" (Drik Panchang based pages such as hindutone.com or drikpanchang.com). Tithi and nakshatra AT SUNRISE in Hyderabad, with their end times. Telugu month (amanta). Rahu Kalam is NOT stored: the app calculates it from the district's sunrise and sunset.

Change only morning.json. Commit "Morning data <date>" with the rest of the run's commit.
