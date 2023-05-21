#!/usr/bin/python
import flapgui as fl
fl.verbose= True
from random import randint as rng
import tkinter as tk
from tkinter import ttk
import re
import math
import sys
import types
import io
import ast

global pi, e
pi = math.pi
e=math.e

#fl.verbose = True
def getTextColor(accentColor):
    # Convert HTML color value to RGB components
    accentColor = accentColor.lstrip('#')
    r = int(accentColor[0:2], 16)
    g = int(accentColor[2:4], 16)
    b = int(accentColor[4:6], 16)

    # Calculate relative luminance of the accent color
    accentLuminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    # Calculate contrast ratio with black and white
    contrastRatioBlack = (accentLuminance + 0.05) / 0.05
    contrastRatioWhite = (1.05) / (accentLuminance + 0.05)

    # Choose text color based on contrast ratio
    if contrastRatioBlack >= 4.5:
        return 'black'
    elif contrastRatioWhite >= 4.5:
        return 'white'
    else:
        # Return default text color (black) if no suitable option found
        return 'black'

def hasSubWindow(root, title=None):
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel) and (title is None or window.title() == title):
            return True
    return False
def destroySubWindows(root, title=None):
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel) and (title is None or window.title() == title):
            window.destroy()
class Redirect:
    def __init__(self, widget):
        self.widget = widget
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.widget.config(state="normal")  # Enable modification initially

    def write(self, text):
        self.widget.insert("end", text)
        self.widget.see("end")  # Scroll to the end of the widget

    def lock_widget(self):
        self.widget.config(state="disabled")  # Disable modification

    def unlock_widget(self):
        self.widget.config(state="normal")  # Enable modification

    def redirect_streams(self):
        sys.stdout = self
        sys.stderr = self

    def restore_streams(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def __del__(self):
        self.restore_streams()  # Restore the original streams when the object is deleted
def insertText(root, text):
    # Check if the root widget is a text widget
    if not isinstance(root, tk.Text):
        raise ValueError("The 'root' parameter must be a tkinter.Text widget.")

    # Get the current position of the text cursor
    cursor_pos = root.index(tk.INSERT)

    # Insert the text at the cursor position
    root.insert(cursor_pos, text)        
def lockWindowSize(root):
    root.resizable(0, 0)
def unlockWindowSize(root):
    root.resizable(1, 1)
def close_parentheses(s):
    # count number of open and close parentheses
    open_parens = s.count('(')
    close_parens = s.count(')')
    
    # add the necessary closing parentheses
    if open_parens > close_parens:
        s += ')' * (open_parens - close_parens)
    
    return s
def roundDP(x, y):
    try:
        x = float(x)
        power = 10 ** y
        rounded = round(x * power) / power
        return rounded
    except ValueError:
        raise ValueError("Invalid input: x must be a numeric value")
from math import log10, floor
def roundSFBase(x, sig=2):
    return round(float(x), sig-int(floor(log10(abs(x))))-1)
def roundSF(self,x):
    y = float(fl.getText(self.display))
    fl.setText(self.display, roundSFBase(y,x))
def roundInt(num):
    return round(num,2)
def Sin(degrees):
    radians = math.radians(degrees)
    return math.sin(radians)

def Cos(degrees):
    radians = math.radians(degrees)
    return math.cos(radians)

def Tan(degrees):
    radians = math.radians(degrees)
    return math.tan(radians)
def doCalc(self):
    if fl.verbose:
        print(f"PreRegexText: \"{fl.getText(self.display)}\"")
    zx = fl.getText(self.display)
    if zx in ["SyntaxError","TypeError","NameError","Error","Exception"]:
        return ""
    s = re.sub(r'[^\d\s+\-*^/.()sintacoqrpxmd%v=]{}+', '', fl.getText(self.display), flags=re.I)
    s=s.replace(" ","")
    s=s.replace("_","")
    try:
        s=close_parentheses(s)
    except Exception as e:
        print("Failed to parse parentheses:",e)
    s=s.replace("^","**")
    s=s.replace("x","*")
    s=s.replace("%","/100")
    s=s.replace("Int(","int(")
    s=s.replace("sqrt(","math.sqrt(")
    if s == "":
        return ""
    if fl.verbose:
        print("PostRegexText:",s)
    try:
        s=eval(s)
        if s == self:
            raise TypeError("Cannot evaluate self")
        if isinstance(s,TypeError):
            return ""
    except Exception as e:
        s=e
    if type(s) in [type(__import__),type,type(Tan),type(fl),types.FrameType,types.ModuleType,io.IOBase,type(Application)]:
        return TypeError(f"Invalid type returned: {type(s).__name__}")
    return s
def createButton(self,text,x,y):
    fl.addGridButton(self.grid,text,lambda:self.button_click(text),x,y,3,2)
class Application:
    def __init__(self):
        self.root=fl.window("zCalc :: Scientific Calculator")
        lockWindowSize(self.root)
        self.result = 0
        self.xbg, self.xfg = self.loadTheme()
        self.mem = self.loadMem()
        self.menu = fl.menuBar(self.root)
        self.fileMenu = fl.addCascade(self.menu,"File")
        self.editMenu = fl.addCascade(self.menu,"Edit")
        self.viewMenu = fl.addCascade(self.menu,"View")
        self.themeMenu = fl.addCascade(self.viewMenu,"Theme")
        self.numMenu = fl.addCascade(self.menu,"Number")
        #self.winmenu = fl.addCascade(self.menu,"Window")
        self.helpMenu = fl.addCascade(self.menu,"Help")
        self.ansHistory=tk.StringVar()

        fl.addCommand(self.fileMenu,"Exit",self.root.destroy,"Ctrl+Q")
        fl.addCommand(self.editMenu,"Clear Display",lambda:self.button_click("C"),"Esc")
        fl.addCommand(self.editMenu,"Add Commas",self.commate,"Ctrl+D")
        fl.addCommand(self.editMenu,"Remove Commas",self.commate,"Ctrl+Shift+D")
        fl.addCommand(self.helpMenu,"About zCalc",self.about,"F1")
        fl.addCommand(self.helpMenu,"Manual",self.manual,"Ctrl+H")
        fl.addCommand(self.viewMenu,"Fix Scale",lambda:fl.autoScaleResolution(self.root))

        self.pThemes=fl.addCascade(self.themeMenu,"Plain")
        self.cThemes=fl.addCascade(self.themeMenu,"Colourful")
        self.dThemes=fl.addCascade(self.themeMenu,"Dark")
        fl.addCommand(self.themeMenu,"Default",lambda:self.changeTheme("#d9d9d9","black"))
        fl.addCommand(self.themeMenu,"Custom...",self.pickTheme,"Ctrl+Z")
        self.textCol=fl.addCascade(self.themeMenu,"Text Colour")
        fl.addCommand(self.textCol,"White",lambda:self.changeTheme(self.xbg,"white"))
        fl.addCommand(self.textCol,"Black",lambda:self.changeTheme(self.xbg,"black"))
        fl.keyBind(self.root,"<Control-z>",self.pickTheme)
        fl.addCommand(self.pThemes,"Dark",lambda:self.changeTheme("#1e1e1e","white"))
        fl.addCommand(self.pThemes,"Light",lambda:self.changeTheme("#e1e1e1","black"))
        fl.addCommand(self.pThemes,"Black",lambda:self.changeTheme("black","white"))
        fl.addCommand(self.pThemes,"White",lambda:self.changeTheme("white","black"))
        fl.addCommand(self.dThemes,"Sea Blue",lambda:self.changeTheme("#008080","white"))
        fl.addCommand(self.cThemes,"Green",lambda:self.changeTheme("#008000","white"))
        fl.addCommand(self.dThemes,"Mustard",lambda:self.changeTheme("#808000","white"))
        fl.addCommand(self.dThemes,"Red",lambda:self.changeTheme("#800000","white"))
        fl.addCommand(self.cThemes,"Light Pink",lambda:self.changeTheme("plum","black"))
        fl.addCommand(self.cThemes,"Olive",lambda:self.changeTheme("#aceca1","black"))
        fl.addCommand(self.cThemes,"Purple",lambda:self.changeTheme("#731DD8","white"))
        fl.addCommand(self.cThemes,"Emerald Green",lambda:self.changeTheme("#23CE6B","black"))
        fl.addCommand(self.cThemes,"Orange",lambda:self.changeTheme("#FFE347","black"))
        fl.addCommand(self.dThemes,"Space Grey",lambda:self.changeTheme("#383B53","white"))
        fl.addCommand(self.cThemes,"Red",lambda:self.changeTheme("#9E2A2B","white"))
        
        self.rndSF=fl.addCascade(self.numMenu,"Significant Figures")
        self.rndDP=fl.addCascade(self.numMenu,"Decimal Places")
        fl.addCommand(self.rndDP,"1",lambda:fl.setText(self.display,roundDP(fl.getText(self.display),1)))
        fl.addCommand(self.rndDP,"2",lambda:fl.setText(self.display,roundDP(fl.getText(self.display),2)))
        fl.addCommand(self.rndDP,"3",lambda:fl.setText(self.display,roundDP(fl.getText(self.display),3)))
        fl.addCommand(self.rndDP,"4",lambda:fl.setText(self.display,roundDP(fl.getText(self.display),4)))
        fl.addCommand(self.rndDP,"5",lambda:fl.setText(self.display,roundDP(fl.getText(self.display),5)))
        fl.addCommand(self.rndSF,"1",lambda:roundSF(self,1))
        fl.addCommand(self.rndSF,"2",lambda:roundSF(self,2))
        fl.addCommand(self.rndSF,"3",lambda:roundSF(self,3))
        fl.addCommand(self.rndSF,"4",lambda:roundSF(self,4))
        fl.addCommand(self.rndSF,"5",lambda:roundSF(self,5))
        fl.addCommand(self.viewMenu,"Console",self.console)
        
        self.display = fl.textEntry(41,1)
        self.display.pack()
        self.grid = fl.createGrid(self.root)
        createButton(self,"9",0,0)
        createButton(self,7,0,0)
        createButton(self,8,0,1)
        createButton(self,9,0,2)
        createButton(self,"/",0,3)
        createButton(self,"Sin(",0,4)
        createButton(self,"MS",0,5)
        createButton(self,"4",1,0)
        createButton(self,"5",1,1)
        createButton(self,"6",1,2)
        createButton(self,"*",1,3)
        createButton(self,"Cos(",1,4)
        createButton(self,"M",1,5)
        createButton(self,"1",2,0)
        createButton(self,"2",2,1)
        createButton(self,"3",2,2)
        createButton(self,"-",2,3)
        createButton(self,"Tan(",2,4)
        createButton(self,"MC",2,5)
        createButton(self,"0",3,0)
        createButton(self,".",3,1)
        createButton(self,"C",3,2)
        createButton(self,"+",3,3)
        createButton(self,"(",3,4)
        createButton(self,")",3,5)
        createButton(self,"Rnd",4,0)
        createButton(self,"=",4,1)
        createButton(self,"Ans",4,2)
        createButton(self,"^",4,3)
        createButton(self,"Rand",4,4)
        createButton(self,"sqrt(",4,5)
        createButton(self,"!",5,0)
        createButton(self,"Pi",5,1)
        createButton(self,"e",5,2)
        createButton(self,"*10^",5,3)
        createButton(self,"Int",5,4)
        createButton(self,"Flt",5,5)
        #createButton(self,"%",6,0)
        
        fl.keyBind(self.root,"<Escape>",lambda event:self.button_click("C"))
        fl.keyBind(self.root,"<Return>",lambda event:self.button_click("="))
        fl.keyBind(self.root,"<Control-q>",lambda event:self.root.destroy())
        fl.keyBind(self.root,"<F1>",self.about)
        fl.keyBind(self.root,"<Control-h>",self.manual)
        fl.keyBind(self.root,"<Control-d>",self.commate)
        fl.keyBind(self.root,"<Control-D>",self.uncommate)
        
        fl.autoScaleResolution(self.root)
        fl.changeAccentColor(self.root,self.xbg,self.xfg)
    def saveTheme(self):
        import pickle
        with open("currentTheme.pkl","wb") as f:
            pickle.dump([self.xbg,self.xfg],f)
    def loadTheme(self):
        import pickle
        try:
            with open("currentTheme.pkl","rb") as f:
                x=pickle.load(f)
                print("Loaded Theme:",x)
                return x[0],x[1]
        except Exception as e:
            print(e)
            return "#d9d9d9","black"
    def saveMem(self,event=None):
        import pickle
        with open("memory.pkl","wb") as f:
            pickle.dump(self.mem,f)
    def loadMem(self,event=None):
        import pickle
        try:
            with open("memory.pkl","rb") as f:
                try:
                    x = int(pickle.load(f))
                except:
                    x =  float(pickle.load(f))
                finally:
                    print(f"Loaded Memory: {x}")
                    return x
        except:
            return 0
    def commate(self,event=None):
        try:
            x=fl.getText(self.display)
            try:
                x='{:,}'.format(int(x))
            except:
                x='{:,}'.format(float(x))
            fl.setText(self.display,x)
        except:
            print(f"Failed to commate text: \"{fl.getText(self.display)}\"")
    def uncommate(self,event=None):
        x=fl.getText(self.display)
        fl.setText(self.display,x.replace(",",""))
    def cmd_help(self,root,event=None):
        r=fl.subWindow(root,"Console Help")
        text = [
            "Console allows you to see the contents of the console,",
            "including errors.",
            "It is useful for examining what the program is doing.",
            "The Console cannot be closed to avoid errors.",
            "To close the console, close zCalc.",
            ]
        text = "\n".join(text)
        fl.addText(r,text)
        fl.createButton(r,"OK",r.destroy)
        fl.keyBind(r,"<Return>",lambda event:r.destroy())
        fl.autoScaleResolution(r)
    def raiseError(self,error,event=None):
        raise error
    def console(self,event=None):
        class DebugError(Exception):
            pass
        if not hasSubWindow(self.root,"Console Output"):
            print("--------------------")
            print("CONSOLE ENABLED")
            print("--------------------")
            print("From this point onwards, the zCalc console handles stdout and stderr requests.")
            print("You will no longer see any output here.")
            print("--------------------")
            w=fl.subWindow(self.root,"Console Output",750,500)
            m = fl.menuBar(w)
            c = fl.addCascade(m,"Menu")
            d = fl.addCascade(m,"Debug")
            t=fl.framedTextEntry(w,100,self.xbg,self.xfg)
            t.pack()
            fl.makeUnclosable(w)
            t=Redirect(t)
            fl.addCommand(c,"Clear Terminal",lambda:fl.setText(t.widget,""))
            fl.addCommand(c,"Help",lambda:self.cmd_help(w))
            fl.addCommand(d,"Raise Error",lambda: self.raiseError(DebugError("TEST ERROR")))
            sys.stdout=t
            sys.stderr = t
            lockWindowSize(w)
            print("zCalc Console:")
            print("This is the console. When you interact with something, you should see an output here.")
        else:
            class ConsoleError(Exception):
                pass
            raise ConsoleError("A Console instance is already running. You cannot open more than one Console instance.")
    def about(self,event=None):
        about = [
            "zCalc 2.0",
            "(c) 2023 WinFan3672, some rights reserved.",
            "Made with FlapGUI 0.4.\n",
            "Build Date: 21 May 2023",
            ]
        about = "\n".join(about)
        root=fl.subWindow(self.root,"About zCalc")
        fl.addText(root,about)
        fl.createButton(root,"OK",root.destroy)
        fl.keyBind(root,"<Return>",lambda event:root.destroy())
        fl.autoScaleResolution(root)
    def changeTheme(self,bg,fg=None):
        print(f"Changed theme to {[bg,fg]}")
        self.xbg = bg
        if fg:
            self.xfg = fg
        fl.changeAccentColor(self.root,bg,fg)
        self.saveTheme()
    def manual(self, event=None):
        x=""
        manual = [
            "--------------------",
            "zCalc Manual",
            "--------------------",
            "zCalc is a scientific calculator for performing mathematical operations with numbers.",
            "Its creator and maintainer is WinFan3672, who created the calculator as well as",
            "the GUI library that it runs on known as Flap.",
            "--------------------",
            "Table of Contents",
            "--------------------",
            "1 Introduction",
            "1.1 What zCalc Is",
            "1.2 What zCalc Isn't",
            "1.3 What's New In Version 2.0\n",
            "2 Using zCalc",
            "2.1 Entering Mathemetical Equations",
            "2.2 Special Buttons",
            "2.3 Memory",
            "2.4 Answer Manipulation",
            "2.5 Sin/Cos/Tan Functions\n",
            "3 General",
            "3.1 Keyboard Shortcuts",
            "3.2 Scripts",
            "4 End of manual",
            "--------------------",
            "1 Introduction",
            "1.1 What zCalc Is",
            "--------------------",
            "zCalc is a scientific calculator. Scientific calculators are designed for performing arithmetic operations on numbers.",
            "zCalc has several functions that allow the user to quickly play with numbers.",
            "It is intended to be used by mathematicians as well as everyday people.",
            "--------------------",
            "1.2 What zCalc Isn't",
            "--------------------",
            "zCalc may be a lot of things, but it it NOT:",
            "[-] A CAS [Computerised Algebra System]",
            "   In other words, it cannot perform operations using algebra.",
            "[-] A Programming Calculator",
            "   It will not convert numbers into other number systems",
            "[-] A unit converter",
            "   You can't convert grams to kilograms with it without knowing the formula.",
            "[-] A graphing calculator",
            "   You will not be able to represent graphs such as y = 2x :(",
            "[-] A toy",
            "   Do not try to put it in your mouth. It will end badly.",
            "--------------------",
            "1.3 What's New In Version 2.0",
            "--------------------",
            "Version 2.0 adds a lot of new features, and makes it better to use.",
            "It is a complete rewrite, hence the 2.0 name.",
            "Main changes:",
            "[-] More compact UI",
            "   This makes it smaller and faster to use, since your hand travels less",
            "[-] Added menu bar",
            "   This lets you access things that were once delegated to buttons.",
            "--------------------",
            "2 Using zCalc",
            "2.1 Entering Mathematical Equations",
            "--------------------",
            "Entering maths equations is simple.",
            "Either type it out using your keyboard or use the buttons to type.",
            "--------------------",
            "2.2 Theming",
            "--------------------",
            "You can change the colour of the entire UI in zCalc.",
            "There are 16 built-in themes to choose from, as well as a custom theme picker.",
            "2.2.1 Picking a Built-In Theme",
            "Go to View > Theme, and you should see 3 categories: Plain, Colourful, and Dark.",
            "Each category contains a theme you can apply.",
            "2.2.2 Custom Themes",
            "To choose a custom accent colour, go to View > Theme > Custom. A colour picker will allow you to add RGB or HTML colour codes.",
            "If the menu and button colours don't match up, you can go to View > Theme > Text Colour to correct it.",
            "--------------------",
            "2.3 Memory",
            "--------------------",
            "There are several functions one can perform using the Memory buttons.",
            "MS: Sets the memory to the contents of the display",
            "M: Sets the display to the contents of the memory",
            "MC: Sets the memory contents to 0",
            "--------------------",
            "2.4 Answer Manipulation",
            "--------------------",
            "There are several functions and buttons that let you manipulate numbers.",
            "The Int and Flt convert the display contents to integers and decimal numbers respectively.",
            "The Rnd button rounds the display contents to 2 decimal places.",
            "The Number menu contains options for rounding to decimal places or significant figures, from 1 to 5.",
            "The ! button performs a factorial operation on the display contents.",
            "--------------------",
            "2.5 Sin/Cos/Tan",
            "--------------------",
            "The Sin(, Cos(, and Tan( buttons add the text to the display, which lets you use those functions on numbers.",
            "Currently, there is no method to switch from Degrees to Radians or Gradians.",
            "--------------------",
            "3 General",
            "--------------------",
            "This section details some general guidance on operating zCalc.",
            "--------------------",
            "3.1 Keyboard Shortcuts",
            "--------------------",
            "Escape: Clear Display",
            "Enter: Press =",
            "Ctrl+D: Insert commas into numbers",
            "Ctrl+Shift+D: Remove commas from numbers",
            "Ctrl+Z: Change accent colour",
            "F1: Launch About menu",
            "Ctrl+H: Launch Manual",
            "Ctrl+Q: Exit",
            "--------------------",
            "3.2 Scripts",
            "--------------------",
            "Scripts have not been implemented yet, but will be soon.",
            "--------------------",
            "3.3 Contact WinFan3672",
            "--------------------",
            "Discord: WinFan3672#8705",
            "Email: winfan3672@gmail.com",
            "GitHub: WinFan3672",
            "--------------------",
            "4 End of Manual",
            "--------------------",
            "This is the end of the zCalc 2 manual.",
            ]
        m=[]
        for item in manual:
            m.append(item+"\n")
        for item in manual:
            if len(item) >= len(x):
                x=item
        manual = "".join(m)
        w=fl.subWindow(self.root,"zCalc Manual [Revision 0001]")
        fl.keyBind(w,"<Control-q>",lambda event:w.destroy())
        t=fl.framedTextEntry(w,100,self.xbg,self.xfg)
        fl.setText(t,manual)
        fl.lockText(t)
        fl.autoScaleResolution(w)
    def pickTheme(self,event=None):
        self.xbg = (fl.colorChoose())
        self.changeTheme(self.xbg,getTextColor(self.xbg))
    def switchTextColour(self,event=None):
        self.xfg = "black" if self.xfg == "white" else "black"
        self.changeTheme(self.xbg,self.xfg)
    def button_click(self,text):
        text = str(text)
        text=text.replace("Rand",str(rng(1,1000000)))
        if text == "C":
            if fl.verbose:
                print("Cleared Calculator Display")
            fl.setText(self.display,"")
        elif text == "M":
            fl.setText(self.display,self.mem)
        elif text == "MC":
            self.mem = 0
        elif text == "MS":
            self.mem = fl.getText(self.display)
            self.saveMem()
        elif text == "Rnd":
            try:
                fl.setText(self.display,roundInt(float(fl.getText(self.display))))
            except Exception as e:
                print(f"RoundingError: {e}")
        elif text == "Ans":
            fl.setText(self.display,self.result)
        elif text == "e":
            insertText(self.display,str(math.e))
        elif text == "Pi":
            insertText(self.display,str(math.pi))
        elif text == "Int":
            try:
                x = int(float(fl.getText(self.display)))
            except Exception as e:
                x = fl.getText(self.display)
                raise e
            finally:
                fl.setText(self.display,x)
        elif text == "Flt":
            try:
                x = float(fl.getText(self.display))
            except Exception as e:
                x = fl.getText(self.display)
                raise e
            finally:
                fl.setText(self.display,x)
        elif text == "!":
            try:
                from math import factorial
                fl.setText(self.display,factorial(int(fl.getText(self.display))))
            except Exception as e:
                print(e)
        elif text == "=":
            x=doCalc(self)
            if isinstance(x,Exception):
                fl.setText(self.display,f"{type(x).__name__}")
                raise x
            else:
                fl.setText(self.display,x)
                self.result = x
                self.ansHistory.set(self.ansHistory.get()+f"{self.result}\n")
        else:
            insertText(self.display,text)
Application().root.mainloop()
