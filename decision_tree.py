import xml.etree.ElementTree as ET
from collections import Counter
import csv
import pandas as pd
import random
import os
import sys

# Define function to import external files when using PyInstaller.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
    
    

class Term:

    """
    A class used to represent terms. 
    Contains information about the termCode, termName, termDefinition and termStatus (Active/Obsolete).
    """
    
    def __init__(self, termCode, termName, termDefinition, termStatus):

        self.termCode = termCode
        self.termName = termName
        self.termDefinition = termDefinition
        self.termStatus = termStatus

class CollectiveTerm:

    """
    A class used to represent Collective terms (CTs). These represent the hierarchy in the explorer. 
    Contains information about the CTid, CTcode, CTname, CTDefinition,
    CTpath (the ids of parent collective terms), the immediate parent of the CT (if any), 
    a list of children CTs (i.e. collective terms under the current collective term),
    and terms which do not belong to any children CT. 
    """
    
    def __init__(self, CTid, CTcode, CTname, CTdefinition, CTpath):

        self.CTid = CTid
        self.CTname = CTname
        self.CTcode = CTcode
        self.CTdefinition = CTdefinition
        self.CTpath = CTpath

        self.parent = None
        self.children = []
        self.terms = []
                

class Database:

    """
    A class used to represent the complete database. This class can be initialised using the 
    complete database and explorer xml files 
    (e.g. Data21_11.xml and explorer_en_20211101.xml respectively). 
    Contains a list of all terms and information about the hierarchy of Collective Terms 
    and their associated terms.
    """

    def __init__(self, database_xml = "Data21_11.xml", explorer_xml = 'explorer_en_20211101.xml'):
        
        """
        Parses the database and explorer database xml files to obtain all required information.
        """

        data = ET.parse(resource_path(database_xml))
        explorer = ET.parse(resource_path(explorer_xml))

        self.terms = {}
        self.tree = {}
        self.baseCT = []


        for term in data.iterfind('term'):
            
            current_term = Term(term.find('termCode').text, 
            term.find('termName').text, term.find('termDefinition').text, term.find('termStatus').text)

            
            self.terms[term.find('termCode').text] = current_term

        for CT in explorer.iterfind('node'):
            # for parent nodes with no code
            if CT.find('code') == None:
                CTcode = None
            else:
                CTcode = CT.find('code').text
                
            current_CT = CollectiveTerm(CT.find('id').text, CTcode, 
            CT.find('name').text, CT.find('definition').text, CT.find('path').text)
            
            self.tree[CT.find('id').text] = current_CT
            if CTcode == None: self.baseCT.append(current_CT)

            for term in CT.findall('termCode'):
                current_term = self.terms[term.text]
                current_CT.terms.append(current_term)
        

        for NA , CT in self.tree.items():
            
            searchstr = '/' + CT.CTid + '/'
            current_path = CT.CTpath
            path_trim = current_path[0:current_path.rfind(searchstr)]

            parent_id = path_trim[path_trim.rfind('/')+1:]
            if parent_id != "":
                parent = self.tree[parent_id]
                parent.children.append(CT)
                CT.parent = parent
            
    
    def get_CT(self, CTid = None, CTcode = None, CTname = None, CTdefinition = None, CTpath = None):
        
        """
        This function returns the CollectiveTerm object for a particular
        id (CTid), code (CTcode), name (CTname), definition (CTdefinition) or path (CTpath).
        """

        if CTid != None:
            return self.tree[CTid]
        else:
            for NA, CT in self.tree.items():
                if CTcode != None:
                    if CT.CTcode == CTcode:
                        return CT
                elif CTname != None:
                    if CT.CTname == CTname:
                        return CT
                elif CTdefinition != None:
                    if CT.CTdefinition == CTdefinition:
                        return CT
                elif CTpath != None:
                    if CT.CTpath == CTpath:
                        return CT
                else:
                    return False
        


    
    def get_term(self, termName = None, termCode = None, termDefinition = None):

        """
        This function returns the object for a particular
        name (termName), code (termCode), or definition (termDefinition).
        """

        if termCode != None:
            return self.terms[termCode]
        else:
            for NA, term in self.terms.items():
                if termName != None:
                    if term.termName == termName:
                        return term
                elif termDefinition != None:
                    if term.termDefinition == termDefinition:
                        return term
                else: 
                    return False
    
    def decision_tree(self, final_dialog = True):

        """
        This function creates an interactive decision tree that can be used to navigate the explorer.
        """
        
        search_tags = []
        for CT in self.baseCT:
            loop = True
            count = 0 
            responses = [f"Would you like to filter devices based on {CT.CTname}?\n", 
            f"Would you like to continue filtering devices based on {CT.CTname}?\n"]
            while True:
                response = input(responses[count])
                while True:
                    if response.lower() == "yes" or response.lower() == "y":
                        count = 1
                        break
                    elif response.lower() == "no" or response.lower() == "n":
                        loop = False
                        break
                    else:
                        response = input("Please enter Yes(Y) or No(N).\n")
                if loop == False:
                    break
                current_CT = CT
                
                while True:
                    i = 0
                    if len(current_CT.children)>0:
                        print("Please choose a term from the following that applies to your device. (0 to skip)\n")
                        for child in current_CT.children:
                            print('['+str(i+1)+'] ' + child.CTname)
                            i += 1
                        while True:
                            response = input("\n")
                            if response.isdigit() or response.lower() == "cancel": break
                            if response.lower() == "help": print(current_CT.CTdefinition)
                            print("Please select a numbered option, choose 0 to skip or type cancel to cancel.")
                        if response == "0" or response.lower() == "cancel": break
                        current_CT = current_CT.children[int(response) - 1]
                    else:
                        response = input("Would you like to confirm? \n")
                        while True:
                            if response.lower() == "yes" or response.lower() == "y":
                                break
                            elif response.lower() == "no" or response.lower() == "n":
                                break
                            elif response.lower() == "help":
                                print(current_CT.CTdefinition)
                                response = input("Please enter Yes(Y) or No(N).\n")
                            else:
                                response = input("Please enter Yes(Y) or No(N).\n")
                        if response.lower() == "yes" or response.lower() == "y": break
                        elif response.lower() == "no" or response.lower() == "n":
                            reponse = "cancel"
                            break
                        
                    
                if response.lower() != "cancel": search_tags.append(current_CT)
        
        

        if final_dialog: self.output(search_tags)
        

        return search_tags


    def output(self,search_tags):

        out = self.search(search_tags)
        if len(out) < 5:
            print("These are your results: \n")
        else:
            print("These are your top 5 results: \n")
        

        i = 0
        for term in out:
            print(term.termCode + ": " + term.termName)
            if i > 4 : break
            i += 1
        return out


    def performance_data(self):
        
        devices = []

        with open('devices.csv', 'r',encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for line in csv_reader:
                devices.append((line[1],line[2]))
        
        random.shuffle(devices)
        paths = {}
        for device in devices:
            print("Choose options that may apply to this device: \n" + device[0])
            search_tags = self.decision_tree(final_dialog = False)
            out = self.search(search_tags)
            paths[device] = search_tags
            device_term =  self.get_term(termName = device[1])
            print("The term you were looking for is: " + device_term.termName)
            try:
                print("The term has been found and it is in position " 
                + str(out.index(device_term) + 1) + " out of " + str(len(out)) + " terms")
            except:
                print("The term could not be found")

        pd.DataFrame(paths).to_csv("data.csv")

        

        


    def search(self, search_tags, strict = False):

        """
        This function can be used to find objects which are common within a list of
        CollectiveTerm objects. Primarily used by the decision_tree() function. It takes
        in a boolean input strict to determine whether or not the search should find
        strict commonalities between the search tags.
        """

        search_terms = []
        output = []

        if strict:

            for CT in search_tags:
                search_terms.append(self.all_terms(CT))
            
            common = search_terms[0]

            for i in range(len(search_terms)-1):
                common = set.intersection(set(common), set(search_terms[i+1]))
            
            
            for term in common:
                if term.termStatus == "Active":
                    output.append(term)     
        else:

            for CT in search_tags:
                search_terms.extend(self.all_terms(CT))

            #output = sorted(search_terms, key = search_terms.count, reverse=True)
            c = Counter(search_terms)
            output_sort = sorted(search_terms, key=c.get, reverse=True)
            
            for i in output_sort:
                if i not in output: output.append(i)

        return output
        


        

    def all_terms(self, CT):

        """
        This is an iterative function which returns a list of all objects underneath 
        a CollectiveTerm object.
        """

        terms = CT.terms 
        for child in CT.children:
            terms.extend(self.all_terms(child))
        terms = list(set(terms))
        return terms





## Starts the decision_tree
