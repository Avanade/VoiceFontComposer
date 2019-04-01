import pandas as pd
import uuid

class HarvardStatments(object):
    """An object to handle the list of Harvard Statments"""
    def __init__(self):
        self.harvard = pd.read_csv(r"Harvard Statements_clean.txt",sep="\t",dtype=str)
        self.iterator = 0
        self.maxiteration = 0
        self.word_rate = 140 #target spoken word rate
        self.pause_count = 8 #pause ocunt in seconds (for full stops)
        self.session_id = str(uuid.uuid1())
    def new_session(self):
        """Start a new session after initiation"""
        self.session_id = str(uuid.uuid1())
        self.iterator = 0
        self.maxiteration = 0
    def shuffle(self):
        """Shuffle the list into a pseudo-random order"""
        self.harvard = self.harvard.sample(frac=1).reset_index(drop=True)
        
    def reset(self):
        """Reset the list to the original order"""
        self.harvard = pd.read_csv(r"Harvard Statements_clean.txt",sep="\t",dtype=str)
    
    def select(self,num):
        """Select the first 'num' of entries required. NB this cannot be reversed.
        
        Parameters
        ----------
        num : number of rows to select
        """
        self.harvard = self.harvard.head(num)
    def iterate(self):
        if self.iterator < len(self.harvard)-1:
            self.iterator += 1
        if self.iterator > self.maxiteration:
            self.maxiteration = self.iterator
    def reverse_iterate(self):
        if self.iterator > 0:
            self.iterator -= 1

    def word_count(self,ID):
        if ID in self.harvard['ID'].values:
            return len(self.harvard[self.harvard['ID']==ID]['Phrases'].iloc[0].split(' '))
        else:
            return -1
    def export_list(self):
        self.select(self.maxiteration) #list up to the last completed recording - what if the user goes back to check?

statements = HarvardStatments()
#statements.shuffle()