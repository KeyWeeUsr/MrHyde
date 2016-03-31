# -*- coding: utf-8 -*-
# MrHyde - A simple way to encrypt your files
# Version: 0.2
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
import pyaes as pa
import os.path as op
import pyscrypt as ps
from kivy.app import App
from kivy.clock import Clock
from functools import partial
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.button import Button
from threading import Thread, Event
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen, ScreenManager

Builder.load_string('''
<Root>:
    canvas:
        Rectangle:
            source: 'background.png'
            size: self.size
    Start:
        id: start
        name: 'start'
    Home:
        name: 'home'
    Lab:
        name: 'laboratory'

<Start>:
    BoxLayout:
        orientation: 'vertical'
        Widget:
            size_hint_y: 0.3
        Label:
            font_size: '20dp'
            text: 'Set unique passwords for me!\\nPlease do not forget them.'
            text_size: self.width, None
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]
        Widget:
            size_hint_y: 0.4
        HomeInput:
            id: pas
            size_hint: 0.8, 0.2
            pos_hint: {'center_x': 0.5}
        Widget:
            size_hint_y: 0.1
        Button:
            id: steps
            size_hint: 0.5,0.2
            pos_hint: {'center_x': 0.5}
            text: str(root.phase)+'/4'
            on_release: root.create()
        Widget:
            size_hint_y: 0.1
        Console:
            id: log
            text: ('Dr. J. Quill welcomes you to his crooked world!\\n\\n'\
                   'First password is only for application. If typed 10 times'\
                   ' incorrectly, the app will delete all its data.\\nThe '\
                   'other two passwords are for data.\\n\\nIt is necessary '\
                   'for passwords to be different from each other for better'\
                   ' security.\\n\\nPasswords are not stored anywhere, there '\
                   'is no chance of retrieving them.')

<Home>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: labtitle
            text: 'Dr. J. Quill'
            font_size: '60dp'
            size_hint_y: None
            height: '180dp'
        Image:
            size_hint_y: 0.3
            source: 'quill.png'
        Widget:
            size_hint_y: 0.2
        Label:
            text: 'Password 1:'
            size_hint_y: None
            height: self.texture_size[1]
        HomeInput:
            id: pas1
        Widget:
            size_hint_y: 0.05
        Label:
            text: 'Password 2:'
            size_hint_y: None
            height: self.texture_size[1]
        HomeInput:
            id: pas2
            disabled: True
        Widget
            size_hint_y: 0.2
        Button:
            text: 'Drink!'
            size_hint: 0.5, None
            pos_hint: {'center_x': 0.5}
            height: '50dp'
            on_release: root.check(self)
        Console:
            id: log

<Lab>:
    content: root.ids.content
    BoxLayout:
        orientation: 'vertical'
        ActionBar:
            pos_hint: {'top':1}
            ActionView:
                ActionPrevious:
                    with_previous: False
                    app_icon: 'quill.png'
                    app_icon_width: root.width*0.8
                    title: 'Mr. Hyde'
                    on_release: root.manager.current = 'home'
                ActionButton:
                    text: 'Uploader'
                    on_release: root.content.current = 'uploader'
                ActionButton:
                    text: 'Viewer'
                    on_release: root.content.current = 'viewer'
                ActionButton:
                    text: 'New Pass'
                    disabled: True
                ActionButton:
                    text: 'About'
                    on_release: root.content.current = 'about'
        ScreenManager:
            id: content
            Screen:
                Console:
                    id: verify
            Uploader:
                name: 'uploader'
            Viewer:
                name: 'viewer'
            Exporter:
                name: 'exporter'
            NewPass:
                name: 'newpass'
            About:
                name: 'about'

<Uploader>:
    BoxLayout:
        orientation: 'vertical'
        Caption:
            size_hint_y: None
            height: self.texture_size[1]
            text: 'Machine'
        Splitter:
            sizable_from: 'bottom'
            min_size: 0
            rescale_with_parent: True
            FileChooserIconView:
                id: machine
        Caption:
            size_hint_y: None
            height: self.texture_size[1]
            text: 'Laboratory'
        FileChooserIconView:
            id: laboratory
            rootpath: root.path+'/transform/dr'
        BoxLayout:
            size_hint_y: None
            height: '100dp'
            ScrollView:
                GridLayout:
                    cols: 1
                    id: filelist
                    size_hint: 0.8, None
                    height: self.minimum_height
            BoxLayout:
                size_hint_x: 0.2
                orientation: 'vertical'
                Button:
                    text: 'Add'
                    on_release: root.add(root.ids.machine.selection)
                Button:
                    text: 'Hyde'
                    on_release: root.hyde(self)

<Viewer>:
    BoxLayout:
        orientation: 'vertical'
        Caption:
            size_hint_y: None
            height: self.texture_size[1]
            text: 'Machine'
        Splitter:
            sizable_from: 'bottom'
            min_size: 0
            rescale_with_parent: True
            FileChooserIconView:
                id: laboratory
                rootpath: root.path+'/transform/dr'
        Caption:
            size_hint_y: None
            height: self.texture_size[1]
            text: 'Laboratory'
        BoxLayout:
            id: drives
            size_hint_y: None
            height: '30dp'
        FileChooserIconView:
            id: machine
            dirselect: True
            filters: ['*.____']
        BoxLayout:
            size_hint_y: None
            height: '100dp'
            ScrollView:
                GridLayout:
                    cols: 1
                    id: filelist
                    size_hint: 0.8, None
                    height: self.minimum_height
            BoxLayout:
                size_hint_x: 0.2
                orientation: 'vertical'
                Button:
                    text: 'Add'
                    on_release: root.add(root.ids.laboratory.selection)
                Button:
                    text: 'Extract'
                    on_release: root.hyde(self, root.ids.machine.selection)

<NewPass>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Change passwords for:'
        Button:
            text: 'Me'
        Button:
            text: 'Data'

<About@Screen>:
    Label:
        markup: True
        text: 'Copyright (C) 2016, KeyWeeUsr(Peter Badida)\\nLicense: GNU '\
              'GPL v3.0\\nFind me @ https://github.com/KeyWeeUsr'

<HomeInput@TextInput>:
    height: '50dp'
    multiline: False
    size_hint: 0.5, None
    pos_hint: {'center_x':0.5, 'center_y': 0.5}

<ScrollLabel@Label>:
    size_hint_y:None
    text_size:self.width,None
    height:self.texture_size[1]

<Caption@Label>:
    canvas.before:
        Color:
            rgba: 0.2,0.2,0.2,1
        Rectangle:
            size: self.size
            pos: self.pos

<Console@ScrollView>:
    text: ''
    ScrollLabel:
        text: root.text
        halign: 'center'

<FileItem>:
    size_hint_y: None
    height: '30dp'
    Button:
        text: 'x'
        size_hint_x: 0.2
        on_release: root.parent.remove_widget(root)
        on_release: root.rm()
    Label:
        text: root.text
        halign: 'left
        text_size: self.parent.size[0]*0.8, self.height
        halign: 'left'
        valign: 'middle'
''')


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
                return
        elif self.phase == 2:
            if pas != '':
                h = ps.hash(pas, self.app.mid, 1024, 1, 1, 32)
                if self.h == h:
                    self.ids.pas.text = ''
                    self.ids.log.text += ('\nData pasword can not be the same'
                                          ' as App password!')
                    return
                else:
                    self.pas = pas
                    self.phase += 1
                    self.ids.pas.text = ''
                    self.ids.steps.text = str(self.phase)+'/4'
                    return
        elif self.phase == 3:
            if pas != '':
                h = ps.hash(pas, self.app.mid, 1024, 1, 1, 32)
                if self.h == h:
                    self.ids.pas.text = ''
                    self.ids.log.text += ('\nData pasword can not be the same'
                                          ' as App password!')
                    return
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
                    self.ids.log.text += ('\n\nNow set a word or a sentence '
                                          'that will tell you if you typed '
                                          'passwords correctly. If the wrong '
                                          'passwords are typed, your text '
                                          'won\'t show.')
        elif self.phase == 4:
            pas = self.ids.pas.text.encode('utf-8')
            if pas != '':
                with open(self.path+'/transform/start.hyde', 'wb') as f:
                    key32 = ps.hash(self.pas, self.pas2, 1024, 1, 1, 32)
                    aes = pa.AESModeOfOperationCTR(key32)
                    f.write(aes.encrypt(pas))
                self.phase += 1
                del self.h, self.pas, self.pas2
                self.manager.current = 'home'


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
                if len(h) < 41:
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
                self.ids.labtitle.text = 'Mr. Hyde'
                button.text = 'Enter!'
                self.ids.pas2.disabled = False
                self.phase += 1
        elif self.phase == 2:
            self.app.pas1 = pas1
            self.app.pas2 = pas2
            self.ids.pas1.text = ''
            self.ids.pas2.text = ''
            self.ids.log.text = ''
            self.app.lab.verify(self.app.lab.ids.verify)
            self.manager.current = 'laboratory'

    def delete(self):
        shutil.rmtree(self.path+'/transform')
        os.remove(self.path+'/._')
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
            aes = pa.AESModeOfOperationCTR(key32)
            dec = aes.decrypt(dec)
            widget.text = dec


