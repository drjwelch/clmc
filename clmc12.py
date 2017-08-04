# CLMC v5
# (C) Dr J Welch jasonwelch@email.com
#
# Free to use in UK state-funded schools as part of CS teaching, except where forbidden below
# Modifications:
# -copy of modified version to be sent to author at above address
# -must include my (C) notice in full view in the GUI, as now
# -must share source in public, open forum
# -must maintain 'free for UK schools' licence as above
#
# Permission is not granted for use in any scenario where a charge is made even if not-for-profit
# Please seek author's permission for any use where money changes hands, directly or indirectly
#
#
# v.12 added auto select of extIS for .lmcx and ability to use comments in source
#

import tkinter as TK
import tkinter.filedialog as TKFD
import tkinter.messagebox as TKMB
import tkinter.simpledialog as TKSD
import tkinter.scrolledtext as TKST

from time import sleep

class CLMC:
    PC = 'PC'
    XREG = 'INDEX(X)'
    MAR = 'MAR'
    MDR = 'MDR'
    CIR = 'CIR'
    ACTIVITY = 'ACTIVITY'
    ACCUMULATOR = 'ACC'
    CU_LABEL = 'CU LABEL'
    SCREEN = 'SCREEN'
    LOADMSG = 'Load LMC source code'
    SAVEMSG = 'Save LMC source code'
    FILETYPES = [('LMC assembly language files','*.lmc?'),
                 ('LMC assembly language files (extended)','*.lmcx'),
                 ('All files','*.*')]
    FILE_STD = '.lmc'
    FILE_EXT = '.lmcx'
    
#
#   Assembly language class - contains MNEMONICS 'global' constant
#

class AssemblyLanguage:
    
    # All mnemonics, opcodes, implied operands and extended flag
    # implied -1 means implied addressing not allowed
    # implied 0 ensures mcode for hlt is 0 - dat handled separately

    MNEMONICS = { "hlt": (0,0,0), "cob": (0,0,0), "dat": (0,0,0),
                  "add": (1,-1,0),
                  "sub": (2,-1,0),
                  "sta": (3,-1,0),
                  "lda": (5,-1,0),
                  "bra": (6,-1,0), "brz": (7,-1,0), "brp": (8,-1,0),
                  "inp": (9,1,0), "out": (9,2,0),
                  "ldx": (4,-1,1), "txa": (9,3,1), "tax": (9,4,1),
                  "inx": (9,5,1), "dex": (9,6,1),
                  "lsl": (9,7,1), "lsr": (9,8,1),
                  "eor": (9,9,1), "and": (9,10,1), "orr": (9,11,1),
                  "mvn": (9,12,1) }


class SourceError:

    ERROR_CODE = 'error!' # keep lowercase
    
########################################################################
#
# GUI object
#
########################################################################

class GUI(TK.Tk):
    def __init__(self,app,*args,**kwargs):
        TK.Tk.__init__(self, *args, **kwargs) # makes 'self' the root TK window
        self.app = app
        self.wm_title('CLMC v5')
        self.geometry('1265x620')
        self.header = Header(app, self)
        self.source = SourceCodeBox(app, self)
        self.buttons = CommandButtons(app, self)
        self.ram = RAMBox(app, self)
        self.registers = Registers(app, self)
        self.header.pack(side=TK.TOP,fill=TK.X)
        self.source.pack(side=TK.LEFT,fill=TK.Y)
        self.buttons.pack(side=TK.LEFT,fill=TK.Y)
        self.ram.pack(side=TK.LEFT,fill=TK.Y)
        self.registers.pack(side=TK.LEFT)
        
    def start(self):
        self.mainloop()

# Methods to implement the interface with the application object
#
# Each call to another GUI class e.g. self.ram.set_data occurs only once
# so any change to that structure only affecs one method in this class

    def get_loadfilename(self, default):
        opts = { 'defaultextension':default,'filetypes':CLMC.FILETYPES}
        return str(TKFD.askopenfilename(title=CLMC.LOADMSG,**opts))

    def get_savefilename(self, default):
        opts = { 'defaultextension':default,'filetypes':CLMC.FILETYPES}
        return str(TKFD.asksaveasfilename(title=CLMC.SAVEMSG,**opts))

    def get_source_code(self):
        return self.source.get_data()
    
    def set_source_code(self, value):
        self.source.set_data(value)

    def set_ram(self, address, value):
        self.ram.set_data(address,value)

    def get_ram(self, address):
        return self.ram.get_data(address)

    def clear_ram(self):
        self.ram.clear()
        self.unhighlight_ram(self.get_reg(CLMC.PC))

    def clear_animation(self):
        self.registers.clear_animation()

    def clear_reg(self):
        self.unhighlight_ram(self.get_reg(CLMC.PC))
        self.registers.clear()
        self.highlight_ram(self.get_reg(CLMC.PC),'red')
        self.update_idletasks()

    def draw_registers(self):
        self.registers.draw_registers()
        self.update_idletasks()

    def copyreg_animate(self, frm, to):
        self.registers.copy_animate(frm, to)

    def get_animate_speed(self):
        return self.buttons.get_animate_speed()

    def bus_read_animate(self, address, data):
        self.registers.bus_req_animate(False)
        self.flash_ram(address)
        self.registers.bus_rsp_animate(data) # data is already stringified
        self.update_idletasks()

    def bus_write_animate(self, address):
        self.registers.bus_req_animate(True)
        self.flash_ram(address)
        self.update_idletasks()

    def refresh_ram(self):
        self.ram.refresh()

    def get_reg(self, register):
        return self.registers.get_reg(register)

    def set_reg(self, register, value):
        if register == CLMC.PC:
            self.unhighlight_ram(self.get_reg(CLMC.PC))
        self.registers.set_reg(register, value)
        if register == CLMC.PC:
            self.highlight_ram(self.get_reg(CLMC.PC),'red')
        self.update_idletasks()

    def highlight_ram(self, address, colour):
        self.ram.highlight(address, colour)
        self.update_idletasks()
        
    def unhighlight_ram(self, address):
        self.ram.unhighlight(address)
        self.update_idletasks()
        
    def update_label(self, label, text, label2=None):
        self.registers.update_label(label,text)
        if self.isAnimate():
            self.flash_reg(label,label2)

    def flash_ram(self, address):
        self.ram.flash(address)

    def flash_reg(self, register1, register2=None):
        self.registers.flash(register1, register2)
        
    def isExtIS(self):
        return self.buttons.isExtIS()
    
    def set_extIS(self):
        self.buttons.set_extIS()
        
    def set_stdIS(self):
        self.buttons.set_stdIS()
        
    def lock_extIS(self):
        self.buttons.lock_extIS()
        
    def unlock_extIS(self):
        self.buttons.unlock_extIS()
        
    def lock_hexmode(self):
        self.buttons.lock_hexmode()
        
    def unlock_hexmode(self):
        self.buttons.unlock_hexmode()
        
    def isAnimate(self):
        return self.buttons.isAnimate()
    
    def isHexMode(self):
        return self.buttons.isHexMode()
    
    def msgbox(self, title, message):
        TKMB.showwarning(title, message)
        self.update()
        self.update_idletasks()

    def okaybox(self, title, message):
        result = TKMB.askokcancel(title, message)
        self.update()
        self.update_idletasks()
        return result

    def inputbox(self, title, message):
        result = TKSD.askinteger(title, message)
        self.update()
        self.update_idletasks()
        return result
    
