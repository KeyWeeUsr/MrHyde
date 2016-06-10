# -*- coding: utf-8 -*-
# MrHyde - A simple way to encrypt your files
# Version: 0.5
# Copyright (C) 2016, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
# License: GNU GPL v3.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# More info in LICENSE.txt
#
# The above copyright notice, warning and additional info together with
# LICENSE.txt file shall be included in all copies or substantial portions
# of the Software.

import os
import re
import ntpath
import shutil
import vial
import os.path as op
import pyscrypt as ps
from kivy.app import App
from kivy.clock import Clock
from functools import partial
from kivy.utils import platform
from kivy.uix.button import Button
from threading import Thread, Event
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, ListProperty
from kivy.uix.screenmanager import Screen, ScreenManager


class Start(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.path = self.app.path
        self.phase = 1
        super(Start, self).__init__(**kw)

    def create(self, *args):
        pas = self.ids.pas.text.encode('utf-8')
        if not op.exists(self.path+'/._'):
            if pas != '':
                self.h = ps.hash(pas, self.app.mid, 1024, 1, 1, 32)
                with open(self.path+'/._', 'wb') as f:
                    f.write(self.h)
                self.phase += 1
                self.ids.pas.text = ''
                self.ids.steps.text = str(self.phase)+'/4'
        elif self.phase == 2:
            if pas != '':
                h = ps.hash(pas, self.app.mid, 1024, 1, 1, 32)
                if self.h == h:
                    self.ids.pas.text = ''
                    self.ids.log.text += ('\n\nData pasword can not be the '
                                          'same as App password!')
                    self.ids.log.scroll_to(self.ids.log.children[0])
                else:
                    self.pas = pas
                    self.phase += 1
                    self.ids.pas.text = ''
                    self.ids.steps.text = str(self.phase)+'/4'
        elif self.phase == 3:
            if pas != '':
                h = ps.hash(pas, self.app.mid, 1024, 1, 1, 32)
                if self.h == h:
                    self.ids.pas.text = ''
                    self.ids.log.text += ('\n\nData pasword can not be the '
                                          'same as App password!')
                    self.ids.log.scroll_to(self.ids.log.children[0])
                else:
                    self.pas2 = pas
                    os.mkdir(self.path+'/transform')
                    os.mkdir(self.path+'/transform/dr')
                    os.mkdir(self.path+'/transform/mr')
                    self.ids.pas.text = ''
                    self.app.pas1 = self.pas
                    self.app.pas2 = self.pas2
                    self.phase += 1
                    self.ids.steps.text = str(self.phase)+'/4'
                    self.ids.log.text += ('\n\n* * *'
                                          '\n\nNow set a word or a sentence '
                                          'that will tell you if you typed '
                                          'your passwords correctly. If the '
                                          'wrong passwords are typed, your '
                                          'text won\'t show correctly.'
                                          '\n\nThe value on the right is '
                                          'a custom increment for your '
                                          'counter. Choose a value from 1 to '
                                          '10. The smaller number, the more '
                                          'often will the counter change. If '
                                          'you don\'t know what the value '
                                          'means, leave the default one.')
                    self.ids.log.scroll_to(self.ids.log.children[0])
                self.ids.ctr_value.width = self.ids.pas.width / 4.0
                self.ids.ctr_value.color = [1, 1, 1, 1]
                self.ids.ctr_value.background_color = [1, 1, 1, 1]
        elif self.phase == 4:
            pas = self.ids.pas.text.encode('utf-8')
            self.app.ctr_value = self.ids.ctr_value.text
            if pas != '':
                with open(self.path+'/transform/start.hyde', 'wb') as f:
                    key32 = ps.hash(self.pas, self.pas2, 1024, 1, 1, 32)
                    aes = vial.Vial(key32, counter_value=self.app.ctr_value)
                    f.write(aes.encrypt(pas, self.path+'/transform/start.ctr'))
                with open(self.path+'/value.ctr', 'wb') as f:
                    f.write(self.app.ctr_value)
                self.phase += 1
                del self.h, self.pas, self.pas2
                self.manager.current = 'home'
        if self.phase <= 4:
            self.ids.pas.focus = True
        else:
            self.app.home.ids.pas1.focus = True


class Home(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.path = self.app.path
        self.deleting = False
        self.app.home = self
        self.phase = 1
        self.stopper = Event()
        super(Home, self).__init__(**kw)

    def check(self, button):
        pas1 = self.ids.pas1.text.encode('utf-8')
        pas2 = self.ids.pas2.text.encode('utf-8')
        pas = ps.hash(pas1, self.app.mid, 1024, 1, 1, 32)
        if self.phase == 1:
            self.ids.pas1.text = ''
            with open(self.path+'/._', 'rb') as f:
                h = f.read()
            if pas not in h:
                if len(h) < 36:
                    self.ids.log.text += '\nWrong password!'
                    with open(self.path+'/._', 'ab') as f:
                        f.write('x')
                else:
                    if not self.deleting:
                        self.deleting = True
                        Thread(target=self.delete).start()
                        self.ids.log.text = ('\nPerfect! Now you\'ve '
                                             'deleted all your data.')
                return
            else:
                with open(self.path+'/._', 'wb') as f:
                    f.write(pas)
                with open(self.path+'/value.ctr', 'rb') as f:
                    self.app.ctr_value = f.read()
                self.ids.labtitle.text = 'Mr. Hyde'
                button.text = 'Enter!'
                self.ids.pas2.disabled = False
                self.phase += 1
            self.ids.pas1.focus = True
        elif self.phase == 2:
            self.app.pas1 = pas1
            self.app.pas2 = pas2
            self.ids.pas1.text = ''
            self.ids.pas2.text = ''
            self.ids.log.text = ''
            self.app.lab.verify(self.app.lab.ids.verify)
            self.manager.current = 'laboratory'

    def delete(self):
        if op.exists(self.path+'/._'):
            os.remove(self.path+'/._')
        if op.exists(self.path+'/value.ctr'):
            os.remove(self.path+'/value.ctr')
        if op.exists(self.path+'/transform'):
            shutil.rmtree(self.path+'/transform')
        Clock.schedule_once(self.deleted, 5)

    def deleted(self, t):
        self.manager.current = 'start'
        self.deleting = False


class Lab(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.path = self.app.path
        super(Lab, self).__init__(**kw)
        self.app.lab = self

    def verify(self, widget):
        if op.exists(self.path+'/transform/start.hyde'):
            with open(self.path+'/transform/start.hyde', 'rb') as f:
                dec = f.read()
            key32 = ps.hash(self.app.pas1, self.app.pas2, 1024, 1, 1, 32)
            aes = vial.Vial(key32, counter_value=self.app.ctr_value)
            dec = aes.decrypt(dec, self.path+'/transform/start.ctr')
            widget.text = dec

    def lock(self):
        home = self.app.home
        home.phase = 1
        home.ids.pas2.disabled = True
        self.app.pas1 = None
        self.app.pas2 = None


class Way(object):
    def __init__(self, screen):
        self.app = App.get_running_app()
        self.upl_screens = []
        self.scr = screen
        self.path = self.scr.app.path
        self.default_target = self.path + '/transform/dr/'

    def add(self, item, from_screen):
        self.get_screens()
        scroll = self.scr.ids.filelist
        if len(item) == 0:
            itemlist = []
            if from_screen == 'upload':
                observablelist = self.scr.ids.machine.files
            elif from_screen == 'view':
                observablelist = self.scr.ids.laboratory.files
            for i in observablelist:
                if i != '..\\':
                    itemlist.append(i)
            for i in itemlist:
                if i not in self.app.flist:
                    self.app.flist.append(i.encode('utf-8'))
                    ipath = i.encode('utf-8')
                    i = ntpath.basename(ipath)
                    scroll.add_widget(FileItem(text=i, way=self, path=ipath))
        else:
            i = item[0].encode('utf-8')
            if i not in self.app.flist:
                self.app.flist.append(i)
                ipath = i
                i = ntpath.basename(i)
                scroll.add_widget(FileItem(text=i, way=self, path=ipath))

    def hyde(self, target=None):
        self.buttons(True)
        target = self.default_target if target is None else target
        if self.app.flist == []:
            self.buttons()
            return
        flist = self.app.flist
        key32 = ps.hash(self.app.pas1, self.app.pas2, 1024, 1, 1, 32)
        aes = vial.Vial(key32, counter_value=self.app.ctr_value)
        for child in self.scr.ids.filelist.children:
            child.children[1].disabled = True
        for item in flist:
            children = self.scr.ids.filelist.children
            i = ntpath.basename(item)
            fin = open(item, 'rb')
            if isinstance(target, ListProperty) or isinstance(target, list):
                target = target[0].encode('utf-8')
            fout = open(op.join(target, i), 'wb')
            if 'transform' + os.path.sep + 'dr' not in item:
                aes.encrypt_stream(fin, fout)
            else:
                aes.decrypt_stream(fin, fout)
            fin.close()
            fout.close()
            for child in children:
                if i in child.children[0].text:
                    self.scr.ids.filelist.remove_widget(child)
                    self.app.flist.remove(item)

        # if Thread ends en(de)crypting too soon, this recursion ensures that
        # all files left in 'flist' i.e. even files that could be broken
        # are en(de)crypted properly, because Thread always fails before
        # removing file from 'flist' i.e. during encryption
        if self.app.flist != []:
            if target == op.join(self.path, '/transform/dr/'):
                self.scr.hyde()
            else:
                self.scr.hyde(target)
        else:
            self.buttons()
            p1 = partial(self.update, self.upl_screens[0])
            p2 = partial(self.update, self.upl_screens[1])
            Clock.schedule_once(p1)
            Clock.schedule_once(p2)

    def get_screens(self):
        if self.upl_screens == []:
            for i, screen in enumerate(self.scr.parent.screen_names):
                if screen == 'uploader':
                    self.upl_screens.append(i)
                elif screen == 'viewer':
                    self.upl_screens.append(i)

    def update(self, i, *args):
        self.scr.parent.screens[i].ids.laboratory._update_files()
        self.scr.parent.screens[i].ids.machine._update_files()

    def buttons(self, disabled=False):
        self.app.uploader.ids.upload_add.disabled = disabled
        self.app.uploader.ids.upload_hyde.disabled = disabled
        self.app.viewer.ids.view_add.disabled = disabled
        self.app.viewer.ids.view_hyde.disabled = disabled


class Uploader(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.app.uploader = self
        self.path = self.app.path
        self.driveltrs = []
        super(Uploader, self).__init__(**kw)
        Clock.schedule_interval(self.checkpath, 1)
        Clock.schedule_once(self.getletters, 1)
        way = Way(self)
        self.add = way.add
        self._hyde = way.hyde

    def checkpath(self, t):
        if op.exists(self.path+'/transform/dr'):
            self.ids.laboratory.rootpath = self.path+'/transform/dr'
            Clock.unschedule(self.checkpath)

    def getletters(self, t):
        if platform == 'win':
            if len(self.driveltrs) != 0:
                return
            self.driveltrs = re.findall(r"[A-Z]+:.*$",
                                        os.popen("mountvol /").read(),
                                        re.MULTILINE)
            for ltr in self.driveltrs:
                d = Button(on_release=partial(self.changerootpath, ltr),
                           text=ltr)
                self.ids.upload_drives.add_widget(d)
            self.ids.machine.rootpath = self.driveltrs[0]
        else:
            self.ids.upload_drives.height = 0

    def changerootpath(self, path, *args):
        self.ids.machine.rootpath = path

    def hyde(self, *args):
        Thread(target=self._hyde).start()


class Viewer(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.app.viewer = self
        self.path = self.app.path
        self.driveltrs = []
        super(Viewer, self).__init__(**kw)
        Clock.schedule_once(self.getletters, 1)
        way = Way(self)
        self.add = way.add
        self._hyde = way.hyde

    def getletters(self, t):
        if platform == 'win':
            if len(self.driveltrs) != 0:
                return
            self.driveltrs = re.findall(r"[A-Z]+:.*$",
                                        os.popen("mountvol /").read(),
                                        re.MULTILINE)
            for ltr in self.driveltrs:
                d = Button(on_release=partial(self.changerootpath, ltr),
                           text=ltr)
                self.ids.view_drives.add_widget(d)
            self.ids.machine.rootpath = self.driveltrs[0]
        else:
            self.ids.view_drives.height = 0

    def changerootpath(self, path, *args):
        self.ids.machine.rootpath = path

    def hyde(self, target):
        # if not target, show popup where warning that to extract you have to
        # select folder!
        self.target = target
        if isinstance(type(target), ListProperty):
            self.target = self.target[0].encode('utf-8')
        from functools import partial
        Thread(target=partial(self._hyde, self.target)).start()


class Exporter(Screen):
    pass


class NewPass(Screen):
    pass


class FileItem(BoxLayout):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.text = kw.get('text', '---')
        self.way = kw.get('way', None)
        self.path = kw.get('path', '')
        super(FileItem, self).__init__(**kw)

    def rm(self):
        for item in self.app.flist:
            if self.text in item:
                self.app.flist.remove(item)

    def trash(self):
        self.rm()
        if op.exists(self.path):
            os.remove(self.path)
        if 'transform' in self.path and op.exists(self.path[:-3]+'ctr'):
            os.remove(self.path[:-3]+'ctr')
        for i in self.way.upl_screens:
            self.way.update(i)
        self.parent.remove_widget(self)


class Root(ScreenManager):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.path = self.app.path
        super(Root, self).__init__(**kw)
        if not op.exists(self.path+'/._'):
            self.current = 'start'


class Unique(object):
    def get(self):
        getattr(self, 'get_'+str(platform))()
        return self.unique

    def get_win(self):
        import _winreg
        registry = _winreg.HKEY_LOCAL_MACHINE
        address = 'SOFTWARE\\Microsoft\\Cryptography'
        keyargs = _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY
        key = _winreg.OpenKey(registry, address, 0, keyargs)
        value = _winreg.QueryValueEx(key, 'MachineGuid')
        _winreg.CloseKey(key)
        self.unique = value[0]

    def get_android(self):
        import subprocess
        cmd = ['getprop', 'ril.serialnumber']
        self.unique = subprocess.check_output(cmd)[:-1]


class MrHyde(App):
    path = op.dirname(op.abspath(__file__))
    flist = []

    def on_pause(self):
        return True

    def display_settings(self, *args):
        pass

    def build(self):
        self.mid = Unique().get()
        return Root()

if __name__ == '__main__':
    MrHyde().run()