class Way(object):
    def __init__(self, screen):
        self.app = App.get_running_app()
        self.upl_screens = []
        self.scr = screen
        self.path = self.scr.app.path
        self.default_target = self.path + '/transform/dr/'

    def add(self, item):
        scroll = self.scr.ids.filelist
        if len(item) == 0:
            itemlist = []
            observablelist = self.scr.ids.machine.files
            for i in observablelist:
                if i != '..\\':
                    itemlist.append(i)
            for i in itemlist:
                if i not in self.app.flist:
                    self.app.flist.append(i.encode('utf-8'))
                    i = ntpath.basename(i.encode('utf-8'))
                    scroll.add_widget(FileItem(text=i))
        else:
            i = item[0].encode('utf-8')
            if i not in self.app.flist:
                self.app.flist.append(i)
                i = ntpath.basename(i)
                scroll.add_widget(FileItem(text=i))

    def hyde(self, target=None):
        target = self.default_target if target is None else target
        if self.app.flist == []:
            return
        flist = self.app.flist
        key32 = ps.hash(self.app.pas1, self.app.pas2, 1024, 1, 1, 32)
        aes = pa.AESModeOfOperationCTR(key32)
        for child in self.scr.ids.filelist.children:
            child.children[1].disabled = True
        for item in flist:
            children = self.scr.ids.filelist.children
            i = ntpath.basename(item)
            for child in children:
                fin = open(item, 'rb')
                fout = open(op.join(target, i), 'wb')
                pa.encrypt_stream(aes, fin, fout)
                fin.close()
                fout.close()
                if i in child.children[0].text:
                    self.scr.ids.filelist.remove_widget(child)
                    self.app.flist.remove(item)
        if self.app.flist != []:
            if target == op.join(self.path, '/transform/dr/'):
                self.scr.hyde(self.scr.unlock)
            else:
                self.scr.hyde(self.scr.unlock, target)
        else:
            self.scr.unlock.disabled = False
            if self.upl_screens == []:
                for i, screen in enumerate(self.scr.parent.screen_names):
                    if screen == 'uploader':
                        self.upl_screens.append(i)
                        Clock.schedule_once(partial(self.update, i))
                    elif screen == 'viewer':
                        Clock.schedule_once(partial(self.update, i))
                        self.upl_screens.append(i)
            else:
                p1 = partial(self.update, self.upl_screens[0])
                p2 = partial(self.update, self.upl_screens[1])
                Clock.schedule_once(p1)
                Clock.schedule_once(p2)

    def update(self, i, *args):
        self.scr.parent.screens[i].ids.laboratory._update_files()
        self.scr.parent.screens[i].ids.machine._update_files()


