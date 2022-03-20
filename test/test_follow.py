import unittest
from follow import followers

class TestFollow(unittest.TestCase):
    def setUp(self):
        self.f = followers()

    def test_addSingle(self):
        self.f.add_follower("l1", "a1")
        x = self.f.get_followers("a1")
        self.assertIsInstance(x, list)
        self.assertEqual(x, ["l1"])

    def test_addDual(self):
        self.f.add_follower("l1", "a1")
        self.f.add_follower("l2", "b1")
        x = self.f.get_followers("a1")
        self.assertIsInstance(x, list)
        self.assertEqual(x, ["l1"])
        x = self.f.get_followers("b1")
        self.assertIsInstance(x, list)
        self.assertEqual(x, ["l2"])

    def test_GetMissing(self):
        self.f.add_follower("l1", "a1")
        self.f.add_follower("l2", "b1")

        x = self.f.get_followers("xx")
        self.assertIs(x, None)

    def test_addToExisting(self):
        self.f.add_follower("l1", "a1")
        self.f.add_follower("l2", "a1")
        x = self.f.get_followers("a1")
        self.assertIsInstance(x, list)
        self.assertEqual(x, ["l1", "l2"])
        self.f.add_follower("l3", "a1")
        self.assertEqual(x, ["l1", "l2", "l3"])

    def test_addToMoreThanOne(self):
        x = self.f.add_follower("l1", "a1")
        self.assertIs(x, True)

        x = self.f.add_follower("l1", "b1")  # Should fail
        self.assertIs(x, False)

        x = self.f.get_followers("a1")
        self.assertEqual(x, ["l1"])

        x = self.f.get_followers("b1")
        self.assertIs(x, None)


    def test_RemoveExisting(self):
        self.f.add_follower("l1", "a1")
        self.f.add_follower("l2", "a1")
        x = self.f.get_followers("a1")
        self.assertEqual(x, ["l1", "l2"])

        x = self.f.remove_follower("l1", "a1")
        self.assertEqual(x, True)

        x = self.f.get_followers("a1")
        self.assertIsInstance(x, list)
        self.assertEqual(x, ["l2"])

    def test_RemoveNonExisting(self):
        self.f.add_follower("l1", "a1")
        self.f.add_follower("l2", "a1")
        x = self.f.get_followers("a1")
        self.assertEqual(x, ["l1", "l2"])

        x = self.f.remove_follower("lx", "a1")
        self.assertEqual(x, False)

        x = self.f.get_followers("a1")
        self.assertIsInstance(x, list)
        self.assertEqual(x, ["l1", "l2"])

    @unittest.skip("Not yet fully implemented")
    def test_AddColourMode(self):
        self.f.add_follower("l1", "a1")
        self.addColourMode("l1", "ColourTemp")
        colour, dimmable = self.f.get_light_attr("l1")
        self.assertEqual(colour, "ColourTemp")
        self.assertIs(dimmable, None)

    @unittest.skip("Not yet fully implemented")
    def test_AddDimmable(self):
        self.f.add_follower("l1", "a1")
        self.setDimmable("l1", True)
        colour, dimmable = self.f.get_light_attr("l1")
        self.assertEqual(colour, "OnOff")
        self.assertIs(dimmable, True)
