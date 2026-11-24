import os
import tempfile
import unittest

from mission_catalog import active_missions, delete_mission, list_catalog, save_mission


class MissionCatalogTests(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(handle)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_add_duplicate_update_delete(self):
        mission_id = save_mission("테스트 미션", "쉬움", True, db_path=self.db_path)

        catalog = list_catalog(self.db_path)
        self.assertEqual(len(catalog), 51)
        self.assertTrue(any(entry.mission.id == mission_id for entry in catalog))
        self.assertEqual(len(active_missions(self.db_path)), 51)

        with self.assertRaises(ValueError):
            save_mission("테스트 미션", "보통", True, db_path=self.db_path)

        save_mission("테스트 미션 수정", "보통", False, mission_id, self.db_path)
        updated = next(
            entry for entry in list_catalog(self.db_path)
            if entry.mission.id == mission_id
        )
        self.assertEqual(updated.mission.content, "테스트 미션 수정")
        self.assertEqual(updated.mission.difficulty, "보통")
        self.assertFalse(updated.active)
        self.assertEqual(len(active_missions(self.db_path)), 50)

        delete_mission(mission_id, self.db_path)
        self.assertFalse(any(
            entry.mission.id == mission_id
            for entry in list_catalog(self.db_path)
        ))

    def test_invalid_input_and_duplicate_spacing(self):
        save_mission("공백 정리 테스트", "어려움", True, db_path=self.db_path)

        with self.assertRaises(ValueError):
            save_mission("공백   정리 테스트", "쉬움", True, db_path=self.db_path)

        with self.assertRaises(ValueError):
            save_mission("", "쉬움", True, db_path=self.db_path)

        with self.assertRaises(ValueError):
            save_mission("유효한 내용", "매우 어려움", True, db_path=self.db_path)


if __name__ == "__main__":
    unittest.main()
