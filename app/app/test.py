"""
sample test
"""

from django.test import SimpleTestCase

from app import count


class CalcTests(SimpleTestCase):
    """
    Test the calc module
    """

    def add_number(self):  # omitted test prefix
        """
            Test adding numnbers together
        """
        res = count.add(5, 6)

        self.assertEqual(res, 11)

    def subtract_numbers(self):
        """ subtracting number """

        res = count.subtract(10, 5)

        self.assertEqual(res, 5)
