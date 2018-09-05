import unittest
import rotation_animation


class Tests(unittest.TestCase):
    def test_get_polars(self):
        for p in rotation_animation.get_polars():
            print(p)

    def test_get_scaled_polars(self):
        for p in rotation_animation.get_cartesian_pts(3500):
            print(p)

    def test_get_layout(self):
        print(rotation_animation.get_layout(3500))

    def test_the_rainbow(self):
        rotation_animation.play_rainbow('192.168.1.44:7890')

    def test_shift(self):
        self.assertEqual([3, 1, 2], rotation_animation.shift([1, 2, 3]))

    def test_shift_tuple(self):
        self.assertEqual((3, 1, 2), rotation_animation.shift((1, 2, 3)))

    def test_counter_clockwise_rainbow(self):
        rotation_animation.counter_clockwise_rainbow('192.168.1.44:7890')

    def test_cone(self):
        rotation_animation.cone('192.168.1.44:7890')


if __name__ == '__main__':
    unittest.main()
