import requests, pyperclip as copier
from bs4 import BeautifulSoup
from rich import print as color_print
import os, sys, json
# This is a weird bug. My CMD seems to be unable to present the Japanese encoding system, below is a solution.
# os.system('chcp 65001')  # Changes CMD to UTF-8 encoding
# # If above not work, 2nd solution is below, is trigged at fn:run 
# def setup_console():
#     # Change console encoding to UTF-8
#     os.system('chcp 65001')
    
#     # Set up console output encoding
#     sys.stdout.reconfigure(encoding='utf-8')
    
#     # Optional: Change console font to a Japanese-compatible one
#     os.system('reg add "HKEY_CURRENT_USER\Console" /v "FaceName" /t REG_SZ /d "MS Gothic" /f')
# Third solution: まだ分からない。。ごめん_(>_<。)_
# Fourth solution: ACTUALLY, this is 3rd solution, install git console (*￣3￣)╭

# Global Configurable Variable
Kanji = "人"  # Required kanji, e.g., alterable.
BaseUrl = f"https://jisho.org/search/*{Kanji}*%20%23words%20%23common"  # Base URL for Jisho search with mustKanji placeholder
hasLearned = '聞疲休憩日一人年大二三四五六七八九十本中出思分立音意口未味長行時見月前生間上入後東金学高円子外来気話女北午百書先名川千水半男西電校語隹言誰俺君僕土木食車何南万毎白天母火右読友左休父雨会同事自社発者地業方丈台至去広公左小早林空田虫耳手足力夕文字村町森玉王石国竹糸貝赤青数多少形太細点丸交光角計直線矢弱親姉兄弟妹体毛豆頭顔首心曜朝昼夜週春夏秋冬今新古遠近内場園谷'  # Kanji been learned  # Kanji been learned
Template = """<div style="text-align:center;"><span style="color: orange; font-family: &quot;JetBrains mono&quot;; font-weight: 700;">Kanji (see stem)</span></div><div style="text-align:center;"><span id="spanspoiler" style="background-color: rgb(10, 10, 10); padding: 2px 4px; border-radius: 4px; color: rgb(10, 10, 10); font-family: sans-serif; transition: background-color 0.1s ease 0s, color 0.1s ease 0s; user-select: none; border: 1px solid rgba(255, 255, 255, 0.05);" onmouseover="this.style.color='#fff';this.style.userSelect='auto';" onmouseout="this.style.color='#0a0a0a';this.style.userSelect='none';">{KANJI}</span><br></div><div style="text-align:center;"><h1 style="font-size:3.052rem;text-shadow: #ffffffaa 0 0 25px;font-weight:1">{VOCAB} (o)</h1>
  <p style="color:#acf;font-size:1.552rem;text-shadow: #acf 0 0 25px;font-family:JetBrains mono;"></p><p style="color:#acf;font-size:1.552rem;text-shadow: #acf 0 0 25px;font-family:JetBrains mono;">{MEANING}<br></p><p style="color:#acf;font-size:1.552rem;text-shadow: #acf 0 0 25px;font-family:JetBrains mono;"><span style="font-size: 1.552rem;"></span></p>

   <span style="color: orange; font-weight: 700;font-family:JetBrains mono;">Romaji</span>
   <h1 style="font-size:3.052rem;text-shadow: #ffffffaa 0 0 25px;padding-bottom:15px">{FURIGANA}</h1>
   <hr>
<span style="color: orange; font-weight: 700;font-family:JetBrains mono;">Clue</span></div><div style="text-align:center;"><span id="spanspoiler" style="background-color: rgb(10, 10, 10); padding: 2px 4px; border-radius: 4px; color: rgb(10, 10, 10); font-family: sans-serif; transition: background-color 0.1s ease 0s, color 0.1s ease 0s; user-select: none; border: 1px solid rgba(255, 255, 255, 0.05);" onmouseover="this.style.color='#fff';this.style.userSelect='auto';" onmouseout="this.style.color='#0a0a0a';this.style.userSelect='none';">&nbsp;&nbsp;</span><br></div>"""
isTemplate = True

