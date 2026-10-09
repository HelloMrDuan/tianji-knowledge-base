import unittest

class ProjectionSmoke(unittest.TestCase):
    def test_projection_module_is_importable(self):
        from tianji_kb.public_projection import project_execution
        self.assertTrue(callable(project_execution))