#
# Utility functions - would be static as only for use by other GUI methods
# but actually used in RAM class (and also needed by App to pass correct argument 
# to a GUI interface method)
#

    def valuise(self, data):
        if ' ' in data: # then it's hex
            v = "0123456789ABCDEF".index(data[0])
            v = v*16 + "0123456789ABCDEF".index(data[1])
            v = v*16 + "0123456789ABCDEF".index(data[3])
            v = v*16 + "0123456789ABCDEF".index(data[4])
            return v
        else: # it's decimal
            return int(data)

    def stringify(self, value, places):
        try:
            hexmode = self.isHexMode()
        except AttributeError: # no app setup on initialising call
            hexmode = False
        if hexmode:
            lsb = value % 256
            msb = value // 256
            s = self.hex2(lsb)
            if places == 4:
                s = self.hex2(msb)+' '+s
        else:
            s = str(value)
            if value>=0:
                s = '0'*(places-len(s))+s
        return s

    def hex2(self, byte):
        return "0123456789ABCDEF"[byte//16]+"0123456789ABCDEF"[byte%16]

#
# GUIBox base class for all GUI elements
#

class GUIBox(TK.Frame):
    def __init__(self, app, parent, *args, **kwargs):
        TK.Frame.__init__(self, parent, *args, **kwargs)
        self.app = app
        self.parent = parent
        self.make_widgets()

#
# GUI elements inherit from GUIBox and expose methods to GUI class
# (make_widgets would be static in each)
#

#
#               Header class
#

class Header(GUIBox):
    def make_widgets(self):
        label = TK.Label(self,text="CLMC Simulator", font=('Arial',24,'bold'),bg='black',fg='white')
        copyw = TK.Label(self,text="(c) Dr J Welch", font=('Arial',10),bg='black',fg='white')
        self.img = TK.PhotoImage(file='lmc.gif').subsample(8)
        icon = TK.Label(self,image=self.img,borderwidth=0)
        icon.pack(side=TK.LEFT)
        label.pack(side=TK.LEFT,fill=TK.BOTH,expand=1) # defaults to anchor centre
        copyw.pack(side=TK.LEFT,fill=TK.BOTH)

#
#               Source class
#

class SourceCodeBox(GUIBox):
    def make_widgets(self):
        label = TK.Label(self,text="Source Code",font=('Arial',12,'bold'))
        label.pack(side=TK.TOP,fill=TK.X) # defaults to anchor centre
        #put a text area into this object's frame
        self.textPad=TK.Frame(self)
        self.text=TKST.ScrolledText(self.textPad,height=33,width=28,font=('Courier',11))
##        self.text=TK.Text(self.textPad,height=33,width=28,font=('Courier',11))
##        # add a vertical scroll bar to the text area
##        self.scscroll=TK.Scrollbar(self.textPad)
##        self.text.configure(yscrollcommand=self.scscroll.set)
##        self.textPad.bind("<Configure>", self.onFrameConfigure)
        #pack everything
        self.text.pack(side=TK.LEFT,fill=TK.Y)
        self.textPad.pack(side=TK.TOP,fill=TK.Y)
##        self.scscroll.pack(side=TK.RIGHT,fill=TK.Y)
##    def onFrameConfigure(self,e):
##        w = self.textPad.winfo_width()
##        h = self.textPad.winfo_height()
##        self.c.configure(scrollregion=self.textPad.bbox(TK.ALL),height=h,width=w)
    def get_data(self):
        return self.text.get(1.0,TK.END)
    def clear(self):
        self.text.delete(1.0,TK.END)
    def set_data(self, value):
        self.clear()
        self.text.insert(TK.END,value)
    
#
#               Buttons class
#

class CommandButtons(GUIBox):
    def make_widgets(self):
        actions = ['Assemble','Lint','Load','Save','Clear RAM','Clear All','Reset PC','Step','RUN']
        for i,a in enumerate(actions):
            # lambda closures below
            b = TK.Button(self, text=actions[i], width='11', #characters
                          font = ('Arial',10),
                          command=lambda u=actions[i]: self.app.handle_event(u))
            b.pack(pady=(6+(14 if i==0 else 0),6),padx=6)
        # checkbox options
        self.checkboxes = []
        self.checkboxlabs = ['Extended IS','Hex Mode','Animate FDE']
        self.checkboxvars = [TK.IntVar(),TK.IntVar(),TK.IntVar()]
        for i in range(len(self.checkboxlabs)):
            self.checkboxes.append(TK.Checkbutton(self, text=self.checkboxlabs[i],
                               variable=self.checkboxvars[i],
                               command=lambda u=self.checkboxlabs[i]: self.app.handle_event(u)))
            self.checkboxes[-1].pack(anchor=TK.W,pady=5,padx=5)
        self.speedlabel = TK.Label(self,text="Animation Speed:")
        self.speedlabel.pack(anchor=TK.W,pady=(5,0),padx=5)
        self.speed = TK.Scale(self, from_=1, to=5, orient=TK.HORIZONTAL)
        self.speed.set(3) # set to middle value
        self.speed.pack(anchor=TK.W,pady=(0,5),padx=5)

    def isExtIS(self):
        return self.checkboxvars[0].get()==1
    def isHexMode(self):
        return self.checkboxvars[1].get()==1
    def isAnimate(self):
        return self.checkboxvars[2].get()==1
    def get_animate_speed(self):
        return (self.speed.get()-1)/2+1
    def set_extIS(self):
        self.checkboxes[0].select()
    def set_stdIS(self):
        self.checkboxes[0].deselect()
    def lock_extIS(self):
        self.checkboxes[0].config(state=TK.DISABLED)
    def unlock_extIS(self):
        self.checkboxes[0].config(state=TK.NORMAL)
    def lock_hexmode(self):
        self.checkboxes[1].config(state=TK.DISABLED)
    def unlock_hexmode(self):
        self.checkboxes[1].config(state=TK.NORMAL)

#
#               Registers class
#

class Registers(GUIBox):
    def make_widgets(self):
        # text specs for canvas
        self.thefonts = [('Consolas',14),('Consolas',20)]
        self.regcoords = [(203,383),(203,446),(318,383),(318,446),(437,383),(437,446),
                          (405,487),(360,97),(660,123)]
        # reg names and storage (in stringvars) - better way to come ...
        self.reg_vars = []
        self.reg_names = [CLMC.MAR,CLMC.MDR,CLMC.PC,CLMC.CIR,CLMC.XREG,CLMC.ACTIVITY,
                          CLMC.CU_LABEL,CLMC.ACCUMULATOR,CLMC.SCREEN]
        for i, name in enumerate(self.reg_names):
            self.reg_vars.append(TK.StringVar(value='0'))
        # setup canvas image
        self.img = TK.PhotoImage(file='registers4.gif')
        self.pic = TK.Canvas(self,width=500,height=350)
        self.pic.create_image(0,0,image=self.img,anchor=TK.NW)
        self.pic.pack(side=TK.LEFT,fill=TK.BOTH,expand=True)
        self.bind("<Configure>", self.onFrameConfigure)
        # clear and paint values into registers
        self.clear()

    def clear(self):
        for reg in self.reg_vars:
            reg.set(self.parent.stringify(0,4))
        self.reg_vars[5].set('IDLE')   # idle activity
        self.reg_vars[6].set('IDLE')   # idle CU
        self.reg_vars[8].set('')       # blank screen
        self.draw_registers()

    def clear_animation(self):
        self.pic.delete('anim') # all animations are tagged as 'anim'

    def draw_registers(self):
        self.pic.delete('reg-text') # all reg contets tagged as 'reg-text'
        # create_text text anchor is centre so coords are centres of boxes
        for i, reg in enumerate(self.reg_vars):
            x = self.regcoords[i][0]
            y = self.regcoords[i][1]
            if i<7:
                self.pic.create_text(x,y,text=reg.get(),font=self.thefonts[0], tag='reg-text')
            else:            
                self.pic.create_text(x,y,text=reg.get(),font=self.thefonts[1],fill="#47ff47",anchor=TK.E, tag='reg-text')

    def flash(self, register1, register2):
        flash_pause = 0.5/self.parent.get_animate_speed()
        details1 = self.reg_details(register1)
        if register2:
            details2 = self.reg_details(register2)
        for i in range(5):
            self.highlight_reg(details1)
            if register2: self.highlight_reg(details2)
            self.parent.update_idletasks()
            sleep(flash_pause)
            self.clear_animation()
            self.parent.update_idletasks()
            sleep(flash_pause)

    def highlight_reg(self,details):
        # highlight register
        d1,bb,a1 = details
        self.pic.create_rectangle(d1[1]-bb[0],d1[2]-bb[1],d1[1]+bb[2],d1[2]+bb[3],fill='blue',tag='anim')
        self.pic.create_text(d1[1],d1[2],text=d1[3],fill='white',font=d1[4],anchor=a1, tag='anim')
        self.parent.update_idletasks()

    def reg_details(self, regname):
        regnum = self.reg_names.index(regname)
        startx = self.regcoords[regnum][0]
        starty = self.regcoords[regnum][1]
        regval = self.reg_vars[regnum].get()
        regfnt = self.thefonts[0] if regnum<7 else self.thefonts[1]
        if len(regval)>5:
            bbox = [45,8,45,8]  # large centre box for activity/cu text
        elif regnum>=7:
            bbox = [90,8,0,8]   # large E anchored box for ACC/SCREEN
        else:
            bbox = [25,7,25,7]  # small box for reg->reg or reg<->ram
        anchor = TK.CENTER if regnum<7 else TK.E
        return [[regnum, startx, starty, regval, regfnt],bbox,anchor]

    def bus_req_animate(self, iswrite): # mar (and mdr) copied across bus to ram controller
        if iswrite:
            ddetails = self.reg_details(CLMC.MDR)
        adetails = self.reg_details(CLMC.MAR)
        steps = int(40/self.parent.get_animate_speed())
        move_pause = 0.05/self.parent.get_animate_speed()
        for i in range(steps):
            self.pic.delete('anim')
            if iswrite:
                ddetails[0][1] -= 150/steps
                ddetails[0][2] += 15/steps
                self.highlight_reg(ddetails)
            adetails[0][1] -= 150/steps
            adetails[0][2] += 55/steps
            self.highlight_reg(adetails)
            self.parent.update_idletasks()
            sleep(move_pause)
            
    def bus_rsp_animate(self, valstring): # value copied from ram controller across bus to mdr
        ddetails = self.reg_details(CLMC.MDR)
        steps = int(30/self.parent.get_animate_speed())
        dx = 150/steps
        dy = -15/steps
        # need to start with RAM value and go to MDR, not reverse
        ddetails[0][1] -= 150
        ddetails[0][2] += 15
        ddetails[0][3] = valstring
        move_pause = 0.05/self.parent.get_animate_speed()
        self.highlight_reg(ddetails)
        sleep(move_pause*10)
        for i in range(steps):
            self.pic.delete('anim')
            ddetails[0][1] += dx
            ddetails[0][2] += dy
            self.highlight_reg(ddetails)
            self.parent.update_idletasks()
            sleep(move_pause)
        sleep(move_pause*10)
        self.pic.delete('anim')

    def copy_animate(self, frm, to):
        destdetails = self.reg_details(to)
        srcedetails = self.reg_details(frm)
        speed = self.parent.get_animate_speed()
        steps = int(20/speed)
        xstep = (destdetails[0][1]-srcedetails[0][1])/steps
        ystep = (destdetails[0][2]-srcedetails[0][2])/steps
        move_pause = 0.05/speed
        if (destdetails[0][0]>=7) is not (srcedetails[0][0]>=7): # logical XOR
            # a move between big and small bbox should use small
            # we use the coords in srcedetails to move the box so make sure they're small
            if srcedetails[1][1]==8:
                srcedetails[1] = [25,7,25,7]
                srcedetails[0][4] = self.thefonts[0]
                srcedetails[2] = TK.CENTER
        for i in range(steps):
            self.pic.delete('anim')
            srcedetails[0][1] += xstep
            srcedetails[0][2] += ystep
            self.highlight_reg(srcedetails)
            self.parent.update_idletasks()
            sleep(move_pause)
        if destdetails[0][0]<7: sleep(10*move_pause) # long pause except if going to acc or screen
        self.pic.delete('anim')
        
    def onFrameConfigure(self,e):
        w = self.winfo_width()
        h = self.winfo_height()
        self.pic.configure(height=h,width=w)

    def get_reg(self, register): # returns int
        if register not in self.reg_names:
            raise RuntimeError("get wrong register name: "+register)
        else:
            data = self.reg_vars[self.reg_names.index(register)].get()
            return self.parent.valuise(data)

    def set_reg(self, register, value): # value is an int
        if register not in self.reg_names:
            raise RuntimeError("set wrong register name: "+register)
        else:
            self.reg_vars[self.reg_names.index(register)].set(self.parent.stringify(value,4))
        self.draw_registers()

    def update_label(self, reg, text): # separate because text not int
        self.reg_vars[self.reg_names.index(reg)].set(text)
        self.draw_registers()
            
#
#               RAM class
#

class RAMBox(GUIBox):
    def make_widgets(self):
        self.c = TK.Canvas(self)
        self.f = TK.Frame(self.c)
        # add a vertical scroll bar to canvas
        self.scroll=TK.Scrollbar(self,orient="vertical",command=self.c.yview)
        self.c.configure(yscrollcommand=self.scroll.set)
        #pack everything
        self.c.pack(side=TK.LEFT,fill=TK.Y) # was fill both and expand true
        self.scroll.pack(side=TK.LEFT,fill=TK.Y)
        self.c.create_window((0,0), window=self.f, anchor="nw",tags='self.f')
#        f.pack() - DO NOT ADD this makes the scrollbar not scroll
        self.f.bind("<Configure>", self.onFrameConfigure)
        self.t = SimpleTable(self.f, 129, 2, [7,8], True)
        self.t.set(0,0,"Address")
        self.t.set(0,1,"Contents")
        self.clear() # set empty memory
        self.t.pack(side=TK.TOP)
        # save bg colour for resetting highlights later
        self.bgcolour = self.cget("bg")

    def onFrameConfigure(self,e):
        w = self.f.winfo_width()
        h = self.f.winfo_height()
        self.c.configure(scrollregion=self.c.bbox(TK.ALL),height=h,width=w)

    def set_data(self, address, value):
        self.t.set(address+1,1,self.parent.stringify(value,4))

    def get_data(self, address):
        return self.t.get(address+1,1)

    def flash(self, address): # int address
        flash_pause = 0.5/self.parent.get_animate_speed()
        for i in range(5):
            self.highlight(address,'blue')
            self.parent.update_idletasks()
            sleep(flash_pause)
            self.unhighlight(address)
            self.parent.update_idletasks()
            sleep(flash_pause)

    def highlight(self, address, colour):
        self.t.set(address+1,0,self.parent.stringify(address,2),bg=colour)
        self.t.set(address+1,1,self.get_data(address),bg=colour)

    def unhighlight(self, address):
        self.t.set(address+1,0,self.parent.stringify(address,2),bg=self.bgcolour) # empty bg is default
        self.t.set(address+1,1,self.get_data(address),bg=self.bgcolour)

    def refresh(self):
        self.show_addresses()
        for i in range(1,129):
            data = self.t.get(i,1)
            self.set_data(i-1,self.parent.valuise(data))

    def clear(self):
        self.show_addresses()
        for i in range(1,129):
            self.set_data(i-1,0)

    def show_addresses(self):
        for i in range(1,129):
            self.t.set(i,0,self.parent.stringify(i-1,2))

#
#           Simple Table class used by RAMBox
#
#           Borrowed and modified from original by the 
#           god of tkinter, Bryan Oakley (nbro on git)
#

class SimpleTable(TK.Frame):
    def __init__(self, parent, rows, columns, widths, highlighttop, bground = 'black'):
        # use black background so it "peeks through" to
        # form grid lines
        TK.Frame.__init__(self, parent, background=bground)
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                widget = self.makewidget(row, column, widths[column], highlighttop if row==0 else False)
                current_row.append(widget)
            self._widgets.append(current_row)
        # set all cols to resize equally
        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def makewidget(self, row, column, width, bold):
        font = ('Arial', 11, 'bold') if bold else ('Arial',11)
        label = TK.Label(self, borderwidth=0, width=width, font=font)
        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
        return label

    def set(self, row, column, value, **kwargs):
        widget = self._widgets[row][column]
        widget.configure(text=value, **kwargs)

    def get(self, row, column, **kwargs):
        widget = self._widgets[row][column]
        return widget.cget('text')

########################################################################
#
#   APP object
#
########################################################################

class CLMCApp():
    
    def __init__(self):
        self.gui = GUI(self)

    def run(self):
        self.gui.start()

    def handle_event(self, message): # handle messages from GUI
        if message == 'Lint':
            self.lint()
        elif message == 'Load':
            self.gui.unlock_extIS() # before load so load can set ext if file requires it
            self.load(self.gui.get_loadfilename(CLMC.FILE_STD))
            self.gui.clear_ram()
            self.gui.clear_reg()
            self.gui.unlock_hexmode()
        elif message == 'Save':
            default = CLMC.FILE_EXT if self.isExtIS() else CLMC.FILE_STD
            self.save(self.gui.get_savefilename(default))
        elif message == 'Assemble':
            if self.gui.okaybox("Assemble","This will clear the RAM and CPU state.  Sure?"):
                self.lint()
                self.gui.clear_ram()
                self.gui.clear_reg()
                self.gui.lock_hexmode()
                self.assemble()
        elif message == 'Clear RAM':
            self.gui.clear_ram()
            self.gui.clear_reg()
            self.gui.unlock_extIS()
            self.gui.unlock_hexmode()
            self.reg_store(CLMC.PC,0)
        elif message == 'Clear All':
            if self.gui.okaybox("Clear All","This will also clear your source code.  Sure?"):
                self.gui.clear_reg()
                self.gui.clear_ram()
                self.gui.unlock_extIS()
                self.gui.unlock_hexmode()
                self.gui.set_source_code('')
                self.reg_store(CLMC.PC,0)
        elif message == 'Hex Mode':
            self.gui.refresh_ram()
            self.gui.clear_reg()
        elif message == 'Extended IS':
            pass
        elif message == 'Animate FDE':
            pass
        elif message == 'RUN':
            self.gui.clear_reg()
            self.run_code(False)
        elif message == 'Step':
            self.run_code(True)
        elif message == 'Reset PC':
            self.gui.clear_reg() # also sets PC to 0
        else:
            raise RuntimeError("Unexpected GUI message: "+message)
        
    def load(self, file):
        if file:
            with open(file,'r') as f:
                if f.readline() == '#!CLMC\n':
                    self.gui.set_source_code(f.read())
                    # turn on ext mode if this is an ext mode program
                    if file[-len(CLMC.FILE_EXT):] == CLMC.FILE_EXT:
                        self.gui.set_extIS()
                else:
                    self.gui.msgbox("Load","File is not a CLMC source code file.")
                
    def save(self, file):
        if file:
            with open(file,'w') as f:
                f.write('#!CLMC\n')
                f.write(self.gui.get_source_code())

#
#
#   Code execution method
#   Note: this is blocking hence the animation methods make calls 
#   to update_idletasks, however gross window events like minimise
#   will mess things up.  The only solution is a proper multi-
#   threaded application which is beyond a 2 day holiday project!
#
#

    def run_code(self, stepping): # runs to completion or just one line
        
        if not stepping: self.reg_store(CLMC.PC,0) # run runs on from current PC
        halted = False
        
        while not halted:
            
            # Fetch
            
            self.reg_activity('FETCH')
            self.reg_copy(CLMC.PC,CLMC.MAR)
            try:
                self.bus_cycle('READ')
            except InvalidAddressError:
                halted = True
                break
            self.reg_copy(CLMC.MDR,CLMC.CIR)
            self.reg_inc(CLMC.PC)
            
            # Decode and execute
            
            self.reg_activity('DECODE')
            cir = self.reg_value(CLMC.CIR)
            addrmode, opcode, addrfield = self.decode_CIR(cir)
            if opcode == 0:
                halted = True
                self.reg_store(CLMC.PC,0)
            elif opcode<9:
                # Opcodes 1-8 require operand address decode
                # I've chosen to consider that part of decode, not execute
                try:
                    op_addr = self.get_operand_address(addrmode, addrfield)
                except InvalidAddressError: # caused by indirect to invalid address
                    halted = True
                    break
                
                # Execution for opcodes 1-8

                if opcode == 1: # add
                    self.reg_activity('EXECUTE 1')
                    operand = self.get_operand(op_addr, addrmode)
                    result = self.reg_value(CLMC.ACCUMULATOR) + operand
                    if self.isAnimate():
                        if addrmode == Instruction.IMMEDIATE:
                            self.gui.copyreg_animate(CLMC.CIR,CLMC.ACCUMULATOR)
                        else:
                            self.gui.copyreg_animate(CLMC.MDR,CLMC.ACCUMULATOR)
                    self.reg_store(CLMC.ACCUMULATOR,result)
                elif opcode == 2: # sub
                    self.reg_activity('EXECUTE 2')
                    operand = self.get_operand(op_addr, addrmode)
                    result = self.reg_value(CLMC.ACCUMULATOR) - operand
                    if self.isAnimate():
                        if addrmode == Instruction.IMMEDIATE:
                            self.gui.copyreg_animate(CLMC.CIR,CLMC.ACCUMULATOR)
                        else:
                            self.gui.copyreg_animate(CLMC.MDR,CLMC.ACCUMULATOR)
                    self.reg_store(CLMC.ACCUMULATOR,result)
                elif opcode == 3: # sta
                    self.reg_activity('EXECUTE 3')
                    if self.isAnimate():
                        if addrmode == Instruction.INDIRECT:
                            self.gui.copyreg_animate(CLMC.MDR,CLMC.MAR)
                        elif addrmode == Instruction.INDEXED:
                            self.gui.copyreg_animate(CLMC.XREG,CLMC.MAR)
                            self.reg_store(CLMC.MAR, self.reg_value(CLMC.XREG)) # just to look good
                            self.gui.copyreg_animate(CLMC.CIR,CLMC.MAR)
                        else:
                            self.gui.copyreg_animate(CLMC.CIR,CLMC.MAR)
                    self.reg_store(CLMC.MAR, op_addr)
                    self.reg_copy(CLMC.ACCUMULATOR, CLMC.MDR)
                    self.bus_cycle('WRITE')
                elif opcode == 4: # ldx
                    if not self.isExtIS(): # ... but shouldn't have assembled unless in ext mode
                        self.gui.msgbox("Run","Halted - instruction in CIR ("+str(cir)+") requires extended mode.")
                        halted = True
                    else:
                        operand = self.get_operand(op_addr, addrmode)
                        self.reg_activity('EXECUTE 4')
                        if self.isAnimate():
                            if addrmode == Instruction.IMMEDIATE:
                                self.gui.copyreg_animate(CLMC.CIR,CLMC.XREG)
                            else:
                                self.gui.copyreg_animate(CLMC.MDR,CLMC.XREG)
                        self.reg_store(CLMC.XREG,operand)
                elif opcode == 5: # lda
                    self.reg_activity('EXECUTE 5')
                    operand = self.get_operand(op_addr, addrmode)
                    if self.isAnimate():
                        if addrmode == Instruction.IMMEDIATE:
                            self.gui.copyreg_animate(CLMC.CIR,CLMC.ACCUMULATOR)
                        else:
                            self.gui.copyreg_animate(CLMC.MDR,CLMC.ACCUMULATOR)
                    self.reg_store(CLMC.ACCUMULATOR,operand)
                elif opcode == 6: # bra
                    self.reg_activity('EXECUTE 6')
                    operand = self.get_operand(op_addr, addrmode, dest=CLMC.PC)
                    self.reg_store(CLMC.PC,operand)
                elif opcode == 7: # brz
                    self.reg_activity('EXECUTE 7')
                    if self.reg_value(CLMC.ACCUMULATOR) == 0:
                        operand = self.get_operand(op_addr, addrmode, dest=CLMC.PC)
                        self.reg_store(CLMC.PC,operand)
                elif opcode == 8: # brp
                    self.reg_activity('EXECUTE 8')
                    if self.reg_value(CLMC.ACCUMULATOR) >= 0:
                        operand = self.get_operand(op_addr, addrmode, dest=CLMC.PC)
                        self.reg_store(CLMC.PC,operand)
            # Opcode 9 don't need operand decode hence safe from 'MAR out of range' error
            elif opcode == 9: # inp, out or extended mode
                if addrfield == 1: # inp
                    self.reg_activity('EXECUTE 9')
                    value = self.gui.inputbox("User Input","Please enter value for accumulator")
                    if not value:
                        self.gui.msgbox("Run","Halted by user input request.")
                        halted = True
                        break
                    self.reg_store(CLMC.ACCUMULATOR, value)
                    if self.isAnimate():
                        self.gui.flash_reg(CLMC.ACCUMULATOR)
                elif addrfield == 2: # out
                    self.reg_activity('EXECUTE 9')
                    self.reg_store(CLMC.SCREEN, self.reg_value(CLMC.ACCUMULATOR))
                    if self.isAnimate():
                        self.gui.flash_reg(CLMC.SCREEN)
                else:
                    self.reg_activity('EXECUTE 9')
                    if not self.isExtIS():
                        self.gui.msgbox("Run","Halted - instruction in CIR ("+str(cir)+") requires extended mode.")
                        halted = True
                    elif addrfield == 3: # txa
                        self.reg_copy(CLMC.XREG,CLMC.ACCUMULATOR)
                    elif addrfield == 4: # tax
                        self.reg_copy(CLMC.ACCUMULATOR,CLMC.XREG)
                    elif addrfield == 5: # inx
                        self.reg_inc(CLMC.XREG)
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.XREG)
                    elif addrfield == 6: # dex
                        self.reg_dec(CLMC.XREG)
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.XREG)
                    elif addrfield == 7: # lsl
                        self.reg_store(CLMC.ACCUMULATOR,self.reg_value(CLMC.ACCUMULATOR)*2)
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.ACCUMULATOR)
                    elif addrfield == 8: # lsr
                        self.reg_store(CLMC.ACCUMULATOR,self.reg_value(CLMC.ACCUMULATOR)//2)
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.ACCUMULATOR)
                    elif addrfield == 9: # eor
                        # save acc vale then copy reg to get animation
                        temp = self.reg_value(CLMC.ACCUMULATOR)
                        self.reg_copy(CLMC.XREG,CLMC.ACCUMULATOR)
                        # use saved value to store correct result
                        self.reg_store(CLMC.ACCUMULATOR,temp^self.reg_value(CLMC.XREG))
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.ACCUMULATOR)
                    elif addrfield == 10: # and
                        temp = self.reg_value(CLMC.ACCUMULATOR)
                        self.reg_copy(CLMC.XREG,CLMC.ACCUMULATOR)
                        self.reg_store(CLMC.ACCUMULATOR,temp&self.reg_value(CLMC.XREG))
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.ACCUMULATOR)
                    elif addrfield == 11: # orr
                        temp = self.reg_value(CLMC.ACCUMULATOR)
                        self.reg_copy(CLMC.XREG,CLMC.ACCUMULATOR)
                        self.reg_store(CLMC.ACCUMULATOR,temp|self.reg_value(CLMC.XREG))
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.ACCUMULATOR)
                    elif addrfield == 12: # mvn
                        self.reg_copy(CLMC.XREG,CLMC.ACCUMULATOR)
                        # move with not - assume 8bit in hexmode otherwise use -ve denary
                        if self.isHexMode():
                            result = 255-self.reg_value(CLMC.XREG)
                        else:
                            result = ~self.reg_value(CLMC.XREG)
                        self.reg_store(CLMC.ACCUMULATOR,result)
                        if self.isAnimate():
                            self.gui.flash_reg(CLMC.ACCUMULATOR)
                    else:
                        raise RuntimeError("Opcode 9 option "+addrfield+" not implemeneted")
            else:
                raise RuntimeError("Opcode is not 0-9?!")

            if stepping: halted = True
            self.gui.draw_registers() ########################## is this needed?

        self.gui.clear_animation()
        
        if not stepping or opcode == 0:
            self.reg_activity('IDLE')
            self.gui.msgbox("Run","Halted - end of program")
            self.gui.draw_registers()
        
    def decode_CIR(self,cir):
        # in hexmode the addrmode and opcode are place in hex placevalue not decimal
        # either way the machine code is sort of readable
        if self.isHexMode():
            addrmode = cir // 4096
            opcode = cir // 256 - 16*addrmode
            addrfield = cir % 256
        else:
            addrmode = cir // 1000
            opcode = cir // 100 - 10*addrmode
            addrfield = cir % 100
        return (addrmode, opcode, addrfield)

    def get_operand_address(self, amode, afield):
        # returns the address where the data is which depends on the addrmode
        if amode == Instruction.IMPLIED:
            raise RuntimeError('get_operand_address with implied addressing?')
        elif amode == Instruction.IMMEDIATE:
            return afield # return *value* in address field - see get_operand
        elif amode == Instruction.DIRECT:
            return afield # return address in address field - see get_operand
        elif amode == Instruction.INDIRECT:
            # fetch pointer from memory
            if self.isAnimate():
                self.gui.copyreg_animate(CLMC.CIR,CLMC.MAR)
            self.reg_store(CLMC.MAR, afield)
            self.bus_cycle('READ')
            return self.reg_value(CLMC.MDR) # return address pointed to
        elif amode == Instruction.INDEXED:
            x = self.reg_value(CLMC.XREG)
            return afield + x # return calculated address

    def get_operand(self, address, amode, dest=CLMC.MAR):
        if amode == Instruction.IMMEDIATE:
            return address # the address IS the operand value
        else: # the address is actually an address!
            if self.isAnimate():
                # the address is going into MAR (or PC for branches)
                # this address comes from different places, depending on amode
                if amode == Instruction.DIRECT:
                    self.gui.copyreg_animate(CLMC.CIR,dest)
                elif amode == Instruction.INDIRECT:
                    self.gui.copyreg_animate(CLMC.MDR,dest)
                elif amode == Instruction.INDEXED:
                    self.gui.copyreg_animate(CLMC.XREG,dest)
                    self.gui.copyreg_animate(CLMC.CIR,dest)
                else:
                    raise RuntimeError("unexpected amode in get_operand")
            self.reg_store(dest, address)
            # if operand is an address, go read it from RAM
            if dest == CLMC.MAR:
                self.bus_cycle('READ')
                return self.reg_value(CLMC.MDR)
            else:
                return address

    def bus_cycle(self, direction):
        address = self.reg_value(CLMC.MAR)
        if address<0 or address>127:
            self.gui.msgbox("Run","Address in MAR is invalid.")
            raise InvalidAddressError
        if direction == 'READ':
            self.reg_culabel('BUS READ')
            self.ram_to_reg()
        elif direction == 'WRITE':
            self.reg_culabel('BUS WRITE')
            self.reg_to_ram()
        else:
            raise RuntimeError("Bus cycle direction invalid")

