"""Live progress sinks: a failing API leaves no open connection behind (spec: live-progress-sinks, wo-gh-47).

R1.5 says a sink call that receives an HTTP status of 400 or higher is
caught and recorded as "<type>: HTTP <status>". The HTTPError urllib raises
holds the open response, so the sink must close it: a line whose API keeps
answering 500 would otherwise hold one socket per state write until garbage
collection. A local HTTP collector on 127.0.0.1 stands in for GitHub.
"""
import gc
import http.server
import os
import sys
import threading
import time
import unittest
import warnings
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from anvil.sinks import SinkSet  # noqa: E402


class _Failing(http.server.BaseHTTPRequestHandler):
    def _fail(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        body = b'{"message": "boom"}'
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = do_PATCH = _fail

    def log_message(self, *args):
        pass


class SinkErrorConnectionTests(unittest.TestCase):
    def setUp(self):
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Failing)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def test_r1_5_http_error_is_recorded_and_its_response_closed(self):
        """R1.5 (S3): repeated HTTP 500 answers give one export error and hold no connection open.

        The exceptions the sink raised are kept alive on purpose (as a logged
        traceback would keep them): their connections must already be closed.
        """
        if not Path("/proc/self/fd").is_dir():
            self.skipTest("needs /proc/self/fd to count open descriptors")
        from anvil import sinks as sinks_module
        env = {"GITHUB_API_URL": f"http://127.0.0.1:{self.server.server_address[1]}",
               "GITHUB_REPOSITORY": "acme/demo", "GH_TOKEN": "ghs_test_value"}
        record = {"run_id": "r-1", "work_order_id": "wo-gh-904", "pipeline": "sdlc-default", "state": "running",
                  "stations": ["intake"], "steps": [], "token_usage": {}, "cost": None}
        errors, kept = [], []
        real_note_for = sinks_module.note_for

        def keeping_note_for(sink_type, exc):
            kept.append(exc)
            return real_note_for(sink_type, exc)

        with mock.patch.dict(os.environ, env, clear=False), \
                mock.patch.object(sinks_module, "note_for", keeping_note_for), \
                warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            sinks = SinkSet([{"type": "github-issue"}], 2.0)
            before = len(os.listdir("/proc/self/fd"))
            for _ in range(5):
                sinks.deliver(record, errors)
            # The collector runs in this process: its handler thread may still be
            # closing the socket of the last request, so the count is given a moment.
            for _ in range(60):
                held = len(os.listdir("/proc/self/fd")) - before
                if held <= 0:
                    break
                time.sleep(0.05)
        self.assertEqual(errors, ["github-issue: HTTP 500"])
        self.assertEqual(len(kept), 5)
        self.assertLessEqual(held, 0, f"{held} descriptors held open by failed sink requests")
        del kept
        gc.collect()


if __name__ == "__main__":
    unittest.main()
