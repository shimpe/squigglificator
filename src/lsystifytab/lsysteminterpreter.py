class LSystemInterpreter(object):
    def __init__(self, lsystem=None, actions=None, globalstate=None):
        self.lsystem = lsystem
        self.actions = actions
        if actions is None:
            self.actions = {}
        self.globalstate = globalstate

    def set_lsystem(self, lsystem):
        self.lsystem = lsystem

    def set_actions(self, actions):
        self.actions = actions

    def add_action(self, symbol, action):
        self.actions[symbol] = action

    def get_action(self, symbol):
        if symbol in self.actions:
            return self.actions[symbol]
        return None

    def set_globalstate(self, globalstate):
        self.globalstate = globalstate

    def get_globalstate(self):
        return self.globalstate

    def size(self):
        return self.lsystem.size()

    def step(self, i):
        str = self.lsystem.get_calculated_string()
        st = str[i] if len(str) > i else ""
        if not self.lsystem.has_constant(st):
            action = self.get_action(st)
            if action:
                gs = self.get_globalstate()
                if gs:
                    self.globalstate = action(gs)
                else:
                    action()

    def stepRange(self, frm, to):
        for i in range(frm, to, 1):
            self.step(i)

    def run(self):
        return self.stepRange(0, self.lsystem.length())
