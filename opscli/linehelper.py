class LineHelper(object):

    def qhelp(self, line):
        pass

    def complete(self, line, show_all):
        pass


class ContextLineHelper(LineHelper):

    def qhelp_items(self, line):
        '''Called when ? is pressed. line is the text up to that point.
        Returns help items to be shown, as a list of (command, helptext).'''
        items = []
        words = line.split()
        if not words:
            # On empty line: show all commands in this context.
            return sorted(self.context.get_help_subtree())

        matches = self.context.find_command(words)
        if not matches:
            raise Exception(CLI_ERR_NOMATCH)
        if line[-1].isspace():
            # Last character is a space, so whatever comes before has
            # to match a command unambiguously if we are to continue.
            if len(matches) != 1:
                raise Exception(CLI_ERR_AMBIGUOUS)

            cmd_complete = False
            # TODO(bluecmd): This cuts all the way through the abstraction
            # Let's move get_help_subtree to cmdobj and use it here
            cmdobj = matches[0]
            for key in cmdobj.branch:
                items.append(self.context.helpline(cmdobj.branch[key], words))
            if hasattr(cmdobj, 'options'):
                opt_words = words[len(cmdobj.command):]
                if not opt_words and flags.F_NO_OPTS_OK in cmdobj.flags:
                    # Didn't use any options, but that's ok.
                    cmd_complete = True
                elif len(opt_words) == len(cmdobj.options):
                    # Used all options, definitely a complete command.
                    cmd_complete = True
                elif opt_words:
                    # Only some options were used, check if we missed
                    # any required ones.
                    try:
                        opt_tokens = tokenize_options(opt_words,
                                                      cmdobj.options)
                        check_required_options(opt_tokens, cmdobj.options)
                        # Didn't bomb out, so all is well.
                        cmd_complete = True
                    except:
                        pass
                items.extend(options.help_options(cmdobj, words))
            else:
                # Command has no options.
                cmd_complete = True
            if cmd_complete and hasattr(cmdobj, 'run'):
                items.insert(0, stringhelp.Str_help(('<cr>', cmdobj.__doc__)))
        else:
            # Possibly incomplete match, not ending in space.
            for cmdobj in matches:
                if len(words) <= len(cmdobj.command):
                    # It's part of the command
                    # TODO(bluecmd): This cuts all the way through the abstraction
                    # Let's move get_help_subtree to cmdobj and use it here
                    items.append(self.context.helpline(cmdobj, words[:-1]))
                else:
                    # Must be an option.
                    items.extend(options.complete_options(cmdobj, words))
        return sorted(items)

    def complete(self, line):
        if not line:
            return
        words = line.split()
        matches = self.context.find_command(words)
        if not matches:
            return

        items = []
        if line[-1].isspace():
            # Showing next possible words or arguments.
            if len(matches) != 1:
                # The line doesn't add up to an unambiguous command.
                return

            if self.reader.last_event != 'complete':
                # Only show next words/arguments on second tab.
                return

            cmdobj = matches[0]
            # Strip matched command words.
            words = words[len(cmdobj.command):]

            if cmdobj.branch.keys():
                # We have some matching words, need to list the rest.
                items = cmdobj.branch.keys()
            else:
                # No more commands branch off of this one. Maybe it
                # has some options?
                items = options.help_options(cmdobj, words)
        else:
            # Completing a word.
            if len(matches) == 1:
                # Found exactly one completion.
                if len(words) <= len(matches[0].command):
                    # It's part of the command
                    cmpl_word = matches[0].command[len(words) - 1]
                else:
                    # Must be an option.
                    cmpl_word = None
                    cmpls = options.complete_options(matches[0], words)
                    if len(cmpls) == 1:
                        # Just one option matched.
                        cmpl_word = cmpls[0]
                    elif len(cmpls) > 1:
                        # More than one match. Ignore the first completion
                        # attempt, and list all possible completions on every
                        # tab afterwards.
                        if self.last_event == 'complete':
                            for cmdobj in matches:
                                items.append(' '.join(cmpls))
                if cmpl_word:
                    cmpl = cmpl_word[len(words[-1]):]
                    self.reader.insert(cmpl + ' ')
            else:
                # More than one match. Ignore the first completion attempt,
                # and list all possible completions on every tab afterwards.
                if self.reader.last_event == 'complete':
                    for cmdobj in matches:
                        items.append(' '.join(cmdobj.command))
        if not items:
            return


