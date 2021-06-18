print(
'Functions defined:\n\n',
'get_web_contents(link)\t\t\treturns "contents"\n',
'get_links(soup)\t\t\treturns "links"\n',
'parse_entry(contents, url, counter)\treturns "dataframe"\n',
'generate_hexes(hex_code = "37E2A2")\treturns "hex links"\n',
'scrape_web(links)\t\t\tsaves web scraped contents to Excel file'
)

def get_web_contents(link):
    
    '''This function get any web contents (except fully dynamic aka DOM)'''
    
    import urllib.request
    
    page = urllib.request.urlopen(link)    
    
    return page.read().decode('utf')
    
def get_links(soup):
    
    '''This function gets links from Document Registry
    The function is used once to understand links pattern'''
    
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(soup, "lxml")

    links = []
    for link in soup.findAll('document'):
        links.append(link.get('href'))
    
    return links
    
def parse_entry(contents, url, counter):
    
    '''
    This function parses out the contents of one document entry in Document Registry
    The idea is to use ad-hoc functionalities based on text manipulation and obtain values 
    for only select fields, which are:
                         columns = ['URL',
                                'Kellelt',
                                'Kellele',
                                'Väljaandja',
                                'Dok No', 
                                'Kuupäev',
                                'Dok Tüüp', 
                                'Dok Klass', 
                                'AK']
    '''
    
    import pandas as pd
    
    e = 'Veateade'
    
    def clean(field):
        
        import re
        
        try:
            field = re.sub('\<field name=".{1,20}">', '' ,field)
        except:
            pass
        return field
        
    def len_check(field):
        
        if len(field) > 35:
            return ''
        else:
            return field
        
    def len_check_long(field):
        
        if len(field) > 50:
            return ''
        else:
            return field
        
    contents = BeautifulSoup(contents, "lxml").decode('utf')
    fields = contents.split('</fieldtitles>')[0]
    contents = contents.split('</fieldtitles>')[-1]

    try: 
        if len(contents.split('govinstitution">')) > 1:           
            source =contents.split('govinstitution">')[-1].strip().split('</')[0].strip()
            source = len_check_long(source)
            if source.find('<') > -1 or source.find('>') > -1:
                source = clean(source)
        else:
            source = ''
                
    except:
        source = e
        
    try:
        if len(contents.split('companyname">')) > 1:
            destination = contents.split('companyname">')[-1].strip().split('</')[0].strip()
            destination = len_check_long(destination)
            if destination.find('<') > -1 or destination.find('>') > -1:
                destination = clean(destination)
        else:
            destination = ''
    except:
        destination = e
    
    try:
        if destination != '' and destination != e:
            direction = fields.split('"companyname">')[-1].split('</fieldtitle>')[0].strip()
            if direction == 'Kellelt':
                source, destination = destination, source
    except:
        pass

    
    try:
        if source != '' and source != e:
            direction = fields.split('govinstitution">')[-1].split('</fieldtitle>')[0].strip()
            if direction == 'Kellele':
                source, destination = destination, source
    except:
        pass
    
    try:
        if len(contents.split('"docissuer">')) > -1:
            issuer = contents.split('"docissuer">')[-1].strip().split('</')[0].strip()
            issuer = len_check(issuer)
            if issuer.find('<') > -1 or issuer.find('>') > -1:
                issuer = clean(issuer)
        else:
            issuer = ''
    except:
        issuer = e
    
    try:
        if len(contents.split('"docid">')) > -1:
            doc_no = contents.split('"docid">')[-1].strip().split('</')[0].strip()
            doc_no = len_check(doc_no)
            if doc_no.find('<') > -1 or doc_no.find('>') > -1:
                doc_no = clean(doc_no)
        else:
            doc_no = ''
    except:
        doc_no = e
    
    try:
        date = contents.split('date">')[-1].strip().split('</')[0].strip()
        date = len_check(date)
        if date.find('<') > -1 or date.find('>') > -1:
            date = clean(date)
    except:
        date = e
    
    try:
        if len(contents.split('type">')) > -1:
            _type=contents.split('type">')[1].strip().split('</')[0].strip()
            _type = len_check(_type)
            if _type.find('<') > -1 or _type.find('>') > -1:
                _type=clean(_type)
        else:
            _type = ''
    except:
        _type = e
    
    try:
        hierarchy = contents.split('"journalkeyhierarchy">')[-1].strip().split('</')[0].strip()
    except:
        hierarchy = e
    
    try:
        if contents.find('docaccesstype">') > -1:
            classified = contents.split('docaccesstype">')[-1].strip().split('</')[0].strip()
            classified = len_check(classified)
            if classified.find('<') > -1 or classified.find('>') > -1:
                classified = clean(classified)
        else:
            classified = ''
    except:
        classified = e
        
    try:
        
        if contents.split('"protocolnumber">')[1].strip().split('</')[0].strip():
            temp = contents.split('"protocolnumber">')[-1].strip().split('</')[0].strip()
            if len(temp) != None and len(temp) != 0 and len(temp) < 100:
                hierarchy = 'Protokoll'
                _type = ''
                doc_no = temp
    except:
        pass
    
    if hierarchy.find('<field name="subject">') > -1:
        #hierarchy = hierarchy.replace('<field name="subject">','')
        if hierarchy.find('<') > -1 or hierarchy.find('>') > -1:
            hierarchy = clean(hierarchy)
        
    df = pd.DataFrame(
                     columns = ['URL',
                                'Kellelt',
                                'Kellele',
                                'Väljaandja',
                                'Dok No', 
                                'Kuupäev',
                                'Dok Tüüp', 
                                'Dok Klass', 
                                'AK'], 
                      index = [counter])
    
    df.at[counter, 'URL'] = url
    df.at[counter, 'Kellelt'] = source
    df.at[counter, 'Kellele'] = destination
    df.at[counter, 'Väljaandja'] = issuer
    df.at[counter, 'Dok No'] = doc_no
    df.at[counter, 'Kuupäev'] = date
    df.at[counter, 'Dok Tüüp'] = _type
    df.at[counter, 'Dok Klass'] = hierarchy
    df.at[counter, 'AK'] = classified
    
    return df
    
