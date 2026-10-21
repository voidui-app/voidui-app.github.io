"""
VoidUI Daemon Core Framework
Provides a drop-in Flask-based CLI daemon engine for VoidUI.
"""

import os
import sys
import time
import argparse
from typing import Callable, Any, Dict
from flask import Flask, jsonify, request, Response


class VoidDaemon:
    """
    VoidDaemon wraps a Flask application to expose local Python logic
    as a standardized CLI daemon for the VoidUI desktop viewer.
    """

    def __init__(
        self,
        name: str = "VoidUI Daemon",
        default_port: int = 8787,
        default_key: str = "default-dev-key",
        data_handler: Callable[[], Dict[str, Any]] = None,
    ):
        self.name = name
        self.default_port = default_port
        self.default_key = default_key
        self.data_handler = data_handler
        self.start_time = time.time()
        self.app = Flask(name)
        self._configure_routes()

    def _configure_routes(self):
        @self.app.after_request
        def add_cors_headers(response: Response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            return response

        @self.app.route("/api/health", methods=["GET", "OPTIONS"])
        def health():
            if request.method == "OPTIONS":
                return "", 204
            return jsonify({
                "status": "ok",
                "name": self.name,
                "uptime_seconds": int(time.time() - self.start_time),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        @self.app.route("/api/data", methods=["GET", "OPTIONS"])
        def get_data():
            if request.method == "OPTIONS":
                return "", 204

            # Verify the API key.
            #
            # The header is the primary channel: the player always sends
            # `X-API-Key`, and a header never lands in a URL, a proxy log, or
            # browser history.
            #
            # `?key=` is accepted as well, because a browser's address bar
            # cannot send custom headers — without it, a daemon's JSON can only
            # be read by the player or by curl, and "let me look at the raw
            # payload in a browser" is a reasonable thing to want. A query
            # string can end up in history and access logs, so treat it as a
            # convenience for local inspection, not as a production channel.
            expected_key = getattr(self, "api_key", self.default_key)
            auth_header = request.headers.get("X-API-Key")
            key_param = request.args.get("key")

            header_ok = auth_header is not None and auth_header == expected_key
            param_ok = key_param is not None and key_param == expected_key

            if not (header_ok or param_ok):
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid or missing X-API-Key header."
                }), 401

            if not self.data_handler:
                return jsonify({
                    "type": "html",
                    "title": self.name,
                    "content": "<p>VoidDaemon running. No custom data handler assigned.</p>"
                })

            try:
                payload = self.data_handler()
                return jsonify(payload)
            except Exception as e:
                return jsonify({
                    "error": "Internal Error",
                    "message": str(e)
                }), 500

    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser(description=f"{self.name} for VoidUI")
        parser.add_argument(
            "--port", "-p",
            type=int,
            default=int(os.environ.get("VOID_PORT", self.default_port)),
            help=f"Port to listen on (default: {self.default_port})"
        )
        parser.add_argument(
            "--host", "-H",
            type=str,
            default=os.environ.get("VOID_HOST", "127.0.0.1"),
            help="Host interface to bind to (default: 127.0.0.1)"
        )
        parser.add_argument(
            "--key", "-k",
            type=str,
            default=os.environ.get("VOID_API_KEY", self.default_key),
            help="API Key for X-API-Key authentication"
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable Flask debug mode"
        )
        return parser.parse_args(argv)

    def run(self, argv=None):
        args = self.parse_args(argv)
        self.api_key = args.key
        
        print(f"==================================================")
        print(f"  Starting {self.name}")
        print(f"  Endpoint: http://{args.host}:{args.port}/api/data")
        print(f"  API Key:  {args.key}")
        print(f"==================================================")
        sys.stdout.flush()

        self.app.run(host=args.host, port=args.port, debug=args.debug)
