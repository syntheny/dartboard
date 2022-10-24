Programming Challenge: Large Random Number Generator
====================================================

The Challenge
-------------

Write a class or module that has a function or method that returns a random number chosen from a set of numbers where each has a specified probability.  For example, the input could be an associative array consisting of:
        1 => 0.25
        2 => 0.5
        7 => 0.25
When the function or method is called repeatedly, the above input might yield 2, 7, 1, 1, 2, 2, 2, 7, 2, etc.

### Additional requirements:
* The random number generator will be called billions of times, so performance is important.
* The probabilities will be updated very infrequently, if ever.  But neither the probabilities nor their distribution is known before processing.
* The size of the set of numbers will typically be at least a thousand, possibly well into the millions, each with its own probability.  No other number should be returned except for those specified in the input.
* The class or module should support the ability to replay the same sequence of random numbers regardless of platform it is compiled on and regardless of whether the program is directly translated to another programming language.  The class does not need to read or write to any device, but it is desirable to minimize the amount of data stored to reproduce the replay.
* The code must be written such that a competent developer could translate your code directly into another common programming language without having to retrieve any code not written by you.
* You can use whatever programming language you like as long as it is suitable for practical use (e.g., Befunge and INTERCAL are not acceptable but Python, C++, or Haskell is), has a visible community online, and is one we can freely and easily download and setup to interpret or run the code (e.g., MATLAB is not acceptable, but Octave is).


Requirements Analysis
---------------------

Create a class design that generates a series of “random” numbers:
* Initialization
  * A set of numbers of any size, each with an associated probability of occurrence.
  * The size of the set may be quite large, millions or more.
  * Once the object is established, the probabilities of the numbers will not change.
  * Because any subsequent instance must be able to “replay” random selection, a random seed may also be specified as an initial input parameter.
* Generator Method Output
  * Returns a number from the input set.
  * Number is randomly selected, based on the probability of occurrence.
  * Generator method may be called many times.
* Other requirements
  * Instantiation of the class multiple times may be required to reproduce the same results each time (i.e., to “replay” the same sequence).
  * Any random number generation used by the implementation of the class should produce the same results regardless of the RNG algorithm or language used to implement the RNG.
* Limitations
  * Limited memory space. 
  * No file storage should be required.
  * The performance of the generator method should be “reasonable” when the data set is large and the generator is called numerous times.
* Analysis
  * For this analysis, assume S is the set of return numbers with N elements, and each element is a tuple (Ni, Pi). 
  * The sum of probabilities of all input numbers should equal 1.0.
  * For a given probability Pn, there may be multiple return numbers associated with that probability. Thus, there may be multiple subsets of return numbers all having the same unique probability. In that subset of numbers with equal probability, the subset is assigned an aggregate probability which is the sum of the probability of each member. For example, with 1=>0.25, 2=>0.5, and 7=>0.25, two subsets emerge: [1, 7] with probability 0.5 and [2] with probability 0.5.
  * The probability of selecting the subset of numbers is the aggregate probability, but once that subset is selected, the probability of selecting a member is the same for all members.
  * To simplify the analysis, the probabilities are transformed to “weights” rather than a probability. First, the minimum probability is found, then all probabilities are normalized to that minimum such that the minimum is 1.0. 
  * Then, the probabilities are rounded to only a few decimal places, depending on the total number of numbers. When the number of different probabilities is large, there is a point at which the difference between two adjacent probabilities is negligible, such as 0.000123 and 0.00125 when N > 10000. Thus, these probabilities can be treated as identical weights. 
  * After conversion to weighting, the sum of all probabilities is no longer required to equal 1.0. For example, where probabilities are 0.1, 0.25, and 0.5, the weights may be 10, 25, and 50 which maintains the probability ratios.
  * The implementation should be able to “cache” the set of numbers and weights. Sufficient space is assumed available to retain the data set in memory. With 10M elements, 1GB memory should be sufficient. Note that if virtual (paged) memory is used, performance of the operation may be impacted, but that is a subject of a follow-up analysis.
  * Because the random number generator algorithm selected for an implementation may vary from one language to another, the implementation should include the source of the RNG method.
