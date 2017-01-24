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


def blog_date(value):
    return value.strftime("%d/%m/%y")
jinja_env.filters['blog_date'] = blog_date

def check_none(value):
    if value:
        return value
    else:
        return ""
jinja_env.filters['check_none'] = check_none

def jinjaAdd(value1, value2):
    return value1 + value2
jinja_env.filters['jinjaAdd'] = jinjaAdd

def format_phone(value):
    value = re.sub('[^0-9]','', value)
    return value
jinja_env.filters['format_phone'] = format_phone

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
        contacts = model.Contact.query().order(-model.Contact.created).fetch()
        year = datetime.datetime.now().year

        labels = ["home", "homeColumn1", "homeColumn2", "homeColumn3", "homeColumn4"]
        content = {}
        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        gallery_images = model.ImageGallery.query(model.ImageGallery.label == "home_banner").fetch()

        self.render("index2.html", year=year, gallery_images=gallery_images, content=content, contacts=contacts)


class PlansPrices(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()
        plan_types = model.PlanType.query().order(model.PlanType.name).fetch()
        erfs = model.Erf.query().order(model.Erf.erf_number).fetch()

        self.render("plans-prices.html", erfs=erfs, plan_types=plan_types, contacts=contacts)

class PlansPricesP2(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()
        plan_types = model.PlanTypeP2.query().order(model.PlanTypeP2.name).fetch()
        erfs = model.ErfP2.query().order(model.ErfP2.erf_number).fetch()

        self.render("plans-prices.html", erfs=erfs, plan_types=plan_types, contacts=contacts, phase2=True)

# TODO
# finish this class it is supposed to display plan options for a particular erf
class ErfPlansP2(MainHandler):
    def get(self, erfID):
        erf = model.ErfP2.get_by_id(int(erfID))
        logging.error("DISPLAY THE PLANS FOR AN ERF....");

        plans = []
        for plan in erf.plan_types:
            plans.append(plan.get())

        self.render("erf-plans.html", erf=erf, plans=plans, phase2=True)

class Location(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()

        labels = ["location_intro", "locality", "adwEstate", "adwPhase1"]
        content = {}
        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        gallery_images = model.ImageGallery.query(model.ImageGallery.label == "location_gallery").fetch()

        self.render("location.html", contacts=contacts, content=content, gallery_images=gallery_images)

class Progress(MainHandler):
    def get(self):
        #posts = model.Progress.query().order(-model.Progress.created).fetch()

        curs = Cursor(urlsafe=self.request.get('cursor'))
        posts, next_curs, more = model.Progress.query().order(-model.Progress.created).fetch_page(20, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        self.render("progress.html", posts=posts, next_curs=next_curs)

class ProgressP2(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        posts, next_curs, more = model.ProgressP2.query().order(-model.ProgressP2.created).fetch_page(20, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        self.render("progress.html", posts=posts, next_curs=next_curs, phase2=True)

class Information(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()
        informations = model.Information.query().order(model.Information.name).fetch()
        self.render("information.html", informations=informations, contacts=contacts)

class ClientChoices(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()
        documents = model.Document.query(model.Document.isClientChoice == True).order(model.Document.order).fetch()
        self.render("client_choices.html", documents=documents, contacts=contacts)

class Documentation(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()
        documents = model.Document.query().order(model.Document.order).fetch()
        self.render("documentation.html", documents=documents, contacts=contacts)

class ContactForm(MainHandler):
    def post(self):
        name = self.request.get("name")
        email = self.request.get("email")
        phone = self.request.get("phone")
        no_ajax = self.request.get("no_ajax")
        existing_phone = None
        existing_email = None
        if email:
            existing_email = model.ClientContact.query(model.ClientContact.email == email).get()
            # if not existing_email:
            #     cc = model.ClientContact(email=email, phone=phone, name=name)
            #     cc.put()

        if phone:
            existing_phone = model.ClientContact.query(model.ClientContact.phone == phone).get()
            # if not existing_phone:
            #     cc = model.ClientContact(email=email, phone=phone, name=name)
            #     cc.put()

        if not existing_phone and not existing_email:
            cc = model.ClientContact(email=email, phone=phone, name=name)
            cc.put()

        if no_ajax:
            self.redirect("/")
        else:
            self.render_json({
                "message": "success"
                })

class Contact(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()
        self.render("contact.html", contacts=contacts)


class ServeFile(MainHandler):
    def get(self):
        file_id = self.request.get("file_id")
        file_obj = model.File.get_by_id(int(file_id))
        gcs_filename = file_obj.gcs_filename
        content_type = str( file_obj.content_type )
        filename = str( file_obj.filename )
        gcs_filename = gcs_filename[3:]
        # self.response.headers['Content-Type'] = str(content_type)
        # self.response.write(gcs.open(gcs_filename, 'r'))

        headers = self.response.headers
        headers['Content-Type'] = content_type or 'application/octet-stream'
        headers['Content-Disposition'] = 'attachment; filename="%s"' % filename

        # Add the file contents to the response.
        self.response.out.write(gcs.open(gcs_filename, 'r'))



class PlanForErf(MainHandler):
    def get(self, erf_number):
        erf = model.Erf.query(model.Erf.erf_number == int(erf_number) ).get()

        utils.track_erf_click(erf_number)

        if erf.plan_type:
            plan = erf.plan_type.get()
            self.render_json({
                "message": "success",
                "id": plan.key.id(),
                "name": plan.name,
                "description": plan.description,
                "image": plan.image,
                "download_link": plan.download_link,
                })
        else:
            plan = None
            self.render_json({
                "message": "success",
                "id": False,
                "name": False,
                "description": False,
                "image": False,
                "download_link": False,
                })


class TrackErfClick(MainHandler):
    def get(self, erf_number):
        utils.track_erf_click(erf_number)


class Contact(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()

        self.render("contact.html", contacts=contacts)




# ==============================
# Admin
# ==============================

class Admin(MainHandler):
    def get(self):
        counter = None
        self.render('cms.html', counter=counter)

class AdminHome(MainHandler):
    def get(self):
        labels = ["home", "homeColumn1", "homeColumn2", "homeColumn3", "homeColumn4"]
        content = {}
        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        gallery_images = model.ImageGallery.query(model.ImageGallery.label == "home_banner").fetch()

        self.render("admin-home-page.html", content=content, gallery_images=gallery_images)

class AdminLocation(MainHandler):
    def get(self):
        labels = ["location_intro", "locality", "adwEstate", "adwPhase1"]
        content = {}
        for label in labels:
            content[label] = model.Content.query(model.Content.label == label).get()

        gallery_images = model.ImageGallery.query(model.ImageGallery.label == "location_gallery").fetch()
        self.render("admin-location.html", content=content, gallery_images=gallery_images)

class AdminProgress(MainHandler):
    def get(self):
        post_id = self.request.get("post_id")
        posts = model.Progress.query().fetch()
        if post_id:
            post = model.Progress.get_by_id(int(post_id))
        else:
            post = None
        self.render("admin-progress.html", post=post, posts=posts)

    def post(self):
        #file_req = self.request.POST["file"]
        image = self.request.get("image")
        title = self.request.get("title")
        body = self.request.get("body")
        post_id = self.request.get("post_id")

        if post_id:
            post = model.Progress.get_by_id(int(post_id))

            post.title = title
            post.body = body
            try:
                #if file_req.value and post.file_key:
                if image and post.file_key:
                    utils.delete_file_from_gcs(post.file_key.get().gcs_filename)
                    post.file_key.delete()

                    #file_obj = utils.save_to_gcs(file_req)
                    file_obj = utils.save_to_gcs(image)
                    post.file_key = file_obj.key
                    post.image_url = file_obj.serving_url
                else:
                    #file_obj = utils.save_to_gcs(file_req)
                    file_obj = utils.save_to_gcs(image)
                    post.file_key = file_obj.key
                    post.image_url = file_obj.serving_url
            except:
                logging.error("something happened error-wise with the file upload for an existing file")


            post.put()

        else:
            #try:
            #if file_req.value:
            if image:
                #file_obj = utils.save_to_gcs(file_req)
                file_obj = utils.save_to_gcs(image)
                file_key = file_obj.key
                image_url = file_obj.serving_url
            else:
                file_key = None
                image_url = None
            # except:
            #     logging.error("something happened error-wise with the file upload for a new file")
            #     file_key = None
            #     image_url = None

            post = model.Progress(title=title, body=body, file_key=file_key, image_url=image_url)
            post.put()

        self.redirect("/admin/progress")

class AdminProgressP2(MainHandler):
    def get(self):
        post_id = self.request.get("post_id")
        posts = model.ProgressP2.query().fetch()
        if post_id:
            post = model.ProgressP2.get_by_id(int(post_id))
        else:
            post = None
        self.render("admin-progress.html", post=post, posts=posts, phase2=True)

    def post(self):
        #file_req = self.request.POST["file"]
        image = self.request.get("image")
        title = self.request.get("title")
        body = self.request.get("body")
        post_id = self.request.get("post_id")

        if post_id:
            post = model.ProgressP2.get_by_id(int(post_id))

            post.title = title
            post.body = body
            try:
                #if file_req.value and post.file_key:
                if image and post.file_key:
                    utils.delete_file_from_gcs(post.file_key.get().gcs_filename)
                    post.file_key.delete()

                    #file_obj = utils.save_to_gcs(file_req)
                    file_obj = utils.save_to_gcs(image)
                    post.file_key = file_obj.key
                    post.image_url = file_obj.serving_url
                else:
                    #file_obj = utils.save_to_gcs(file_req)
                    file_obj = utils.save_to_gcs(image)
                    post.file_key = file_obj.key
                    post.image_url = file_obj.serving_url
            except:
                logging.error("something happened error-wise with the file upload for an existing file")


            post.put()

        else:
            #try:
            #if file_req.value:
            if image:
                #file_obj = utils.save_to_gcs(file_req)
                file_obj = utils.save_to_gcs(image)
                file_key = file_obj.key
                image_url = file_obj.serving_url
            else:
                file_key = None
                image_url = None
            # except:
            #     logging.error("something happened error-wise with the file upload for a new file")
            #     file_key = None
            #     image_url = None

            post = model.ProgressP2(title=title, body=body, file_key=file_key, image_url=image_url)
            post.put()

        self.redirect("/admin/p2/progress")

class AdminInformation(MainHandler):
    pass

class AdminDocumentation(MainHandler):
    def get(self):

        document_id = self.request.get("document_id")
        if document_id:
            document = model.Document.get_by_id(int(document_id))
        else:
            document = None

        documents = model.Document.query().order(model.Document.order).fetch()

        if document:
            # can only choose from an existing order
            order_len = len(documents) + 1
        else:
            # can choose to be the next item / default
            order_len = len(documents) + 2

        self.render("admin-documentation.html", documents=documents, order_len=order_len, document=document)

    def post(self):
        file_req = self.request.POST["file"]
        name = self.request.get("name")
        description = self.request.get("description")
        document_id = self.request.get("document_id")
        order = self.request.get("order")
        isClientChoice = self.request.get("isClientChoice")
        if isClientChoice:
            isClientChoice = True
        else:
            isClientChoice = False

        try:
            order = int(order)
        except:
            logging.error("something wrong with getting document order to be an integer")
            order = False

        if not order:
            last_document = model.Document.query().order(-model.Document.order).get()
            if last_document:
                last_order = last_document.order
                order = last_order + 1
            else:
                order = 1

        # reset order
        utils.order_documents(order)

        if document_id:
            document = model.Document.get_by_id(int(document_id))

            document.name = name
            document.description = description
            document.order = order
            document.isClientChoice = isClientChoice
            try:
                if file_req.value and document.file_key:
                    utils.delete_file_from_gcs(document.file_key.get().gcs_filename)
                    document.file_key.delete()

                    file_obj = utils.save_file_to_gcs(file_req)
                    document.file_key = file_obj.key
                    document.download_link = file_obj.download_link
                else:
                    file_obj = utils.save_file_to_gcs(file_req)
                    document.file_key = file_obj.key
                    document.download_link = file_obj.download_link
            except:
                logging.error("something happened error-wise with the file upload for an existing file")


            document.put()

        else:
            try:
                if file_req.value:
                    file_obj = utils.save_file_to_gcs(file_req)
                    file_key = file_obj.key
                    download_link = file_obj.download_link
                else:
                    file_key = None
                    download_link = None
            except:
                logging.error("something happened error-wise with the file upload for a new file")
                file_key = None
                download_link = None

            document = model.Document(name=name, description=description, file_key=file_key, download_link=download_link, order=order, isClientChoice=isClientChoice)
            document.put()

        self.redirect("/admin/documentation")

class AdminErf(MainHandler):
    def get(self):

        erfs = model.Erf.query().order(model.Erf.erf_number).fetch()
        plans = model.PlanType.query().order(model.PlanType.name).fetch()

        if not erfs:
            for i in range(1,103):
                e = model.Erf(erf_number=i)
                e.put()

            erfs = model.Erf.query().order(model.Erf.erf_number).fetch()

        self.render('admin-erf.html', erfs=erfs, plans=plans)

class AdminErfP2(MainHandler):
    def get(self):

        erfs = model.ErfP2.query().order(model.ErfP2.erf_number).fetch()
        plans = model.PlanTypeP2.query().order(model.PlanTypeP2.name).fetch()

        if not erfs:
            for i in range(1,10):
                e = model.ErfP2(erf_number=i)
                e.put()

            erfs = model.ErfP2.query().order(model.ErfP2.erf_number).fetch()

        self.render('admin-erf.html', erfs=erfs, plans=plans, phase2=True)

class AdminSaveErf(MainHandler):
    def post(self, erf_id):
        erf = model.Erf.get_by_id(int(erf_id))

        plan_type = self.request.get("plan_type")
        size = self.request.get("size")
        price = self.request.get("price")
        turnkey_price = self.request.get("turnkey_price")
        status = self.request.get("status")

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
        if turnkey_price:
            try:
                erf.turnkey_price = int(turnkey_price)
            except:
                logging.error("turnkey_price - probably int error for %s" % erf_id)
        if status:
            erf.status = status

        if plan_type:
            plan_obj = model.PlanType.get_by_id(int(plan_type))
            erf.plan_type = plan_obj.key
            erf.plan_name = plan_obj.name

        erf.put()

        self.render_json({
            "message": "success",
            "erf_id": erf_id
            })

class AdminSaveErfP2(MainHandler):
    def post(self, erf_id):
        erf = model.ErfP2.get_by_id(int(erf_id))

        plan_ids = self.request.get("plan_ids")

        size = self.request.get("size")
        price = self.request.get("price")
        turnkey_price = self.request.get("turnkey_price")
        status = self.request.get("status")

        logging.error("plan_ids......")
        logging.error(plan_ids)

        plan_ids = plan_ids.split(",")
        logging.error("plan_ids, list?")
        logging.error(plan_ids)

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
        if turnkey_price:
            try:
                erf.turnkey_price = int(turnkey_price)
            except:
                logging.error("turnkey_price - probably int error for %s" % erf_id)
        if status:
            erf.status = status

        if len(plan_ids) > 0:
            plan_keys = []
            new_plan_ids = []
            plan_names = []
            for plan_id in plan_ids:
                plan_obj = model.PlanTypeP2.get_by_id(int(plan_id))
                plan_keys.append(plan_obj.key)
                plan_names.append(plan_obj.name)
                new_plan_ids.append(int(plan_id))
                logging.error(" - - - - " + plan_obj.name)

            erf.plan_types = plan_keys
            erf.plan_ids = new_plan_ids
            erf.plan_names = plan_names

        erf.put()

        self.render_json({
            "message": "success",
            "erf_id": erf_id
            })


class AdminClientContacts(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        contacts, next_curs, more = model.ClientContact.query().order(model.ClientContact.name).fetch_page(100, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        self.render("admin-client-contacts.html", contacts=contacts, next_curs=next_curs)

class AdminContactedClient(MainHandler):
    def post(self):
        contact_id = self.request.get("contact_id")
        contact = model.ClientContact.get_by_id(int(contact_id))
        contact.contacted = not contact.contacted
        contact.put()

        self.render_json({
            "message": "success"
            });

class AdminApprovedClient(MainHandler):
    def post(self):
        contact_id = self.request.get("contact_id")
        contact = model.ClientContact.get_by_id(int(contact_id))
        contact.approved = not contact.approved

        logging.error("contact.approved? %s" % contact.approved)

        contact.put()

        logging.error("HEEEELLLLOOOO ")

        self.render_json({
            "message": "success"
            });

class AdminPlanTypes(MainHandler):
    def get(self):

        plan_id = self.request.get("plan_id")

        plans = model.PlanType.query().order(model.PlanType.name).fetch()

        if plan_id:
            plan = model.PlanType.get_by_id(int(plan_id))
        else:
            plan = None

        self.render("admin-plan-types.html", plans=plans, plan=plan)

    def post(self):
        image = self.request.get("image")
        pdf = self.request.get("pdf")
        file_req = self.request.POST["file"]

        name = self.request.get("name")
        description = self.request.get("description")
        plan_id = self.request.get("plan_id")
        content_type = self.request.get("content_type")

        if plan_id:
            plan = model.PlanType.get_by_id(int(plan_id))

            plan.name = name
            plan.description = description
            if image and plan.image:
                utils.delete_from_gcs(plan.media_obj.get().gcs_filename)
                plan.media_obj.delete()

                media_obj = utils.save_to_gcs(image)
                plan.image = media_obj.serving_url

            # if pdf and plan.file_key:
            #     utils.delete_file_from_gcs(plan.file_media_key.get().gcs_filename)
            #     plan.file_media_key.delete()

            #     file_media_obj = utils.save_file_to_gcs(pdf, content_type)
            #     plan.file_media_key = file_media_obj.key
            try:
                if file_req.value and plan.file_key:
                    utils.delete_file_from_gcs(plan.file_key.get().gcs_filename)
                    plan.file_key.delete()

                    file_obj = utils.save_file_to_gcs(file_req)
                    plan.file_key = file_obj.key
                    plan.download_link = file_obj.download_link
                else:
                    file_obj = utils.save_file_to_gcs(file_req)
                    plan.file_key = file_obj.key
                    plan.download_link = file_obj.download_link
            except:
                logging.error("something happened error-wise with the file upload for an existing file")


            plan.put()

        else:
            logging.error("hello? again?")
            if image:
                media_obj = utils.save_to_gcs(image)
                media_key = media_obj.key
                serving_url = media_obj.serving_url
            else:
                serving_url = None
                media_key = None

            try:
                if file_req.value:
                    logging.error("hello?")
                    file_obj = utils.save_file_to_gcs(file_req)
                    file_key = file_obj.key
                    download_link = file_obj.download_link
                else:
                    file_key = None
                    download_link = None
            except:
                logging.error("something happened error-wise with the file upload for a new file")
                file_key = None
                download_link = None

            plan = model.PlanType(name=name, description=description, image=serving_url, media_obj=media_key, file_key=file_key, download_link=download_link)
            plan.put()

        self.redirect("/admin/plan_types")

class AdminPlanTypesP2(MainHandler):
    def get(self):

        plan_id = self.request.get("plan_id")

        plans = model.PlanTypeP2.query().order(model.PlanTypeP2.name).fetch()

        if plan_id:
            plan = model.PlanTypeP2.get_by_id(int(plan_id))
        else:
            plan = None

        self.render("admin-plan-types.html", plans=plans, plan=plan, phase2=True)

    def post(self):
        image = self.request.get("image")
        pdf = self.request.get("pdf")
        file_req = self.request.POST["file"]

        name = self.request.get("name")
        price = int(self.request.get("price"))
        description = self.request.get("description")
        plan_id = self.request.get("plan_id")
        content_type = self.request.get("content_type")

        if plan_id:
            plan = model.PlanTypeP2.get_by_id(int(plan_id))

            plan.name = name
            plan.price = price
            plan.description = description
            if image and plan.image:
                utils.delete_from_gcs(plan.media_obj.get().gcs_filename)
                plan.media_obj.delete()

                media_obj = utils.save_to_gcs(image)
                plan.image = media_obj.serving_url

            # if pdf and plan.file_key:
            #     utils.delete_file_from_gcs(plan.file_media_key.get().gcs_filename)
            #     plan.file_media_key.delete()

            #     file_media_obj = utils.save_file_to_gcs(pdf, content_type)
            #     plan.file_media_key = file_media_obj.key
            try:
                if file_req.value and plan.file_key:
                    utils.delete_file_from_gcs(plan.file_key.get().gcs_filename)
                    plan.file_key.delete()

                    file_obj = utils.save_file_to_gcs(file_req)
                    plan.file_key = file_obj.key
                    plan.download_link = file_obj.download_link
                else:
                    file_obj = utils.save_file_to_gcs(file_req)
                    plan.file_key = file_obj.key
                    plan.download_link = file_obj.download_link
            except:
                logging.error("something happened error-wise with the file upload for an existing file")


            plan.put()

        else:
            logging.error("hello? again?")
            if image:
                media_obj = utils.save_to_gcs(image)
                media_key = media_obj.key
                serving_url = media_obj.serving_url
            else:
                serving_url = None
                media_key = None

            try:
                if file_req.value:
                    logging.error("hello?")
                    file_obj = utils.save_file_to_gcs(file_req)
                    file_key = file_obj.key
                    download_link = file_obj.download_link
                else:
                    file_key = None
                    download_link = None
            except:
                logging.error("something happened error-wise with the file upload for a new file")
                file_key = None
                download_link = None

            plan = model.PlanTypeP2(name=name, price=price, description=description, image=serving_url, media_obj=media_key, file_key=file_key, download_link=download_link)
            plan.put()

        self.redirect("/admin/p2/plan_types")

class AdminErfClicks(MainHandler):
    def get(self):
        erf_clicks = model.ErfClick.query().order(-model.ErfClick.clicks).fetch()
        self.render("admin-erf-clicks.html", erf_clicks=erf_clicks)

class AdminInformation(MainHandler):
    def get(self):

        information_id = self.request.get("information_id")

        informations = model.Information.query().order(model.Information.name).fetch()

        if information_id:
            information = model.Information.get_by_id(int(information_id))
        else:
            information = None

        self.render("admin-information.html", informations=informations, information=information)

    def post(self):
        image = self.request.get("image")
        file_req = self.request.POST["file"]

        name = self.request.get("name")
        description = self.request.get("description")
        information_id = self.request.get("information_id")

        if information_id:
            information = model.Information.get_by_id(int(information_id))

            information.name = name
            information.description = description
            if image and information.image:
                utils.delete_from_gcs(information.media_obj.get().gcs_filename)
                information.media_obj.delete()

                media_obj = utils.save_to_gcs(image)
                information.image = media_obj.serving_url
            try:
                if file_req.value and information.file_key:
                    utils.delete_file_from_gcs(information.file_key.get().gcs_filename)
                    information.file_key.delete()

                    file_obj = utils.save_file_to_gcs(file_req)
                    information.file_key = file_obj.key
                    information.download_link = file_obj.download_link
                else:
                    file_obj = utils.save_file_to_gcs(file_req)
                    information.file_key = file_obj.key
                    information.download_link = file_obj.download_link
            except:
                logging.error("something happened error-wise with the file upload for an existing file")


            information.put()

        else:
            logging.error("hello? again?")
            if image:
                media_obj = utils.save_to_gcs(image)
                media_key = media_obj.key
                serving_url = media_obj.serving_url
            else:
                serving_url = None
                media_key = None

            try:
                if file_req.value:
                    logging.error("hello?")
                    file_obj = utils.save_file_to_gcs(file_req)
                    file_key = file_obj.key
                    download_link = file_obj.download_link
                else:
                    file_key = None
                    download_link = None
            except:
                logging.error("something happened error-wise with the file upload for a new file")
                file_key = None
                download_link = None

            information = model.Information(name=name, description=description, image=serving_url, media_obj=media_key, file_key=file_key, download_link=download_link)
            information.put()

        self.redirect("/admin/information")

# class AdminDeletePlan(MainHandler):
#     def post(self, plan_id):
#         plan = model.PlanType.get_by_id(int(plan_id))
#         if plan.file_key:
#             utils.delete_file_from_gcs(plan.file_key.get().gcs_filename)
#         if plan.media_obj:
#             utils.delete_from_gcs(plan.media_obj.get().gcs_filename)

#         plan.key.delete()
#         self.redirect("/admin/plan_types")

class AdminDeleteDocument(MainHandler):
    def post(self, document_id):

        document = model.Document.get_by_id(int(document_id))

        utils.delete_file_from_gcs(document.file_key.get().gcs_filename)

        document.key.delete()

        self.redirect("/admin/documentation")



class AdminContact(MainHandler):
    def get(self):
        contacts = model.Contact.query().order(-model.Contact.created).fetch()

        contact_id = self.request.get("contact_id")
        contact = None
        if contact_id:
            contact = model.Contact.get_by_id(int(contact_id))

        self.render("admin-contact.html", contacts=contacts, contact=contact)

    def post(self):
        name = self.request.get("name")
        email = self.request.get("email")
        description = self.request.get("description")
        phone = self.request.get("phone")
        mobile = self.request.get("mobile")
        landline = self.request.get("landline")

        contact_id = self.request.get("contact_id")

        if contact_id:
            contact = model.Contact.get_by_id(int(contact_id))

            contact.name = name
            contact.description = description
            contact.email = email
            contact.phone = phone
            contact.mobile = mobile
            contact.landline = landline
            contact.put()

        else:
            contact = model.Contact( name=name, email=email, description=description, phone=phone, mobile=mobile, landline=landline )
            contact.put()

        self.redirect("/admin/contact")






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
        tag = self.request.get("tag")
        caption  =self.request.get("caption")

        logging.error("LABEL................... %s" % label)

        if image_id == "new":
            media_obj = utils.save_to_gcs(image)
            gallery_image = model.ImageGallery(label=label, caption=caption, image=media_obj.serving_url, media_id = str(media_obj.key.id()), media_key = media_obj.key, tag=tag)
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
            gallery_image.tag = tag
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
    ('/p2/plans_prices', PlansPricesP2),
    ('/p2/erf/(\w+)', ErfPlansP2),
    ('/location', Location),
    ('/progress', Progress),
    ('/p2/progress', ProgressP2),
    ('/information', Information),
    ('/client_choices', ClientChoices),
    ('/documentation', Documentation),
    ('/client_contact', ContactForm),
    ('/contact', Contact),

    # serving files
    ('/file', ServeFile),

    #api
    ('/plan/erf/(\w+)', PlanForErf),
    ('/erf/track/(\w+)', TrackErfClick),

    # admin
    ('/admin', Admin),
    ('/admin/home', AdminHome),
    ('/admin/location', AdminLocation),
    ('/admin/information', AdminInformation),
    ('/admin/progress', AdminProgress),
    ('/admin/p2/progress', AdminProgressP2),
    ('/admin/documentation', AdminDocumentation),
    ('/client_contact', ContactForm),
    ('/admin/erf', AdminErf),
    ('/admin/p2/erf', AdminErfP2),
    ('/admin/erf/(\w+)', AdminSaveErf),
    ('/admin/p2/erf/(\w+)', AdminSaveErfP2),
    ('/admin/client_contacts', AdminClientContacts),
    ('/admin/contacted_client', AdminContactedClient),
    ('/admin/approved_client', AdminApprovedClient),
    ('/admin/plan_types', AdminPlanTypes),
    ('/admin/p2/plan_types', AdminPlanTypesP2),
    ('/admin/erf_clicks', AdminErfClicks),
    ('/admin/information', AdminInformation),
    # ('/admin/plan/delete/(\w+)', AdminDeletePlan),
    ('/admin/document/delete/(\w+)', AdminDeleteDocument),

    ('/admin/contact', AdminContact),



    # Old Nicholas stuff
    # ('/gallery', Gallery),
    # ('/about', About),
    # ('/what_we_do', WhatWeDo),
    # ('/contact', Contact),

    # ('/admin/front_page', AdminFrontPage),
    # ('/admin/gallery', AdminGallery),
    # ('/admin/about', AdminAbout),
    # ('/admin/what_we_do', AdminWhatWeDo),

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
