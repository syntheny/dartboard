#!/usr/bin/python3 -u
"""
DartBoard -- Generate random selection from a given set of numbers,
each with varying probabilities of occurrence.

This module is intended as a library to be imported to get the DartBoard class, using:
    from dartboard import DartBoard

The "DartBoard" class is initialized with one argument which provides the list
of number and probability pairs, and several optional keywords. If the inputs are unacceptable,
a ValueError exception is raised during the instantiation.

The DartBoard "getNumber" method is used to return a randomly selected number for the input list,
using the associated probability of occurrence.

Copyright 2022, Sammy Sousa Software, LLC.
"""
import math
import random


class DartBoard:
    """DartBoard class:

        instantiation:      DartBoard(number_probability_list, [seed], [get_method])

        method:             getNumber()
    """

    def __init__(self, number_probability_list: 'list',
                 *, seed: 'float'=None, get_method: 'str'='two-tier'):
        """
        :param number_probability_list:     List of tuples consisting of (number, probability)
        :keyword seed:                      Optional seed for random number generation
        :keyword get_method:                For test purpose only, if 'simple' use a simple
                                            random.choice method for returned number selection;
                                            otherwise, use the two-tier selection method.
        """

        # Because many transformations are performed on the probabilities, 
        # separate the numbers and probabilities into two lists.
        self.numbers = []
        self.probabilities = []
        for n, p in number_probability_list:
            self.numbers.append(n)
            self.probabilities.append(p)
        self.population_size = len(self.numbers)
            
        self.tier_one_size = 0

        random.seed(seed)

        if get_method == 'simple':
            self.getNumber = self._getNumberSimple
            self.__numbers = []
            self.weights = []
            for (n, p) in number_probability_list:
                self.__numbers.append(n)
                self.weights.append(p)
        else:
            self.getNumber = self._getNumberTwoTier
            self._checkInput()
            self._normalizeProbabilities()
            self._createWeightGroups()
            self._createSelectionTable()

    def _checkInput(self):
        """Verify no duplicate number and probabilities < 1.0"""
        number_dup_check = {}
        for i, n in enumerate(self.numbers):
            if n in number_dup_check:
                raise ValueError(f"Number {n} in position {i} is a "
                                 f"duplicate of position {number_dup_check[n]}")
            number_dup_check[n] = i
        for i, p in enumerate(self.probabilities):
            if p >= 1.0:
                raise ValueError(f"Probability of {p} in position {i} is 1.0 or more")

    def _normalizeProbabilities(self):
        """Discover the minimum probability and use it as a normalizer, such that
        all other probabilities can be expressed as a factor of that minimum.

        For example, in probs of 0.25, 0.3, 0.2, 0.5, the minimum is 0.2. When the values
        are normalized to that minimum, the relative probs become 1.25, 1.5, 1, and 2.5. Thus, the
        probabilities range from 1.0 to a maximum.

        The normalized probabilities are then "reduced" to manageable level by rounding them
        using a decimal count based on the total number of probabilities. This is because when
        the count of probabilities is high, there is little distinction between two nearby
        probabilities. For example, given two probabilities of 0.000023 and 0.000025, the frequency
        of choosing the higher over the lower is negligible.  The rounding process is considered a
        reasonable approach to reducing the number of unique probabilities.

        The number and probabilities lists are then recreated using sorted normalized probabilities.
        """
        self.min_prob = min(self.probabilities)
        self.normalizer = 1.0 / self.min_prob

        rounder = 3 if self.population_size < 1000 else 2 if self.population_size < 100000 else 1

        # Create a new list of probability/number pairs, using rounded normalized probabilities.
        probs = [round(p * self.normalizer, rounder) for p in self.probabilities]
        prob_nums = list(zip(probs, self.numbers))

        # This new list can be sorted on the rounded normalized probabilities, allowing the
        # numbers for same probabilities to be combined into lists. Note that the original
        # numbers and probabilities list can be discarded (to reduce overall memory footprint).
        prob_nums.sort()
        self.probabilities, self.numbers = map(list, zip(*prob_nums))

    def _createWeightGroups(self):
        """Using the sorted normalized probabilities, create a list of weight groups such that
        each list member is composed of the normalized priority and a list of associated numbers.

        [ 1.0, [1, 3, 9, 27, ...],
        [ 1.01, [93, 129, 256, ...], ...
        """
        self.weight_groups = []
        group = []
        previous = -1
        for i in range(self.population_size):
            n = self.numbers[i]
            p = self.probabilities[i]
            if p != previous:
                if previous != -1:
                    self.weight_groups.append((previous,  group))
                group = []
                previous = p
            group.append(n)
        if group:
            self.weight_groups.append((p, group))

        self.tier_one_size = len(self.weight_groups)

    def _createSelectionTable(self):
        """Create a random selection table where each weight group is repeated for
        respective probability and for each member. The number

        Because of the possible immensity of selection table, the corresponding
        dictionary element is deleted (popped) as creation of the table proceeds.
        """
        self.selection_table = []
        for p,nums in self.weight_groups:
            nums_len = len(nums)
            w = int(p * nums_len)
            for _ in range(w):
                self.selection_table.append((nums_len, nums))
        self.selection_table_len = len(self.selection_table)

    def _getNumberSimple(self):
        """Return a randomly selected number using the stock random.choices method"""
        return random.choices(self.__numbers, self.weights, k=1)[0]

    def _getNumberTwoTier(self):
        """Return a randomly selected number using the two-tier look-up scheme"""
        rand = random.randrange(self.selection_table_len)
        nums_len, nums = self.selection_table[rand]
        if nums_len == 1:
            number = nums[0]
        else:
            rand = random.randrange(nums_len)
            number = nums[rand]
        return number

    def getNumber(self):
        """Return a randomly selected number--virtual method replaced with simple or two-tier"""
        print("ERROR: getNumber not implemented")