#
#       GUI interface functions used by run_code above
#

    def ram_to_reg(self):
        addr = self.get_reg(CLMC.MAR)
        data = self.get_ram(addr) # gets stringy data
        if self.isAnimate():
            self.gui.bus_read_animate(addr, data) # needs stringy data
        self.set_reg(CLMC.MDR,data)

    def reg_to_ram(self):
        addr = self.get_reg(CLMC.MAR)
        data = self.get_reg(CLMC.MDR)
        if self.isAnimate():
            self.gui.bus_write_animate(addr)
        self.set_ram(addr,data)

    def get_reg(self, reg):
        return self.gui.get_reg(reg)
    def get_ram(self, addr):
        return self.gui.get_ram(addr)
    def set_ram(self, addr, data):
        self.gui.set_ram(addr, data)
    def set_reg(self, reg, data):
        self.gui.set_reg(reg, self.gui.valuise(data)) # must valuise here

    def reg_inc(self,register):
        self.reg_store(register,self.reg_value(register)+1)
        
    def reg_dec(self,register):
        self.reg_store(register,self.reg_value(register)-1)
        
    def reg_copy(self, frm, to):
        if self.isAnimate():
            self.gui.copyreg_animate(frm,to)
        self.reg_store(to, self.reg_value(frm))

    def reg_value(self, register):
        return self.gui.get_reg(register)
        
    def reg_activity(self, text):
        if text=='DECODE': # flash label and CIR together for decode
            self.gui.update_label(CLMC.ACTIVITY, text, CLMC.CIR)
        else:
            self.gui.update_label(CLMC.ACTIVITY, text)
        
    def reg_culabel(self, text):
        self.gui.update_label(CLMC.CU_LABEL,text)
        
    def reg_store(self, register, value):
        self.gui.set_reg(register, value)
        
    def isExtIS(self):
        return self.gui.isExtIS()
    def lock_extIS(self):
        self.gui.lock_extIS()
    def unlock_extIS(self):
        self.gui.unlock_extIS()

    def isAnimate(self):
        return self.gui.isAnimate()

    def isHexMode(self):
        return self.gui.isHexMode()

