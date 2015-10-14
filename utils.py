
import re
import hashlib
import hmac
import random
import string
from string import letters
import logging
import json
import time

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import mail
from google.appengine.api import app_identity

import cloudstorage as gcs

#for mandrill api
from google.appengine.api import urlfetch

import model

app_id = app_identity.get_application_id()

secret = 'Est!eMi001'
sender_email = "emile.esterhuizen@gmail.com"

# Mandrill
mandrill_key = "9y6hFh8u9Ii6IZj5Ib2Mbg"# "qODMJ7be5Cy68y7M7z6q4w"

# Twitter
twitter_consumer_key = "aUYWh62q9x9k1fL1i65fsgwJm"
twitter_consumer_secret = "BKYCrbAs61xYTXYuxc3OabAiLf7noMExJFQqYEC2Sy91Gl4jfi"


#PW HASHING
def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)
    
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))
    
# returns a cookie with a value value|hashedvalue
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())
# returns the origional value and validates if given hashed cookie matches our hash of the value    
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
        
def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


#REGEX for register validtion
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return email and EMAIL_RE.match(email)
    
def request_blob_url(self, callback_url, max_bytes):
    upload_url = blobstore.create_upload_url(callback_url, max_bytes)
    return upload_url
    
def send_gmail(email, subject, body):
    try:
        logging.error("sending subscription mail")
        message = mail.EmailMessage(sender="Emile <%s>" % sender_email,
                                subject=subject)
        message.to = email
        message.html = body
        message.send()
    except:
        logging.error("couldnt send gmail... probably invalid email")




def generate_random_token(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))



# =============================
# Google Cloud Storage
# =============================
# http://storage.googleapis.com/<bucket name>/<object name>
# grant access to AllUsers as a group - Bucket
# grant acc to AllUsers as a group for default object permissions
# comparison between serve adn direct from GCS: http://audio-test.appspot.com

def save_gcs_to_media(gcs_filename, serving_url):
    media = model.Media(gcs_filename=gcs_filename, serving_url=serving_url)
    media.put()
    return media

def save_gcs_to_audio(gcs_filename):
    audio = model.Audio(gcs_filename=gcs_filename)
    audio.put()
    return audio


def delete_media(gcs_filename):
    images.delete_serving_url(blobstore.create_gs_key(gcs_filename))
    gcs.delete(gcs_filename[3:])
    return True

def delete_from_gcs(gcs_filename):
    if gcs_filename:
        images.delete_serving_url(blobstore.create_gs_key(gcs_filename))
        gcs.delete(gcs_filename[3:])

def save_to_gcs(file_obj):
    serving_url = ''#just assign it adn reassign later

    time_stamp = int(time.time())
    app_id = app_identity.get_application_id()

    fname = '/%s.appspot.com/post_%s.jpg' % (app_id, time_stamp)
    # logging.error(fname)

    # Content Types
    # audio/mpeg
    # image/jpeg

    gcs_file = gcs.open(fname, 'w', content_type="image/jpeg")
    gcs_file.write(file_obj)
    gcs_file.close()

    height = images.Image(image_data=file_obj).height
    width = images.Image(image_data=file_obj).width

    gcs_filename = "/gs%s" % fname
    serving_url = images.get_serving_url(blobstore.create_gs_key(gcs_filename))
    media_obj = save_gcs_to_media(gcs_filename, serving_url)

    return media_obj

def upload_image(image):
    media_obj = save_to_gcs(image)

    json_obj = {
        "message":"success",
        "media_id": media_obj.key.id(),
        "post_id": post.key.id()
        }

    return json_obj



# ==================================
#  CMS utils
# ==================================

