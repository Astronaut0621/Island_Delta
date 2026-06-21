import importlib.util
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# scripts/ 不是包，按文件路径加载构建脚本，避免改动包结构。
_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_campus_emotion_dataset_v3.py"
_spec = importlib.util.spec_from_file_location("build_campus_emotion_dataset_v3", _SCRIPT_PATH)
build_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_v3)

REQUIRED_FIELDS = build_v3.REQUIRED_FIELDS
LABELS = build_v3.LABELS


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    import csv

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class BuildDatasetV3Test(unittest.TestCase):
    def test_required_fields_match_contract(self) -> None:
        # 任务四数据集格式契约：id,text,emotion_type,source
        self.assertEqual(REQUIRED_FIELDS, ["id", "text", "emotion_type", "source"])

    def test_labels_cover_ten_emotions(self) -> None:
        self.assertEqual(len(LABELS), 10)
        for code in [
            "lonely", "anxious", "stressed", "tired", "sad",
            "calm", "healed", "secure", "happy", "hopeful",
        ]:
            self.assertIn(code, LABELS)

    def test_sources_only_manual_and_ai_generated(self) -> None:
        # 与 validate_emotion_dataset.py 收敛后的口径一致：去掉 social_excerpt。
        # validate_rows 内部断言 source 必须在这两个值里，这里直接验证行为。
        rows = [{"id": "1", "text": "ok", "emotion_type": "calm", "source": "social_excerpt"}]
        with self.assertRaises(ValueError):
            build_v3.validate_rows("fake.csv", rows)

    def test_validate_rows_rejects_invalid_emotion(self) -> None:
        rows = [{"id": "1", "text": "ok", "emotion_type": "angry", "source": "manual"}]
        with self.assertRaises(ValueError):
            build_v3.validate_rows("fake.csv", rows)

    def test_validate_rows_rejects_empty_text(self) -> None:
        rows = [{"id": "1", "text": "", "emotion_type": "calm", "source": "manual"}]
        with self.assertRaises(ValueError):
            build_v3.validate_rows("fake.csv", rows)

    def test_validate_rows_accepts_clean_rows(self) -> None:
        rows = [
            {"id": "1", "text": "湖边晚风吹过来", "emotion_type": "healed", "source": "manual"},
            {"id": "2", "text": "明天考试我很慌", "emotion_type": "anxious", "source": "ai_generated"},
        ]
        # 不抛异常即通过
        build_v3.validate_rows("fake.csv", rows)

    def test_repair_row_ignores_non_mazhenjie_file(self) -> None:
        # 只有马振杰的文件才需要标签错位修复，其它文件原样返回。
        path = Path("manual_samples_王宇航.csv")
        row = {"id": "1", "text": "原文", "emotion_type": "manual", "source": "manual"}
        result = build_v3.repair_row(path, dict(row))
        self.assertNotIn("_repaired", result)
        self.assertEqual(result["emotion_type"], "manual")

    def test_repair_row_fixes_shifted_label_for_mazhenjie(self) -> None:
        # 马振杰提交的损坏行形如：text 里夹着 label，emotion_type/source 都被错位成 manual。
        path = Path("manual_samples_马振杰.csv")
        row = {
            "id": "999",  # 不在 MA_ZHENJIE_TEXT_FIXES 里，只走标签后缀修复分支
            "text": "明天就要考试了，心里一直发慌anxious",
            "emotion_type": "manual",
            "source": "manual",
        }
        result = build_v3.repair_row(path, dict(row))
        self.assertEqual(result["_repaired"], "true")
        self.assertEqual(result["emotion_type"], "anxious")
        self.assertEqual(result["text"], "明天就要考试了，心里一直发慌")

    def test_repair_row_applies_manual_text_fix_for_mazhenjie(self) -> None:
        # 在 MA_ZHENJIE_TEXT_FIXES 表里的 id，文本会被强制覆盖为已校对版本。
        path = Path("manual_samples_马振杰.csv")
        row = {
            "id": "1",
            "text": "损坏的占位文本",
            "emotion_type": "anxious",
            "source": "manual",
        }
        result = build_v3.repair_row(path, dict(row))
        self.assertEqual(result["_repaired"], "true")
        self.assertEqual(
            result["text"],
            "身边同学都开始实习了，我也开始担心自己是不是该去找实习",
        )

    def test_decode_csv_text_reads_utf8_sig(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.csv"
            _write_csv(path, [
                {"id": "1", "text": "图书馆很安静", "emotion_type": "calm", "source": "manual"},
            ])
            _text, encoding = build_v3.decode_csv_text(path)
            self.assertEqual(encoding, "utf-8-sig")
            self.assertIn("图书馆很安静", _text)

    def test_read_csv_any_encoding_rejects_wrong_fields(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.csv"
            path.write_text("id,wrong\n1,foo\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_v3.read_csv_any_encoding(path)


if __name__ == "__main__":
    unittest.main()
