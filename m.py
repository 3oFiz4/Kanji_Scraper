import requests
from bs4 import BeautifulSoup

# Global Configurable Variable
Kanji = "国"  # Required kanji
BaseUrl = f"https://jisho.org/search/*{Kanji}*%20%23words%20%23common"  # Base URL for Jisho search with mustKanji placeholder
hasLearned = '外人'  # Kanji been learned
Template = """<div style="text-align:center;"><span style="color: orange; font-family: &quot;JetBrains mono&quot;; font-weight: 700;">Kanji (see stem)</span></div><div style="text-align:center;"><span id="spanspoiler" style="background-color: rgb(10, 10, 10); padding: 2px 4px; border-radius: 4px; color: rgb(10, 10, 10); font-family: sans-serif; transition: background-color 0.1s ease 0s, color 0.1s ease 0s; user-select: none; border: 1px solid rgba(255, 255, 255, 0.05);" onmouseover="this.style.color='#fff';this.style.userSelect='auto';" onmouseout="this.style.color='#0a0a0a';this.style.userSelect='none';">{KANJI}</span><br></div><div style="text-align:center;"><h1 style="font-size:3.052rem;text-shadow: #ffffffaa 0 0 25px;font-weight:1">{VOCAB} (o)</h1>
  <p style="color:#acf;font-size:1.552rem;text-shadow: #acf 0 0 25px;font-family:JetBrains mono;"></p><p style="color:#acf;font-size:1.552rem;text-shadow: #acf 0 0 25px;font-family:JetBrains mono;">{MEANING}<br></p><p style="color:#acf;font-size:1.552rem;text-shadow: #acf 0 0 25px;font-family:JetBrains mono;"><span style="font-size: 1.552rem;"></span></p>

   <span style="color: orange; font-weight: 700;font-family:JetBrains mono;">Romaji</span>
   <h1 style="font-size:3.052rem;text-shadow: #ffffffaa 0 0 25px;padding-bottom:15px">{FURIGANA}</h1>
   <hr>
<span style="color: orange; font-weight: 700;font-family:JetBrains mono;">Clue</span></div><div style="text-align:center;"><span id="spanspoiler" style="background-color: rgb(10, 10, 10); padding: 2px 4px; border-radius: 4px; color: rgb(10, 10, 10); font-family: sans-serif; transition: background-color 0.1s ease 0s, color 0.1s ease 0s; user-select: none; border: 1px solid rgba(255, 255, 255, 0.05);" onmouseover="this.style.color='#fff';this.style.userSelect='auto';" onmouseout="this.style.color='#0a0a0a';this.style.userSelect='none';">&nbsp;&nbsp;</span><br></div>"""
isTemplate = True

# ----------------- P R O G R A M --------------------------------------

hasLearned = list(hasLearned)
def isVocab(scrVocab):
    if Kanji not in scrVocab:return False

    # isVocab rule:
    # 1. eChar Must have Kanji
    # 2. eChar have any character in hasLearned
    for eChar in scrVocab:
        if eChar != Kanji and eChar not in hasLearned: return False 
    return True, scrVocab

# div.concept_light-readings.japanese.japanese_gothic
# div.concept_light-representation
# span.text OR span.furigana

def scrape(Kanji, p):
    r = requests.get(BaseUrl+f'?page={p}')

    if r.status_code != 200:
        print(f"[!] Failure.\nCode: {r.status_code}")
        return []
    
    p = BeautifulSoup(r.content, 'html.parser')

    results = []

    # Find all elements matching the structure
    # OK
    targetElementCharacter = p.select("div.concept_light-readings.japanese.japanese_gothic > div.concept_light-representation")
    targetElementMeaning = p.select("div.meanings-wrapper")
    for eTargetElementCharacter, eTargetElementMeaning in zip(targetElementCharacter, targetElementMeaning):
        scrVocab = eTargetElementCharacter.select_one("span.text").get_text(strip=True) if eTargetElementCharacter.select_one("span.text") else None
        scrFuri = eTargetElementCharacter.select_one("span.furigana").get_text(strip=True) if eTargetElementCharacter.select_one("span.furigana") else None

        if isVocab(scrVocab) and scrFuri:
            Vocab = scrVocab
            Furi = scrFuri
            Meaning = formatMeaning(eTargetElementMeaning)
            results.append({"Vocab": Vocab, "Furi": Furi, "Meaning": Meaning})
    return results

# Had to create another utility function, to avoid messy code.
def formatMeaning(html):
    fP = BeautifulSoup(str(html), 'html.parser')
    meanings = fP.find_all('div', class_='meaning-wrapper')
    tags = fP.find_all('div', class_='meaning-tags')

    formatted_meanings = []

    for i, meaning in enumerate(meanings):
        meaning_text = meaning.find('span', class_='meaning-meaning')
        meaning_text = meaning_text.text.strip() if meaning_text else None
        tag_text = tags[i].text.strip() if i < len(tags) else None
        if meaning_text:
            formatted_meaning = f"{meaning_text} ({tag_text})" if tag_text else meaning_text
            formatted_meanings.append(formatted_meaning)
    
    # Return the formatted meanings
    return formatted_meanings

# Handle pagination.
def paginationHandler(Kanji, p=5):
    resultsMerge = []
    for p in range(1, p+1):
        print("Scraper at Pagination", p)
        results = scrape(Kanji, p)
        resultsMerge.extend(results)
    return resultsMerge

def run(Kanji, limit=10):
    # List of Vocabs
    Scraper = paginationHandler(Kanji, 5)

    if Scraper:
        print("Scraped Vocabulary:")
        count = 0
        for eVocab in Scraper:
            if count >= limit:
                break 
            formatted_template = Template.format(
                KANJI=Kanji, 
                VOCAB=r"{{c1::"+str(eVocab['Vocab'])+r"}}",
                MEANING=r"{{c2::"+str(r"<br>".join(eVocab['Meaning']))+r"}}",
                FURIGANA=r"{{c3::"+str(eVocab['Furi'])+r"}}"
            )
            print(f"""


            ------------------------------------
            {formatted_template}
            ------------------------------------


            """)
        
            count += 1
    else:
        print("Nil.")

run(Kanji, 2)
