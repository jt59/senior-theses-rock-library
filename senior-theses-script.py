import csv
import sys
from lxml import etree as et
import requests

with open('2018-Senior-Theses-Metadata-Sheet1.csv') as csvDataFile:
    fileNum = 0
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        if fileNum != 0:
            # prefixes
            mods = "http://www.loc.gov/mods/v3"
            xsi = "http://www.w3.org/2001/XMLSchema-instance"
            NS_map = {"mods": mods, "xsi": xsi}

            # register namespace prefix
            et.register_namespace('mods', mods)
            et.register_namespace('xsi', xsi)

            rootName = et.QName(mods, 'mods')
            root = et.Element(rootName, nsmap=NS_map)
            root.set('{' + xsi + '}schemaLocation',
                     "http://www.loc.gov/mods/v3 http://www.loc.gov/mods/v3/mods-3-6.xsd")
            tree = et.ElementTree(root)

            # record the title of your thesis
            titleInfo = et.SubElement(root, et.QName(mods, "titleInfo"))
            title = et.SubElement(titleInfo, et.QName(mods, "title"))
            title.text = row[0]
            title.text = title.text.replace("’", "'")
            title.text = title.text.replace("–", "--")

            # record your name as you want it to appear
            name_author = et.SubElement(root, et.QName(mods, "name"), type="personal")
            namePart_author = et.SubElement(name_author, et.QName(mods, "namePart"))
            namePart_author.text = row[1]
            role_author = et.SubElement(name_author, et.QName(mods, "role"))
            roleTerm_author = et.SubElement(role_author, et.QName(mods, "roleTerm"), type="text",
                                            authority="marcrelator")
            roleTerm_author.text = "author"

            # select your degree
            note_degree = et.SubElement(root, et.QName(mods, "note"), type="thesis")
            note_degree.text = "Senior thesis (" + row[2] + ")--Brown University, 2018"

            # select the department that is granting your degree
            name_dpt = et.SubElement(root, et.QName(mods, "name"), type="corporate")
            namePart_brown = et.SubElement(name_dpt, et.QName(mods, "namePart"))
            namePart_brown.text = "Brown University"
            namePart_dpt = et.SubElement(root, et.QName(mods, "namePart"))
            namePart_dpt = row[3]

            role_dpt = et.SubElement(name_dpt, et.QName(mods, "role"))
            roleTerm_dpt = et.SubElement(role_dpt, et.QName(mods, "roleTerm"), type="text", authority="marcrelator")
            roleTerm_dpt.text = "sponsor"

            # record your concentration
            note_concentration = et.SubElement(root, et.QName(mods, "note"), displayLabel="Concentration")
            note_concentration.text = row[4]

            # record the name of your primary advisor
            name_adv = et.SubElement(root, et.QName(mods, "name"), type="personal")
            namePart_adv = et.SubElement(name_adv, et.QName(mods, "namePart"))
            namePart_adv.text = row[5]
            role_adv = et.SubElement(name_adv, et.QName(mods, "role"))
            roleTerm_adv = et.SubElement(role_adv, et.QName(mods, "roleTerm"), type="text", authority="marcrelator")
            roleTerm_adv.text = "advisor"

            # record your second reader's name
            if row[6] != "":
                name_r2 = et.SubElement(root, et.QName(mods, "name"), type="personal")
                namePart_r2 = et.SubElement(name_r2, et.QName(mods, "namePart"))
                namePart_r2.text = row[6]
                role_r2 = et.SubElement(name_r2, et.QName(mods, "role"))
                roleTerm_r2 = et.SubElement(role_r2, et.QName(mods, "roleTerm"), type="text", authority="marcrelator")
                roleTerm_r2.text = "reader"

            # write a brief abstract of 200-250 words
            abstract = et.SubElement(root, et.QName(mods, "abstract"))
            abstract.text = row[7]
            abstract.text = abstract.text.replace("’","'")
            abstract.text = abstract.text.replace("–", "--")
            abstract.text = abstract.text.replace("π", "(pi)")
            abstract.text = abstract.text.replace("β", "(Beta)")
            abstract.text = abstract.text.replace("γ", "(gamma)")
            abstract.text = abstract.text.replace("α", "(alpha)")
            abstract.text = abstract.text.replace("<", "less than")

            # suggest 2-4 key words that describe the content
            given_words = row[8].split('|')
            if len(given_words) == 1:
                given_words = given_words[0].split(', ')
            if len(given_words) == 1:
                given_words = given_words[0].split('--')
            if len(given_words) == 1:
                given_words = given_words[0].split('/')
            num_words = len(given_words)
            unassigned_fast = 0
            for word in given_words:
                keywords_loc = et.SubElement(root, et.QName(mods, "subject"), authority="local")
                facet_loc = et.SubElement(keywords_loc, et.QName(mods, "topic"))
                facet_loc.text = word

                # fast headings
                word_URL = word.replace(' ', '%20')
                r = requests.get(
                'http://fast.oclc.org/searchfast/fastsuggest?&query=' + word_URL +'&queryIndex=suggestall&queryReturn=suggestall%2Cdroot%2Cauth%2Ctag%2Ctype%2Craw%2Cbreaker%2Cindicator&suggest=autoSubject&rows=5')
                json = r.json()
                if len(json['response']['docs']) > 0:
                    keywords_fast = et.SubElement(root, et.QName(mods, "subject"), authority="FAST", authorityURI="http://id.worldcat.org/fast", valueURI="http://id.worldcat.org/fast/01086288")
                    facet_tag = json['response']['docs'][0]['tag']
                    facet_name = None
                    if facet_tag == 100:
                        facet_name = "personal"
                    elif facet_tag == 110:
                        facet_name = "corporate"
                    elif facet_tag == 111:
                        facet_name = "event"
                    elif facet_tag == 130:
                        facet_name = "uniform"
                    elif facet_tag == 150:
                        facet_name = "topic"
                    elif facet_tag == 151:
                        facet_name = "geographic"
                    elif facet_tag == 155:
                        facet_name = "form"
                    else:
                        print("tag error")
                    facet_fast = et.SubElement(keywords_fast, et.QName(mods, facet_name))
                    facet_fast.text = json['response']['docs'][0]['auth']
                else:
                    unassigned_fast += 1
                    if unassigned_fast == num_words:
                        print("no fast heading assigned for" + fileNum)


            # type
            type = et.SubElement(root, et.QName(mods, "typeOfResource"))
            type.text = "text"

            # genre
            genre = et.SubElement(root, et.QName(mods, "genre"), authority="aat")
            genre.text = "theses"

            # date
            originInfo = et.SubElement(root, et.QName(mods, "originInfo"))
            dateCreated = et.SubElement(originInfo, et.QName(mods, "dateCreated"), keyDate="yes", encoding="w3cdtf")
            dateCreated.text = "2018"

            # language
            language = et.SubElement(root, et.QName(mods, "language"))
            languageTerm = et.SubElement(language, et.QName(mods, "languageTerm"), type="code", authority="iso639-2b")
            languageTerm.text = "eng"

            # physical description
            physicalDescription = et.SubElement(root, et.QName(mods, "physicalDescription"))
            digitalOrigin = et.SubElement(root, et.QName(mods, "digitalOrigin"))
            digitalOrigin.text = "born digital"

            xml = tree.write('2018_senior_thesis_' + str(fileNum) + '.xml', encoding="utf-8", pretty_print=True)
        fileNum += 1






