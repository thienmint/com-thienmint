#main.py

# [START imports]
import logging, traceback
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message

# Custom stuff
from email_info import get_info
from blog_parser import parse_swe_blog, make_preview
# Regex
import xml.etree.ElementTree as ET
import re
import os
from operator import itemgetter, attrgetter
# [END imports]

# [START create_app]
app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('config.py')
email_username, email_password = get_info()
app.config['MAIL_USERNAME'] = email_username
app.config['MAIL_PASSWORD'] = email_password
mail = Mail(app)
# [END create_app]

# [START constants]

quotes = [
    {
        'text': '"If we knew each other\'s secrets, what comfort we should find."',
        'person': 'John Churton Collins'
    },
    {
        'text': '"Someday this pain will be useful to you."',
        'person': 'Peter Cameron'
    },
    {
        'text': '"You don\'t need to be a genius to code. You need to be determined."',
        'person': 'Vanessa Hurst'
    },
]

user_info = {
    'first_name': 'Thien',
    'last_name': 'Vo',
    'middle_name': 'Quang',
    'phone': '(512) 954-4289',
    'email': 'thienqvo@gmail.com'
}


@app.context_processor
def inject_quotes():
    return dict(quotes=quotes)\



@app.context_processor
def inject_user_info():
    return dict(user_info=user_info)

# [END constants]
# [START routing]


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/demo')
def demo():
    return render_template("demo.html")


@app.route('/blog')
def blog():
    return render_template("blog.html")


@app.route('/blog/swe')
def swe():
    swe_entry_path = os.path.join(app.static_folder, 'swe-entries')

    files = os.listdir(swe_entry_path)

    exclusion = ['template.xml']
    # Remove all files from exclusions list from listing
    for exclude_file in exclusion:
        if exclude_file in files:
            files.remove(exclude_file)

    entries_list = []
    # Compile a list of all SWE blog's entries
    for file_name in files:
        if not file_name.endswith('.xml'):
            continue

        post = ET.parse(os.path.join(swe_entry_path, file_name))
        parse_items = parse_swe_blog(post)

        id = parse_items['id']
        title = parse_items['title']
        file_name = re.sub('\.xml', '', file_name)
        preview = make_preview(parse_items['headers'], parse_items['texts'])

        entries_list.append(dict(id=int(id), file_name=file_name, preview=preview, title=title))

    return render_template('blog/swe.html', entries_list=sorted(entries_list, key=lambda entry: entry['id']))


@app.route('/blog/swe/<name>')
def swe_entry(name=None):
    if name is None:
        return page_not_found(NotImplementedError)

    try:
        f = app.open_resource('static/swe-entries/{0}.xml'.format(str(name)))
    except IOError:
        return page_not_found(IOError)

    post = ET.parse(f)
    parse_items = parse_swe_blog(post)
    headers = parse_items['headers']
    texts = parse_items['texts']
    banner_title = parse_items['title']

    entry_infos = [{
        'header': h,
        'text': t} for (h, t) in zip(headers, texts)]

    return render_template('blog/swe/template.html',
                           head_title='SWE: {0} | Blog'.format(banner_title.split(":")[0]),
                           entry_infos=entry_infos,
                           banner_title="{0}".format(banner_title))


@app.route('/send_message', methods=['POST'])
def send_message():
    if email_username is None or email_password is None:
        return "Something went wrong. Please try again later or send an email to thienqvo@gmail.com!"

    contact_name = request.form['contactName']
    contact_subject = request.form['contactSubject']
    contact_message = "Received from: {0}\n{1}".format(request.form['contactEmail'], request.form['contactMessage'])

    if contact_subject is None or contact_subject == "":
        contact_subject = "Message sent from thienmint.com"

    msg = Message(subject=contact_subject,
                  body=contact_message,
                  sender=(contact_name, email_username),
                  recipients=["thienqvo@gmail.com"])
    try:
        mail.send(msg)
    except Exception as e:
        logging.error(traceback.format_exc())
        return "Couldn't send email. Please try again later or send an email to thienqvo@gmail.com!"

    return "OK"


@app.route('/send_message', methods=['GET', 'PUT', 'DELETE'])
def redirect_contact():
    return redirect(url_for('home', _anchor='contact'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html")
# [END routing]


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run()
