from google.appengine.ext import ndb
import utils

def users_key(group='default'):
    return ndb.Key('users', group)

class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    pw_hash = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent = users_key())

    @classmethod
    def login(cls, email, pw):
        u = cls.by_email(email)
        if u:
            name = u.name
        if u and utils.valid_pw(name, pw, u.pw_hash):
            return u

    @classmethod
    def by_email(cls, email):
        u = User.query(User.email == email).get()
        return u

class Erf(ndb.Model):
    erf_number = ndb.IntegerProperty()
    price = ndb.IntegerProperty()
    turnkey_price = ndb.IntegerProperty()
    size = ndb.IntegerProperty()
    plan_type = ndb.KeyProperty(kind="PlanType")
    plan_name = ndb.StringProperty()
    status = ndb.StringProperty(default="available")
    created = ndb.DateTimeProperty(auto_now_add=True)

class ErfP2(ndb.Model):
    erf_number = ndb.IntegerProperty()
    price = ndb.IntegerProperty()
    turnkey_price = ndb.IntegerProperty()
    size = ndb.IntegerProperty()
    plan_types = ndb.KeyProperty(kind="PlanTypeP2", repeated=True)
    plan_ids = ndb.IntegerProperty(repeated=True)
    plan_names = ndb.StringProperty(repeated=True)
    status = ndb.StringProperty(default="available")
    created = ndb.DateTimeProperty(auto_now_add=True)

class ErfClick(ndb.Model):
    erf_number = ndb.IntegerProperty()
    clicks = ndb.IntegerProperty(default=0)

