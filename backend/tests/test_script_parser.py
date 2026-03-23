import unittest
from unittest.mock import patch

from modules import script_parser


def _cfg():
    return {
        "api_key": "test-key",
        "model": "test-model",
        "temperature": 0.7,
        "max_tokens": 1200,
        "base_url": "https://example.com/v1",
    }


class ScriptParserStrictTests(unittest.TestCase):
    def test_valid_json_success(self):
        content = """{
  \"scenes\": [
    {
      \"scene_id\": \"scene_1\",
      \"StartFrame\": \"中景平视，人物站在台阶下。\",
      \"motion_instruction\": \"人物向前一步并抬头\",
      \"target_state\": \"承接迈步动作后，人物重心逐渐稳定，衣摆摆动缓慢收束。\",
      \"shot_plan\": [
        {
          \"beat_id\": \"beat_1\",
          \"shot_type\": \"中景\",
          \"camera_angle\": \"平视\",
          \"camera_movement\": \"缓推\",
          \"blocking\": \"人物站立\",
          \"action\": \"站立\",
          \"dialogue\": \"\",
          \"duration\": \"2s\",
          \"transition\": \"切\"
        },
        {
          \"beat_id\": \"beat_2\",
          \"shot_type\": \"中景\",
          \"camera_angle\": \"平视\",
          \"camera_movement\": \"缓推\",
          \"blocking\": \"人物迈步\",
          \"action\": \"迈步\",
          \"dialogue\": \"\",
          \"duration\": \"2s\",
          \"transition\": \"切\"
        }
      ]
    }
  ]
}"""
        with patch("modules.script_parser.chat_completion", return_value={"success": True, "content": content}):
            result = script_parser.parse_script("主角停步并抬头", "8s", _cfg())
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.get("scenes"), list)
        self.assertEqual(len(result["scenes"]), 1)
        self.assertIsInstance(result["scenes"][0].get("shot_plan"), list)
        scene = result["scenes"][0]
        self.assertTrue(scene.get("target_state"))
        self.assertTrue(scene.get("prev_state"))
        self.assertTrue(scene.get("continuity_hint"))
        self.assertTrue(scene.get("visual_anchor"))
        self.assertTrue(scene.get("motion_instruction"))
        self.assertIsNone(scene.get("EndFrame"))
        self.assertIsNone(scene.get("end_frame_goal"))
        first_beat = scene.get("shot_plan")[0]
        second_beat = scene.get("shot_plan")[1]
        self.assertTrue(first_beat.get("prev_state"))
        self.assertTrue(first_beat.get("motion_instruction"))
        self.assertTrue(first_beat.get("target_state"))
        self.assertTrue(first_beat.get("visual_anchor"))
        self.assertTrue(first_beat.get("continuity_hint"))
        self.assertEqual(second_beat.get("prev_state"), first_beat.get("target_state"))

    def test_non_json_response_raises(self):
        with patch("modules.script_parser.chat_completion", return_value={"success": True, "content": "这不是JSON"}):
            with self.assertRaises(ValueError):
                script_parser.parse_script("主角停步并抬头", "8s", _cfg())

    def test_top_level_array_raises(self):
        content = """[
  {"scene_id": "scene_1", "StartFrame": "A", "target_state": "B"}
]"""
        with patch("modules.script_parser.chat_completion", return_value={"success": True, "content": content}):
            with self.assertRaises(ValueError):
                script_parser.parse_script("主角停步并抬头", "8s", _cfg())

    def test_invalid_scene_item_raises(self):
        content = """{"scenes": ["bad-scene"]}"""
        with patch("modules.script_parser.chat_completion", return_value={"success": True, "content": content}):
            with self.assertRaises(ValueError):
                script_parser.parse_script("主角停步并抬头", "8s", _cfg())

    def test_trailing_commas_are_repaired(self):
        content = """{
  "scenes": [
    {
      "scene_id": "scene_1",
      "StartFrame": "中景平视，人物站在台阶下。",
      "motion_instruction": "人物向前一步",
      "target_state": "人物重心逐步前移后趋于稳定。",
      "shot_plan": [
        {
          "beat_id": "beat_1",
          "shot_type": "中景",
          "camera_angle": "平视",
          "camera_movement": "固定",
          "blocking": "人物站立",
          "action": "抬头",
          "dialogue": "",
          "duration": "2s",
          "transition": "切",
        },
      ],
      "character_actions": "听到AI回应",
      "action_arc": "从迷茫到坚定",
    },
  ],
  "story_package": {"character_bible": []},
}"""
        with patch("modules.script_parser.chat_completion", return_value={"success": True, "content": content}):
            result = script_parser.parse_script("主角停步并抬头", "8s", _cfg())
        self.assertEqual(len(result.get("scenes") or []), 1)

    def test_duplicate_comma_is_repaired(self):
        content = """{
  "scenes": [
    {
      "scene_id": "scene_1",
      "StartFrame": "近景，人物凝视前方。",
      "motion_instruction": "人物低声宣言",
      "target_state": "声音落下后，人物呼吸逐渐放缓，视线稳定向前。",
      "shot_plan": [],
      "character_actions": "听到AI回应、分析时代、说出宣言",
      "action_arc": "从确认现实到立下野心",,
      "dialogue": "那这一世……我就是规则。"
    }
  ],
  "story_package": {"character_bible": []}
}"""
        with patch("modules.script_parser.chat_completion", return_value={"success": True, "content": content}):
            result = script_parser.parse_script("主角停步并抬头", "8s", _cfg())
        self.assertEqual(len(result.get("scenes") or []), 1)


if __name__ == "__main__":
    unittest.main()