def save_content(request):
    label = request.get("label")
    content_id = request.get("content_id")

    title = request.get("title")
    subtitle = request.get("subtitle")
    text = request.get("text")
    image = request.get("image")

    if image:
        logging.error("HELLO CARROT!...........")

    cta_text = request.get("cta_text")
    cta_link = request.get("cta_link")

    phone = request.get("phone")
    email = request.get("email")
    contact_name = request.get("contact_name")
    address_1 = request.get("address_1")
    address_2 = request.get("address_2")
    address_3 = request.get("address_3")

    if content_id:
        content = model.Content.get_by_id(int(content_id))
        logging.error(content)
        content.title = title
        content.subtitle = subtitle
        content.text = text
        content.label = label

        content.cta_text = cta_text
        content.cta_link = cta_link

        content.phone = phone
        content.email = email
        content.contact_name = contact_name
        content.address_1 = address_1
        content.address_2 = address_2
        content.address_3 = address_3

        if image:
            # check if there is already an image... to delete
            if content.media_key:
                delete_from_gcs(content.media_key.get().gcs_filename)
            # replace image
            image_media_obj = save_to_gcs(image)
            image_media_key = image_media_obj.key
            image = image_media_obj.serving_url
            content.image = image
            content.media_key = image_media_key

        content.put()
    else:
        if image:
            image_media_obj = save_to_gcs(image)
            image_media_key = image_media_obj.key
            image_media_id = str( image_media_obj.key.id() )
            image = image_media_obj.serving_url
        else:
            image = None
            image_media_key = None
            image_media_id = ''

        content = model.Content(
            title=title, 
            subtitle=subtitle, 
            text=text, 
            label=label, 
            image=image, 
            media_key=image_media_key,
            media_id=image_media_id,
            phone=phone,
            email=email,
            contact_name=contact_name,
            address_1=address_1,
            address_2=address_2,
            address_3=address_3,
            cta_text=cta_text,
            cta_link=cta_link
            )

        content.put()
        content_id = content.key.id()

    return content_id

def save_list_content(request):
    label = request.get("label")
    content_id = request.get("content_id")

    titles = request.get_all("title")
    subtitles = request.get_all("subtitle")
    texts = request.get_all("text")
    images = request.get_all("image")
    phones = request.get_all("phone")
    emails = request.get_all("email")
    contact_names = request.get_all("contact_name")
    address_1s = request.get_all("address_1")
    address_2s = request.get_all("address_2")
    address_3s = request.get_all("address_3")

    cta_texts = request.get_all("cta_text")
    cta_links = request.get_all("cta_link")

    if content_id:
        content = model.Content.get_by_id(int(content_id))
        content.titles = titles
        content.subtitles = subtitles
        content.texts = texts
        content.label = label

        content.cta_texts = cta_texts
        content.cta_links = cta_links

        content.phones = phones
        content.emails = emails
        content.contact_names = contact_names
        content.address_1s = address_1s
        content.address_2s = address_2s
        content.address_3s = address_3s

        if len(content.images) == len(images):
            for idx, image in enumerate(images):
                if image:
                    time.sleep(1)
                    # new iamge
                    new_media_obj = save_to_gcs(image)

                    #old image
                    old_media_id = content.media_ids[idx]
                    if len(old_media_id) > 0:
                        old_media_obj = model.Media.get_by_id(int(old_media_id))
                        if old_media_obj:
                            delete_from_gcs(old_media_obj.gcs_filename)
                            old_media_obj.key.delete()

                    content.images[idx] = new_media_obj.serving_url
                    content.media_ids[idx] = str( new_media_obj.key.id() )

        content.put()

    else:
        image_list = []
        media_id_list = []

        for image in images:
            if image:
                time.sleep(1) # sleep for 1 second to keep file names different, since save_to_gcs function use time to create unique names
                media_obj = None

                media_obj = save_to_gcs(image)
                image_list.append(media_obj.serving_url)
                media_id_list.append( str(media_obj.key.id()) )

        content = model.Content(
            label=label,
            titles=titles, 
            subtitles=subtitles,
            texts=texts,
            phones=phones,
            emails=emails,
            contact_names=contact_names,
            address_1s=address_1s,
            address_2s=address_2s,
            address_3s=address_3s,
            images=image_list, 
            media_ids=media_id_list,
            cta_links=cta_links,
            cta_texts=cta_texts
            )
        content.put()

    return content.key.id()



# ==================================
#  Mandrill
# ==================================


def send_mandrill_mail(subject, html, text, email_list):
    
    url = "https://mandrillapp.com/api/1.0/messages/send.json"

    form_json = {
            "key": mandrill_key,
            "message": {
                "html": html,
                "text": text,
                "subject": subject,
                "from_email": sender_email,
                "from_name": "Emile",
                "to": email_list,
                "headers": {
                    "Reply-To": sender_email
                },
                "important": False,
                "track_opens": True,
                "track_clicks": True,
                "auto_text": None,
                "auto_html": None,
                "inline_css": None,
                "url_strip_qs": None,
                "preserve_recipients": False,
                "view_content_link": None,
                "bcc_address": None,
                "tracking_domain": None,
                "signing_domain": "http://hollowfish.com",
            },
            "async": False,
            "ip_pool": "Main Pool",
            "send_at": None
        }
    

    result = urlfetch.fetch(url=url, payload=json.dumps(form_json), method=urlfetch.POST)

    logging.error("MANDRILL RESULT")

    logging.error(dir(result))
    logging.error(result.status_code)
    logging.error(json.loads(result.content))
    
    
    
    
    
    
    
    
    
    