def generate_hexes(hex_code = '37E2A2'):
    
    ''' Generate hexes for links'''

    selection = [hex(number).split('x')[-1] for number in range(0,256)]
    selection = ['0' + number.upper() if len(number) == 1 else number.upper() for number in selection]

    generated_links = []

    base = 'https://dhs.riigikantselei.ee'
    iterative_part_numbers = '/avalikteave.nsf/documents/NT'#003822' # two figures are missing

    for i in range(16341):
        generated_number = '00' + str(hex(int(hex_code, 16) + i)).upper().split('X')[-1]
        generated_link = base + iterative_part_numbers + generated_number
        
        if generated_link not in generated_links:
            generated_links.append(generated_link)
            
    return generated_links
    
def scrape_web(generated_links):

    import time
    from datetime import datetime
    import pandas as pd
    from bs4 import BeautifulSoup

    collected_entries = pd.DataFrame()

    counter = 0
    iterator = 0

    print('Commencing scraping...', datetime.now().strftime("%H:%M:%S"))

    for l in generated_links:

        df = pd.DataFrame()
        
        try:
            contents = get_web_contents(l)
            df = parse_entry(contents, l, iterator)
            
            if counter == 0:
                collected_entries = df
            else:
                collected_entries = collected_entries.append(df)
            
            iterator += 1
        
        except Exception as e:
            time.sleep(.5)
            pass
        
        if iterator == 100:
            now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            filename = now + '_' + str(counter) + '_temp_.xlsx'
            collected_entries.to_excel(filename)
            print('Saving..', filename, 'on', str(counter), 'iteration', datetime.now().strftime("%H:%M:%S"))
            iterator = 0
            time.sleep(5)
            
        counter += 1
        
    now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    filename = now + '_' + str(counter) + '_FINAL_.xlsx'
    collected_entries.to_excel(filename)
    print('Saving..', filename, 'on', str(counter), 'iteration')
    print('Scraping completed with', str(counter), 'runs altogether', str(len(collected_entries)), 'collected', datetime.now().strftime("%H:%M:%S"))