#
#
#   Assembler method
#   Note: this is also blocking but takes nada time
#
#

    def assemble(self):
        
        src = SourceCode(self.gui.get_source_code())
        
        try:
            object_code = Assembler(src,self.isHexMode())
        except MnemonicError as ex:
            self.gui.msgbox("Assemble","Bad mnemonic: "+str(ex.args[0]))
        except AddressError as ex:
            self.gui.msgbox("Assemble","Address out of range: "+str(ex.args[0]))
        except LabelError as ex:
            self.gui.msgbox("Assemble","Could not resolve label: "+str(ex.args[0]))
        except ImpliedError as ex:
            self.gui.msgbox("Assemble","Implied addressing not available: "+str(ex.args[0]))
        except AddrModeError as ex:
            self.gui.msgbox("Assemble","Addressing mode not allowed here: "+str(ex.args[0]))
        except ErrorLinesError:
            self.gui.msgbox("Assemble", "Remove/replace lines marked as errors")
        except DuplicateLabelError as ex:
            self.gui.msgbox("Assemble","Duplicate label: "+ex.args[0])
        except BadLabelError as ex:
            self.gui.msgbox("Assemble","Bad label: "+ex.args[0])
        else:
            if object_code.usesExtIS():
                if self.isExtIS():
                    self.lock_extIS()
                else:
                    self.gui.msgbox("Assemble","Code uses extended instruction set: enable and re-try")
                    return
            for instruction in object_code:
                self.gui.set_ram(instruction.address, instruction.machinecode)                
            self.reg_store(CLMC.PC,0) # highlights PC in RAM

    def lint(self):
        # tidy-up the sourcecode - I hate pressing tab :)
        src = SourceCode(self.gui.get_source_code())
        linted = Linter(src)
        for line_number, statement in enumerate(linted):
            if not statement.isValid():
                src.mark_error(line_number)
            else:
                src.set(line_number, str(statement))
        self.gui.set_source_code(str(src))
            
