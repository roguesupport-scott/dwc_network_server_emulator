"""DWC Network Server Emulator

    Copyright (C) 2014 SMTDDR
    Copyright (C) 2014 kyle95wm
    Copyright (C) 2014 AdmiralCurtiss
    Copyright (C) 2015 Sepalani

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.internet.error import ReactorAlreadyRunning
import re
import base64
import codecs
import sqlite3
import collections
import json
import time
import datetime
import logging

import other.utils as utils
import gamespy.gs_utility as gs_utils
import dwc_config

logger = dwc_config.get_logger('RegisterPage')
_, port = dwc_config.get_ip_port('RegisterPage')


class RegPage(resource.Resource):
    isLeaf = True

    def __init__(self, regpage):
        self.regpage = regpage

    def get_header(self, title=None):
        if not title:
            title = 'Register a Console'
        s = """
        <html>
        <head>
            <title>%s</title>
        </head>
        <body>
            <p>
                <b>Register a console</b>
            </p>""" % title
        return s

    def get_footer(self):
        s = """
        </body>
        </html>"""
        return s

    def update_maclist(self, request):
        address = request.getClientIP()
        dbconn = sqlite3.connect('gpcm.db')
        macadr = request.args['macadr'][0].strip()
        actiontype = request.args['action'][0]
        macadr = macadr.lower()
        if not re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",
                        macadr):
            request.setResponseCode(500)
            return "The MAC you entered was invalid." \
                   "Please click the back button and try again!"
        macadr = macadr.replace(":", "").replace("-", "")
        if actiontype == 'add':
            dbconn.cursor().execute(
                'INSERT INTO pending VALUES(?)',
                (macadr,)
            )
            responsedata = "Added %s to pending list." % (macadr)
            responsedata += "Please close this window now."
            " It's also not a bad idea to check back on the status of your"
            " activation by attempting to connect your console to the server."
        dbconn.commit()
        dbconn.close()
        request.setHeader("Content-Type", "text/html; charset=utf-8")
        request.setResponseCode(303)
        return responsedata
        if not referer:
            referer = "/register"
        request.setHeader("Location", referer)

        request.setResponseCode(303)
        return responsedata

    def render_maclist(self, request):
        address = request.getClientIP()
        dbconn = sqlite3.connect('gpcm.db')
        responsedata = """
        <form action='updatemaclist' method='POST'>
        macadr (must be in the format of %s or %s):
            <input type='text' name='macadr'>
            <input type='hidden' name='action' value='add'>
            <input type='submit' value='Register console'>
        </form>
        <table border='1'>""" % ('aa:bb:cc:dd:ee:ff', 'aa-bb-cc-dd-ee-ff')
        dbconn.close()
        request.setHeader("Content-Type", "text/html; charset=utf-8")
        return responsedata

    def render_GET(self, request):
        title = None
        response = ''
        if request.path == "/register":
            title = 'Register a Console'
            response = self.render_maclist(request)

        return self.get_header(title) + response + self.get_footer()

    def render_POST(self, request):
        if request.path == "/updatemaclist":
            return self.update_maclist(request)
        else:
            return self.get_header() + self.get_footer()


class RegPageServer(object):
    def start(self):
        site = server.Site(RegPage(self))
        reactor.listenTCP(port, site)
        logger.log(logging.INFO,
                   "Now listening for connections on port %d...",
                   port)
        try:
            if not reactor.running:
                reactor.run(installSignalHandlers=0)
        except ReactorAlreadyRunning:
            pass


if __name__ == "__main__":
    RegPageServer().start()