class Contact(ndb.Model):
    name = ndb.StringProperty()
    description = ndb.TextProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    mobile = ndb.StringProperty()
    landline = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class ClientContact(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    contacted = ndb.BooleanProperty()
    approved = ndb.BooleanProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Document(ndb.Model):
    name = ndb.StringProperty()
    file_key = ndb.KeyProperty(kind="File")
    download_link = ndb.StringProperty()
    description = ndb.TextProperty()
    approved = ndb.BooleanProperty(default=True)
    order = ndb.IntegerProperty()
    isClientChoice = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

class DocumentP2(ndb.Model):
    name = ndb.StringProperty()
    file_key = ndb.KeyProperty(kind="File")
    download_link = ndb.StringProperty()
    description = ndb.TextProperty()
    approved = ndb.BooleanProperty(default=True)
    order = ndb.IntegerProperty()
    isClientChoice = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

class PlanType(ndb.Model):
    name = ndb.StringProperty()
    image = ndb.StringProperty()
    media_obj = ndb.KeyProperty(kind="Media")
    file_key = ndb.KeyProperty(kind="File")
    download_link = ndb.StringProperty()
    description = ndb.TextProperty()
    approved = ndb.BooleanProperty(default=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

class PlanTypeP2(ndb.Model):
    name = ndb.StringProperty()
    price = ndb.IntegerProperty()
    image = ndb.StringProperty()
    media_obj = ndb.KeyProperty(kind="Media")
    file_key = ndb.KeyProperty(kind="File")
    download_link = ndb.StringProperty()
    description = ndb.TextProperty()
    approved = ndb.BooleanProperty(default=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

class Information(ndb.Model):
    name = ndb.StringProperty()
    image = ndb.StringProperty()
    media_obj = ndb.KeyProperty(kind="Media")
    file_key = ndb.KeyProperty(kind="File")
    download_link = ndb.StringProperty()
    description = ndb.TextProperty()
    approved = ndb.BooleanProperty(default=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

class InformationP2(ndb.Model):
    name = ndb.StringProperty()
    image = ndb.StringProperty()
    media_obj = ndb.KeyProperty(kind="Media")
    file_key = ndb.KeyProperty(kind="File")
    download_link = ndb.StringProperty()
    description = ndb.TextProperty()
    approved = ndb.BooleanProperty(default=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

class Progress(ndb.Model):
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    image_url = ndb.StringProperty()
    file_key = ndb.KeyProperty(kind="Media")
    created = ndb.DateTimeProperty(auto_now_add=True)

class ProgressP2(ndb.Model):
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    image_url = ndb.StringProperty()
    file_key = ndb.KeyProperty(kind="Media")
    created = ndb.DateTimeProperty(auto_now_add=True)

# ============================
# CMS --> should be along these lines
# ============================

# class Content(ndb.Model):
#     page = ndb.KeyProperty(kind="Page")
#     nameID = ndb.StringProperty()
#     title = ndb.StringProperty()
#     subtitle = ndb.StringProperty()
#     text = ndb.TextProperty()
#     image = ndb.StringProperty()
#     media_key = ndb.KeyProperty(kind="Media")
#     created = ndb.DateTimeProperty(auto_now_add=True)

# class Page(ndb.Model):
#     name = ndb.StringProperty()
#     number_of_content_sections = ndb.IntegerProperty()
#     created = ndb.DateTimeProperty(auto_now_add=True)


# ============================
# CMS --> super custom for Nicholas
# ============================

class Content(ndb.Model):
    label = ndb.StringProperty()

    title = ndb.StringProperty()
    subtitle = ndb.StringProperty()
    text = ndb.TextProperty()
    image = ndb.StringProperty()
    media_key = ndb.KeyProperty(kind="Media")
    media_id = ndb.StringProperty()
    cta_text = ndb.StringProperty()
    cta_link = ndb.StringProperty()

    num_items = ndb.IntegerProperty(default=0)
    titles = ndb.StringProperty(repeated=True)
    subtitles = ndb.StringProperty(repeated=True)
    texts = ndb.TextProperty(repeated=True)
    images = ndb.StringProperty(repeated=True)
    media_keys = ndb.KeyProperty(kind="Media", repeated=True)
    media_ids = ndb.StringProperty(repeated=True)# so can store a blank string
    cta_texts = ndb.StringProperty(repeated=True)
    cta_links = ndb.StringProperty(repeated=True)

    phone = ndb.StringProperty()
    email = ndb.StringProperty()
    contact_name = ndb.StringProperty()
    address_1 = ndb.StringProperty()
    address_2 = ndb.StringProperty()
    address_3 = ndb.StringProperty()

    phones = ndb.StringProperty(repeated=True)
    emails = ndb.StringProperty(repeated=True)
    contact_names = ndb.StringProperty(repeated=True)
    address_1s = ndb.StringProperty(repeated=True)
    address_2s = ndb.StringProperty(repeated=True)
    address_3s = ndb.StringProperty(repeated=True)

    created = ndb.DateTimeProperty(auto_now_add=True)

class ImageGallery(ndb.Model):
    image = ndb.StringProperty()
    media_key = ndb.KeyProperty(kind="Media")
    media_id = ndb.StringProperty()
    tag = ndb.StringProperty()
    label = ndb.StringProperty()
    caption = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Social(ndb.Model):
    facebook_page = ndb.StringProperty()
    twitter_page = ndb.StringProperty()
    instagram_page = ndb.StringProperty()
    linkedin_page = ndb.StringProperty()
    pinterest_page = ndb.StringProperty()

    created = ndb.DateTimeProperty(auto_now_add=True)



class Blog(ndb.Model):
    approved = ndb.BooleanProperty(default=False)
    title = ndb.StringProperty()
    cover_img = ndb.StringProperty(default = None)
    gcs_filename = ndb.StringProperty(default = None)
    media_obj = ndb.KeyProperty(kind="Media")
    post = ndb.TextProperty()
    short_text = ndb.TextProperty()
    tags = ndb.StringProperty(repeated=True)
    featured = ndb.BooleanProperty(default=False)
    url = ndb.StringProperty(default=None)
    blog_type = ndb.StringProperty(default="work")
    created = ndb.DateTimeProperty(auto_now_add=True)

class Media(ndb.Model):
    gcs_filename = ndb.StringProperty(default = None)
    serving_url = ndb.StringProperty(default = None)
    content_type = ndb.StringProperty(default = None)
    created = ndb.DateTimeProperty(auto_now_add=True)

class File(ndb.Model):
    gcs_filename = ndb.StringProperty(default = None)
    filename = ndb.StringProperty(default = None)
    content_type = ndb.StringProperty(default = None)
    download_link = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
