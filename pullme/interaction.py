class Interaction(object):

    @classmethod
    def confirm_continue(cls, settings, confirmation_message):
        if settings['assume']: return
        confirm = raw_input('%s Continue? [Yna?] ' % confirmation_message)
        if confirm.lower() == 'n':
            exit(1)
        elif confirm.lower() == 'a':
            settings['assume'] = True
        elif confirm == '?':
            print """y:  yes, continue (default)
n:  no, exit immediately
a:  turn on assume-mode for this and all future prompts
?:  print this message and ask again"""
            cls.confirm_continue(settings, confirmation_message)
        elif confirm and confirm.lower() != 'y':
            print "I don't know what you mean by '%s'" % confirm
            cls.confirm_continue(settings, confirmation_message)

    @classmethod
    def confirm_assumptions(cls, settings, confirm_message,
                            correction_message, **kwargs):
        if settings['assume']: return kwargs
        confirm = raw_input('%s [Ynaq?] ' % confirm_message)
        corrections = {}
        if confirm.lower() == 'n':
            for correction in kwargs:
                corrections[correction] = raw_input(
                                          correction_message % correction)
            return corrections
        elif confirm.lower() == 'a':
            settings['assume'] = True
            return kwargs
        elif confirm.lower() == 'q':
            exit(0)
        elif confirm == '?':
            print """y:  yes, this is correct (default)
n:  no, prompt for a corrected value
a:  turn on assume-mode for this and all future prompts
q:  exit immediately
?:  print this message and ask again"""
            return cls.confirm_assumptions(settings, confirm_message,
                                           correction_message, **kwargs)
        elif confirm and confirm.lower() != 'y':
            print "I don't know what you mean by '%s'" % confirm
            return cls.confirm_assumptions(settings, confirm_message,
                                           correction_message, **kwargs)
        else:
            return kwargs

