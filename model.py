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
    size = ndb.IntegerProperty()
    plan_type = ndb.StringProperty()
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
    page = ndb.StringProperty()
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

class FrontPage(ndb.Model):
    headline = ndb.StringProperty()
    subheadline = ndb.StringProperty()
    content_sections = ndb.KeyProperty(kind="Content", repeated=True)



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
    created = ndb.DateTimeProperty(auto_now_add=True)
    
class Contact(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    description = ndb.TextProperty()
    web = ndb.BooleanProperty(default=False)
    mobile = ndb.BooleanProperty(default=False)
    game = ndb.BooleanProperty(default=False)
    spam = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

class Subscriber(ndb.Model):
    email = ndb.StringProperty()
    name = ndb.StringProperty()
    active = ndb.BooleanProperty(default=True)
    created = ndb.DateTimeProperty(auto_now_add=True)



# ------- admin stuff

class PaymentDetails(ndb.Model):
    account_name = ndb.StringProperty()
    account_number = ndb.StringProperty()
    accoutn_type = ndb.StringProperty()
    bank = ndb.StringProperty()
    branch_code = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class QuoteNumber(ndb.Model):
    number = ndb.IntegerProperty(default=0)

class Client(ndb.Model):
    client_email = ndb.StringProperty()
    client_tel = ndb.StringProperty()
    client_cell = ndb.StringProperty()
    client_street = ndb.StringProperty()
    client_city = ndb.StringProperty()
    client_country = ndb.StringProperty()
    client_postal = ndb.StringProperty()
    client_id = ndb.StringProperty()

class Quote(ndb.Model):
    number = ndb.IntegerProperty()
    reference = ndb.StringProperty()
    quote_items = ndb.JsonProperty()
    issue_date = ndb.DateTimeProperty()
    valid = ndb.DateTimeProperty()# auto claculate to be + 10 days
    due_date = ndb.DateTimeProperty()
    accepted = ndb.BooleanProperty()
    notes = ndb.TextProperty()
    discount = ndb.IntegerProperty()# discount in percent
    tax = ndb.IntegerProperty()# tax in percent
    total = ndb.FloatProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


# this is for staging projects
# email_address=sbtu01%40payfast.co.za&merchant_id=10002344&signature=e376f5dcecf9897b60fda101ef0bba10
class PayfastPayment(ndb.Model):
    m_payment_id = ndb.StringProperty()
    pf_payment_id = ndb.StringProperty()
    payment_status = ndb.StringProperty()
    item_name = ndb.StringProperty()
    item_description = ndb.StringProperty()
    amount_gross = ndb.StringProperty()
    amount_fee = ndb.StringProperty()
    amount_net = ndb.StringProperty()
    custom_int1 = ndb.StringProperty()# can be up to 5 custom_int1-5
    custom_str1 = ndb.StringProperty()# can be up to 5 custom_str1-5
    name_first = ndb.StringProperty()
    name_last = ndb.StringProperty()
    email_address = ndb.StringProperty()
    merchant_id = ndb.StringProperty()
    signature = ndb.StringProperty()

    registered_email = ndb.KeyProperty(kind='RegisteredEmail')
    registered_email_address = ndb.StringProperty()# this will be the email address that the user registers in app

    created = ndb.DateTimeProperty(auto_now_add=True)

class TokenCount(ndb.Model):
    count = ndb.IntegerProperty(default=0)
    created = ndb.DateTimeProperty(auto_now_add=True)

class UsedToken(ndb.Model):
    token = ndb.StringProperty()
    payment = ndb.KeyProperty(kind="PayfastPayment")
    created = ndb.DateTimeProperty(auto_now_add=True)

class RegisteredEmail(ndb.Model):
    email = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class MenuItem(ndb.Model):
    name = ndb.StringProperty()
    description = ndb.TextProperty()
    price = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True) 

class Menu(ndb.Model):
    items = ndb.KeyProperty(kind="MenuItem", repeated=True)

class Totem(ndb.Model):
    name = ndb.StringProperty()
    menu = ndb.KeyProperty(kind="Menu")
    created = ndb.DateTimeProperty(auto_now_add=True)

    
    

    