class Linter:

    def __init__(self, source):
        self.statements = []
        self.ptr = 0
        for line in source:
            statement = Statement(line)
            self.statements.append(statement)

    def __iter__(self):
        return self

    def __next__(self):
        if self.ptr >= len(self.statements):
            self.ptr = 0
            raise StopIteration
        else:
            self.ptr += 1
            return self.statements[self.ptr-1]
        
class Assembler:

    def __init__(self, source, hexmode):
        
        self.objcode = []
        self.ptr = 0

        linted = Linter(source)
        
        # Halt if any lines in error
        if any([not s.isValid() for s in linted]):
            raise ErrorLinesError

        # Collect symbols (first pass)
        symtbl = SymbolTable(linted)

        # Translate and collect symbol addresses while passing
        address = 0
        for statement in linted:
            instruction = Instruction(statement)
            if not instruction.isComment():
                instruction.set_address(address)
                if instruction.get_label() != '':
                    symtbl.fix_address(instruction.get_label(),address)
                address += 1
                self.objcode.append(instruction)

        # Fixup addresses
        for instruction in self.objcode:
            this_operand = instruction.get_operand()
            this_opstring = instruction.get_opstring()
            if this_operand is None:
                if symtbl.is_valid_label(this_opstring):
                    instruction.set_operand(symtbl.resolve_label(this_opstring))
                else:
                    raise LabelError(this_opstring)
            instruction.translate(hexmode) # sets machinecode values

    def usesExtIS(self):
        return any([i.usesExtIS() for i in self.objcode])

    def __iter__(self):
        return self

    def __next__(self):
        if self.ptr >= len(self.objcode):
            self.ptr = 0
            raise StopIteration
        else:
            self.ptr += 1
            return self.objcode[self.ptr-1]
        
