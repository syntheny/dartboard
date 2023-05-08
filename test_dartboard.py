#!/usr/bin/python3 -u
"""
test_dartboard -- Test the DartBoard class

Perform unit testing and/or functional testing of the DartBoard number/probability sampling.

This module is to be run as a stand-alone Python module to test the DartBoard implementation
found in dartboard.py. To run the unit test suite of the test module, enter a shell command of:
    python3  test_dartboard.py
or  python3  test_dartboard.py  unit

To run the functional test suite, which can take many minutes, enter:
    python3  test_dartboard.py  func

To run both test suites:
    python3  test_dartboard.py  unit  func

Note: The module prevents running the functional test suite under Python or Pycharm debug;
      however, this may be overridden using the "allow" option on the command line.

A few Python library modules are used by dartboard and this test module.

Copyright 2023, Sammy Sousa Software, LLC.
"""
import os

from dartboard import DartBoard
from datetime import datetime
import inspect
from math import ceil
import random
import sys
import time
import unittest


leading_nl = True

def prt(text):
    """Print a line of text with a timestamp"""
    global leading_nl
    if leading_nl:
        print('\n')
        leading_nl = False
    print(f"{datetime.now().strftime('%H:%M:%S.%f')}  {text}")
    

class DBTest:
    """Create a DartBoard instance and offer validation testing"""
    db: DartBoard = None
    num_list: [(int, float)] = []
    randomizer: float = 0.0

    def create(self, *args, **kwargs):
        """Create a DartBoard instance"""
        self.num_list = kwargs.get('self.num_list')
        errs = kwargs.get('errs')
        seed = kwargs.get('seed')
        get_method = kwargs.get('get_method', 'two-tier')
        if self.num_list is None and args:
            self.num_list = args[0]
        if errs:
            if not isinstance(errs, (list, tuple)):
                errs = [errs]
            errs = [err.__class__.__name__ for err in errs]
        try:
            self.db = DartBoard(self.num_list, seed=seed, get_method=get_method)
            if errs:
                raise AssertionError(f"DartBoard instantiated, but expected an error:"
                                     f" {str(errs)}")
        except KeyboardInterrupt:
            print(f"Keyboard interrupt")
            sys.exit(3)
        except Exception as exc:
            if errs:
                if exc.__class__.__name__ in errs:
                    return
            raise AssertionError(str(exc))

        if self.db.tier_one_size:
            prt(f"Tier 1 size: {self.db.tier_one_size}")

        self.db.createTable()

        return self.db

    def genDataSet(self, randomizer=0.0001, numbers=None):
        """Generate the numbers/probability list, with optional starting list of numbers and 
        probabilities. 
        
        The randomizer argument indicates the approximate size of the number set. 
        A randomizer of 1 would create a number set of 1; randomizer of 0.1 would create a small 
        number population of around 10 to 20. The smaller the randomized, the larger the number 
        population. 
        """
        self.randomizer = randomizer
        num = 1
        if numbers is None:
            numbers = []
        rand_low = randomizer * 0.5
        rand_high = randomizer * 1.5
        if rand_high > 1.0:
            rand_high = randomizer
        accum_probability = sum([p for (_, p) in numbers])
        while True:
            prob = random.uniform(rand_low, rand_high)
            accum_probability += prob
            if accum_probability > 1.00:
                prob = 1.0 - (accum_probability - prob)
                if prob < randomizer * 0.05:
                    break
                numbers.append((num, prob))
                break
            numbers.append((num, prob))
            num += 3
        prt(f"Generated {len(numbers)} number/probability pairs")
        return numbers

    def sample(self, sample_size=10, tolerance=None):
        """Validate the DartBoard instance table, for {sample_size} iterations"""
        counts = {n[0]: 0 for n in self.num_list}
        interrupted = False
        start_time = time.time()
        try:
            for i in range(sample_size):
                number = self.db.getNumber()
                counts[number] += 1
        except KeyboardInterrupt:
            interrupted = True
            prt(f"Keyboard Interrupt -- {i} samples collected")
        end_time = time.time()
        collect_time = end_time - start_time

        prt(f"Collect time =        {collect_time:.9f} sec")
        prt(f"Time per sample =     {(collect_time/sample_size):.9f} sec")

        if interrupted:
            sys.exit(3)

        # Check that the number counts are within tolerance % of their probabilities
        errors = 0
        if tolerance is not None:
            tolerance_percent = tolerance * 0.01
            deviations = {}
            accum_deviation = 0
            allowed_deviation = sample_size * (self.randomizer * 20.0) * tolerance_percent
            for n, p in self.num_list:
                ideal_count = int(ceil(p * sample_size))
                if ideal_count > 1:
                    actual_count = counts[n]
                    diff = abs(actual_count - ideal_count)
                    if diff > allowed_deviation:
                        deviations[n] = diff
                        accum_deviation += diff
            if deviations:
                avg_deviation = accum_deviation / len(deviations)
                if abs(avg_deviation - allowed_deviation) > 2:
                    if avg_deviation > (allowed_deviation * (1 + tolerance_percent)):
                        prt(f"ERROR: Excessive deviations in sampling: allowed {allowed_deviation} "
                            f"actual {accum_deviation / len(deviations)}")
        if errors:
            raise AssertionError("Error in DartBoard sampling validation")
        return counts


