class LSystem(object):
    def __init__(self, iterations=None, axiom=None, constants=None, rules=None):
        self.axiom = axiom
        if axiom is None:
            self.axiom = ""

        self.rules = rules
        if rules is None:
            self.rules = {}

        self.constants = constants
        if constants is None:
            self.constants = set()

        self.iterations = iterations
        if iterations is None:
            self.iterations = 0

        self.cache_valid = False
        self.calculated_string = ""

    def set_iterations(self, iterations):
        if iterations != self.iterations:
            self.iterations = iterations
            self.cache_valid = False

    def get_iterations(self):
        return self.iterations

    def set_axiom(self, axiom):
        if axiom != self.axiom:
            self.axiom = axiom
            self.cache_valid = False

    def get_axiom(self):
        return self.axiom

    def add_rule(self, lhs, rhs):
        if lhs not in self.rules or self.rules[lhs] != rhs:
            self.rules[lhs] = rhs
            self.cache_valid = False

    def get_rule(self, lhs):
        return self.rules[lhs]

    def has_rule(self, lhs):
        return lhs in self.rules

    def get_rules(self):
        return self.rules

    def set_rules(self, rules):
        if rules != self.rules:
            self.rules = rules
            self.cache_valid = False

    def set_constants(self, constants):
        if self.constants != constants:
            self.constants = set()
            for c in constants:
                self.add_constant(c)
            self.cache_valid = False

    def add_constant(self, constant):
        if constant not in self.constants:
            self.constants.add(constant)
            self.cache_valid = False

    def has_constant(self, constant):
        return constant in self.constants

    def get_calculated_string(self):
        if self.cache_valid:
            return self.calculated_string
        return self.__calculate_string()

    def length(self):
        if self.cache_valid:
            return len(self.calculated_string)
        return len(self.__calculate_string())

    def __calculate_string(self):
        self.calculated_string = self.axiom
        for i in range(self.iterations):
            newstring = ""
            for c in self.calculated_string:
                rule_found = False
                for lhs in self.rules:
                    if not rule_found and c == lhs:
                        # match!
                        newstring = newstring + self.rules[lhs]
                        rule_found = True
                if not rule_found:
                    newstring = newstring + c
            self.calculated_string = newstring
        self.cache_valid = True
        return self.calculated_string
