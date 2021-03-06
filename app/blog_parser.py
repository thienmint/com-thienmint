import xml.etree.ElementTree as ET
import re


def parse_swe_blog(post):
    entry = post.getroot()
    id = entry.find('id').text
    title = entry.find('title').text
    content = entry.find('content')

    headers = []
    texts = []

    for row in content:
        header, text = list(row)
        header = header.text.strip()

        text_children = list(text)
        text_list = [text.text.strip()]

        for text_elem in text_children:
            text_list.append(parse_swe_element(text_elem))
            text_list.append(text_elem.tail)

        text = ''.join(text_list)
        coalese_empty_space = re.sub(r'[ \t\r\f\v]+', ' ', text)
        line_break = re.sub(r'(?<=\s)\n', '</br>\n', coalese_empty_space)
        final_text = ''.join(line_break.split('\n'))

        headers.append(header)
        texts.append(final_text)

    return dict(id=id, title=title, headers=headers, texts=texts)


def parse_swe_element(elem):
    if elem.tag == 'link':
        return '<a href="{0}">{1}</a>'.format(elem.attrib['href'], elem.text)


def make_preview(headers, texts):
    if len(headers) <= 0 or len(texts) <= 0:
        return "", ""

    header = headers[0][:100]
    text = texts[0][:250] + ' ...'

    return dict(header=header, text=text)


if __name__ == '__main__':
    post = ET.parse('static/swe-entries/w01.xml')
    t, h, te = parse_swe_blog(post)
    d = {k:v for (k,v) in zip(h, te)}
    for header in d.keys():
        print header
        print d[header]
