from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os
import io
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from lxml import etree as et
import requests
from io import BytesIO

def update_xmls(service):
    results = service.files().list(pageSize = 300, q = "parents in '1MuZ3F4Pmf678oNnNqUfBTccUD7N3U77m'", fields="nextPageToken, files(id, name,mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        print('Filename (File ID)')
        for item in items:
            if item['name'] != 'Updated':
                get_xml(item['id'], item['name'].encode('utf-8'))


def get_xml(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    renamed_file = 'OLD' + file_name
    os.rename(file_name, renamed_file)
    xml = parse_xml(renamed_file, file_name)
    file_metadata = {'name': xml, 'parents': ['1rnETUjOevkE1ZEFdo6yxdspV2XrFzHID']}
    media = MediaFileUpload(xml,mimetype='text/xml')
    file = service.files().create(body=file_metadata,media_body=media,fields='id').execute()
    os.remove(renamed_file)
    os.remove(file_name)

def parse_xml(renamed_file, file_name):
    parser = et.XMLParser(remove_blank_text=True)
    tree = et.parse(renamed_file, parser)
    root = tree.getroot()
    mods = tree.xpath('namespace-uri(.)')
    update_fields(tree,root,mods)
    for subject in root.findall('{http://www.loc.gov/mods/v3}subject'):
        authority = subject.get('authority')
        if authority == 'local':
            update_headings(subject[0].text,tree,root, mods)
    tree.write(file_name, pretty_print = True)
    return file_name

def update_fields(tree, root, mods):

    #typeOfResource
    if len(root.findall('{' + mods + '}typeOfResource')) == 0:
        type = et.SubElement(root, et.QName(mods, "typeOfResource"))
        type.text = "text"

    # genre
    if len(root.findall('{' + mods + '}genre')) == 0:
        genre = et.SubElement(root, et.QName(mods, "genre"), authority="aat")
        genre.text = "theses"

    # language
    if len(root.findall('{' + mods + '}language')) == 0:
        language = et.SubElement(root, et.QName(mods, "language"))
        languageTerm = et.SubElement(language, et.QName(mods, "languageTerm"), type="code", authority="iso639-2b")
        languageTerm.text = "eng"

    # physical description
    if len(root.findall('{' + mods + '}physicalDescription')) == 0:
        physicalDescription = et.SubElement(root, et.QName(mods, "physicalDescription"))
        digitalOrigin = et.SubElement(root, et.QName(mods, "digitalOrigin"))
        digitalOrigin.text = "born digital"

def update_headings(local_word, tree, root, mods):
    word_URL = local_word.replace(' ', '%20')
    r = requests.get('http://fast.oclc.org/searchfast/fastsuggest?&query=' + word_URL +'&queryIndex=suggestall&queryReturn=suggestall%2Cdroot%2Cauth%2Ctag%2Ctype%2Craw%2Cbreaker%2Cindicator&suggest=autoSubject&rows=5')
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

scope = ['https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('Theses-1596154aeca8.json',scope)

service = build('drive', 'v3', http = credentials.authorize(Http()))

update_xmls(service)

