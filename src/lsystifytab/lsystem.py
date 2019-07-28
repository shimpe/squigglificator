class LSystem(object):
    """
    class to represent an LSystem
    """
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
        """
        set up number of iterations
        :param iterations:
        :return:
        """
        if iterations != self.iterations:
            self.iterations = iterations
            self.cache_valid = False

    def get_iterations(self):
        """
        return number of iterations
        :return: no of iterations
        """
        return self.iterations

    def set_axiom(self, axiom):
        """
        set up axion
        :param axiom: string
        :return:
        """
        if axiom != self.axiom:
            self.axiom = axiom
            self.cache_valid = False

    def get_axiom(self):
        """
        return axiom
        :return: string
        """
        return self.axiom

    def add_rule(self, lhs, rhs):
        """
        add a rule
        :param lhs:
        :param rhs:
        :return:
        """
        if lhs not in self.rules or self.rules[lhs] != rhs:
            self.rules[lhs] = rhs
            self.cache_valid = False

    def get_rule(self, lhs):
        """
        return rhs given lhs of rule
        :param lhs: string
        :return:
        """
        return self.rules[lhs]

    def has_rule(self, lhs):
        """
        return True if lhs is defined as a rule
        :param lhs: string
        :return:
        """
        return lhs in self.rules

    def get_rules(self):
        """
        return list of all rules
        :return: dictionary of lhs -> rhs
        """
        return self.rules

    def set_rules(self, rules):
        """
        set up all rules at once
        :param rules: dictionary of lhs -> rhs
        :return:
        """
        if rules != self.rules:
            self.rules = rules
            self.cache_valid = False

    def set_constants(self, constants):
        """
        define which symbols are to be interpreted as constants (i.e. won't be assigned an lsystem drawing operation)
        :param constants: set of symbols
        :return:
        """
        if self.constants != constants:
            self.constants = set()
            for c in constants:
                self.add_constant(c)
            self.cache_valid = False

    def add_constant(self, constant):
        """
        define additional symbol to be constant
        :param constant: string representing the symbol
        :return:
        """
        if constant not in self.constants:
            self.constants.add(constant)
            self.cache_valid = False

    def has_constant(self, constant):
        """
        check if constant is defined as a constant
        :param constant: string representing symbol
        :return:
        """
        return constant in self.constants

    def get_calculated_string(self):
        """
        return the expanded lsystem
        :return: string
        """
        if self.cache_valid:
            return self.calculated_string
        return self.__calculate_string()

    def length(self):
        """
        return the number of symbols in the expanded lsystem
        :return:
        """
        if self.cache_valid:
            return len(self.calculated_string)
        return len(self.__calculate_string())

    def __calculate_string(self):
        """
        expand the lsystem given the rules and the number of iterations
        :return:
        """
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
