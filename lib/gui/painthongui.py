#!/usr/bin/python
 
# Import packages
import pygtk
pygtk.require("2.0")
import gtk
import gettext
import math
import cairo
import os
import sys

from lib.misc.hsvgenerator import HSVGenerator
from lib.graphics.colorcell import ColorCell
from lib.graphics.fancycanvas import FancyCanvas
from lib.graphics.rgbacolor import RGBAColor
from lib.io.generic import ImageFile

_ = gettext.gettext
 
class GUI():
   PAINTHON = None

   def __init__(self, painthon):
      self.PAINTHON = painthon

      builder = gtk.Builder()
      builder.add_from_file(os.path.join(os.path.dirname( os.path.realpath( __file__ ) ) + os.sep + "painthon.xml"))

      # Get the window properly
      self.window = builder.get_object("main-window")

      # Initialize canvas
      viewport = builder.get_object("viewport-for-canvas")
      viewport.add(self.PAINTHON.get_canvas())

      # Set the first tool to use...
      # TODO: select the proper default tool
      #current_tool = "btn-tool-free-select"
      current_tool = "btn-tool-draw-rectangle"
      self.active_tool_button = None
      builder.get_object(current_tool).set_active(True)
      self.change_tool_gui(builder.get_object(current_tool))

      # Get the toolbar and set it not to show text
      self.toolbar = builder.get_object("toolbar")
      self.toolbar.set_style(gtk.TOOLBAR_ICONS)

      # Initialize palette
      self.__init_colors(builder.get_object("colors-grid"))

      # Initialize working colors
      self.primary = ColorCell(0, 0, 0)
      self.primary.enable_scroll_to_modify_alpha()
      self.primary.connect("color-changed-event", self.color_changed)
      primary_frame = builder.get_object("primary-color")
      primary_frame.add(self.primary)
      self.secondary = ColorCell(1, 1, 1)
      self.secondary.enable_scroll_to_modify_alpha()
      self.secondary.connect("color-changed-event", self.color_changed)
      secondary_frame = builder.get_object("secondary-color")
      secondary_frame.add(self.secondary)

      # Fix alpha sliders
      a1 = builder.get_object("primary-color-alpha")
      a1.set_value(a1.get_value())
      self.MAX_ALPHA_1 = a1.get_value()
      a2 = builder.get_object("secondary-color-alpha")
      a2.set_value(a2.get_value())
      self.MAX_ALPHA_2 = a2.get_value()

      # Connecting signals properly...
      builder.connect_signals(self)

      # Show the window
      self.window.show_all()


   def __init_colors(self, colorsgrid):
      colors = colorsgrid.get_children()
      rows = colorsgrid.get_property("n-rows")
      columns = colorsgrid.get_property("n-columns")

      # Color[0][0]
      color_frame = colors[0]
      colorcell = ColorCell(0, 0, 0)
      colorcell.connect("color-changed-event", self.color_changed)
      color_frame.add(colorcell)
      # Color[0][1]
      color_frame = colors[columns]
      colorcell = ColorCell(1, 1, 1)
      colorcell.connect("color-changed-event", self.color_changed)
      color_frame.add(colorcell)

      # Color[1][0]
      color_frame = colors[1]
      colorcell = ColorCell(0.33, 0.33, 0.33)
      colorcell.connect("color-changed-event", self.color_changed)
      color_frame.add(colorcell)
      # Color[1][1]
      color_frame = colors[columns + 1]
      colorcell = ColorCell(0.66, 0.66, 0.66)
      colorcell.connect("color-changed-event", self.color_changed)
      color_frame.add(colorcell)

      hsv = HSVGenerator()

      # The other colors
      for i in range(rows):
         for j in range(2, columns):
            # Each cell is: frame{ eventbox{label} }
            color_frame = colors[i*columns + j]
            color = hsv.get_hsv_color(360*(j-2)/(columns-2), 1.0-0.7*i, 1.0)
            colorcell = ColorCell()
            colorcell.connect("color-changed-event", self.color_changed)
            colorcell.set_color(RGBAColor.create_from_gtk_color(color))
            color_frame.add(colorcell)


   def quit(self, window):
      self.PAINTHON.quit(self.window)


   def color_changed(self, widget, event):
      c = widget.get_color()
      if event.button == 1:
         c.set_alpha(self.PAINTHON.get_primary_color().get_alpha())
         self.PAINTHON.set_primary_color(c)
         self.primary.set_color(c)
      elif event.button == 3:
         c.set_alpha(self.PAINTHON.get_secondary_color().get_alpha())
         self.PAINTHON.set_secondary_color(c)
         self.secondary.set_color(c)


   def change_tool_gui(self, newtool):
      if newtool.get_active():
          prevtool = self.active_tool_button
          if newtool != prevtool:
              self.active_tool_button = newtool
              if prevtool != None:
                 prevtool.set_active(False)
              self.PAINTHON.change_tool(gtk.Buildable.get_name(newtool).replace("btn-tool-", ""))


   def change_primary_alpha(self, slider):
      c = self.PAINTHON.get_primary_color()
      value = slider.get_value()/self.MAX_ALPHA_1
      c.set_alpha(value)
      self.PAINTHON.set_primary_color(c)
      self.primary.set_color(c)


   def change_secondary_alpha(self, slider):
      c = self.PAINTHON.get_secondary_color()
      value = slider.get_value()/self.MAX_ALPHA_2
      c.set_alpha(value)
      self.PAINTHON.set_secondary_color(c)
      self.secondary.set_color(c)


   def new(self, widget):
      self.PAINTHON.new()


   def open(self, widget):
      self.PAINTHON.open()


   def save(self, widget):
      self.PAINTHON.save()


   def save_as(self, widget):
      self.PAINTHON.save_as()


   def cut(self, widget):
      self.PAINTHON.cut()


   def copy(self, widget):
      self.PAINTHON.copy()


   def paste(self, widget):
      self.PAINTHON.paste()


   def redo(self, widget):
      self.PAINTHON.redo()


   def undo(self, widget):
      self.PAINTHON.undo()
