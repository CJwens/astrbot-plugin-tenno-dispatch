import unittest

from formatting import (
    format_alerts,
    format_arbitration,
    format_fissures,
    format_sortie,
)


class FormattingTests(unittest.TestCase):
    def test_format_fissures_handles_empty_data(self):
        self.assertEqual(format_fissures([]), "当前没有可显示的虚空裂隙。")

    def test_format_fissures_displays_node_and_tier(self):
        result = format_fissures(
            [
                {
                    "tier": "Lith",
                    "missionType": "Capture",
                    "node": "Earth - Cambria",
                    "expiry": "2099-01-01T00:00:00.000Z",
                }
            ]
        )

        self.assertIn("Lith", result)
        self.assertIn("捕获", result)
        self.assertIn("Earth - Cambria", result)

    def test_format_sortie_handles_expected_payload(self):
        result = format_sortie(
            {
                "boss": "Kela De Thaym",
                "expiry": "2099-01-01T00:00:00.000Z",
                "variants": [
                    {
                        "missionType": "Defense",
                        "node": "Sedna - Kelashin",
                        "modifier": "Enemy Physical Enhancement",
                    }
                ],
            }
        )

        self.assertIn("Kela De Thaym", result)
        self.assertIn("防御", result)
        self.assertIn("Sedna - Kelashin", result)

    def test_format_arbitration_handles_missing_data(self):
        result = format_arbitration({})
        self.assertIn("当前没有可显示的仲裁任务", result)

    def test_format_alerts_handles_reward_and_empty_data(self):
        result = format_alerts(
            [
                {
                    "expiry": "2099-01-01T00:00:00.000Z",
                    "mission": {
                        "type": "Rescue",
                        "node": "Earth - Cervantes",
                    },
                    "reward": {"asString": "Credits Cache"},
                }
            ]
        )

        self.assertIn("救援", result)
        self.assertIn("Credits Cache", result)
        self.assertIn("当前没有可显示的警报任务", format_alerts([]))
