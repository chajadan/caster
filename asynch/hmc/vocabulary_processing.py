'''
Created on Dec 24, 2014

@author: dave
'''
import re

import dragonfly
from dragonfly.actions.action_focuswindow import FocusWindow
from dragonfly.actions.action_key import Key
from dragonfly.actions.action_waitwindow import WaitWindow

from asynch.hmc import squeue
from asynch.hmc import h_launch, homunculus
from lib import utilities, context, settings


def add_vocab():
    engine=dragonfly.get_engine()
    if engine.name!="natlink":
        utilities.report("feature unavailable in your speech recognition engine", speak=True)
        return
    
    
    # attempts to get what was highlighted first
    highlighted=context.read_selected_without_altering_clipboard(True)
    
    # change the following regex to accept alphabetical only
    disallow="^[A-Za-z]*$"
    selected=None
    
    if highlighted[0]==0 and highlighted[1]!="":
        if not re.match(disallow, highlighted[1]):
            utilities.report("only used for single words", speak=True)
            return
        
        selected=highlighted[1]
    try: 
        squeue.add_query(process_set)
        h_launch.launch(settings.QTYPE_SET, selected)
        WaitWindow(title=settings.HOMUNCULUS_VERSION+settings.HMC_TITLE_VOCABULARY, timeout=5)._execute()
        FocusWindow(title=settings.HOMUNCULUS_VERSION+settings.HMC_TITLE_VOCABULARY)._execute()
        Key("tab")._execute()
    except Exception:
        utilities.simple_log(False)

def del_vocab():
    try: 
        squeue.add_query(process_delete)
        h_launch.launch(settings.QTYPE_REM)
        WaitWindow(title=settings.HOMUNCULUS_VERSION+settings.HMC_TITLE_VOCABULARY, timeout=5)._execute()
        FocusWindow(title=settings.HOMUNCULUS_VERSION+settings.HMC_TITLE_VOCABULARY)._execute()
        Key("tab")._execute()
    except Exception:
        utilities.simple_log(False)

def process_set(data):
    ''''''
    word=data["word"]
    pronunciation=data["pronunciation"]
    if pronunciation=="":
        pronunciation=None
    word_info=data["word_info"]
    #missingno
    import natlink
    result=0
    if pronunciation==None:
        result=natlink.addWord(word, word_info)
        if result==0 and data["force"]==1:
            process_delete(data)
            result=natlink.addWord(word, word_info)
    else:
        result=natlink.addWord(word, word_info, str(pronunciation))
        if result==0 and data["force"]==1:
            process_delete(data)
            result=natlink.addWord(word, word_info, str(pronunciation))
    
    if result==1:
        utilities.report("word added successfully: "+word, False)
    else:
        utilities.report("word add failed: "+word, False)

def process_delete(data):
    import natlink
    natlink.deleteWord(data["word"])
    