#
#   Records the address of any labels used in the program
#

class SymbolTable:
    
    def __init__(self, code):
        self.labels = dict()
        for n, statement in enumerate(code):
            if statement.label: # relies on None and '' both evaluating to False
                if statement.label in self.labels:
                    raise DuplicateLabelError(statement.label)
                elif any(s in statement.label for s in "#(),"):
                    raise BadLabelError(statement.label)
                else:
                    self.labels[statement.label] = -1 # set illegal address
                    
    def is_valid_label(self,text):
        return text in self.labels
    
    def fix_address(self, label, address):
        if label not in self.labels:
            raise RuntimeError("foxup address with unseen label")
        self.labels[label] = address

    def resolve_label(self,text):
        if self.labels[text] == -1:
            raise RuntimeError("resolve_label with no address set")
        return self.labels[text]

#
#   Instruction object
#   This class defines some constants used elsewhere to identify addressing modes
#

class Instruction:

    IMPLIED = 9
    IMMEDIATE = 1
    DIRECT = 0
    INDIRECT = 2
    INDEXED = 4
    
    # key is opcode; value is tuple of allowed addressing modes

    MATRIX = { 0:(0,9), 1:(0,1,2,4), 2:(0,1,2,4),
               3:(0,2,4), 4:(0,1,2), 5:(0,1,2,4),
               6:(0,2,4), 7:(0,2,4), 8:(0,2,4),
               9:(9,) } # final comma to prevent coercion to int
    
    def __init__(self, statement):
        self.address = None
        self.label = statement.label
        self.mnemonic = statement.mnemonic
        self.opstring = statement.opstring
        self.opcode = None
        self.addrmode = None
        self.operand = None
        self.machinecode = -1
        self.needsExtIS = False
        self.commentline = False

        if self.label and self.label[0] == "'": # might be None ...
            self.commentline = True
        else:
            self.decode()

    def isComment(self):
        return self.commentline
    
    def decode(self):
        # get operation type into opcode
        if self.mnemonic in AssemblyLanguage.MNEMONICS:
            self.opcode = AssemblyLanguage.MNEMONICS[self.mnemonic][0]
        else:
            raise MnemonicError(self.mnemonic)
        if AssemblyLanguage.MNEMONICS[self.mnemonic][2] == 1:
            self.needsExtIS = True
        # identify addressing mode and extract operand
        if self.opstring == '':
            self.addrmode = Instruction.IMPLIED
            self.operand = ''
        elif self.opstring[0] == '(' and self.opstring[-1] == ')':
            self.addrmode = Instruction.INDIRECT
            self.operand = self.opstring[1:-1]
        elif self.opstring[-2:] == ',x':
            self.addrmode = Instruction.INDEXED
            self.operand = self.opstring[:-2]
            if self.operand[0] == '(':
                raise AddrModeError(str(self))
        elif self.opstring[0] == '#':
            self.addrmode = Instruction.IMMEDIATE
            self.operand = self.opstring[1:]
        else:
            self.addrmode = Instruction.DIRECT
            self.operand = self.opstring
        # only implied or direct allowed if not extended mode
        if self.addrmode not in [Instruction.IMPLIED, Instruction.DIRECT]:
            self.needsExtIS = True

        # check operand is valid address - raises exception if not
        self.validate_operand()

        # check combination of opcode and addr mode is allowed
        if self.addrmode not in Instruction.MATRIX[self.opcode]:
            raise AddrModeError(str(self))

    def translate(self, hexmode):
        amode = self.addrmode if self.addrmode !=9 else 0
        if hexmode:
            self.machinecode = amode*4096 + self.opcode*256 + self.operand
        else:
            self.machinecode = amode*1000 + self.opcode*100 + self.operand

    def validate_operand(self):
        '''
        operand is valid if it is:
        blank (for implied addressing),
        an address or
        a label in the symboltable
        '''
        # add address field for implied-only instructions
        if self.operand == '':
            if AssemblyLanguage.MNEMONICS[self.mnemonic][1] != -1:
                self.operand = AssemblyLanguage.MNEMONICS[self.mnemonic][1]
                return
            else:
                raise ImpliedError
        # handle addresses
        if self.operand.isdigit():
            self.operand = int(self.operand)
            if (self.operand < 0 or self.operand > 127) and self.opcode != 0 and self.addrmode != Instruction.IMMEDIATE:
                print(self)#debug
                raise AddressError(self)
        else: # symbolic address handled by assembler - need to fixup is signalled by None operand
            self.opstring = self.operand # make opstring be the label to lookup later
            self.operand = None

    def __str__(self):
        return self.label+' '+self.mnemonic+' '+self.opstring

    def get_label(self):
        return self.label
    def set_address(self, address):
        self.address = address
    def usesExtIS(self):
        return self.needsExtIS
    def get_operand(self):
        return self.operand
    def set_operand(self, value):
        self.operand = value
    def get_opstring(self):
        return self.opstring

