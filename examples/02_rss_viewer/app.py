#!/usr/bin/env python3
"""
VoidUI Example 2: RSS Multi-Feed CLI Daemon (3-Pane JSON Mode)
Aggregates ("cooks") 3 live RSS/Atom feeds (BBC World, Ars Technica, Python Blog)
into a structured JSON payload conforming to the VoidUI 3-Pane specification.
"""

import os
import sys
import argparse

# `daemon_core/` is the shared framework this daemon is built on. It sits in
# the same folder as this file when the daemon runs from an unzipped download,
# and one folder up when the daemon runs from the repo. Try both.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                    # next to app.py
sys.path.insert(1, os.path.dirname(_HERE))  # one level up

try:
    from daemon_core.void_daemon import VoidDaemon
except ImportError:
    from void_daemon import VoidDaemon

from rss_parser import MultiFeedAggregator

aggregator = MultiFeedAggregator(ttl_seconds=300)


def provide_rss_3pane_data():
    """Callback returning the cooked 3-pane JSON dataset."""
    return aggregator.get_cooked_feeds()


def main():
    daemon = VoidDaemon(
        name="RSS 3-Pane Aggregator Daemon",
        default_port=8788,
        default_key="default-dev-key",
        data_handler=provide_rss_3pane_data
    )
    daemon.run()


if __name__ == "__main__":
    main()
