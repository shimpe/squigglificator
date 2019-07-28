class LSystemInterpreter(object):
    """
    class to add an interpretation to lsystems
    """
    def __init__(self, lsystem=None, actions=None, globalstate=None):
        self.lsystem = lsystem
        self.actions = actions
        if actions is None:
            self.actions = {}
        self.globalstate = globalstate

    def set_lsystem(self, lsystem):
        """
        set up lsystem
        :param lsystem: LSystem instance
        :return:
        """
        self.lsystem = lsystem

    def set_actions(self, actions):
        """
        define semantic actions as dictionary of symbol -> function
        each such function needs to take a global state parameter, and return an updated global state
        :param actions: dictionary of symbol->function
        :return:
        """
        self.actions = actions

    def add_action(self, symbol, action):
        """
        register an action for a given symbol
        :param symbol: string
        :param action: function needs to take a global state parameter, and return an updated global state
        :return:
        """
        self.actions[symbol] = action

    def get_action(self, symbol):
        """
        lookup action for symbol
        :param symbol: string
        :return: function (or None, if no action defined for symbol)
        """
        if symbol in self.actions:
            return self.actions[symbol]
        return None

    def set_globalstate(self, globalstate):
        """
        define global state
        :param globalstate: (often a dictionary of key->value pairs, but it's up to you)
        :return:
        """
        self.globalstate = globalstate

    def get_globalstate(self):
        """
        return global state
        :return:
        """
        return self.globalstate

    def size(self):
        """
        return size of internal LSystem
        :return:
        """
        return self.lsystem.size()

    def step(self, i):
        """
        interpret the ith symbol in the expanded LSystem
        by calling the action associated to the symbol.
        Calling this action will update the global state if one is defined.
        If no global state was ever defined, actions are called without global state argument.
        :param i: index in expanded LSystem
        :return:
        """
        calculated = self.lsystem.get_calculated_string()
        st = calculated[i] if len(calculated) > i else ""
        if not self.lsystem.has_constant(st):
            action = self.get_action(st)
            if action:
                gs = self.get_globalstate()
                if gs:
                    self.globalstate = action(gs)
                else:
                    action()

    def stepRange(self, frm, to):
        """
        interpret a range of expanded LSystem symbols, see step
        :param frm:
        :param to:
        :return:
        """
        for i in range(frm, to, 1):
            self.step(i)

    def run(self):
        """
        interpret all expanded LSystem symbols, see step.
        :return:
        """
        return self.stepRange(0, self.lsystem.length())