# ----------------- P R O G R A M --------------------------------------
def Log(text, status=0):
    if status == "f":
        color_print(f"[red bold][X]{text}[/]") 
    elif status == "s":
        color_print(f"[green bold][V]{text}[/]") 
    elif status == "c":
        color_print(f"[yellow bold][?]{text}[/]") 
    elif status == "w":
        color_print(f"[orange bold][!]{text}[/]") 
    elif status == "i":
        color_print(f"[blue]{text}[/]") 
    elif status == '_':
        color_print(text)
    else:
        color_print(f"[green bold]{text}[/]") 
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
        Log(f"Failure.\nCode: {r.status_code}", "f")
        return []
    
    p = BeautifulSoup(r.content, 'html.parser')

    results = []

    # Check if "More Words" exist, if no, do not continue to next page, therefore break.
    isNextPagination = bool(p.select_one('a.more'))
    # Return True if the element exists, otherwise False

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
            
    return results, isNextPagination

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
def paginationHandler(Kanji, p):
    resultsMerge = []
    for p in range(1, p):
        results, isNextPagination = scrape(Kanji, p)
        Log(f"Scraper at Pagination [{p}] Do next Pagination [{isNextPagination}]", '_')
        resultsMerge.extend(results)
        if not isNextPagination:
            break 
    return resultsMerge

def run(Kanji, limit=10):
    # setup_console() # Fix smoe CMD unable to represent the japanese character.
    
    # List of Vocabs with limit
    Scraper = paginationHandler(Kanji, limit)  # passing limit to paginationHandler
    
    if not Scraper:
        Log("Nil.", "f")
        return
    
    # Pagination settings    
    paginationLimit = 10  # number of items per page
    total_items = len(Scraper)
    current_page = 0
    total_pages = (total_items + paginationLimit - 1) // paginationLimit
    
    while True:
        # Clear previous output
        print("\033[H\033[J")
        
        # Show pagination info
        Log(f"Page {current_page + 1} of {total_pages}")
        Log(f"Items {current_page * paginationLimit + 1}-{min((current_page + 1) * paginationLimit, total_items)} of {total_items}")
        Log("Scraped Vocabulary:")
        
        # Display current page items
        start_idx = current_page * paginationLimit
        end_idx = min(start_idx + paginationLimit, total_items)
        
        # Print enumerated vocabulary items
        for i in range(start_idx, end_idx):
            eVocab = Scraper[i]
            color_print(f"{i + 1}. [cyan bold]{eVocab['Vocab']}[/] ([#0ff i]{eVocab['Furi']})[/] \n=> [#0f0 bold]{eVocab['Meaning']}[/]")
            
        # Navigation and copy instructions
        Log("\nNavigation: < (previous) | > (next) | _ (exit)")
        Log("To copy a vocabulary item, enter its number")
        command = input("Enter command or number: ").strip()
        
        if command == "<":
            current_page = max(0, current_page - 1)
        elif command == ">":
            current_page = min(total_pages - 1, current_page + 1)
        elif command == "_":
            break
        elif command.isdigit():
            index = int(command) - 1
            if 0 <= index < total_items:
                eVocab = Scraper[index]
                formatted_template = Template.format(
                    KANJI=Kanji, 
                    VOCAB=r"{{c1::"+eVocab['Vocab']+r"}}",
                    MEANING=r"{{c2::"+str(r"<br>".join(eVocab['Meaning']))+r"}}",
                    FURIGANA=r"{{c3::"+str(eVocab['Furi'])+r"}}"
                )
                # Copy to clipboard
                copier.copy(formatted_template)
                print("\nTemplate copied to clipboard:")
                Log("Recorded to clipboard", "s")
                input("Enter to continue...")
            else:
                Log("Invalid number. Enter a valid vocabulary number.", "c")
                input("Enter to continue...")
        else:
            Log("Use <, >, _ to navigate or enter a number", "c")
            input("Enter to continue...")
kanji = input("Target Kanji: ").strip()
howmuch = int(input("Total page: ").strip())
run(kanji, howmuch)