#
#   Exception classes
#

class Error(Exception):
    pass
class OperandError(Error):
    pass
class MnemonicError(Error):
    pass
class AddressError(Error):
    pass
class LabelError(Error):
    pass
class ImpliedError(Error):
    pass
class AddrModeError(Error):
    pass
class InstructionSetError(Error):
    pass
class InvalidAddressError(Error):
    pass
class DuplicateLabelError(Error):
    pass
class BadLabelError(Error):
    pass
class ErrorLinesError(Error):
    pass
#
#   Statement class
#

class Statement:
    
    def __init__(self, text):
        
        # a line of text is a statement if it looks like asemblable source code
        self.valid = False
        self.translatable = False
        self.label = None
        self.mnemonic = None
        self.opstring = None
        
        parts = text.lower().split() # split on whitespace
        
        if len(parts) == 0 or text[0] == "'": # comments and blank lines
            self.valid = True
            self.translatable = False
            self.label = text
            self.opstring = ''
            self.mnemonic = ''
        elif SourceError.ERROR_CODE in text or len(parts)>3: # already marked error or too many parts
            self.valid = False
            self.translatable = False
            self.label = text
            self.opstring = ''
            self.mnemonic = ''
        else:
            self.valid = True
            self.translatable = True
            if len(parts)==3:
                self.label, self.mnemonic, self.opstring = parts
                if not self.isMnemonic(self.mnemonic):
                    self.valid = False
                    self.translatable = False
            elif len(parts)==1: # mnemonic + implied addressing or just label
                if self.isMnemonic(parts[0]):
                    self.label = ''
                    self.opstring = ''
                    self.mnemonic = parts[0]
                else:
                    self.label = parts[0]
                    self.mnemonic = 'dat'
                    self.opstring = ''
            else: # two parts - label mnemonic or mnemonic operand
                if self.isMnemonic(parts[0]):
                    self.label = ''
                    self.mnemonic, self.opstring = parts
                elif self.isMnemonic(parts[1]):
                    self.label, self.mnemonic = parts
                    self.opstring = ''
                else:
                    self.valid = False
                    self.translatable = False

    def __str__(self):
        parts = [self.label,self.mnemonic,self.opstring]
        return '\t'.join(parts)

    def isValid(self):
        return self.valid

