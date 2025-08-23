#!/usr/bin/env python3
"""
Simple launcher for Mail Writer Agent
Run this file directly: python run.py
"""

from agent import AgentCLI

if __name__ == "__main__":
    agent_cli = AgentCLI()
    agent_cli.run()
