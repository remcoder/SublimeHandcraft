# (c) Remco Veldkamp 2012
# MIT License

import sublime, sublime_plugin
from xml.dom import minidom
import urllib, logging, urllib2, sys
import re, os.path,HTMLParser
from BeautifulSoup import BeautifulSoup

hh = urllib2.HTTPHandler()
hsh = urllib2.HTTPSHandler()
#hh.set_http_debuglevel(1)
#hsh.set_http_debuglevel(1)
opener = urllib2.build_opener(hh, hsh, urllib2.HTTPCookieProcessor())
email = ""
pwd = ""
prototype = ""
sheet_db = {};

_ = lambda x: 0


class HandcraftSaveCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    content = self.view.substr(sublime.Region(0, self.view.size()))

    global sheet_db

    view = sublime.active_window().active_view()
    prototype, sheet = sheet_db[view.id()]
    print "saving", prototype, sheet, content
    def callback():
      saveSheet(prototype, sheet, content )
      view.set_scratch(True)
    login(callback)

class HandcraftListSheetsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    def callback(): listSheets(edit)
    login(callback)


def listSheets(edit):
  # get prototypes
  url = "http://handcraft.it/prototypes"
  response2 = opener.open(url)
  soup = BeautifulSoup(response2)
  "section li .visual a"
  prototypes = [os.path.basename(li.find("div", "visual").a["href"]) for li in soup.section.findAll("li")]
  print prototypes

  # show list of prototypes
  def on_select_prototype(index):
    if index != -1:
      prototype = prototypes[index]

      # retrieve sheets
      url = "http://handcraft.it/workon/%s/sheets" % prototype
      soup = BeautifulSoup(opener.open(url))
      sheets = [li.a.string for li in soup.find("div", id="otherSheets").ol.findAll("li")]

      def on_select_sheet(i):
        if i != -1:
          def callback(): loadSheet(edit, prototype, sheets[i])
          login(callback)


      sublime.active_window().show_quick_panel(sheets, on_select_sheet)


  sublime.active_window().show_quick_panel(prototypes, on_select_prototype)

def loadSheet(edit, prototype, sheet):
  url = "http://handcraft.it/workon/%s/sheets/%s" % (prototype, sheet)
  print url
  response2 = opener.open(url)
  soup = BeautifulSoup(response2)
  h = HTMLParser.HTMLParser()
  code = h.unescape(soup.textarea.string)

  view = sublime.active_window().new_file()
  view.insert(edit, view.size(), code)
  view.set_syntax_file("Packages/XML/XML.tmLanguage")
  global sheet_db
  sheet_db[view.id()] = (prototype, sheet)

def saveSheet(prototype, sheet, content):
  url = 'http://handcraft.it/workon/%s/action?type=save' % prototype
  data = urllib.urlencode({ "sheetName" : sheet, "code" : content })
  response2 = opener.open(url, data)

  print "save complete"

def login(callback):
  #print 'checking login'
  if len(email) > 0 and len(pwd) > 0:
    return callback()


  def setEmail(s):
    global email
    email = s
    sublime.active_window().show_input_panel("pwd", pwd, setPwd, _, _)

  def setPwd(s):
    global pwd
    pwd = s
    cred = urllib.urlencode({ "email" : email, "password" : pwd})
    response = opener.open("http://handcraft.it/signin", cred)
    callback()

  sublime.active_window().show_input_panel("email", email, setEmail, _,_)



