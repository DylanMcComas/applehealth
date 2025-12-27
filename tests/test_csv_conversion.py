import os
import tempfile

import pandas as pd

import src.applehealth as applehealth


def run_conversion(sample_path: str, output_dir: str, use_multiprocessing: bool):
    applehealth._output_dir = None
    applehealth._export_xml_path = None
    os.environ['OUTPUT_DIR'] = output_dir
    os.environ['EXPORT_XML'] = sample_path
    applehealth.convert_xml_to_csv(
        worker_count=2 if use_multiprocessing else 1,
        batch_size=2,
        use_multiprocessing=use_multiprocessing,
    )


def test_parallel_and_serial_csv_equivalence():
    sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'sample_export.xml'))
    with tempfile.TemporaryDirectory() as tmp:
        serial_out = os.path.join(tmp, 'serial')
        parallel_out = os.path.join(tmp, 'parallel')
        os.makedirs(serial_out, exist_ok=True)
        os.makedirs(parallel_out, exist_ok=True)

        run_conversion(sample_path, serial_out, use_multiprocessing=False)
        run_conversion(sample_path, parallel_out, use_multiprocessing=True)

        files = ['records.csv', 'workouts.csv', 'activity_summary.csv']
        for name in files:
            serial_df = pd.read_csv(os.path.join(serial_out, name))
            parallel_df = pd.read_csv(os.path.join(parallel_out, name))
            pd.testing.assert_frame_equal(serial_df, parallel_df)

    # Cleanup environment variables
    os.environ.pop('OUTPUT_DIR', None)
    os.environ.pop('EXPORT_XML', None)
    applehealth._output_dir = None
    applehealth._export_xml_path = None
