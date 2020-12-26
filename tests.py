import unittest


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_loader.sortTestMethodsUsing = None
    test_suite = test_loader.discover('tests', pattern='test*.py')
    unittest.TextTestRunner(verbosity=2).run(test_suite)
    return test_suite


if __name__ == '__main__':
    my_test_suite()