* Testability
  * The implementation must also include a means of verifying:
    * The random selection of numbers. 
    * Repeatable selection, using a specified random seed.
    * Handling of large numbers of numbers.
    * Handling of large iterations of calls to retrieve the random numbers.
  * In Python, the random library has a “choices” method wherein the list of numbers and a list of the associated probabilities can be specified: random.choices(numbers, probabilities). This is the simplest form and would likely be selected by the programmer. The testing should also use this simple method and compare duration of the simple solution to that of the challenge solution.

General Design
--------------

* Python 3 is used for a quick modeling of the implementation; however, it should be rewritten in C++ to improve performance by at least 20-fold.
* A class is envisioned that manages the list of return values and associated probabilities, as well as provides a “generator” method that randomly selects a number and returns it (this is not a true generator, so use of the “yield” term is not appropriate).
* A random number generator function is envisioned that will select and return a quasi-random integer (not float). A function from a stock random library may initially be used as the random integer generator (RIG), but to maintain compatibility among all languages, the RIG should be implemented in this module.
* A test component is envisioned which applies various test scenarios to the class instantiation and number generator.

Specific Design
---------------

“**_DartBoard_**” Class Design
* Because the random selection of a number with ranging probabilities is like throwing darts at a board while blindfolded, the class is aptly named “**DartBoard**”.
* Initializer method
  * The class instance initializer will take input two arguments:
    * A mutable list of mutable lists, where each sublist contains the return number and its probability expressed as a real number between 0.0 and 1.0 (Note: the lists should be mutable so that the same heap memory may be used to hold the transformational data to mitigate excessive memory grab.
    * An optional random number generator seed value to “prime” the RNG algorithm. If not specified, the RNG may select the seed.
  * The initializer will examine the list to:
    * Assure no repeating return values. If a duplicate, raise an error.
    * Assure no probability exceeds 1.0.
    * Determine the total number of return values.
  * The class initializer will examine the collection of probabilities and establish the weight transformation.
* Because of the data set is potentially very large, a two-tier random selection scheme is considered, but final choice of this scheme depends on the testing with the simpler random.choices call:
  * The data set is consumed during initialization such that for each duplicate probability (after normalizing to integer weight representation), a list of associated input numbers is maintained for each weight. A random selection using a random integer index is first applied to this table.
  * Once the weighted subset is selected, a random integer index is used to select within that subset for the return number.
* The two-tier scheme is expected to use substantially less memory than the stock “random.choice” method. 
* The two-tier scheme is also expected to be much faster than random.choice.


Post-Implementation Analysis
----------------------------

Two Python source files are developed for this exercise: a “dartboard.py” importable library module, and “test_dartboard.py” free-standing Python module to exercise and test the class and getNumber method.

To run the test, install the two source files (in a virtual environment or not). The testing will require a Python 3 distribution along with the random, time, datetime, and inspect libraries (usually standard with the minimal Python distribution). Then, enter on a shell command line (the Python interpreter executable name may differ):
	
    python3  test_dartboard.py

The testing for the DartBoard instantiation and “getNumber” method revealed some interesting information (timing performed on a 4-core i5 laptop):

* Using small count of numbers and iterations, the difference between the two-tier scheme and use of the random.choices call is quite significant. Initialization of the two-tier scheme does take more time, 25 seconds for a population of 500K, and up to 2 minutes for a population of 2M numbers whereas the random.choices method takes only a fraction of a second. 
* Retrieval of 500K numbers takes less than a second with the two-tier, but the random.choices takes nearly 3 minutes. 

The test results are found in “dartboard_test_results.txt”. A test case generally shows the times in seconds to initialize the class instance and to perform a repetition of getNumber calls. Sometimes, the times shown are 0 – this is likely because of Windows OS does not properly provide the duration of very short time intervals.


