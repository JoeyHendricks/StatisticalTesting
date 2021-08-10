import numpy as np


class PercentileHypothesisTest:
    """
    A percentile hypothesis test to find the difference in the behaviour of two populations.
    This hypothesis test is originally designed to pick up changes in measurement patterns.

    For this to work properly this test expects a large baseline and benchmark population.
    This is why this test works great for finding spotting difference in large performance test
    results sets in an automated way.

    Please share feedback and let me know if you encounter any type 1 or type 2 errors using this test.
    """
    # The change matrix
    MATRIX = [
        [2, 0.07688676],
        [4, 0.13395531],
        [8, 0.20272898],
        [16, 0.21770635],
        [32, 0.36872261],
    ]
    # The percentile curve distribution
    PERCENTILE_DISTRIBUTION = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]

    def __init__(self, group_a: list, group_b: list) -> None:
        """
        Will construct the class and calculate a list of percentiles for both group A and B.
        The list of percentiles used range from 5th to 95th.

        :param group_a: An list of floats of the A population (baseline).
        :param group_b: An list of floats of the B population (benchmark).
        """
        self.group_a = [
            self._calculate_percentile(group_a, percentile) for percentile in self.PERCENTILE_DISTRIBUTION
        ]
        self.group_b = [
            self._calculate_percentile(group_b, percentile) for percentile in self.PERCENTILE_DISTRIBUTION
        ]
        self._p_value = None
        self.absolute_scores = []

    @staticmethod
    def _calculate_percentile(array: list, percentile: int) -> float:
        """
        Used to calculate the percentile over the given array.
        :return: a float number of the requested percentile
        """
        return float(np.percentile(array, percentile))

    def _score_percentage_variance_number_against_change_matrix(self, number: float) -> float:
        """
        Will score the number against the change matrix.
        More broken "thresholds" will result in a lower score for this percentile

        0 to means there is a significant amount of regression 
        while 1 means there is no regression for the given percentile.
          
        :param number: The difference in percentage between two percentiles.
        :return: The score which is a float between 0.00 to 1.00.
        """
        score = 1
        for threshold, punishment in self.MATRIX:
            if number >= threshold:
                score -= punishment
            else:
                continue
        return score

    @property
    def probability_value(self) -> float:
        """
        Will find out what the difference in percentage is between each percentile.
        It will than feed that percentage through a matrix to find out
        how much positive or negative change exists.

        After that the array of scores gets computed into a score taking the
        standard deviation in account. This is done to verify if the change is
        across all of the percentiles or just within certain areas.

        :return: A float which represent the probability value
        """
        if self._p_value is None:
            for A, B in zip(self.group_a, self.group_b):
                percentage_variance = abs((B - A) / A * 100)
                self.absolute_scores.append(
                    self._score_percentage_variance_number_against_change_matrix(
                        number=percentage_variance
                    )
                )

            self._p_value = sum(self.absolute_scores) / len(self.PERCENTILE_DISTRIBUTION) - np.std(
                self.absolute_scores
            )
        #print("------------------")
        #print(self._p_value)
        #print(self.absolute_scores)
        #print(np.std(self.absolute_scores))
        #print("------------------")
        return self._p_value

    def test(self) -> bool:
        """
        This method will execute the hypothesis test.
        It will test if group B is slower than group A.

        If hypothesis test is correct a False boolean will be returned.
        When the hypothesis is wrong this method will reply True.

        :return: The outcome of the hypothesis test
        """
        if float(self.probability_value) < 0.90:  # <-- Everything below this score contains to much change.
            # We can reject the null hypothesis. (Failed)
            return False

        else:
            # We can NOT reject the null hypothesis. (Passed)
            return True
