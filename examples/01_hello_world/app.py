#!/usr/bin/env python3
"""
VoidUI Example 1: Hello World CLI Daemon (HTML Mode)
Demonstrates live server-side dynamic HTML DOM payloads rendered directly into VoidUI.
Displays: "Today is [Date]", "Now is [Time]", and dynamic server metrics.
"""

import os
import sys
import time
from datetime import datetime
import platform

# `daemon_core/` is the shared framework this daemon is built on. It sits in
# the same folder as this file when the daemon runs from an unzipped download,
# and one folder up when the daemon runs from the repo. Try both.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                    # next to app.py
sys.path.insert(1, os.path.dirname(_HERE))  # one level up

try:
    from daemon_core.void_daemon import VoidDaemon
except ImportError:
    # Standalone fallback if copied outside repo
    from void_daemon import VoidDaemon

request_counter = 0
start_time = time.time()


def generate_hello_world_payload():
    global request_counter
    request_counter += 1

    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M:%S %p")
    uptime_sec = int(time.time() - start_time)
    mins, secs = divmod(uptime_sec, 60)
    hours, mins = divmod(mins, 60)
    uptime_formatted = f"{hours}h {mins}m {secs}s" if hours else f"{mins}m {secs}s"

    html_content = f"""
    <div style="max-width: 740px; margin: 0 auto; padding: 24px 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
      
      <!-- Header Banner -->
      <div style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; padding: 28px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25); margin-bottom: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <span style="background: rgba(255,255,255,0.22); font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.05em; text-transform: uppercase;">Mode: HTML DOM</span>
          <span style="font-size: 13px; opacity: 0.95; font-weight: 500;">Sync #{request_counter}</span>
        </div>
        <h1 style="margin: 0 0 8px 0; font-size: 26px; font-weight: 700; letter-spacing: -0.02em;">Hello World from VoidUI Daemon!</h1>
        <p style="margin: 0; font-size: 14.5px; opacity: 0.92; line-height: 1.5;">This interface is dynamically generated in Python and rendered instantly in the VoidUI desktop shell.</p>
      </div>

      <!-- Live Date & Time Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px;">
        
        <!-- Date Card -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="width: 40px; height: 40px; border-radius: 10px; background: #eff6ff; color: #2563eb; display: flex; align-items: center; justify-content: center; font-size: 20px;">📅</div>
            <div>
              <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em;">Calendar</div>
              <div style="font-size: 13px; font-weight: 600; color: #334155;">Today is:</div>
            </div>
          </div>
          <div style="font-size: 20px; font-weight: 700; color: #1e40af; margin-top: 4px; letter-spacing: -0.01em;">
            {date_str}
          </div>
        </div>

        <!-- Time Card -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="width: 40px; height: 40px; border-radius: 10px; background: #ecfdf5; color: #059669; display: flex; align-items: center; justify-content: center; font-size: 20px;">🕒</div>
            <div>
              <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em;">Local Clock</div>
              <div style="font-size: 13px; font-weight: 600; color: #334155;">Now is:</div>
            </div>
          </div>
          <div style="font-size: 20px; font-weight: 700; color: #047857; margin-top: 4px; letter-spacing: -0.01em;">
            {time_str}
          </div>
        </div>

      </div>

      <!-- Live Server Telemetry -->
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
        <h3 style="margin: 0 0 16px 0; font-size: 14px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
          <span>⚡ Daemon Telemetry</span>
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; font-size: 13px;">
          <div style="padding: 12px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
            <span style="color: #64748b; display: block; font-size: 11px; font-weight: 600; margin-bottom: 2px;">UPTIME</span>
            <strong style="color: #0f172a; font-size: 13.5px;">{uptime_formatted}</strong>
          </div>
          <div style="padding: 12px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
            <span style="color: #64748b; display: block; font-size: 11px; font-weight: 600; margin-bottom: 2px;">REQUEST COUNT</span>
            <strong style="color: #0f172a; font-size: 13.5px;">{request_counter} polls</strong>
          </div>
          <div style="padding: 12px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
            <span style="color: #64748b; display: block; font-size: 11px; font-weight: 600; margin-bottom: 2px;">PYTHON RUNTIME</span>
            <strong style="color: #0f172a; font-size: 13.5px;">{platform.python_implementation()} {platform.python_version()}</strong>
          </div>
          <div style="padding: 12px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
            <span style="color: #64748b; display: block; font-size: 11px; font-weight: 600; margin-bottom: 2px;">PLATFORM</span>
            <strong style="color: #0f172a; font-size: 13.5px;">{platform.system()} ({platform.machine()})</strong>
          </div>
        </div>
      </div>

    </div>
    """

    return {
        "type": "html",
        "title": f"Hello World Monitor — {time_str}",
        "updated_at": now.isoformat(),
        "content": html_content
    }


def main():
    daemon = VoidDaemon(
        name="Hello World CLI Daemon",
        default_port=8787,
        default_key="default-dev-key",
        data_handler=generate_hello_world_payload
    )
    daemon.run()


if __name__ == "__main__":
    main()
