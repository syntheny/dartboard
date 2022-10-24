#!/usr/bin/python3 -u
"""
test_dartboard -- Test the DartBoard class

This module is to be run as a stand-alone Python module to test the DartBoard implementation
found in dartboard.py. To run the test module, enter a shell command of:
    python3  dartboard.py

A few Python library modules are used by dartboard and this test module.

Copyright 2022, Sammy Sousa Software, LLC.
"""
from dartboard import DartBoard
from datetime import datetime
import inspect
import random
import time


def prt(text):
    """Print a line of text with a timestamp"""
    print(f"{datetime.now().strftime('%H:%M:%S.%f')}  {text}")


def genDataSet(randomizer=0.0001, numbers=[]):
    """Generate the numbers/probability list, with optional starting list"""
    num = 1
    accum_probability = sum([p for (_, p) in numbers])
    while accum_probability < 1.0:
        prob = random.random() * randomizer
        num += 3
        if prob < 0.00000001: continue
        accum_probability += prob
        numbers.append((num, prob))
    return numbers


def dartboardTest(numbers, count, seed=None, tolerance=10, get_method='two-tier'):
    """Test a dartboard instance by repeatedly getting random numbers

    :param numbers:     List of tuples (number, probability)
    :param count:       Number of iterations
    :param seed:        Optional random seed
    :param tolerance:   +/- percent of expected range before calling an error.
                        If None, checking is not performed.
    :param get_method:  If 'simple', use the simple random.choice method to get a random number,
                        otherwise, use the complex two-tier method.
    :return: counts     counts dictionary.
    """
    caller = inspect.stack()[1].function
    print(f"\n=== {caller} {'='*20}")
    prt(f"Test DartBoard ({get_method}): numbers count: {len(numbers)}, {count} iterations")
    counts = {}
    for n, _ in numbers:
        counts[n] = 0
    start_time = time.time()
    dartboard = DartBoard(numbers, seed=seed, get_method=get_method)
    if dartboard.tier_one_size:
        prt(f"Tier 1 size: {dartboard.tier_one_size}")

    init_time = time.time()
    try:
        for i in range(count):
            number = dartboard.getNumber()
            counts[number] += 1
    except KeyboardInterrupt:
        prt(f"Keyboard interrupt -- iteration #{i}")
        raise
    end_time = time.time()
    collect_time = end_time - init_time

    prt(f"Initialization time= {(init_time-start_time):.9f} sec")
    prt(f"Collect time=        {collect_time:.9f} sec")
    prt(f"Time per iteration=  {(collect_time/count):.9f} sec")

    # Check that the number counts are within tolerance % of their probabilities
    if tolerance is not None:
        prt("Checking counts")
        low_bound = 1.00 - (tolerance / 100)
        high_bound = 1.00 + (tolerance / 100)
        errors = 0
        for n, p in numbers:
            expected_low = int(p * count * low_bound)
            expected_high = int(p * count * high_bound)
            num_count = counts[n]
            if num_count < expected_low:
                prt(f"ERROR: Count {num_count} for number {n} "
                      f"is below expected {expected_low}")
                errors += 1
            elif num_count > expected_high:
                prt(f"ERROR: Count {num_count} for number {n} "
                      f"is above expected {expected_high}")
                errors += 1
            if errors > 50:
                prt("ERROR: Too many errors...stopping check")
                break
    return counts


def testChallenge():
    # Create an instance using the Diveplane challenge example.
    numbers = [(1, 0.25), (2, 0.59), (7, 0.25)]
    db = DartBoard(numbers)
    for i in range(10):
        selection = []
        for _ in range(16):
            selection.append(db.getNumber())
        prt(f"Diveplane challenge example returned numbers #{i+1}: {selection}")


def testChallengeHighIterations():
    # Test high iteration count with the challenge example
    numbers = [(1, 0.25), (2, 0.49999999999), (7, 0.25)]
    counts = dartboardTest(numbers, 10000)
    prt(counts)


def testRepeatableResults():
    # Test for repeatable results, given the same seed value.
    numbers = [(1, 0.25), (2, 0.49999999999), (7, 0.25)]
    seed = time.time()
    counts1 = dartboardTest(numbers, 10000, seed)
    counts2 = dartboardTest(numbers, 10000, seed)
    if counts2 != counts1:
        prt("ERROR: Reuse of seed did not produce same results")


def testSameProbability():
    # Test for large number of values with same probability.
    # Check a tolerance of 30%. The pseudo-random number generator of the python library
    # is rather poor in producing random choices.
    numbers = []
    num_count = 1000
    prob = 1.0 / num_count
    for x in range(num_count):
        numbers.append((x, prob))
    dartboardTest(numbers, 100000, tolerance=30)


def testSameProbabilitySimple():
    # Repeat the same, but with simple random choice method
    numbers = []
    num_count = 1000
    prob = 1.0 / num_count
    for x in range(num_count):
        numbers.append((x, prob))
    dartboardTest(numbers, 100000, tolerance=30, get_method='simple')


def testHighIteration():
    # Test with a very large number of iterations, with a list of varying probabilities.
    # Use a count of 1/2 million to keep the simple text method shorter run time
    numbers = genDataSet(0.0001)
    count = 500000
    dartboardTest(numbers, count, tolerance=None)


def testHighIterationSimple():
    # Test with a very large number of iterations, with a list of varying probabilities,
    # using the simple random.choices method. A count of 1/2 million is used to reduce 
    # the run time of the simple method.
    numbers = genDataSet(0.0001)
    count = 500000
    dartboardTest(numbers, count, tolerance=None, get_method='simple')


def testLargeNumberCount():
    # Use a very low probability to generate a large data set, but use a small count to expedite
    # the test.
    numbers = genDataSet(0.000001)
    count = 1000
    dartboardTest(numbers, count, tolerance=None)


def testBillionIterations():
    # Repeat the same using the two-tier get method, but with a count of 10 billion
    # The simple method is not attempted because it will take hours.
    numbers = genDataSet(0.0001)
    dartboardTest(numbers, 1000000000, tolerance=None)


def testLargeNumberCountSimple():
    # Use a very low probability to generate a large data set, but use a small count to expedite
    # the test.
    numbers = genDataSet(0.00001)
    count = 1000
    dartboardTest(numbers, count, tolerance=None, get_method='simple')

###################################################################################################
###  MAIN PROCEDURE
###################################################################################################
try:
    testChallenge()
    testChallengeHighIterations()
    testRepeatableResults()
    testSameProbability()
    testSameProbabilitySimple()
    testHighIteration()
    testHighIterationSimple()
    testLargeNumberCount()
    testBillionIterations()
    prt("Testing done")
    quit(0)
except KeyboardInterrupt:
    prt("Exit test module due to keyboard interrupt")
    quit(2)