class DartBoardUnitTest(unittest.TestCase, DBTest):

    def setUp(self):
        global leading_nl
        leading_nl = True

    def test_Empty(self):
        # A dartBoard must have at least one number/probability pair
        self.create([], errs=ValueError())

    def test_very_small_population(self):
        num_list = self.genDataSet(1)
        self.create(num_list)

    def test_small_population(self):
        num_list = self.genDataSet(0.1)
        self.create(num_list)

    def testChallenge(self):
        # Create an instance using the Requirements example and run several times to show
        # various sample sets.
        num_list = self.genDataSet(0.01, [(1, 0.25), (2, 0.50), (7, 0.25)])
        db = self.create(num_list)
        for i in range(10):
            selection = []
            for _ in range(16):
                selection.append(db.getNumber())
            prt(f"Requirements example returned num_list #{i+1}: {selection}")

    def test_large_population(self):
        num_list = self.genDataSet(0.001)
        self.create(num_list)

    def test_duplicate_number(self):
        num_list = self.genDataSet(0.001)
        third_way = len(num_list) // 3
        half_way = len(num_list) // 2
        num_list[third_way] = num_list[half_way]
        self.create(num_list, errs=ValueError())

    def test_prob_too_high(self):
        num_list = self.genDataSet(0.001)
        half_way = len(num_list) // 2
        num_list[half_way] = (num_list[half_way][0], 2.345)
        self.create(num_list, errs=ValueError())

    def test_simple_method(self):
        num_list = self.genDataSet(0.1)
        self.create(num_list, get_method='simple')

    def test_two_tier_method(self):
        num_list = self.genDataSet(0.01)
        self.create(num_list, get_method='two-tier')

    def test_invalid_method(self):
        num_list = self.genDataSet(0.1)
        self.create(num_list, get_method='three-tier', errs=ValueError())

    def test_seed(self):
        num_list = self.genDataSet(0.01)
        self.create(num_list, seed=time.time())

    def test_repeated_seed(self):
        num_list = self.genDataSet(0.01)
        db1 = self.create(num_list, seed=12345)
        db2 = self.create(num_list, seed=12345)
        self.assertEqual(db1.selection_table, db2.selection_table,
                         "Same random seed did not produce identical sample sets")

    def test_small_population_validate(self):
        num_list = self.genDataSet(0.1)
        self.create(num_list)
        self.sample(500, tolerance=None)

    def test_same_probability(self):
        # Test for large number of values with same probability.
        # Check a tolerance of 30%. The pseudo-random number generator of the python library
        # is rather poor in producing random choices.
        num_list = []
        num_count = 1000
        prob = 1.0 / num_count
        for x in range(num_count):
            num_list.append((x, prob))
        num_list = self.genDataSet(0.0001, num_list)
        self.create(num_list)
        self.sample(100000, tolerance=30)

    def test_same_probability_simple(self):
        # Test for large number of values with same probability.
        # Check a tolerance of 30%. The pseudo-random number generator of the python library
        # is rather poor in producing random choices.
        num_list = []
        num_count = 1000
        prob = 1.0 / num_count
        for x in range(num_count):
            num_list.append((x, prob))
        num_list = self.genDataSet(0.0001, num_list)
        self.create(num_list, get_method='simple')
        self.sample(100000, tolerance=30)

    def test_large_population_validate(self):
        num_list = self.genDataSet(0.001)
        self.create(num_list)
        self.sample(5000, tolerance=10)

    def test_very_large_population_validate(self):
        num_list = self.genDataSet(0.00001)
        self.create(num_list, get_method='two-tier')
        self.sample(500000, tolerance=20)


