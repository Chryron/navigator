from tkinter import *
from tkinter import font
from decision_tree import *
import tkinter.tix as tix
import csv
import random
import pandas as pd

dt = Database()
    
devices = []

with open(resource_path('devices.csv'), 'r',encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for line in csv_reader:
        devices.append((line[1],line[2]))

random.shuffle(devices)
paths = {}





class View(object):
    def __init__(self, root):
        self.root = root
        self.makeCheckList()
        self.searchtag_dict = {"devices": devices, "path":[]}

    def makeCheckList(self):
        self.cl = tix.CheckList(self.root)
        #self.cl.pack(ipadx = 600, ipady= 100)
        self.cl.grid(row = 1, column = 0, columnspan = 2, ipadx = 600, ipady = 100)
        
        for CT in dt.baseCT:
            id = CT.CTid
            self.cl.hlist.add(id, text=CT.CTname)
            self.cl.setstatus(id, "off")
            self.get_children(CT, id)
        self.cl.autosetmode()

        for CT in dt.baseCT:
            id = CT.CTid
            self.cl.close(id)
            self.close_branches(CT, id)
        
        
        



    def get_children(self, CT, id):
        if len(CT.children)==0: return
        for child in CT.children:
            new_id = id +"."+ child.CTid
            self.cl.hlist.add(new_id, text=child.CTname)
            self.cl.setstatus(new_id, "off")
            self.get_children(child, new_id)

    def close_branches(self, CT, id):
        if len(CT.children)==0: return
        for child in CT.children:
            new_id = id +"."+ child.CTid
            self.cl.close(new_id)
            self.close_branches(child, new_id)

    
    
    def get_searchtags(self):
        search_tags = []
        indx = self.root.getvar(name = "index")
        
        for CT in dt.baseCT:
            id = CT.CTid

            if self.cl.getstatus(id) == "on": search_tags.append(CT)
            self.get_childstatus(CT, id, search_tags)
        
        out = dt.search(search_tags)
        textout = ""
        if len(out) < 5:
            textout += "These are your results: \n"
        else:
            textout += "These are your top 3 results: \n"
        
        i = 0
        for term in out:
            textout += term.termCode + ": " + term.termName + "\n\n"
            if i > 1 : break
            i += 1
        

        device_term =  dt.get_term(termName = devices[indx][1])
            
        textout += "The term you were looking for is: " + device_term.termName + "\n\n"
        if device_term in out:
            out.index(device_term)
            textout += "The term has been found and it is in position " + str(out.index(device_term) + 1) + " out of " + str(len(out)) + " terms\n"
        else:
            textout += "The term could not be found\n"


        # iterate over devices
    
        self.reset()
        self.root.setvar(name = "textout", value = textout)
        tags=[]
        for CT in search_tags:
            tags.append(CT.CTid)
        self.searchtag_dict["path"].append(tags)  

        if indx+1 < len(devices):
            self.root.setvar(name = "index", value = indx + 1)
            self.root.setvar(name = "desc", value = devices[indx+1][0])
        else:
            self.root.setvar(name = "desc", value = "Thank you for your response!")
            button = Button(self.root, text="Confirm", state = DISABLED)
            button.grid(row = 2,column = 0, sticky = 'w',padx=10,pady=10)
            self.reset(terminal_clear = False)
        
        
            
            


        
        
        
        
    def get_childstatus(self, CT, id, search_tags):
        if len(CT.children)==0: return
        for child in CT.children:
            new_id = id +"."+ child.CTid
            if self.cl.getstatus(new_id) == "on": search_tags.append(child)
            self.get_childstatus(child, new_id, search_tags)
    
    def reset(self, terminal_clear=True):
        if terminal_clear: self.root.setvar(name = "textout", value = " \n \n \n \n \n")
        for CT in dt.baseCT:
            id = CT.CTid
            self.cl.setstatus(id, "off")
            self.cl.close(id)
            self.reset_children(CT, id)
            self.close_branches(CT, id)

        
    
    def reset_children(self,CT, id):
        if len(CT.children)==0: return
        for child in CT.children:
            new_id = id +"."+ child.CTid
            self.cl.setstatus(new_id, "off")
            self.reset_children(child, new_id)






    

def main():
    root = tix.Tk()
    root.title("Database")
    root.iconbitmap(resource_path("icon.ico"))
    root.option_add('*Font', 'Arial 16')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)



    textout = StringVar(root, name ="textout", value =" \n \n \n \n \n")
    desc = StringVar(root, name ="desc")
    index = IntVar(root, name="index")
    index.set(0)

    desc.set(devices[0][0])


    description = Message(root, textvariable = desc, font = ("Arial", 12),
    aspect=1200).grid(row=0, column = 0,
     columnspan = 2, sticky = 'w')



    
    view = View(root)




    button = Button(root, text="Confirm", command = view.get_searchtags)
    reset = Button(root, text="Reset", command = view.reset)
    #button.pack(pady=20, padx = 20, side=RIGHT) 
    button.grid(row = 2,column = 0, sticky = 'w',padx=10,pady=10)
    reset.grid(row = 2,column = 1, sticky = 'e',padx=10,pady=10)

    Label(root, textvariable = textout).grid(row=3,column = 0, columnspan = 2)


    #root.minsize(width=1600, height=950)
    #root.maxsize(width=1600, height=950)

    root.update()
    root.mainloop()
    return view.searchtag_dict

if __name__ == '__main__':
    data = main()
    if len(data["path"])==len(data["devices"]): pd.DataFrame(data).to_csv("data.csv")
    
    