##    def isTranslatable(self): CAN REMOVE ALL USE OF THIS ATTRIBUTE
##        return self.translatable

    def isMnemonic(self, text):
        return text in AssemblyLanguage.MNEMONICS







#
#   Source code class
#   Mainly to handle messiness of text box content so that
#   code using sourcecode can treat it as an iterable of statements
#

class SourceCode:
    
    def __init__(self, text):
        self.code = []
        self.ptr = 0 # used to make iterable
        for line in text.split('\n'):
            text = line.strip()
            if len(text)>0:
                self.code.append(line.strip())
        while len(self.code)>0 and len(self.code[-1]) == 0: # if we have any code, strip trailing blank lines
            del self.code[-1]
            
    def __str__(self):
        return '\n'.join(self.code)
    
    def mark_error(self, n):
        if self.code[n][-len(SourceError.ERROR_CODE):] != SourceError.ERROR_CODE:
            self.code[n] += ' ' + SourceError.ERROR_CODE
            
    def set(self,n,text):
        self.code[n] = text
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.ptr >= len(self.code):
            self.ptr = 0
            raise StopIteration
        else:
            self.ptr += 1
            return self.code[self.ptr-1]



##############################################################
#
#   Set up and run the application object
#
##############################################################
        
app = CLMCApp()
app.run()
