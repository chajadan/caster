'''
_main.py

General enhancements for Dragon NaturallySpeaking.

'''

from dragonfly import (BringApp, Key, Function, Grammar, Playback,
                       IntegerRef, Dictation, Choice, Pause, MappingRule, Text)
from dragonfly.actions.action_focuswindow import FocusWindow

from asynch.hmc import vocabulary_processing
from asynch.sikuli import sikuli
from lib import ccr
from lib import control, settings, navigation, password, context
from lib import utilities


def fix_Dragon_double():
    try:
        lr = control.DICTATION_CACHE[len(control.DICTATION_CACHE) - 1]
        lu = " ".join(lr)
        Key("left/5:" + str(len(lu)) + ", del")._execute()
    except Exception:
        utilities.simple_log(False)
        
def repeat_that(n):
    try:
        if len(control.DICTATION_CACHE) > 0:
            for i in range(int(n)):
                Playback([([str(x) for x in " ".join(control.DICTATION_CACHE[len(control.DICTATION_CACHE) - 1]).split()], 0.0)])._execute()
    except Exception:
        utilities.simple_log(False)

def change_monitor():
    if settings.SETTINGS["miscellaneous"]["sikuli_enabled"]:
        Playback([(["monitor", "select"], 0.0)])._execute()
    else:
        utilities.report("This command requires SikuliX to be enabled in the settings file")
       
class MainRule(MappingRule):
    
    @staticmethod
    def generate_CCR_choices():
        choices = {}
        for ccr_choice in settings.get_list_of_ccr_config_files():
            choices[settings.get_ccr_config_file_pronunciation(ccr_choice)] = ccr_choice
        return Choice("ccr_mode", choices)
    
    mapping = {
    # Dragon NaturallySpeaking management
    '(lock Dragon | deactivate)':   Playback([(["go", "to", "sleep"], 0.0)]),
    '(number|numbers) mode':        Playback([(["numbers", "mode", "on"], 0.0)]),
    'spell mode':                   Playback([(["spell", "mode", "on"], 0.0)]),
    'dictation mode':               Playback([(["dictation", "mode", "on"], 0.0)]),
    'normal mode':                  Playback([(["normal", "mode", "on"], 0.0)]),
    "reboot dragon":                Function(utilities.reboot),
    "fix dragon double":            Function(fix_Dragon_double),
    "add word to vocabulary":       Function(vocabulary_processing.add_vocab),
    "delete word from vocabulary":  Function(vocabulary_processing.del_vocab),
    
    # hardware management
    "(<volume_mode> [system] volume [to] <n> | volume <volume_mode> <n>)": Function(navigation.volume_control, extra={'n', 'volume_mode'}),
    "change monitor":               Key("w-p")+Pause("100")+Function(change_monitor),
    
    # window management
    'minimize':                     Playback([(["minimize", "window"], 0.0)]),
    'maximize':                     Playback([(["maximize", "window"], 0.0)]),
    "remax":                        Key("a-space/10,r/10,a-space/10,x"),
        
    # passwords
    'hash password <text> <text2> <text3>':                    Function(password.hash_password, extra={'text', 'text2', 'text3'}),
    'get password <text> <text2> <text3>':                     Function(password.get_password, extra={'text', 'text2', 'text3'}),
    'get restricted password <text> <text2> <text3>':          Function(password.get_restricted_password, extra={'text', 'text2', 'text3'}),
    'quick pass <text> <text2> <text3>':                       Function(password.get_simple_password, extra={'text', 'text2', 'text3'}),
    
    # mouse alternatives
    "legion":                       Function(navigation.mouse_alternates, mode="legion"),
    "rainbow":                      Function(navigation.mouse_alternates, mode="rainbow"),
    "douglas":                      Function(navigation.mouse_alternates, mode="douglas"),
    
    # miscellaneous
    "<enable_disable> <ccr_mode>":  Function(ccr.set_active, extra={"enable_disable", "ccr_mode"}),
    "again <n> [(times|time)]":     Function(repeat_that, extra={"n"}),
    "begin recording macro":        Function(context.null_func),
    "end recording macro":          Function(context.get_macro_spec),
    "delete recorded macros":       Function(context.delete_recorded_rules),
    "find":                         Key("c-f"),
    "replace":                      Key("c-h"),
    }
    extras = [
              IntegerRef("n", 1, 100),
              Dictation("text"),
              Dictation("text2"),
              Dictation("text3"),
              Choice("enable_disable",
                    {"enable": 1, "disable": 0
                    }),
              Choice("volume_mode",
                    {"set": "set", "increase": "up", "decrease": "down",
                     "up":"up", "down":"down"
                     }),
              generate_CCR_choices.__func__()
             ]
    defaults = {"n": 1, "nnv": 1,
               "text": "", "volume_mode": "setsysvolume",
               "enable":-1
               }


grammar = Grammar('general')
grammar.add_rule(MainRule())
grammar.load()

def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
    ccr.unload()
    sikuli.unload()
