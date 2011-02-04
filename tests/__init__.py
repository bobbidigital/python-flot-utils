import json
import unittest

from pyflot import Flot, MissingDataException, \
        DuplicateLabelException


SERIES = (
    ((1, 1), (2, 2), (3, 3)),
)
S1, = SERIES

FAKE_NESTED_OPTIONS = {
    'level1': {
        'level2': {
            'a':1, 
            'level3': {
                'b':2}}},
    'c':3}



class TestFlot(unittest.TestCase):

    def setUp(self):
        self.flot = Flot()

    def check_add_series(self, raw, label=None):
        count = len(self.flot._series)
        self.flot.add_series(raw, label)
        self.assertEqual(count+1, len(self.flot._series))
        series = self.flot._series[count]
        self.assertEqual(raw, series['data'])
        if label:
            self.assertEqual(label, series['label'])
        else:
            self.assertFalse('label' in series)

    def test_initial_state(self):
        "make sure internal structures initialize properly"
        self.assertEqual(self.flot._series, [])
        self.assertEqual(self.flot._options, {})

    def test_basic_add_series(self):
        "make sure a series can be added with no label or options"
        self.check_add_series(S1)

    def test_reject_empty_series(self):
        """don't accept empty series"""
        self.assertRaises(MissingDataException, self.flot.add_series, [])
        self.assertEqual(len(self.flot._series), 0)

    def test_add_series_with_label(self):
        """make sure a label can be associated with a series"""
        self.flot.add_series(S1, "as_arg")
        self.flot._series = []
        self.flot.add_series(S1, label="as_kwarg")

    def test_reject_duplicate_label(self):
        "make sure a series is not added if it has a duplicate label"
        self.check_add_series(S1, "label1")
        self.assertRaises(DuplicateLabelException, self.flot.add_series, S1, "label1")

    def test_add_multiple_series(self):
        "make sure multiple series can be added"
        self.check_add_series(S1)
        self.check_add_series(S1)

    def test_series_json(self):
        "make sure conversion to JSON works for simple series"
        self.assertEqual("[]", self.flot.series_json)
        series = {'data': S1}
        self.flot.add_series(S1)
        self.assertEqual(json.dumps([series]), self.flot.series_json)

    def test_series_with_label_json(self):
        "make sure series with label converts to JSON properly"
        series = {'data': S1, 'label': 'label1'}
        self.flot.add_series(S1, 'label1')
        self.assertEqual(json.dumps([series]), self.flot.series_json)

    def test_empty_options_json(self):
        "make sure conversion to JSON works for default options"
        self.assertEqual("{}", self.flot.options_json)

    def test_options(self):
        "make sure options are applied correctly for a Flot subclass" 
        class MyFlot(Flot):
            options = FAKE_NESTED_OPTIONS

        f = MyFlot()
        self.assertEqual(f._options, FAKE_NESTED_OPTIONS)
        self.assertEqual(f.options_json,
                json.dumps(FAKE_NESTED_OPTIONS))

    def test_options_inheritance(self):
        "make sure options in an inheritance chain are applied correctly"
        class MyFlot(Flot):
            options = FAKE_NESTED_OPTIONS

        class AnotherFlot(MyFlot):
            options = {
                'level1': {
                    'd': 4,
                    'level2': {
                        'a': 10}}}

        f = AnotherFlot()
        self.assertEqual(f._options,
                {'level1': {'d': 4, 'level2': {'a':10, 'level3': {'b':2}}}, 'c':3})
        #TODO will the dumped dict string match work across platforms?
        self.assertEqual(f.options_json,
                 '{"level1": {"level2": {"a": 10, "level3": {"b": 2}}, "d": 4}, "c": 3}')