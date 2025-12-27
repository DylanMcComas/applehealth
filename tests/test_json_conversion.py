import json
import os
import tempfile

import src.applehealth as applehealth


def run_json_conversion(sample_path: str, output_dir: str, use_multiprocessing: bool):
    applehealth._output_dir = None
    applehealth._export_xml_path = None
    os.environ['OUTPUT_DIR'] = output_dir
    os.environ['EXPORT_XML'] = sample_path
    applehealth.convert_xml_to_json(
        worker_count=2 if use_multiprocessing else 1,
        batch_size=2,
        use_multiprocessing=use_multiprocessing,
    )


def _load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _normalize_rows(rows):
    return sorted(rows, key=lambda r: json.dumps(r, sort_keys=True))


def test_parallel_and_serial_json_equivalence():
    sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'sample_export.xml'))
    with tempfile.TemporaryDirectory() as tmp:
        serial_out = os.path.join(tmp, 'serial')
        parallel_out = os.path.join(tmp, 'parallel')
        os.makedirs(serial_out, exist_ok=True)
        os.makedirs(parallel_out, exist_ok=True)

        run_json_conversion(sample_path, serial_out, use_multiprocessing=False)
        run_json_conversion(sample_path, parallel_out, use_multiprocessing=True)

        files = ['records.json', 'workouts.json', 'activity_summary.json']
        for name in files:
            serial_rows = _load_json(os.path.join(serial_out, name))
            parallel_rows = _load_json(os.path.join(parallel_out, name))
            assert _normalize_rows(serial_rows) == _normalize_rows(parallel_rows)

    os.environ.pop('OUTPUT_DIR', None)
    os.environ.pop('EXPORT_XML', None)
    applehealth._output_dir = None
    applehealth._export_xml_path = None
