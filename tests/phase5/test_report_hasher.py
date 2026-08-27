import pytest
import tempfile
import os
from reporting.hasher import ReportHasher

def test_report_hasher():
    with tempfile.NamedTemporaryFile(delete=False) as f1:
        f1.write(b"%PDF-1.4\nTest PDF content")
        f1_name = f1.name
        
    with tempfile.NamedTemporaryFile(delete=False) as f2:
        f2.write(b"%PDF-1.4\nTest PDF content")
        f2_name = f2.name
        
    with tempfile.NamedTemporaryFile(delete=False) as f3:
        f3.write(b"%PDF-1.4\nDifferent PDF content")
        f3_name = f3.name

    try:
        h1 = ReportHasher.hash_file(f1_name)
        h2 = ReportHasher.hash_file(f2_name)
        h3 = ReportHasher.hash_file(f3_name)
        
        assert h1 == h2
        assert h1 != h3
        assert ReportHasher.verify(f1_name, h1)
        assert ReportHasher.is_valid_pdf(f1_name)
        
    finally:
        os.unlink(f1_name)
        os.unlink(f2_name)
        os.unlink(f3_name)
