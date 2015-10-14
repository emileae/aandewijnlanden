#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import logging
import os
from string import letters
import json
from datetime import datetime, timedelta
import datetime
import time
import urllib
from urlparse import urlparse
import re

from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import mail
from google.appengine.datastore.datastore_query import Cursor

import model
import utils

import cloudstorage as gcs

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

front_page_content = ["banner", 'FPgallery', 'FPabout', 'FPhowWeWork', 'FPfooterText', 'FPgalleryIMG', 'contact', 'FPaboutIMG', 'FPhowWeWorkIMG']
gallery_content = ["galleryBanner", 'gallerySections']
about_us_labels = ['AboutUsBanner', 'AboutUsStudio', 'AboutUsStudioIMG', 'AboutUsNicholas', 'AboutUsAnastasia', 'AboutUsTeam', 'AboutUsContact']
what_we_do_labels = ['WWDBanner', 'WWDRestoration', 'WWDResidential', 'WWDLogistics', 'WWDSpirituality', 'WWDArt', 'WWDQuote']

def blog_date(value):
    return value.strftime("%d/%m/%y")
jinja_env.filters['blog_date'] = blog_date

def check_none(value):
    if value:
        return value
    else:
        return ""
jinja_env.filters['check_none'] = check_none

def get_val_from_list(value, dict_key, attribute, idx):
    try:
        list_items = getattr(value[dict_key], attribute)
        return list_items[idx]
    except:
        return ""
jinja_env.filters['get_val_from_list'] = get_val_from_list

def get_val(value, dict_key, attribute):
    try:
        return getattr(value[dict_key], attribute)
    except:
        return ""
jinja_env.filters['get_val'] = get_val

class MainHandler(webapp2.RequestHandler):

#TEMPLATE FUNCTIONS    
    def write(self, *a, **kw):
        self.response.headers['Host'] = 'localhost'
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        params['user'] = self.user
        #params['buyer'] = self.buyer
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #JSON rendering
    def render_json(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Host'] = 'localhost'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.out.write(json.dumps(obj))
   
    #COOKIE FUNCTIONS
    # sets a cookie in the header with name, val , Set-Cookie and the Path---not blog    
    def set_secure_cookie(self, name, val):
        cookie_val = utils.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))# consider imcluding an expire time in cookie(now it closes with browser), see docs
    # reads the cookie from the request and then checks to see if its true/secure(fits our hmac)    
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val:
            cookie_val = urllib.unquote(cookie_val)
        return cookie_val and utils.check_secure_val(cookie_val)
    
    def login(self, user):
        self.set_secure_cookie('nic_estappspotcom', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'nic_estappspotcom=; Path=/')
    
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('nic_estappspotcom')

        self.user = uid and model.User.by_id(int(uid))
        
        
        
# ==============================
# Client Facing
# ==============================
        
class Home(MainHandler):
    def get(self):
        year = datetime.datetime.now().year

        # front_page_labels = front_page_content

        # content = {}

        # for label in front_page_labels:
        #     content[label] = model.Content.query(model.Content.label == label).get()

        # social = model.Social.query().get()

        self.render("index.html", year=year)


class PlansPrices(MainHandler):
    def get(self):

        self.render("plans-prices.html")









        
class Gallery(MainHandler):
    def get(self):

        gallery_filter = self.request.get("type")

        gallery_labels = gallery_content

        front_page_labels = ['contact', 'banner']
        content = {}
        for label in front_page_labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        social = model.Social.query().get()

        for label in gallery_labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        if gallery_filter:
            gallery_images = model.ImageGallery.query(model.ImageGallery.label == gallery_filter).order(-model.ImageGallery.created).fetch()
        else:
            gallery_images = model.ImageGallery.query().order(-model.ImageGallery.created).fetch()

        self.render("gallery.html", content=content, social=social, gallery_images=gallery_images)

class About(MainHandler):
    def get(self):
        labels = about_us_labels

        front_page_labels = ['contact', 'banner']
        content = {}
        for label in front_page_labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        social = model.Social.query().get()

        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        self.render("about.html", content=content, social=social)

class WhatWeDo(MainHandler):
    def get(self):
        labels = what_we_do_labels

        front_page_labels = ['contact', 'banner']
        content = {}
        for label in front_page_labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        social = model.Social.query().get()

        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        self.render("what-we-do.html", content=content, social=social)

class Contact(MainHandler):
    def get(self):
        front_page_labels = ['contact', 'banner']
        content = {}
        for label in front_page_labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        social = model.Social.query().get()

        self.render("contact.html", content=content, social=social)


# ==============================
# Admin
# ==============================

class Admin(MainHandler):
    def get(self):
        counter = None
        self.render('cms.html', counter=counter)

class AdminErf(MainHandler):
    def get(self):

        erfs = model.Erf.query().order(model.Erf.erf_number).fetch()

        if not erfs:
            for i in range(1,103):
                e = model.Erf(erf_number=i)
                e.put()

            erfs = model.Erf.query().order(model.Erf.erf_number).fetch()

        self.render('admin-erf.html', erfs=erfs)

class AdminSaveErf(MainHandler):
    def post(self, erf_id):
        erf = model.Erf.get_by_id(int(erf_id))

        plan_type = self.request.get("plan_type")
        size = self.request.get("size")
        price = self.request.get("price")

        if size:
            try:
                erf.size = int(size)
            except:
                logging.error("size - probably int error for %s" % erf_id)
        if price:
            try:
                erf.price = int(price)
            except:
                logging.error("price - probably int error for %s" % erf_id)
        if plan_type:
            erf.plan_type = plan_type

        erf.put()

        self.render_json({
            "message": "success",
            "erf_id": erf_id
            })