class DartBoardFunctionalTest(unittest.TestCase, DBTest):
    """Long-term functional tests to generate and verify large number of samples"""

    def setUp(self):
        global leading_nl
        leading_nl = True

    def test_high_iterations(self):
        # Test with a very large number of iterations, with a list of varying probabilities.
        # Use a count of 1/2 million to keep the simple text method shorter run time
        num_list = self.genDataSet(0.0001)
        self.create(num_list)
        self.sample(500000, tolerance=None)

    def test_high_iterations_simple(self):
        # Test with a very large number of iterations, with a list of varying probabilities,
        # using the simple random.choices method. A count of 1/2 million is used to reduce
        # the run time of the simple method. Compare the collection time of this test case vs the
        # previous test_high_iterations which uses the two-tier method (should be about 200x
        # difference).
        num_list = self.genDataSet(0.0001)
        self.create(num_list, get_method='simple')
        self.sample(500000, tolerance=None)

    def test_large_sample_size(self):
        # Use a very low probability to generate a large data set, but use a small count to expedite
        # the test.
        num_list = self.genDataSet(0.000001)
        self.create(num_list)
        self.sample(1000, tolerance=None)

    def test_large_sample_size_validate(self):
        num_list = self.genDataSet(0.00001)
        self.create(num_list, get_method='two-tier')
        self.sample(500000, tolerance=20)

    def test_huge_sample_size(self):
        # Repeat the same using the two-tier get method, but with a count of 10 million
        # The simple method is not attempted because it will take hours.
        count = 10_000_000
        num_list = self.genDataSet(0.000001)
        self.create(num_list, get_method='two')
        self.sample(count, tolerance=None)


###################################################################################################
###  MAIN PROCEDURE
###################################################################################################

# Determine if running under debug (Python debugger or Pycharm debug)
in_debug = False
mods = list(sys.modules.keys())
for mod in mods:
    if 'dbg' in mod or 'debug' in mod:
        in_debug = True
        break

# Request for unit tests or functional tests? Either or both. If not specified, only unit tests.
request_ut = False
request_ft = False
allow_debug = False
args = sys.argv[1:]
while args:
    arg = args.pop(0).lower()
    if arg in ['u', 'unit', 'unittest', 'unitttests']:
        request_ut = True
    elif arg in ['f', 'ft', 'func', 'functional', 'fvt']:
        request_ft = True
    elif arg in ['d', 'debug', 'allow']:
        allow_debug = True
    else:
        print(f"ERROR: Invalid command argument: {arg}")
        sys.exit(2)
if not request_ut and not request_ft:
    request_ut = True
if request_ft and not allow_debug and in_debug:
    print(f"ERROR: Using Python Debug for functional testing requires 'debug' override")
    sys.exit(2)


def addTestsToSuite(suite, test_class):

    # Get the names from the test class. unittest.loader returns the list in sorted
    # order, but the unsorted order (as presented in the source file) is required.
    lineno_names = []
    for name in dir(test_class):
        if name.startswith('test'):
            func = getattr(test_class, name)
            if callable(func):
                lineno_names.append((func.__code__.co_firstlineno, name))
    lineno_names.sort()
    names = [ln[1] for ln in lineno_names]
    suite.addTests(map(test_class, names))


try:
    result = unittest.TestResult()
    suite = unittest.TestSuite()

    if request_ut:
        addTestsToSuite(suite, DartBoardUnitTest)
    if request_ft:
        addTestsToSuite(suite, DartBoardFunctionalTest)

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    prt("Testing done")
    quit(0)
except KeyboardInterrupt:
    prt("Exit test module due to keyboard interrupt")
    quit(2)