class Uploader(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.path = self.app.path
        super(Uploader, self).__init__(**kw)
        Clock.schedule_interval(self.checkpath, 1)
        way = Way(self)
        self.add = way.add
        self._hyde = way.hyde

    def checkpath(self, t):
        if op.exists(self.path+'/transform/dr'):
            self.ids.laboratory.rootpath = self.path+'/transform/dr'
            Clock.unschedule(self.checkpath)

    def hyde(self, button):
        button.disabled = True
        self.unlock = button
        Thread(target=self._hyde).start()


class Viewer(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.path = self.app.path
        self.driveltrs = []
        self.phase = 1
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
                self.ids.drives.add_widget(d)
            self.ids.machine.rootpath = self.driveltrs[0]
        else:
            self.ids.drives.height = 0

    def changerootpath(self, path, *args):
        self.ids.machine.rootpath = path

    def hyde(self, button, target):
        button.disabled = True
        self.unlock = button
        if type(target) != type(''):
            target = target[0].encode('utf-8')
        Thread(target=self._hyde(target)).start()


class Exporter(Screen):
    pass


class NewPass(Screen):
    pass


class FileItem(BoxLayout):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.text = kw['text']
        super(FileItem, self).__init__(**kw)

    def rm(self):
        for item in self.app.flist:
            if self.text in item:
                self.app.flist.remove(item)


class Root(ScreenManager):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.path = self.app.path
        super(Root, self).__init__(**kw)
        if op.exists(self.path+'/._'):
            self.current = 'home'


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