class AdminSaveContent(MainHandler):
    def post(self):

        request = self.request

        list_items = self.request.get("list_items")

        if list_items:
            logging.error(". . . . . . . . . . ---- multiple")
            content_id = utils.save_list_content( request )
        else:
            logging.error(". . . . . . . . . . ---- NOT multiple")
            content_id = utils.save_content( request )

        self.render_json({
            "message": "success",
            "content_id": content_id
            })

class AdminSaveSingleImage(MainHandler):
    def post(self, image_id):
        image = self.request.get("image")
        label = self.request.get("label")
        caption  =self.request.get("caption")

        logging.error("LABEL................... %s" % label)

        if image_id == "new":
            media_obj = utils.save_to_gcs(image)
            gallery_image = model.ImageGallery(label=label, caption=caption, image=media_obj.serving_url, media_id = str(media_obj.key.id()), media_key = media_obj.key)
            gallery_image.put()

        else:
            gallery_image = model.ImageGallery.get_by_id(int(image_id))

            if image:
                media_obj = utils.save_to_gcs(image)
                if gallery_image.media_id:
                    old_media_obj = model.Media.get_by_id(int(gallery_image.media_id))
                    utils.delete_from_gcs(old_media_obj.gcs_filename)
                    old_media_obj.key.delete()

                gallery_image.image = media_obj.serving_url
                gallery_image.media_key = media_obj.key
                gallery_image.media_id = str(media_obj.key.id())

            gallery_image.caption = caption
            gallery_image.label = label
            gallery_image.put()

        self.render_json({
            "message": 'success',
            "gallery_image_id": gallery_image.key.id(),
            "gallery_image_url": gallery_image.image
            })

class DeleteSingleImage(MainHandler):
    def post(self, image_id):
        gallery_image = model.ImageGallery.get_by_id(int(image_id))

        media_obj = model.Media.get_by_id(int(gallery_image.media_id))

        utils.delete_from_gcs(media_obj.gcs_filename)
        media_obj.key.delete()

        gallery_image.key.delete()

        self.render_json({
            "message": 'success',
            "long_message": "deleted",
            "gallery_image_id": image_id
            })



class AdminSaveSocial(MainHandler):
    def post(self):
        facebook_page = self.request.get("facebook_page")
        twitter_page = self.request.get("twitter_page")
        instagram_page = self.request.get("instagram_page")
        linkedin_page = self.request.get("linkedin_page")
        pinterest_page = self.request.get("pinterest_page")

        social = model.Social.query().get()

        social_id = ''

        if not social:
            social = model.Social(
                facebook_page = facebook_page,
                twitter_page = twitter_page,
                instagram_page = instagram_page,
                linkedin_page = linkedin_page,
                pinterest_page = pinterest_page
                )
            social.put()

            social_id = social.key.id()

        else:
            social.facebook_page = facebook_page
            social.twitter_page = twitter_page
            social.instagram_page = instagram_page
            social.linkedin_page = linkedin_page
            social.pinterest_page = pinterest_page

            social.put()

            social_id = social.key.id()

        self.render_json({
            "message": "success",
            "social_id": social_id
            })


class AdminFrontPage(MainHandler):
    def get(self):
        front_page_labels = front_page_content
        content = {}
        for label in front_page_labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        social = model.Social.query().get()

        self.render("admin-front-page.html", content=content, social=social)

class AdminGallery(MainHandler):
    def get(self):
        gallery_labels = gallery_content

        content = {}
        for label in gallery_labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        gallery_images = model.ImageGallery.query().order(-model.ImageGallery.created).fetch()

        self.render("admin-gallery.html", content=content, gallery_images=gallery_images)

class AdminAbout(MainHandler):
    def get(self):
        labels = about_us_labels

        content = {}
        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        self.render("admin-about-us.html", content=content)

class AdminWhatWeDo(MainHandler):
    def get(self):
        labels = what_we_do_labels

        content = {}
        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        self.render("admin-what-we-do.html", content=content)

class TestAjax(MainHandler):
    def post(self):
        pass




app = webapp2.WSGIApplication([
    ('/', Home),
    ('/plans_prices', PlansPrices),

    # admin
    ('/admin', Admin),
    ('/admin/erf', AdminErf),
    ('/admin/erf/(\w+)', AdminSaveErf),



    # Old Nicholas stuff
    ('/gallery', Gallery),
    ('/about', About),
    ('/what_we_do', WhatWeDo),
    ('/contact', Contact),

    ('/admin/front_page', AdminFrontPage),
    ('/admin/gallery', AdminGallery),
    ('/admin/about', AdminAbout),
    ('/admin/what_we_do', AdminWhatWeDo),

    ('/admin/save_content', AdminSaveContent),
    # ('/admin/save_multiple_images', AdminSaveMultipleImages),
    ('/admin/save_single_image/(\w+)', AdminSaveSingleImage),
    ('/admin/delete_single_image/(\w+)', DeleteSingleImage),
    ('/admin/save_social', AdminSaveSocial),

    # testing & misc
    # ('/test_ajax_upload', TestAjax),

], debug=False)



# curs = Cursor(urlsafe=self.request.get('cursor'))
# responses, next_curs, more = model.Response.query( model.Response.project == project.key ).order(-model.Response.created).fetch_page(20, start_cursor=curs)
# if more and next_curs:
#     next_curs = next_curs.urlsafe()
# else:
#     next_curs = False
