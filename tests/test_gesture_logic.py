import unittest

from gesture_logic import classify_gesture, distance, is_pinching


class GestureLogicTests(unittest.TestCase):
    def base(self):
        return {
            "thumb": (0.30, 0.50),
            "index_tip": (0.50, 0.25),
            "index_pip": (0.50, 0.40),
            "middle_tip": (0.60, 0.55),
            "middle_pip": (0.60, 0.45),
            "wrist": (0.50, 0.80),
            "middle_mcp": (0.50, 0.55),
        }

    def test_distance(self):
        self.assertAlmostEqual(distance((0, 0), (3, 4)), 5)

    def test_pinching_uses_hand_scale(self):
        self.assertTrue(is_pinching((0, 0), (0.05, 0), 0.20))
        self.assertFalse(is_pinching((0, 0), (0.10, 0), 0.20))

    def test_move_when_only_index_is_extended(self):
        p = self.base()
        self.assertEqual(classify_gesture(**p), "move")

    def test_left_click_has_priority(self):
        p = self.base()
        p["thumb"] = (0.49, 0.26)
        self.assertEqual(classify_gesture(**p), "left_click")

    def test_right_click(self):
        p = self.base()
        p["thumb"] = (0.59, 0.54)
        self.assertEqual(classify_gesture(**p), "right_click")

    def test_scroll_up_requires_two_extended_fingers_and_large_gap(self):
        p = self.base()
        p["middle_tip"] = (0.60, 0.40)
        p["middle_pip"] = (0.60, 0.52)
        self.assertEqual(classify_gesture(**p), "scroll_up")

    def test_no_action_for_ambiguous_open_hand(self):
        p = self.base()
        p["middle_tip"] = (0.60, 0.27)
        p["middle_pip"] = (0.60, 0.45)
        self.assertEqual(classify_gesture(**p), "none")


if __name__ == "__main__":
    unittest.main()
