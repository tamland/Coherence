# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# Copyright 2008, Frank Scholz <coherence@beebits.net>

import pygtk
pygtk.require("2.0")
import gtk

from coherence.ui.av_widgets import TreeWidget
from coherence.ui.av_widgets import UPNP_CLASS_COLUMN,SERVICE_COLUMN


import totem

class UPnPClient(totem.Plugin):

    def __init__ (self):
        totem.Plugin.__init__(self)
        self.ui = TreeWidget()
        self.ui.cb_item_right_click = self.button_pressed
        self.ui.window.show_all()
        self.create_item_context()
        selection = self.ui.treeview.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)

    def button_pressed(self, widget, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            try:
                row_path,column,_,_ = self.ui.treeview.get_path_at_pos(x, y)
                selection = self.ui.treeview.get_selection()
                if not selection.path_is_selected(row_path):
                    self.ui.treeview.set_cursor(row_path,column,False)
                iter = self.ui.store.get_iter(row_path)
                upnp_class,url = self.ui.store.get(iter,UPNP_CLASS_COLUMN,SERVICE_COLUMN)
                if(not upnp_class.startswith('object.container') and
                   not upnp_class == 'root'):
                    self.context.popup(None,None,None,event.button,event.time)
                    return 1
            except TypeError:
                pass
            return 1

    def create_item_context(self):
        """ create context menu for right click in treeview item"""

        def action(menu, text):
            selection = self.ui.treeview.get_selection()
            model, selected_rows = selection.get_selected_rows()
            if(len(selected_rows) > 0 and
               text ==' item.play'):
                row_path = selected_rows.pop(0)
                iter = self.ui.store.get_iter(row_path)
                url, = self.ui.store.get(iter,SERVICE_COLUMN)
                self.totem_object.action_remote(totem.REMOTE_COMMAND_REPLACE,url)
                self.totem_object.action_remote(totem.REMOTE_COMMAND_PLAY,url)
            for row_path in selected_rows:
                iter = self.ui.store.get_iter(row_path)
                url, = self.ui.store.get(iter,SERVICE_COLUMN)
                self.totem_object.action_remote(totem.REMOTE_COMMAND_ENQUEUE,url)
                self.totem_object.action_remote(totem.REMOTE_COMMAND_PLAY,url)

        self.context = gtk.Menu()
        play_menu = gtk.MenuItem("Play")
        play_menu.connect("activate", action, 'item.play')
        enqueue_menu = gtk.MenuItem("Enqueue")
        enqueue_menu.connect("activate", action, 'item.enqueue')
        self.context.append(play_menu)
        self.context.append(enqueue_menu)
        self.context.show_all()

    def activate (self, totem_object):
        totem_object.add_sidebar_page ("upnp-coherence", _("Coherence DLNA/UPnP Client"), self.ui.window)
        self.totem_object = totem_object

        def load_and_play(url):
            totem_object.action_remote(totem.REMOTE_COMMAND_REPLACE,url)
            totem_object.action_remote(totem.REMOTE_COMMAND_PLAY,url)

        self.ui.cb_item_dbl_click = load_and_play

    def deactivate (self, totem_object):
        totem_object.remove_sidebar_page ("upnp-coherence")