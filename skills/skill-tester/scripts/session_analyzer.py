#!/usr/bin/env python3
"""
session_analyzer.py — Analyze Claude Code session JSONL files for API usage and conversation audit.

Parses parent session + subagent transcripts from Claude Code's session logs.
Produces a JSON summary and/or a searchable HTML conversation report.

Usage:
  # Analyze most recent session for a project
  python scripts/session_analyzer.py --project-dir ~/.claude/projects/<hash> --output session/session_report.html

  # Analyze a specific session
  python scripts/session_analyzer.py --session-id <uuid> --project-dir ~/.claude/projects/<hash>

  # JSON summary only
  python scripts/session_analyzer.py --project-dir ~/.claude/projects/<hash> --format json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# JSONL parsing
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> list[dict]:
    results = []
    if not path.exists():
        return results
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return results


def _find_project_dir() -> Optional[Path]:
    """Find the Claude project dir for the current working directory."""
    cwd = os.getcwd()
    slug = cwd.replace("/", "-")
    if slug.startswith("-"):
        slug = slug[1:]
    candidate = Path.home() / ".claude" / "projects" / f"-{slug}"
    if candidate.exists():
        return candidate
    # Try parent directories
    parts = Path(cwd).parts
    for i in range(len(parts), 1, -1):
        test = "-".join(parts[1:i])
        candidate = Path.home() / ".claude" / "projects" / f"-{test}"
        if candidate.exists():
            return candidate
    return None


def _find_latest_session(project_dir: Path) -> Optional[str]:
    """Find the most recently modified session JSONL in a project dir."""
    jsonl_files = sorted(
        project_dir.glob("*.jsonl"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if jsonl_files:
        return jsonl_files[0].stem
    return None


# ---------------------------------------------------------------------------
# Session data extraction
# ---------------------------------------------------------------------------

def _is_system_noise(text: str) -> bool:
    """Detect Claude Code internal/hook messages that aren't useful to display."""
    noise_markers = ("isSidechain", "hookEvent", "parentUuid", "hook_progress",
                     "PostToolUse:", "PreToolUse:", "UserPromptSubmit hook")
    return any(m in text for m in noise_markers)


def _parse_tool_result(block: dict) -> dict:
    """Parse a tool_result block into a structured, renderable dict."""
    tool_use_id = block.get("tool_use_id", "")
    content = block.get("content", "")
    is_error = block.get("is_error", False)

    # Content can be a string or a list of content blocks
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                ctype = c.get("type", "")
                if ctype == "tool_reference":
                    parts.append({"type": "tool_loaded", "tool_name": c.get("tool_name", "?")})
                elif ctype == "text":
                    text = (c.get("text", "") or "")[:2000]
                    if _is_system_noise(text):
                        continue  # skip internal hook/system messages
                    parts.append({"type": "text", "text": text})
                elif ctype == "tool_result":
                    # Nested tool_result — extract text content
                    inner = c.get("content", "")
                    if isinstance(inner, str) and not _is_system_noise(inner):
                        parts.append({"type": "text", "text": inner[:1500]})
                else:
                    text = str(c)[:500]
                    if not _is_system_noise(text):
                        parts.append({"type": "text", "text": text})
            else:
                text = str(c)[:500]
                if not _is_system_noise(text):
                    parts.append({"type": "text", "text": text})
    elif isinstance(content, str):
        if _is_system_noise(content):
            parts = [{"type": "system_noise", "summary": "System/hook message (filtered)"}]
        else:
            parts = [{"type": "text", "text": content[:2000]}]
    else:
        parts = [{"type": "text", "text": str(content)[:500]}]

    return {
        "tool_use_id": tool_use_id,
        "is_error": is_error,
        "parts": parts,
    }


def _parse_conversation(records: list[dict]) -> list[dict]:
    """Parse JSONL records into a structured conversation timeline."""
    messages = []
    for rec in records:
        rec_type = rec.get("type")
        if rec_type in ("user", "assistant"):
            msg = rec.get("message", {})
            content_blocks = msg.get("content", [])
            if isinstance(content_blocks, str):
                content_blocks = [{"type": "text", "text": content_blocks}]

            tool_calls = []
            thinking = []
            text_parts = []
            tool_results = []
            for block in content_blocks:
                if isinstance(block, dict):
                    if block.get("type") == "tool_use":
                        tool_calls.append({
                            "id": block.get("id", ""),
                            "name": block.get("name", "?"),
                            "input": block.get("input", {}),
                        })
                    elif block.get("type") == "thinking":
                        thinking.append(block.get("thinking", "")[:1000])
                    elif block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif block.get("type") == "tool_result":
                        tr = _parse_tool_result(block)
                        tool_results.append(tr)

            entry = {
                "type": rec_type,
                "timestamp": rec.get("timestamp", ""),
                "uuid": rec.get("uuid", ""),
                "text": "\n".join(text_parts),
                "tool_calls": tool_calls,
                "tool_results": tool_results,
                "thinking": thinking,
            }

            if rec_type == "assistant":
                usage = msg.get("usage", {})
                entry["model"] = msg.get("model", "")
                entry["usage"] = {
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "cache_read": usage.get("cache_read_input_tokens", 0),
                    "cache_create": usage.get("cache_creation_input_tokens", 0),
                }
                entry["stop_reason"] = msg.get("stop_reason")
                entry["message_id"] = msg.get("id", "")

            messages.append(entry)
    return messages


def _tool_to_op(tool_name: str) -> str:
    """Map a tool name to a short operation code for file-level tracking."""
    _MAP = {
        "Read": "R", "read_file": "R", "read_text_file": "R", "read_multiple_files": "R",
        "Edit": "E", "edit_file": "E",
        "Write": "W", "write_file": "W",
        "Grep": "G", "search_files": "G",
        "Bash": "B",
        "Glob": "S",  # S for Search/Scan
    }
    return _MAP.get(tool_name, "")


def analyze_session(project_dir: str, session_id: Optional[str] = None) -> dict:
    """Analyze a Claude Code session and return structured data."""
    proj = Path(project_dir)
    if not proj.exists():
        raise FileNotFoundError(f"Project dir not found: {proj}")

    if not session_id:
        session_id = _find_latest_session(proj)
        if not session_id:
            raise FileNotFoundError(f"No session files found in {proj}")

    session_file = proj / f"{session_id}.jsonl"
    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")

    records = _load_jsonl(session_file)
    parent_conversation = _parse_conversation(records)

    session_meta = {}
    for rec in records:
        if rec.get("sessionId"):
            session_meta = {
                "session_id": rec.get("sessionId", ""),
                "slug": rec.get("slug", ""),
                "version": rec.get("version", ""),
                "cwd": rec.get("cwd", ""),
                "git_branch": rec.get("gitBranch", ""),
            }
            break

    parent_stats = _compute_stats(parent_conversation)

    # Parse subagent sessions
    subagents_dir = proj / session_id / "subagents"
    agents = []
    if subagents_dir.exists():
        for meta_file in sorted(subagents_dir.glob("*.meta.json")):
            agent_id = meta_file.stem.replace(".meta", "")
            jsonl_file = subagents_dir / f"{agent_id}.jsonl"

            meta = {}
            try:
                meta = json.loads(meta_file.read_text())
            except Exception:
                pass

            agent_records = _load_jsonl(jsonl_file)
            agent_conversation = _parse_conversation(agent_records)
            agent_stats = _compute_stats(agent_conversation)

            # Extract description and files touched with operation types
            description = ""
            files_ops: dict[str, set[str]] = {}  # filename -> set of op codes
            for amsg in agent_conversation:
                for tc in amsg.get("tool_calls", []):
                    inp = tc.get("input", {})
                    name = tc.get("name", "")
                    if isinstance(inp, dict) and inp.get("file_path"):
                        fname = inp["file_path"].rsplit("/", 1)[-1]
                        op = _tool_to_op(name)
                        if op:
                            files_ops.setdefault(fname, set()).add(op)

            agents.append({
                "agent_id": agent_id,
                "agent_type": meta.get("agentType", "unknown"),
                "description": description,
                "stats": agent_stats,
                "conversation": agent_conversation,
                "files_touched": sorted(files_ops.keys()),
                "files_ops": {f: sorted(ops) for f, ops in sorted(files_ops.items())},
            })

    # Aggregate totals
    total_stats = {**parent_stats, "tools": dict(parent_stats["tools"])}
    for agent in agents:
        a = agent["stats"]
        total_stats["api_calls"] += a["api_calls"]
        total_stats["input_tokens"] += a["input_tokens"]
        total_stats["output_tokens"] += a["output_tokens"]
        total_stats["cache_read"] += a["cache_read"]
        total_stats["cache_create"] += a["cache_create"]
        for tool, count in a["tools"].items():
            total_stats["tools"][tool] = total_stats["tools"].get(tool, 0) + count

    # Build execution flow timeline
    # Group consecutive tool calls into phases, track agent spawn/complete
    parent_files: dict[str, set[str]] = {}  # filename -> set of op codes
    agent_descriptions = {}
    agent_idx_counter = 0
    flow_phases = []  # list of {type, msg_index, tools, agent_index, ...}
    current_phase_tools = []
    current_phase_start = 0

    def _flush_phase(end_idx: int):
        nonlocal current_phase_tools, current_phase_start
        if current_phase_tools:
            # Summarize: group by tool name
            tool_counts: dict[str, int] = {}
            files = []
            for t in current_phase_tools:
                tool_counts[t["name"]] = tool_counts.get(t["name"], 0) + 1
                if t.get("file"):
                    files.append(t["file"])
            flow_phases.append({
                "type": "work",
                "msg_start": current_phase_start,
                "msg_end": end_idx,
                "tools": tool_counts,
                "files": files[:6],
                "total_calls": len(current_phase_tools),
            })
            current_phase_tools = []

    for msg_i, msg in enumerate(parent_conversation):
        if msg["type"] != "assistant":
            continue
        for tc in msg.get("tool_calls", []):
            inp = tc.get("input", {})
            name = tc.get("name", "?")

            if name == "Agent":
                # Flush any accumulated work before the spawn
                _flush_phase(msg_i)
                desc = inp.get("description", "") if isinstance(inp, dict) else ""
                flow_phases.append({
                    "type": "agent_spawn",
                    "msg_index": msg_i,
                    "agent_index": agent_idx_counter,
                    "description": desc,
                    "tool_use_id": tc.get("id", ""),
                })
                agent_descriptions[agent_idx_counter] = {"desc": desc, "parent_msg": msg_i}
                agent_idx_counter += 1
                current_phase_start = msg_i + 1
            elif name == "TaskOutput":
                # Agent result check — marks return from agent
                _flush_phase(msg_i)
                flow_phases.append({
                    "type": "agent_return",
                    "msg_index": msg_i,
                })
                current_phase_start = msg_i + 1
            else:
                if not current_phase_tools:
                    current_phase_start = msg_i
                step: dict[str, Any] = {"name": name}
                if isinstance(inp, dict) and inp.get("file_path"):
                    fname = inp["file_path"].rsplit("/", 1)[-1]
                    step["file"] = fname
                    op = _tool_to_op(name)
                    if op:
                        parent_files.setdefault(fname, set()).add(op)
                current_phase_tools.append(step)

    _flush_phase(len(parent_conversation))

    # Match agent descriptions to agent list
    for i, agent in enumerate(agents):
        if i in agent_descriptions:
            agent["description"] = agent_descriptions[i]["desc"]
            agent["parent_msg_index"] = agent_descriptions[i]["parent_msg"]

    return {
        "session": session_meta,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "parent": {
            "stats": parent_stats,
            "conversation": parent_conversation,
            "files_touched": sorted(parent_files.keys()),
            "files_ops": {f: sorted(ops) for f, ops in sorted(parent_files.items())},
        },
        "agents": agents,
        "totals": total_stats,
        "flow": flow_phases,
    }


def _compute_stats(conversation: list[dict]) -> dict:
    stats = {
        "api_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read": 0,
        "cache_create": 0,
        "tools": {},
        "models": {},
        "user_messages": 0,
    }
    for msg in conversation:
        if msg["type"] == "assistant":
            stats["api_calls"] += 1
            usage = msg.get("usage", {})
            stats["input_tokens"] += usage.get("input_tokens", 0)
            stats["output_tokens"] += usage.get("output_tokens", 0)
            stats["cache_read"] += usage.get("cache_read", 0)
            stats["cache_create"] += usage.get("cache_create", 0)
            model = msg.get("model", "unknown")
            stats["models"][model] = stats["models"].get(model, 0) + 1
            for tc in msg.get("tool_calls", []):
                name = tc.get("name", "?")
                stats["tools"][name] = stats["tools"].get(name, 0) + 1
        elif msg["type"] == "user":
            stats["user_messages"] += 1
    return stats


# ---------------------------------------------------------------------------
# HTML report generation
# ---------------------------------------------------------------------------

def _esc(s: Any) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def generate_html_report(data: dict, output_path: str):
    """Generate a searchable HTML conversation report."""
    session = data.get("session", {})
    totals = data.get("totals", {})
    parent = data.get("parent", {})
    agents = data.get("agents", [])

    skill_name = session.get("slug", session.get("session_id", "Unknown"))

    # Build conversation JSON for the frontend
    all_conversations = {
        "parent": parent.get("conversation", []),
    }
    for i, agent in enumerate(agents):
        key = f"agent_{i}_{agent['agent_id'][:12]}"
        all_conversations[key] = agent.get("conversation", [])

    # Truncate large tool inputs to keep HTML size manageable
    def _truncate_for_html(convs):
        for key, msgs in convs.items():
            for msg in msgs:
                for tc in msg.get("tool_calls", []):
                    inp = tc.get("input", {})
                    if not isinstance(inp, dict):
                        continue
                    # Write/Edit: truncate content fields
                    for field in ("content", "new_string", "old_string"):
                        if field in inp and isinstance(inp[field], str) and len(inp[field]) > 2000:
                            inp[field] = inp[field][:2000] + f"\n... ({len(inp[field]) - 2000} more chars)"
                    # Agent: truncate prompt
                    if "prompt" in inp and isinstance(inp["prompt"], str) and len(inp["prompt"]) > 3000:
                        inp["prompt"] = inp["prompt"][:3000] + f"\n... ({len(inp['prompt']) - 3000} more chars)"
                # Truncate tool_result text parts
                for tr in msg.get("tool_results", []):
                    for part in tr.get("parts", []):
                        if part.get("type") == "text" and isinstance(part.get("text"), str):
                            if len(part["text"]) > 1500:
                                part["text"] = part["text"][:1500] + f"\n... ({len(part['text']) - 1500} more chars)"
        return convs

    _truncate_for_html(all_conversations)
    # Escape </script> in JSON to prevent breaking the HTML script tag
    conversations_json = json.dumps(all_conversations).replace("</", "<\\/")

    # Build panel metadata for cross-referencing (agent panels get parent_msg_index)
    panel_meta: dict[str, dict] = {"parent": {"type": "parent"}}
    for i, agent in enumerate(agents):
        panel_key = f"agent_{i}_{agent['agent_id'][:12]}"
        panel_meta[panel_key] = {
            "type": "agent",
            "parent_msg_index": agent.get("parent_msg_index"),
            "agent_index": i,
        }
    panel_meta_json = json.dumps(panel_meta).replace("</", "<\\/")

    # Build flow diagram data
    flow_data = {
        "steps": data.get("flow", []),
        "agents": [
            {
                "agent_id": a["agent_id"][:12],
                "agent_type": a["agent_type"],
                "description": a.get("description", ""),
                "api_calls": a["stats"]["api_calls"],
                "output_tokens": a["stats"]["output_tokens"],
                "tools": a["stats"]["tools"],
                "files": a.get("files_touched", []),
                "files_ops": a.get("files_ops", {}),
                "parent_msg_index": a.get("parent_msg_index"),
            }
            for a in agents
        ],
        "parent_files": data.get("parent", {}).get("files_touched", []),
        "parent_api_calls": parent.get("stats", {}).get("api_calls", 0),
    }
    flow_json = json.dumps(flow_data).replace("</", "<\\/")

    # Stats cards
    tools_sorted = sorted(totals.get("tools", {}).items(), key=lambda x: -x[1])
    tools_html = "".join(
        f'<span class="tool-badge">{_esc(name)} <strong>{count}</strong></span>'
        for name, count in tools_sorted[:15]
    )

    agent_rows = ""
    for i, agent in enumerate(agents):
        s = agent["stats"]
        top_tools = ", ".join(f"{k}({v})" for k, v in sorted(s["tools"].items(), key=lambda x: -x[1])[:5])
        agent_rows += f"""<tr>
            <td><code>{_esc(agent['agent_id'][:16])}</code></td>
            <td>{_esc(agent['agent_type'])}</td>
            <td>{s['api_calls']}</td>
            <td>{s['input_tokens']:,}</td>
            <td>{s['output_tokens']:,}</td>
            <td>{_esc(top_tools)}</td>
        </tr>"""

    agent_tabs_html = "".join(
        f'<div class="agent-tab" data-target="agent_{i}_{_esc(a["agent_id"][:12])}">'
        f'{_esc(a["agent_type"])} ({a["stats"]["api_calls"]} calls)</div>'
        for i, a in enumerate(agents)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Session Analysis &mdash; {_esc(skill_name)}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; background: #f9fafb; color: #111827; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .stat-card {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; background: #fff; border-top: 3px solid var(--accent, #3b82f6); }}
  .stat-card .label {{ font-size: .7rem; color: #6b7280; text-transform: uppercase; letter-spacing: .05em; }}
  .stat-card .value {{ font-size: 1.3rem; font-weight: 700; margin-top: .25rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .875rem; }}
  th, td {{ text-align: left; padding: .5rem .75rem; border-bottom: 1px solid #e5e7eb; }}
  th {{ font-weight: 600; font-size: .75rem; text-transform: uppercase; letter-spacing: .04em; color: #374151; background: #f3f4f6; }}
  .tool-badge {{ display: inline-block; background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-size: .75rem; margin: 2px; }}
  section {{ margin: 2rem 0; }}
  section h2 {{ font-size: 1.1rem; font-weight: 700; border-bottom: 2px solid #e5e7eb; padding-bottom: .4rem; margin-bottom: 1rem; }}
  .conv-controls {{ display: flex; gap: .75rem; flex-wrap: wrap; align-items: center; margin-bottom: 1rem; padding: 1rem; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; position: sticky; top: 0; z-index: 20; }}
  .conv-controls input[type="search"] {{ flex: 1; min-width: 200px; padding: .5rem .75rem; border: 1px solid #d1d5db; border-radius: 6px; font-size: .875rem; }}
  .conv-controls select {{ padding: .5rem; border: 1px solid #d1d5db; border-radius: 6px; font-size: .8rem; }}
  .conv-controls label {{ font-size: .8rem; color: #374151; display: flex; align-items: center; gap: .3rem; }}
  .match-count {{ font-size: .75rem; color: #6b7280; min-width: 80px; }}
  .flow-filter-banner {{ display: none; background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; padding: .5rem .75rem; margin-bottom: .75rem; font-size: .82rem; color: #92400e; align-items: center; gap: .5rem; }}
  .flow-filter-banner.active {{ display: flex; }}
  .flow-filter-banner button {{ background: #f59e0b; color: #fff; border: none; border-radius: 4px; padding: .25rem .6rem; font-size: .75rem; cursor: pointer; font-weight: 600; }}
  .flow-filter-banner button:hover {{ background: #d97706; }}
  .message {{ margin: .5rem 0; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; overflow: hidden; }}
  .message.hidden {{ display: none; }}
  .message.highlight {{ border-color: #fbbf24; box-shadow: 0 0 0 2px rgba(251,191,36,.3); }}
  .msg-header {{ display: flex; justify-content: space-between; align-items: center; padding: .5rem .75rem; font-size: .8rem; cursor: pointer; user-select: none; }}
  .msg-header:hover {{ background: #f9fafb; }}
  .msg-user .msg-header {{ background: #eff6ff; border-bottom: 1px solid #dbeafe; }}
  .msg-assistant .msg-header {{ background: #f0fdf4; border-bottom: 1px solid #dcfce7; }}
  .msg-body {{ padding: .75rem; font-size: .82rem; white-space: pre-wrap; word-break: break-word; max-height: 600px; overflow-y: auto; display: none; }}
  .msg-body.expanded {{ display: block; }}
  .msg-meta {{ display: flex; gap: 1rem; align-items: center; }}
  .msg-meta span {{ font-size: .72rem; color: #6b7280; }}
  .msg-role {{ font-weight: 700; font-size: .8rem; }}
  .msg-role.user {{ color: #2563eb; }}
  .msg-role.assistant {{ color: #16a34a; }}
  .msg-role.user.subagent {{ color: #7c3aed; }}
  .msg-role.assistant.subagent {{ color: #b45309; }}
  .msg-role.tool-response {{ color: #64748b; font-weight: 600; }}
  .msg-tool-response .msg-header {{ background: #f8fafc; border-bottom: 1px solid #e2e8f0; }}
  .tool-call {{ background: #fefce8; border: 1px solid #fde68a; border-radius: 6px; padding: .6rem .8rem; margin: .5rem 0; font-size: .8rem; }}
  .tool-call-header {{ display: flex; align-items: center; gap: .5rem; margin-bottom: .4rem; }}
  .tool-name {{ font-weight: 700; color: #92400e; font-size: .82rem; }}
  .tool-file {{ font-family: ui-monospace, monospace; font-size: .75rem; color: #4338ca; background: #e0e7ff; padding: 1px 6px; border-radius: 3px; }}
  .tool-desc {{ font-size: .72rem; color: #6b7280; font-style: italic; }}
  .code-block {{ background: #1e1e2e; color: #cdd6f4; padding: .6rem .8rem; border-radius: 4px; font-family: ui-monospace, monospace; font-size: .75rem; white-space: pre-wrap; overflow-x: auto; max-height: 300px; overflow-y: auto; margin-top: .3rem; }}
  .diff-block {{ background: #1a1b26; color: #c0caf5; padding: .6rem .8rem; border-radius: 4px; font-family: ui-monospace, monospace; font-size: .75rem; white-space: pre-wrap; overflow-x: auto; max-height: 400px; overflow-y: auto; margin-top: .3rem; }}
  .diff-del {{ color: #f7768e; background: rgba(247,118,142,.1); display: block; }}
  .diff-add {{ color: #9ece6a; background: rgba(158,206,106,.1); display: block; }}
  .diff-hdr {{ color: #7aa2f7; display: block; margin-bottom: .3rem; }}
  .tool-call.bash-call {{ background: #f0fdf4; border-color: #bbf7d0; }}
  .tool-call.edit-call {{ background: #faf5ff; border-color: #e9d5ff; }}
  .tool-call.read-call {{ background: #eff6ff; border-color: #bfdbfe; }}
  .tool-call.write-call {{ background: #fff7ed; border-color: #fed7aa; }}
  .tool-call.grep-call {{ background: #f0fdfa; border-color: #99f6e4; }}
  .tool-call.agent-call {{ background: #fef2f2; border-color: #fecaca; }}
  .tool-result {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: .5rem .7rem; margin: .4rem 0; font-size: .8rem; }}
  .tool-result.error {{ background: #fef2f2; border-color: #fecaca; }}
  .tool-result-header {{ font-size: .72rem; color: #64748b; font-weight: 600; margin-bottom: .3rem; text-transform: uppercase; letter-spacing: .04em; }}
  .tool-loaded-badge {{ display: inline-block; background: #dbeafe; color: #1e40af; padding: 1px 8px; border-radius: 4px; font-size: .72rem; font-weight: 600; margin: 1px 3px; }}
  .tool-result-code {{ background: #1e293b; color: #e2e8f0; padding: .5rem .7rem; border-radius: 4px; font-family: ui-monospace, monospace; font-size: .72rem; white-space: pre-wrap; overflow-x: auto; max-height: 250px; overflow-y: auto; margin-top: .3rem; line-height: 1.4; }}
  .tool-result-code .line-num {{ color: #64748b; user-select: none; display: inline-block; min-width: 3ch; text-align: right; margin-right: .8ch; }}
  .tool-call.glob-call {{ background: #fefce8; border-color: #fde68a; }}
  .tool-search {{ font-family: ui-monospace, monospace; font-size: .75rem; color: #0d9488; }}
  .thinking-block {{ background: #f5f3ff; border: 1px solid #e9d5ff; border-radius: 4px; padding: .4rem .6rem; margin: .3rem 0; font-size: .75rem; color: #6b21a8; font-style: italic; max-height: 150px; overflow-y: auto; }}
  .agent-tabs {{ display: flex; gap: 2px; flex-wrap: wrap; margin-bottom: .5rem; }}
  .agent-tab {{ padding: .4rem .8rem; border: 1px solid #e5e7eb; border-bottom: none; border-radius: 6px 6px 0 0; font-size: .8rem; cursor: pointer; background: #f3f4f6; }}
  .agent-tab.active {{ background: #fff; font-weight: 600; border-bottom: 2px solid #fff; margin-bottom: -1px; z-index: 1; }}
  .conv-panel {{ border: 1px solid #e5e7eb; border-radius: 0 0 8px 8px; padding: 1rem; background: #fff; }}
  .conv-panel.hidden {{ display: none; }}
  nav {{ background: #fff; border-bottom: 1px solid #e5e7eb; padding: .6rem 0; font-size: .85rem; position: sticky; top: 0; z-index: 10; }}
  nav a {{ color: #3b82f6; text-decoration: none; }}
  nav a:hover {{ text-decoration: underline; }}
  /* Flow diagram */
  #flow-legend {{ display: flex; align-items: center; gap: .75rem; padding: .5rem .75rem; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px 8px 0 0; border-bottom: none; font-size: .75rem; color: #6b7280; flex-wrap: wrap; }}
  #flow-legend .leg-title {{ font-weight: 700; color: #374151; margin-right: .25rem; }}
  #flow-legend .leg-item {{ display: inline-flex; align-items: center; gap: 3px; }}
  #flow-legend .leg-badge {{ display: inline-block; width: 16px; height: 13px; border-radius: 2px; text-align: center; font-size: 8px; font-weight: 700; font-family: ui-monospace, monospace; line-height: 13px; }}
  #flow-wrapper {{ width: 100%; overflow-x: auto; background: #fafbfc; border: 1px solid #e5e7eb; border-radius: 0 0 8px 8px; padding: 1rem; }}
  #flow-canvas {{ position: relative; }}
</style>
</head>
<body>
<header style="background:#1e1e2e;color:#cdd6f4;padding:1rem 0">
  <div style="max-width:1200px;margin:0 auto;padding:0 1rem;display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-size:.7rem;color:#a6e3a1;text-transform:uppercase;letter-spacing:.1em">Session Analysis</div>
      <div style="font-size:1.3rem;font-weight:700">{_esc(skill_name)}</div>
      <div style="font-size:.75rem;color:#6c7086;margin-top:.2rem">{_esc(session.get('cwd', ''))}</div>
    </div>
    <div style="text-align:right;font-size:.75rem;color:#6c7086">
      <div>Session: <code>{_esc(session.get('session_id', '?')[:16])}</code></div>
      <div>Branch: {_esc(session.get('git_branch', '?'))}</div>
      <div>v{_esc(session.get('version', '?'))}</div>
    </div>
  </div>
</header>

<nav>
  <div style="max-width:1200px;margin:0 auto;padding:0 1rem">
    <a href="#stats">Stats</a> &middot;
    <a href="#agents">Agents</a> &middot;
    <a href="#tools">Tools</a> &middot;
    <a href="#flow">Flow</a> &middot;
    <a href="#conversation">Conversation</a>
  </div>
</nav>

<div class="container">

<section id="stats">
  <h2>API Usage Summary</h2>
  <div class="stats-grid">
    <div class="stat-card" style="--accent:#3b82f6"><div class="label">API Calls</div><div class="value">{totals.get('api_calls', 0)}</div></div>
    <div class="stat-card" style="--accent:#8b5cf6"><div class="label">Input Tokens</div><div class="value">{totals.get('input_tokens', 0):,}</div></div>
    <div class="stat-card" style="--accent:#0ea5e9"><div class="label">Output Tokens</div><div class="value">{totals.get('output_tokens', 0):,}</div></div>
    <div class="stat-card" style="--accent:#14b8a6"><div class="label">Cache Read</div><div class="value">{totals.get('cache_read', 0):,}</div></div>
    <div class="stat-card" style="--accent:#f59e0b"><div class="label">Cache Created</div><div class="value">{totals.get('cache_create', 0):,}</div></div>
    <div class="stat-card" style="--accent:#10b981"><div class="label">Agents Spawned</div><div class="value">{len(agents)}</div></div>
  </div>
</section>

<section id="agents">
  <h2>Agent Breakdown</h2>
  {"<p><em>No subagents spawned in this session.</em></p>" if not agents else f'''
  <table>
    <thead><tr><th>Agent ID</th><th>Type</th><th>API Calls</th><th>Input Tokens</th><th>Output Tokens</th><th>Top Tools</th></tr></thead>
    <tbody>{agent_rows}</tbody>
  </table>'''}
</section>

<section id="tools">
  <h2>Tool Usage</h2>
  <div style="padding:1rem">{tools_html or '<em>No tool calls recorded.</em>'}</div>
</section>

<section id="flow">
  <h2>Execution Flow</h2>
  <div id="flow-legend"></div>
  <div id="flow-wrapper"><div id="flow-canvas"></div></div>
</section>

<section id="conversation">
  <h2>Conversation Audit</h2>

  <div id="flow-filter-banner" class="flow-filter-banner">
    <span id="flow-filter-text"></span>
    <button id="flow-filter-clear">Clear Filter</button>
  </div>

  <div class="conv-controls">
    <input type="search" id="search-input" placeholder="Search messages, tool calls, thinking..." autocomplete="off">
    <select id="type-filter">
      <option value="all">All Types</option>
      <option value="user">User Only</option>
      <option value="assistant">Assistant Only</option>
    </select>
    <select id="content-filter">
      <option value="all">All Content</option>
      <option value="tool_calls">With Tool Calls</option>
      <option value="thinking">With Thinking</option>
      <option value="text">Text Only</option>
    </select>
    <label><input type="checkbox" id="show-thinking" checked> Thinking</label>
    <label><input type="checkbox" id="show-tools" checked> Tools</label>
    <label><input type="checkbox" id="auto-expand"> Auto-expand</label>
    <span class="match-count" id="match-count"></span>
  </div>

  <div class="agent-tabs" id="agent-tabs">
    <div class="agent-tab active" data-target="parent">Main Session ({parent.get('stats', {}).get('api_calls', 0)} calls)</div>
    {agent_tabs_html}
  </div>

  <div id="conv-panels"></div>
</section>

</div>

<script>
(function() {{
  "use strict";
  var CONVERSATIONS = {conversations_json};
  var PANEL_META = {panel_meta_json};
  var currentPanel = "parent";

  function escText(s) {{
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }}

  function createEl(tag, attrs, children) {{
    var el = document.createElement(tag);
    if (attrs) {{
      for (var k in attrs) {{
        if (k === "className") el.className = attrs[k];
        else if (k === "textContent") el.textContent = attrs[k];
        else if (k.indexOf("data-") === 0) el.setAttribute(k, attrs[k]);
        else el.setAttribute(k, attrs[k]);
      }}
    }}
    if (children) {{
      for (var i = 0; i < children.length; i++) {{
        if (typeof children[i] === "string") el.appendChild(document.createTextNode(children[i]));
        else if (children[i]) el.appendChild(children[i]);
      }}
    }}
    return el;
  }}

  function buildSearchText(msg) {{
    var parts = [msg.text || ""];
    if (msg.thinking) {{
      for (var i = 0; i < msg.thinking.length; i++) parts.push(msg.thinking[i]);
    }}
    if (msg.tool_calls) {{
      for (var j = 0; j < msg.tool_calls.length; j++) {{
        var tc = msg.tool_calls[j];
        parts.push(tc.name);
        var inp = tc.input || {{}};
        parts.push(inp.command || "");
        parts.push(inp.file_path || "");
        parts.push(inp.pattern || "");
        parts.push(inp.content || "");
        parts.push(inp.old_string || "");
        parts.push(inp.new_string || "");
        parts.push(inp.description || "");
        parts.push(inp.prompt || "");
        parts.push(inp.query || "");
      }}
    }}
    if (msg.model) parts.push(msg.model);
    return parts.join(" ");
  }}

  function shortPath(p) {{
    if (!p) return "";
    var parts = p.split("/");
    if (parts.length <= 3) return p;
    return ".../" + parts.slice(-3).join("/");
  }}

  function renderToolCall(tc) {{
    var name = tc.name;
    var inp = tc.input || {{}};
    var wrapper = createEl("div", {{ className: "tool-call" }});
    var cssClass = "";

    // Determine styling class
    var lcName = name.toLowerCase();
    if (lcName === "bash") cssClass = "bash-call";
    else if (lcName === "edit") cssClass = "edit-call";
    else if (lcName === "read") cssClass = "read-call";
    else if (lcName === "write") cssClass = "write-call";
    else if (lcName === "grep") cssClass = "grep-call";
    else if (lcName === "agent") cssClass = "agent-call";
    else if (lcName === "glob") cssClass = "glob-call";
    if (cssClass) wrapper.classList.add(cssClass);

    // Header with tool name
    var header = createEl("div", {{ className: "tool-call-header" }});
    header.appendChild(createEl("span", {{ className: "tool-name", textContent: name }}));

    // File path badge for file-based tools
    if (inp.file_path) {{
      header.appendChild(createEl("span", {{ className: "tool-file", textContent: shortPath(inp.file_path) }}));
    }}

    // Description for Bash/Agent
    if (inp.description) {{
      header.appendChild(createEl("span", {{ className: "tool-desc", textContent: inp.description }}));
    }}

    wrapper.appendChild(header);

    // Tool-specific body rendering
    if (name === "Bash" && inp.command) {{
      var codeBlock = createEl("div", {{ className: "code-block" }});
      codeBlock.appendChild(createEl("span", {{ textContent: "$ " + inp.command }}));
      wrapper.appendChild(codeBlock);

    }} else if (name === "Edit" && (inp.old_string || inp.new_string)) {{
      var diffBlock = createEl("div", {{ className: "diff-block" }});
      if (inp.file_path) {{
        var hdr = createEl("span", {{ className: "diff-hdr", textContent: "--- " + shortPath(inp.file_path) }});
        diffBlock.appendChild(hdr);
      }}
      if (inp.old_string) {{
        var oldLines = inp.old_string.split("\\n");
        for (var oi = 0; oi < oldLines.length; oi++) {{
          diffBlock.appendChild(createEl("span", {{ className: "diff-del", textContent: "- " + oldLines[oi] }}));
        }}
      }}
      if (inp.new_string) {{
        var newLines = inp.new_string.split("\\n");
        for (var ni = 0; ni < newLines.length; ni++) {{
          diffBlock.appendChild(createEl("span", {{ className: "diff-add", textContent: "+ " + newLines[ni] }}));
        }}
      }}
      if (inp.replace_all) {{
        diffBlock.appendChild(createEl("span", {{ className: "diff-hdr", textContent: "(replace_all: true)" }}));
      }}
      wrapper.appendChild(diffBlock);

    }} else if (name === "Write" && inp.content) {{
      var preview = inp.content;
      if (preview.length > 500) preview = preview.substring(0, 500) + "\\n... (" + (inp.content.length - 500) + " more chars)";
      var writeBlock = createEl("div", {{ className: "code-block" }});
      writeBlock.appendChild(document.createTextNode(preview));
      wrapper.appendChild(writeBlock);

    }} else if (name === "Read") {{
      // Already shown file path in header, add offset/limit if present
      var readInfo = [];
      if (inp.offset) readInfo.push("offset: " + inp.offset);
      if (inp.limit) readInfo.push("limit: " + inp.limit);
      if (readInfo.length > 0) {{
        wrapper.appendChild(createEl("span", {{ className: "tool-desc", textContent: readInfo.join(", ") }}));
      }}

    }} else if (name === "Grep") {{
      var grepParts = [];
      if (inp.pattern) grepParts.push(inp.pattern);
      var grepBlock = createEl("div", {{ className: "code-block" }});
      var grepCmd = "grep";
      if (inp["-i"]) grepCmd += " -i";
      if (inp.output_mode) grepCmd += " --" + inp.output_mode;
      if (inp.glob) grepCmd += ' --glob "' + inp.glob + '"';
      if (inp.type) grepCmd += " --type " + inp.type;
      grepCmd += ' "' + (inp.pattern || "") + '"';
      if (inp.path) grepCmd += " " + shortPath(inp.path);
      grepBlock.appendChild(document.createTextNode("$ " + grepCmd));
      wrapper.appendChild(grepBlock);

    }} else if (name === "Glob") {{
      var globBlock = createEl("div", {{ className: "code-block" }});
      var globCmd = "glob " + (inp.pattern || "");
      if (inp.path) globCmd += " in " + shortPath(inp.path);
      globBlock.appendChild(document.createTextNode("$ " + globCmd));
      wrapper.appendChild(globBlock);

    }} else if (name === "Agent") {{
      if (inp.prompt) {{
        var agentBlock = createEl("div", {{ className: "code-block" }});
        agentBlock.style.background = "#1c1917";
        agentBlock.style.color = "#fbbf24";
        var promptPreview = inp.prompt;
        if (promptPreview.length > 800) promptPreview = promptPreview.substring(0, 800) + "\\n... (" + (inp.prompt.length - 800) + " more chars)";
        agentBlock.appendChild(document.createTextNode(promptPreview));
        wrapper.appendChild(agentBlock);
      }}
      if (inp.subagent_type) {{
        wrapper.querySelector(".tool-call-header").appendChild(
          createEl("span", {{ className: "tool-file", textContent: inp.subagent_type }})
        );
      }}

    }} else {{
      // Generic: show JSON
      var genericBlock = createEl("div", {{ className: "code-block" }});
      var jsonStr = JSON.stringify(inp, null, 2);
      if (jsonStr.length > 600) jsonStr = jsonStr.substring(0, 600) + "\\n...";
      genericBlock.appendChild(document.createTextNode(jsonStr));
      wrapper.appendChild(genericBlock);
    }}

    return wrapper;
  }}

  function renderToolResult(tr) {{
    var parts = tr.parts || [];
    // Skip entirely empty results or results with only system noise
    if (parts.length === 0) return createEl("span");
    var allNoise = true;
    for (var cn = 0; cn < parts.length; cn++) {{
      if (parts[cn].type !== "system_noise") {{ allNoise = false; break; }}
    }}
    if (allNoise) return createEl("span");

    var wrapper = createEl("div", {{
      className: "tool-result" + (tr.is_error ? " error" : "")
    }});

    var header = createEl("div", {{ className: "tool-result-header" }});
    header.textContent = tr.is_error ? "Error Result" : "Tool Result";
    wrapper.appendChild(header);

    var toolLoadedNames = [];
    var textParts = [];

    for (var pi = 0; pi < parts.length; pi++) {{
      var part = parts[pi];
      if (part.type === "tool_loaded") {{
        toolLoadedNames.push(part.tool_name);
      }} else if (part.type === "text") {{
        textParts.push(part.text || "");
      }}
    }}

    // Render tool_loaded as compact badges
    if (toolLoadedNames.length > 0) {{
      header.textContent = "Tools Loaded";
      var badgeRow = createEl("div", {{}});
      badgeRow.style.display = "flex";
      badgeRow.style.flexWrap = "wrap";
      badgeRow.style.gap = "4px";
      for (var tl = 0; tl < toolLoadedNames.length; tl++) {{
        badgeRow.appendChild(createEl("span", {{
          className: "tool-loaded-badge",
          textContent: toolLoadedNames[tl]
        }}));
      }}
      wrapper.appendChild(badgeRow);
    }}

    // Render text content
    for (var ti = 0; ti < textParts.length; ti++) {{
      var text = textParts[ti];
      if (!text || text.length < 3) continue;

      // Detect file content with line numbers (e.g. "  1→#!/usr/bin/env python3")
      var hasLineNums = /^\\s*\\d+\\u2192/.test(text) || /^\\s*\\d+→/.test(text);
      if (hasLineNums) {{
        var codeBlock = createEl("div", {{ className: "tool-result-code" }});
        var lines = text.split("\\n");
        var maxLines = Math.min(lines.length, 30);
        for (var li = 0; li < maxLines; li++) {{
          var line = lines[li];
          // Split on → to separate line number from content
          var arrowIdx = line.indexOf("\u2192");
          if (arrowIdx === -1) arrowIdx = line.indexOf("→");
          if (arrowIdx !== -1) {{
            var numSpan = createEl("span", {{
              className: "line-num",
              textContent: line.substring(0, arrowIdx).trim()
            }});
            codeBlock.appendChild(numSpan);
            codeBlock.appendChild(document.createTextNode(line.substring(arrowIdx + 1) + "\\n"));
          }} else {{
            codeBlock.appendChild(document.createTextNode(line + "\\n"));
          }}
        }}
        if (lines.length > 30) {{
          var moreSpan = createEl("span", {{
            textContent: "\\n... " + (lines.length - 30) + " more lines",
            style: "color: #94a3b8; font-style: italic;"
          }});
          codeBlock.appendChild(moreSpan);
        }}
        wrapper.appendChild(codeBlock);
      }} else if (text.length > 200) {{
        // Long text — show in a code block
        var longBlock = createEl("div", {{ className: "tool-result-code" }});
        var preview = text.length > 1500 ? text.substring(0, 1500) + "\\n... (" + (text.length - 1500) + " more chars)" : text;
        longBlock.appendChild(document.createTextNode(preview));
        wrapper.appendChild(longBlock);
      }} else {{
        // Short text — inline
        wrapper.appendChild(createEl("div", {{
          textContent: text,
          style: "color: #475569; font-size: .78rem;"
        }}));
      }}
    }}

    return wrapper;
  }}

  function buildPanels() {{
    var container = document.getElementById("conv-panels");
    while (container.firstChild) container.removeChild(container.firstChild);

    for (var key in CONVERSATIONS) {{
      var messages = CONVERSATIONS[key];
      var panel = createEl("div", {{
        className: "conv-panel" + (key === "parent" ? "" : " hidden"),
        id: "panel-" + key,
        "data-key": key
      }});

      for (var i = 0; i < messages.length; i++) {{
        var msg = messages[i];

        // Header
        var isParent = (key === "parent");
        var panelMeta = PANEL_META[key] || {{}};
        // Distinguish real user input from tool result messages
        var hasToolResults = msg.tool_results && msg.tool_results.length > 0;
        var hasRealText = msg.text && msg.text.trim().length > 0 && !/^\\[tool_result/.test(msg.text.trim());
        var isToolResponse = (msg.type === "user" && hasToolResults && !hasRealText);

        var div = createEl("div", {{
          className: "message msg-" + msg.type + (isToolResponse ? " msg-tool-response" : ""),
          "data-type": msg.type,
          "data-index": String(i),
          "data-has-tools": (msg.tool_calls && msg.tool_calls.length > 0) ? "1" : "0",
          "data-has-thinking": (msg.thinking && msg.thinking.length > 0) ? "1" : "0",
          "data-search-text": buildSearchText(msg).toLowerCase()
        }});
        var roleName;
        if (msg.type === "user") {{
          if (isToolResponse) {{
            roleName = "TOOL RESPONSE";
          }} else {{
            roleName = isParent ? "USER" : "CALLER";
          }}
        }} else {{
          roleName = isParent ? "AGENT" : "SUBAGENT";
        }}
        var roleLabel = roleName + " \u00b7 msg " + i;
        // Cross-reference: show parent msg index on first CALLER message
        if (!isParent && msg.type === "user" && i === 0 && panelMeta.parent_msg_index != null) {{
          roleLabel += " (parent msg " + panelMeta.parent_msg_index + ")";
        }}
        var roleSpan = createEl("span", {{
          className: "msg-role " + msg.type + (isParent ? "" : " subagent") + (isToolResponse ? " tool-response" : ""),
          textContent: roleLabel
        }});

        var metaEl = createEl("div", {{ className: "msg-meta" }});

        if (msg.type === "assistant" && msg.usage) {{
          metaEl.appendChild(createEl("span", {{
            textContent: "in:" + (msg.usage.input_tokens || 0).toLocaleString() +
                         " out:" + (msg.usage.output_tokens || 0).toLocaleString()
          }}));
          if (msg.model) {{
            metaEl.appendChild(createEl("span", {{
              textContent: msg.model.replace("claude-", "")
            }}));
          }}
        }}

        if (msg.tool_calls && msg.tool_calls.length > 0) {{
          var toolNames = [];
          for (var t = 0; t < msg.tool_calls.length; t++) toolNames.push(msg.tool_calls[t].name);
          var toolSpan = createEl("span", {{ textContent: toolNames.join(", ") }});
          toolSpan.style.color = "#92400e";
          metaEl.appendChild(toolSpan);
        }}

        var expandIcon = createEl("span", {{ textContent: "+" }});
        expandIcon.style.fontWeight = "700";
        expandIcon.style.color = "#9ca3af";

        var header = createEl("div", {{ className: "msg-header" }}, [roleSpan, metaEl, expandIcon]);
        (function(d, icon) {{
          header.addEventListener("click", function() {{
            var body = d.querySelector(".msg-body");
            var isExpanded = body.classList.contains("expanded");
            body.classList.toggle("expanded");
            icon.textContent = isExpanded ? "+" : "-";
          }});
        }})(div, expandIcon);

        div.appendChild(header);

        // Body
        var body = createEl("div", {{ className: "msg-body" }});

        // Thinking blocks
        if (msg.thinking && msg.thinking.length > 0) {{
          for (var ti = 0; ti < msg.thinking.length; ti++) {{
            body.appendChild(createEl("div", {{
              className: "thinking-block",
              textContent: msg.thinking[ti]
            }}));
          }}
        }}

        // Text content
        if (msg.text) {{
          var textDiv = createEl("div", {{ textContent: msg.text }});
          textDiv.style.whiteSpace = "pre-wrap";
          body.appendChild(textDiv);
        }}

        // Tool calls — rich rendering per type
        if (msg.tool_calls && msg.tool_calls.length > 0) {{
          for (var tc = 0; tc < msg.tool_calls.length; tc++) {{
            body.appendChild(renderToolCall(msg.tool_calls[tc]));
          }}
        }}

        // Tool results — rendered as structured response blocks
        if (msg.tool_results && msg.tool_results.length > 0) {{
          for (var tr = 0; tr < msg.tool_results.length; tr++) {{
            body.appendChild(renderToolResult(msg.tool_results[tr]));
          }}
        }}

        div.appendChild(body);
        panel.appendChild(div);
      }}

      container.appendChild(panel);
    }}
  }}

  function applyFilters() {{
    var search = document.getElementById("search-input").value.toLowerCase();
    var typeFilter = document.getElementById("type-filter").value;
    var contentFilter = document.getElementById("content-filter").value;
    var showThinking = document.getElementById("show-thinking").checked;
    var showTools = document.getElementById("show-tools").checked;
    var autoExpand = document.getElementById("auto-expand").checked;

    var panel = document.getElementById("panel-" + currentPanel);
    if (!panel) return;

    var messages = panel.querySelectorAll(".message");
    var visible = 0;
    var matched = 0;

    for (var i = 0; i < messages.length; i++) {{
      var msg = messages[i];
      var show = true;

      if (typeFilter !== "all" && msg.getAttribute("data-type") !== typeFilter) show = false;
      if (contentFilter === "tool_calls" && msg.getAttribute("data-has-tools") !== "1") show = false;
      if (contentFilter === "thinking" && msg.getAttribute("data-has-thinking") !== "1") show = false;
      if (contentFilter === "text" && msg.getAttribute("data-has-tools") === "1") show = false;

      var isMatch = search && msg.getAttribute("data-search-text").indexOf(search) !== -1;
      if (search && !isMatch) show = false;

      if (show) msg.classList.remove("hidden");
      else msg.classList.add("hidden");

      if (isMatch && search.length > 0) msg.classList.add("highlight");
      else msg.classList.remove("highlight");

      if (show) {{
        visible++;
        if (isMatch) matched++;
      }}

      var thinkEls = msg.querySelectorAll(".thinking-block");
      for (var j = 0; j < thinkEls.length; j++) thinkEls[j].style.display = showThinking ? "" : "none";
      var toolEls = msg.querySelectorAll(".tool-call");
      for (var k = 0; k < toolEls.length; k++) toolEls[k].style.display = showTools ? "" : "none";

      if (autoExpand && show) {{
        var bodyEl = msg.querySelector(".msg-body");
        if (bodyEl) bodyEl.classList.add("expanded");
        var iconEl = msg.querySelector(".msg-header span:last-child");
        if (iconEl) iconEl.textContent = "-";
      }}
    }}

    var countEl = document.getElementById("match-count");
    if (search) countEl.textContent = matched + " matches / " + visible + " visible";
    else countEl.textContent = visible + " messages";
  }}

  // Tab switching
  document.getElementById("agent-tabs").addEventListener("click", function(e) {{
    var tab = e.target;
    while (tab && !tab.classList.contains("agent-tab")) tab = tab.parentElement;
    if (!tab) return;

    var tabs = document.querySelectorAll(".agent-tab");
    for (var i = 0; i < tabs.length; i++) tabs[i].classList.remove("active");
    tab.classList.add("active");

    currentPanel = tab.getAttribute("data-target");
    var panels = document.querySelectorAll(".conv-panel");
    for (var j = 0; j < panels.length; j++) {{
      if (panels[j].id === "panel-" + currentPanel) panels[j].classList.remove("hidden");
      else panels[j].classList.add("hidden");
    }}
    applyFilters();
  }});

  document.getElementById("search-input").addEventListener("input", applyFilters);
  document.getElementById("type-filter").addEventListener("change", applyFilters);
  document.getElementById("content-filter").addEventListener("change", applyFilters);
  document.getElementById("show-thinking").addEventListener("change", applyFilters);
  document.getElementById("show-tools").addEventListener("change", applyFilters);
  document.getElementById("auto-expand").addEventListener("change", applyFilters);

  document.addEventListener("keydown", function(e) {{
    if ((e.ctrlKey || e.metaKey) && e.key === "f") {{
      e.preventDefault();
      document.getElementById("search-input").focus();
    }}
  }});

  // Flow diagram — horizontal timeline with dynamic sizing
  var FLOW = {flow_json};

  function buildFlowDiagram() {{
    // Build HTML legend above the diagram
    var legendEl = document.getElementById("flow-legend");
    if (legendEl && (FLOW.agents || []).length > 0) {{
      var legendItems = [
        {{ code: "R", label: "Read", bg: "#dbeafe", fg: "#1e40af" }},
        {{ code: "E", label: "Edit", bg: "#fef3c7", fg: "#92400e" }},
        {{ code: "W", label: "Write", bg: "#d1fae5", fg: "#065f46" }},
        {{ code: "G", label: "Grep", bg: "#ede9fe", fg: "#5b21b6" }},
        {{ code: "B", label: "Bash", bg: "#fee2e2", fg: "#991b1b" }},
        {{ code: "S", label: "Glob", bg: "#e0f2fe", fg: "#075985" }}
      ];
      legendEl.appendChild(createEl("span", {{ className: "leg-title", textContent: "File Operations:" }}));
      for (var lgi = 0; lgi < legendItems.length; lgi++) {{
        var li = legendItems[lgi];
        var item = createEl("span", {{ className: "leg-item" }});
        var badge = createEl("span", {{ className: "leg-badge", textContent: li.code }});
        badge.style.background = li.bg;
        badge.style.color = li.fg;
        badge.style.border = "1px solid " + li.fg;
        item.appendChild(badge);
        item.appendChild(createEl("span", {{ textContent: li.label }}));
        legendEl.appendChild(item);
      }}
    }}

    var canvas = document.getElementById("flow-canvas");
    if (!canvas) return;
    while (canvas.firstChild) canvas.removeChild(canvas.firstChild);

    var phases = FLOW.steps || [];
    var agents = FLOW.agents || [];
    if (phases.length === 0) {{
      canvas.appendChild(createEl("div", {{ textContent: "No flow data recorded." }}));
      return;
    }}

    // --- Text measurement ---
    var measureCanvas = document.createElement("canvas");
    var mctx = measureCanvas.getContext("2d");

    function measureText(text, fontSize, fontFamily, bold) {{
      mctx.font = (bold ? "700 " : "400 ") + fontSize + "px " + (fontFamily || "system-ui, sans-serif");
      return mctx.measureText(text).width;
    }}
    var MONO = "ui-monospace, monospace";
    var SANS = "system-ui, sans-serif";

    // --- Layout constants ---
    var PAD_X = 16;         // horizontal padding inside boxes
    var PAD_Y = 8;          // vertical padding
    var LINE_H = 16;        // line height for text rows
    var PHASE_GAP = 28;     // gap between timeline nodes
    var MAIN_Y = 30;        // Y of main timeline
    var AGENT_GAP_Y = 70;   // gap between timeline and agent row
    var FILE_GAP_Y = 36;    // gap between agent boxes and files
    var FILE_H = 24;
    var FILE_GAP_V = 5;
    var ARROW_COLOR = "#94a3b8";
    var SPAWN_COLOR = "#f59e0b";
    var RETURN_COLOR = "#10b981";
    var MIN_NODE_W = 100;

    // --- Pre-compute node dimensions ---
    // Each node: {{ x, y, w, h, type, phase, agentW, agentH, agentX, fileW }}
    var nodes = [];

    for (var pi = 0; pi < phases.length; pi++) {{
      var phase = phases[pi];
      var lines = [];  // array of {{text, size, font, bold}}
      var nd = {{ type: phase.type, phase: phase, lines: [] }};

      if (phase.type === "work") {{
        var toolKeys = Object.keys(phase.tools || {{}});
        var toolLine = toolKeys.map(function(t) {{ return t + "(" + phase.tools[t] + ")"; }}).join("  ");
        var fileLine = (phase.files || []).join(", ");
        var msgLine = "msg " + (phase.msg_start || 0) + " - " + (phase.msg_end || 0);
        nd.lines = [
          {{ text: toolLine, size: 10, font: MONO, bold: true }},
          {{ text: fileLine, size: 9, font: MONO, bold: false }},
          {{ text: msgLine, size: 9, font: SANS, bold: false }},
        ];
      }} else if (phase.type === "agent_spawn") {{
        var desc = phase.description || "Agent";
        nd.lines = [
          {{ text: "SPAWN", size: 11, font: SANS, bold: true }},
          {{ text: desc, size: 10, font: SANS, bold: true }},
          {{ text: "msg #" + (phase.msg_index || 0), size: 9, font: SANS, bold: false }},
        ];
      }} else if (phase.type === "agent_return") {{
        nd.lines = [
          {{ text: "RETURN", size: 11, font: SANS, bold: true }},
          {{ text: "agents complete", size: 9, font: SANS, bold: false }},
        ];
      }}

      // Compute width from widest line + padding
      var maxLineW = 0;
      for (var li = 0; li < nd.lines.length; li++) {{
        var lw = measureText(nd.lines[li].text, nd.lines[li].size, nd.lines[li].font, nd.lines[li].bold);
        if (lw > maxLineW) maxLineW = lw;
      }}
      nd.w = Math.max(Math.ceil(maxLineW) + PAD_X * 2, MIN_NODE_W);
      nd.h = nd.lines.length * LINE_H + PAD_Y * 2;
      nodes.push(nd);
    }}

    // --- Pre-compute agent box dimensions ---
    var agentNodes = [];
    for (var ai = 0; ai < agents.length; ai++) {{
      var a = agents[ai];
      var aTitle = a.description || a.agent_type || "Agent";
      var aStats = a.api_calls + " calls / " + (a.output_tokens || 0).toLocaleString() + " tokens";
      var aTools = Object.keys(a.tools || {{}}).map(function(t) {{ return t + "(" + a.tools[t] + ")"; }}).join("  ");
      var aFileCount = (a.files || []).length + " files touched";

      var aLines = [
        {{ text: aTitle, size: 11, font: SANS, bold: true }},
        {{ text: aStats, size: 9, font: SANS, bold: false }},
        {{ text: aTools, size: 8, font: MONO, bold: false }},
        {{ text: aFileCount, size: 9, font: SANS, bold: false }},
      ];

      var aMaxW = 0;
      for (var ali = 0; ali < aLines.length; ali++) {{
        var alw = measureText(aLines[ali].text, aLines[ali].size, aLines[ali].font, aLines[ali].bold);
        if (alw > aMaxW) aMaxW = alw;
      }}

      // Also measure file name widths (including badge space)
      var fileW = 80;
      var afiles = a.files || [];
      var aOpsMap = a.files_ops || {{}};
      var BADGE_UNIT = 18; // BADGE_W + BADGE_GAP
      for (var afi = 0; afi < afiles.length && afi < 6; afi++) {{
        var afn = afiles[afi];
        var afOps = aOpsMap[afn] || [];
        var ffw = measureText(afn, 9, MONO, false) + 20 + afOps.length * BADGE_UNIT;
        if (ffw > fileW) fileW = ffw;
      }}

      var aw = Math.max(Math.ceil(aMaxW) + PAD_X * 2, Math.ceil(fileW) + 20, MIN_NODE_W + 40);
      var ah = aLines.length * LINE_H + PAD_Y * 2;

      agentNodes.push({{ lines: aLines, w: aw, h: ah, fileW: Math.ceil(fileW), agent: a }});
    }}

    // --- Assign X positions based on accumulated widths ---
    // Reserve space for swimlane labels on the left
    var LANE_LABEL_W = 100;
    var curX = LANE_LABEL_W + 20;
    var spawnNodeIndices = [];  // indices into nodes[] for spawn phases

    for (var ni = 0; ni < nodes.length; ni++) {{
      nodes[ni].x = curX;
      nodes[ni].y = MAIN_Y;
      if (nodes[ni].type === "agent_spawn") {{
        spawnNodeIndices.push(ni);
      }}
      curX += nodes[ni].w + PHASE_GAP;
    }}

    // Check if agent boxes (which are wider) would overlap under spawn nodes
    // If so, push spawn nodes apart
    if (spawnNodeIndices.length > 1) {{
      for (var si = 1; si < spawnNodeIndices.length; si++) {{
        var prevIdx = spawnNodeIndices[si - 1];
        var currIdx = spawnNodeIndices[si];
        var prevAi = nodes[prevIdx].phase.agent_index;
        var currAi = nodes[currIdx].phase.agent_index;

        if (prevAi < agentNodes.length && currAi < agentNodes.length) {{
          var prevCx = nodes[prevIdx].x + nodes[prevIdx].w / 2;
          var currCx = nodes[currIdx].x + nodes[currIdx].w / 2;
          var prevHalfW = agentNodes[prevAi].w / 2;
          var currHalfW = agentNodes[currAi].w / 2;
          var neededGap = prevHalfW + currHalfW + 20;
          var actualGap = currCx - prevCx;

          if (actualGap < neededGap) {{
            var shift = neededGap - actualGap;
            // Shift this node and all after it
            for (var sj = currIdx; sj < nodes.length; sj++) {{
              nodes[sj].x += shift;
            }}
            curX += shift;
          }}
        }}
      }}
    }}

    // --- Compute total dimensions ---
    var lastNode = nodes[nodes.length - 1];
    var totalW = lastNode.x + lastNode.w + 40;
    var maxNodeH = Math.max.apply(null, nodes.map(function(n) {{ return n.h; }}));
    var AGENT_Y_POS = MAIN_Y + maxNodeH + AGENT_GAP_Y;
    var maxAgentH = agentNodes.length > 0 ? Math.max.apply(null, agentNodes.map(function(an) {{ return an.h; }})) : 0;
    var FILE_Y_POS = AGENT_Y_POS + maxAgentH + FILE_GAP_Y;
    var maxFiles = 0;
    for (var mfi = 0; mfi < agents.length; mfi++) {{
      var mfc = Math.min((agents[mfi].files || []).length, 6);
      if (mfc > maxFiles) maxFiles = mfc;
    }}
    var hasMoreFiles = agents.some(function(ag) {{ return (ag.files || []).length > 6; }});
    var filesRowH = maxFiles * (FILE_H + FILE_GAP_V) + (hasMoreFiles ? 24 : 0);
    var totalH = agents.length > 0
      ? FILE_Y_POS + filesRowH + 20
      : MAIN_Y + maxNodeH + 40;

    // Swimlane boundaries (Y ranges for each lane)
    var LANE_PAD = 10;
    var lane1Top = MAIN_Y - LANE_PAD;
    var lane1Bot = MAIN_Y + maxNodeH + LANE_PAD;
    var lane2Top = AGENT_Y_POS - LANE_PAD;
    var lane2Bot = AGENT_Y_POS + maxAgentH + LANE_PAD;
    var lane3Top = FILE_Y_POS - LANE_PAD;
    var lane3Bot = FILE_Y_POS + filesRowH + LANE_PAD;

    // --- Create SVG ---
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", String(totalW));
    svg.setAttribute("height", String(totalH));
    svg.setAttribute("viewBox", "0 0 " + totalW + " " + totalH);
    svg.style.display = "block";

    function svgEl(tag, attrs) {{
      var el = document.createElementNS("http://www.w3.org/2000/svg", tag);
      if (attrs) for (var k in attrs) el.setAttribute(k, attrs[k]);
      return el;
    }}

    // Arrow markers
    var defs = svgEl("defs");
    function addMarker(id, color) {{
      var m = svgEl("marker", {{ id: id, markerWidth: "10", markerHeight: "7", refX: "9", refY: "3.5", orient: "auto", fill: color }});
      m.appendChild(svgEl("polygon", {{ points: "0 0, 10 3.5, 0 7" }}));
      defs.appendChild(m);
    }}
    addMarker("arr", ARROW_COLOR);
    addMarker("arr-spawn", SPAWN_COLOR);
    addMarker("arr-ret", RETURN_COLOR);
    svg.appendChild(defs);

    // --- Swimlane backgrounds and labels ---
    var laneLabels = [];  // collect for HTML overlay
    var laneRects = {{}};  // id -> rect element
    var laneCount = 0;
    function drawLane(yTop, yBot, fill, label, labelColor) {{
      var laneId = "lane-" + laneCount++;
      var laneRect = svgEl("rect", {{
        x: "0", y: String(yTop), width: String(totalW), height: String(yBot - yTop),
        fill: fill, rx: "0", id: laneId
      }});
      svg.appendChild(laneRect);
      laneRects[label] = laneRect;
      // Separator line at bottom
      var sepLine = svgEl("line", {{
        x1: "0", y1: String(yBot), x2: String(totalW), y2: String(yBot),
        stroke: "#e5e7eb", "stroke-width": "1"
      }});
      svg.appendChild(sepLine);
      laneRects[label + "_sep"] = sepLine;
      // Collect label info for HTML overlay (no SVG text — it scrolls away)
      laneLabels.push({{ yTop: yTop, yBot: yBot, label: label, color: labelColor || "#6b7280" }});
    }}

    drawLane(lane1Top, lane1Bot, "#f8fafc", "MAIN SESSION", "#475569");
    if (agents.length > 0) {{
      drawLane(lane2Top, lane2Bot, "#fffbeb", "SUBAGENTS", "#92400e");
      drawLane(lane3Top, lane3Bot, "#eff6ff", "FILES", "#1e40af");
    }}

    // Background timeline line
    svg.appendChild(svgEl("line", {{
      x1: String(LANE_LABEL_W), y1: String(MAIN_Y + nodes[0].h / 2),
      x2: String(totalW - 20), y2: String(MAIN_Y + nodes[0].h / 2),
      stroke: "#e5e7eb", "stroke-width": "3"
    }}));

    // --- Render helper ---
    function drawNodeBox(nd, fill, stroke, strokeW, clickFn) {{
      var r = svgEl("rect", {{
        x: String(nd.x), y: String(nd.y), width: String(nd.w), height: String(nd.h),
        fill: fill, stroke: stroke, "stroke-width": String(strokeW || 1.5), rx: "8",
        style: clickFn ? "cursor:pointer" : ""
      }});
      if (clickFn) r.addEventListener("click", clickFn);
      svg.appendChild(r);

      // Render text lines centered
      var textY = nd.y + PAD_Y + nd.lines[0].size;
      for (var tli = 0; tli < nd.lines.length; tli++) {{
        var ln = nd.lines[tli];
        var t = svgEl("text", {{
          x: String(nd.x + nd.w / 2), y: String(textY),
          "text-anchor": "middle", fill: ln.color || "#374151",
          "font-size": String(ln.size), "font-weight": ln.bold ? "700" : "400",
          "font-family": ln.font || SANS
        }});
        t.textContent = ln.text;
        svg.appendChild(t);
        textY += LINE_H;
      }}
    }}

    // --- Draw nodes ---
    var agentSpawnX = {{}};

    for (var di = 0; di < nodes.length; di++) {{
      var nd = nodes[di];
      var midX = nd.x + nd.w / 2;
      var midY = nd.y + nd.h / 2;

      if (nd.type === "work") {{
        nd.lines[0].color = "#374151";
        nd.lines[1].color = "#6b7280";
        nd.lines[2].color = "#9ca3af";
        drawNodeBox(nd, "#fff", "#d1d5db", 1.5, (function(p) {{ return function() {{ filterToPhase(p); }}; }})(nd.phase));
        svg.appendChild(svgEl("circle", {{ cx: String(midX), cy: String(midY), r: "4", fill: "#3b82f6" }}));

      }} else if (nd.type === "agent_spawn") {{
        var aidx = nd.phase.agent_index;
        nd.lines[0].color = "#92400e";
        nd.lines[1].color = "#b45309";
        nd.lines[2].color = "#d97706";
        drawNodeBox(nd, "#fffbeb", "#f59e0b", 2, (function(idx) {{ return function() {{ activateAgentTab(idx); }}; }})(aidx));
        svg.appendChild(svgEl("circle", {{ cx: String(midX), cy: String(midY), r: "5", fill: "#f59e0b" }}));
        agentSpawnX[aidx] = midX;

        // Draw agent box below
        if (aidx < agentNodes.length) {{
          var an = agentNodes[aidx];
          var ax = midX - an.w / 2;
          an.cx = midX;
          an.lines[0].color = "#92400e";
          an.lines[1].color = "#78716c";
          an.lines[2].color = "#9ca3af";
          an.lines[3].color = "#6b7280";

          // Arrow down from spawn to agent
          svg.appendChild(svgEl("line", {{
            x1: String(midX), y1: String(nd.y + nd.h),
            x2: String(midX), y2: String(AGENT_Y_POS),
            stroke: SPAWN_COLOR, "stroke-width": "2", "stroke-dasharray": "4,3", "marker-end": "url(#arr-spawn)"
          }}));

          // Agent box
          var agentBoxNode = {{ x: ax, y: AGENT_Y_POS, w: an.w, h: an.h, lines: an.lines }};
          drawNodeBox(agentBoxNode, "#fff", "#f59e0b", 2, (function(idx) {{ return function() {{ activateAgentTab(idx); }}; }})(aidx));

          // File nodes below agent
          var afiles = an.agent.files || [];
          var fShown = afiles.length;  // render all, hide overflow via toggle
          if (fShown > 0) {{
            svg.appendChild(svgEl("line", {{
              x1: String(midX), y1: String(AGENT_Y_POS + an.h),
              x2: String(midX), y2: String(FILE_Y_POS),
              stroke: "#93c5fd", "stroke-width": "1", "stroke-dasharray": "3,3"
            }}));
          }}
          var opsMap = an.agent.files_ops || {{}};
          var OP_COLORS = {{
            R: {{ bg: "#dbeafe", fg: "#1e40af" }},
            E: {{ bg: "#fef3c7", fg: "#92400e" }},
            W: {{ bg: "#d1fae5", fg: "#065f46" }},
            G: {{ bg: "#ede9fe", fg: "#5b21b6" }},
            B: {{ bg: "#fee2e2", fg: "#991b1b" }},
            S: {{ bg: "#e0f2fe", fg: "#075985" }}
          }};
          var BADGE_W = 16;
          var BADGE_H = 14;
          var BADGE_GAP = 2;
          var ALL_OPS = ["R", "E", "W", "G", "B", "S"];

          // Helper: render a single file node into a parent SVG group
          function renderFileNode(parent, fn, fy) {{
            var fileOps = opsMap[fn] || [];
            var badgesW = fileOps.length * (BADGE_W + BADGE_GAP);
            var fnTextW = measureText(fn, 9, MONO, false);
            var fw = Math.max(badgesW + fnTextW + 20, an.fileW + 16);
            var fx = midX - fw / 2;

            parent.appendChild(svgEl("rect", {{
              x: String(fx), y: String(fy), width: String(fw), height: String(FILE_H),
              fill: "#eff6ff", stroke: "#bfdbfe", "stroke-width": "1", rx: "4"
            }}));

            var badgeX = fx + 4;
            var badgeY = fy + (FILE_H - BADGE_H) / 2;
            for (var bi = 0; bi < fileOps.length; bi++) {{
              var opCode = fileOps[bi];
              var opC = OP_COLORS[opCode] || {{ bg: "#f3f4f6", fg: "#374151" }};
              parent.appendChild(svgEl("rect", {{
                x: String(badgeX), y: String(badgeY),
                width: String(BADGE_W), height: String(BADGE_H),
                fill: opC.bg, stroke: opC.fg, "stroke-width": "0.5", rx: "2"
              }}));
              var bt = svgEl("text", {{
                x: String(badgeX + BADGE_W / 2), y: String(badgeY + BADGE_H - 3),
                "text-anchor": "middle", fill: opC.fg,
                "font-size": "8", "font-weight": "700", "font-family": MONO
              }});
              bt.textContent = opCode;
              parent.appendChild(bt);
              badgeX += BADGE_W + BADGE_GAP;
            }}

            var fnX = fx + 4 + badgesW + 4;
            var ft = svgEl("text", {{
              x: String(fnX), y: String(fy + 16),
              "text-anchor": "start", fill: "#1e40af", "font-size": "9", "font-family": MONO
            }});
            ft.textContent = fn;
            parent.appendChild(ft);
          }}

          // Render first 6 files directly
          var VISIBLE_FILES = 6;
          for (var fi = 0; fi < Math.min(fShown, VISIBLE_FILES); fi++) {{
            renderFileNode(svg, afiles[fi], FILE_Y_POS + fi * (FILE_H + FILE_GAP_V));
          }}

          // Overflow files in a hidden group, toggled by clicking "+N more"
          if (afiles.length > VISIBLE_FILES) {{
            var overflowGroup = svgEl("g", {{ display: "none" }});
            overflowGroup.id = "overflow-files-" + aidx;
            for (var ofi = VISIBLE_FILES; ofi < afiles.length; ofi++) {{
              renderFileNode(overflowGroup, afiles[ofi], FILE_Y_POS + ofi * (FILE_H + FILE_GAP_V));
            }}
            svg.appendChild(overflowGroup);

            // Clickable toggle text
            var collapsedToggleY = FILE_Y_POS + VISIBLE_FILES * (FILE_H + FILE_GAP_V) + 14;
            var expandedToggleY = FILE_Y_POS + afiles.length * (FILE_H + FILE_GAP_V) + 14;
            var moreT = svgEl("text", {{
              x: String(midX), y: String(collapsedToggleY),
              "text-anchor": "middle", fill: "#3b82f6", "font-size": "10",
              "font-weight": "600", style: "cursor:pointer; text-decoration: underline;"
            }});
            moreT.textContent = "+" + (afiles.length - VISIBLE_FILES) + " more files";
            (function(group, toggle, count, svgRef, origH, collY, expY, origLane3Bot) {{
              var expanded = false;
              var expandedH = expY + 20;
              toggle.addEventListener("click", function() {{
                expanded = !expanded;
                group.setAttribute("display", expanded ? "inline" : "none");
                toggle.textContent = expanded
                  ? "show less"
                  : "+" + count + " more files";
                toggle.setAttribute("y", String(expanded ? expY : collY));
                // Resize SVG to fit
                var newH = expanded ? Math.max(origH, expandedH) : origH;
                svgRef.setAttribute("height", String(newH));
                svgRef.setAttribute("viewBox", "0 0 " + svgRef.getAttribute("width") + " " + newH);
                // Resize FILES lane background and separator
                var filesRect = laneRects["FILES"];
                var filesSep = laneRects["FILES_sep"];
                if (filesRect) {{
                  var newBot = expanded ? expY + 10 : origLane3Bot;
                  filesRect.setAttribute("height", String(newBot - lane3Top));
                  if (filesSep) {{
                    filesSep.setAttribute("y1", String(newBot));
                    filesSep.setAttribute("y2", String(newBot));
                  }}
                }}
                // Resize sidebar and FILES label
                var sb = document.querySelector(".lane-sidebar");
                if (sb) {{
                  sb.style.height = String(newH + 32) + "px";
                  var labels = sb.querySelectorAll(".lane-label");
                  // FILES is the last label
                  if (labels.length > 0) {{
                    var filesLabel = labels[labels.length - 1];
                    var newLaneH = expanded ? (expY + 10 - lane3Top) : (origLane3Bot - lane3Top);
                    filesLabel.style.height = String(newLaneH) + "px";
                  }}
                }}
              }});
            }})(overflowGroup, moreT, afiles.length - VISIBLE_FILES, svg, totalH, collapsedToggleY, expandedToggleY, lane3Bot);
            svg.appendChild(moreT);
          }}
        }}

      }} else if (nd.type === "agent_return") {{
        nd.lines[0].color = "#065f46";
        nd.lines[1].color = "#6b7280";
        drawNodeBox(nd, "#ecfdf5", "#10b981", 2);
        svg.appendChild(svgEl("circle", {{ cx: String(midX), cy: String(midY), r: "5", fill: "#10b981" }}));

        // Return arrows from agents
        for (var rk in agentSpawnX) {{
          var spCx = agentSpawnX[rk];
          var rAi = parseInt(rk, 10);
          if (rAi >= agentNodes.length) continue;
          var rAn = agentNodes[rAi];
          var returnTopY = AGENT_Y_POS + rAn.h;
          var curveY = returnTopY + 24;
          var pathD = "M " + spCx + " " + returnTopY +
                      " L " + spCx + " " + (curveY - 12) +
                      " Q " + spCx + " " + curveY + " " + (spCx + 16) + " " + curveY +
                      " L " + (midX - 16) + " " + curveY +
                      " Q " + midX + " " + curveY + " " + midX + " " + (curveY - 12) +
                      " L " + midX + " " + (nd.y + nd.h);
          svg.appendChild(svgEl("path", {{
            d: pathD, fill: "none", stroke: RETURN_COLOR,
            "stroke-width": "1.5", "stroke-dasharray": "5,3", "marker-end": "url(#arr-ret)"
          }}));
        }}
      }}

      // Connector arrow to next node
      if (di < nodes.length - 1) {{
        var nextNd = nodes[di + 1];
        svg.appendChild(svgEl("line", {{
          x1: String(nd.x + nd.w), y1: String(MAIN_Y + nd.h / 2),
          x2: String(nextNd.x), y2: String(MAIN_Y + nextNd.h / 2),
          stroke: ARROW_COLOR, "stroke-width": "1.5", "marker-end": "url(#arr)"
        }}));
      }}
    }}

    canvas.appendChild(svg);

    // Fixed sidebar column that tracks horizontal scroll
    var wrapper = document.getElementById("flow-wrapper");
    canvas.style.position = "relative";

    // Create a single sidebar div that spans the full diagram height
    var sidebar = createEl("div", {{ className: "lane-sidebar" }});
    sidebar.style.position = "absolute";
    sidebar.style.top = "-16px";
    sidebar.style.left = "-16px";
    sidebar.style.width = String(LANE_LABEL_W + 16) + "px";
    sidebar.style.height = String(totalH + 32) + "px";
    sidebar.style.zIndex = "10";
    sidebar.style.pointerEvents = "none";
    sidebar.style.borderRight = "2px solid #d1d5db";

    for (var lli = 0; lli < laneLabels.length; lli++) {{
      var ll = laneLabels[lli];
      var lDiv = createEl("div", {{ className: "lane-label", textContent: ll.label }});
      lDiv.style.position = "absolute";
      lDiv.style.top = String(ll.yTop + 16) + "px";
      lDiv.style.left = "0";
      lDiv.style.width = "100%";
      lDiv.style.height = String(ll.yBot - ll.yTop) + "px";
      lDiv.style.display = "flex";
      lDiv.style.alignItems = "center";
      lDiv.style.justifyContent = "center";
      lDiv.style.color = ll.color;
      lDiv.style.fontWeight = "700";
      lDiv.style.fontSize = "11px";
      lDiv.style.fontFamily = "system-ui, sans-serif";
      lDiv.style.letterSpacing = "0.05em";
      lDiv.style.background = ll.color === "#475569" ? "#f8fafc" :
                               ll.color === "#92400e" ? "#fffbeb" : "#eff6ff";
      sidebar.appendChild(lDiv);
    }}

    canvas.appendChild(sidebar);

    // Track horizontal scroll to keep sidebar pinned flush with wrapper edge
    var wrapperPad = 16; // 1rem padding on flow-wrapper
    sidebar.style.left = String(-wrapperPad) + "px";
    wrapper.addEventListener("scroll", function() {{
      sidebar.style.left = String(wrapper.scrollLeft - wrapperPad) + "px";
    }});
  }}

  // --- Flow filter banner management ---
  var activeFlowFilter = null;

  function showFlowBanner(text) {{
    var banner = document.getElementById("flow-filter-banner");
    document.getElementById("flow-filter-text").textContent = text;
    banner.classList.add("active");
    activeFlowFilter = text;
  }}

  function clearFlowFilter() {{
    var banner = document.getElementById("flow-filter-banner");
    banner.classList.remove("active");
    activeFlowFilter = null;
    document.getElementById("search-input").value = "";
    // Reset all filters
    document.getElementById("type-filter").value = "all";
    document.getElementById("content-filter").value = "all";
    applyFilters();
  }}

  document.getElementById("flow-filter-clear").addEventListener("click", clearFlowFilter);

  // Click: filter conversation to phase message range
  function filterToPhase(phase) {{
    // Switch to parent tab
    var tabs = document.querySelectorAll(".agent-tab");
    for (var i = 0; i < tabs.length; i++) {{
      if (tabs[i].getAttribute("data-target") === "parent") {{ tabs[i].click(); break; }}
    }}
    document.getElementById("search-input").value = "";

    var toolLine = Object.keys(phase.tools || {{}}).map(function(t) {{
      return t + "(" + phase.tools[t] + ")";
    }}).join(", ");
    showFlowBanner("Flow filter: Messages #" + (phase.msg_start || 0) + " - #" + (phase.msg_end || "?") + "  |  " + toolLine);

    setTimeout(function() {{
      var panel = document.getElementById("panel-parent");
      if (!panel) return;
      var msgs = panel.querySelectorAll(".message");
      var start = phase.msg_start || 0;
      var end = phase.msg_end || msgs.length;
      var count = 0;
      var firstVisible = null;
      for (var j = 0; j < msgs.length; j++) {{
        var idx = parseInt(msgs[j].getAttribute("data-index"), 10);
        if (idx >= start && idx <= end) {{
          msgs[j].classList.remove("hidden");
          msgs[j].classList.add("highlight");
          msgs[j].querySelector(".msg-body").classList.add("expanded");
          var icon = msgs[j].querySelector(".msg-header span:last-child");
          if (icon) icon.textContent = "-";
          count++;
          if (!firstVisible) firstVisible = msgs[j];
        }} else {{
          msgs[j].classList.add("hidden");
          msgs[j].classList.remove("highlight");
        }}
      }}
      document.getElementById("match-count").textContent = count + " messages in phase";
      // Scroll to first matching message, not just the section
      if (firstVisible) {{
        firstVisible.scrollIntoView({{ behavior: "smooth", block: "start" }});
      }} else {{
        document.getElementById("conversation").scrollIntoView({{ behavior: "smooth" }});
      }}
    }}, 100);
  }}

  // Click: activate agent conversation tab and show all its messages
  function activateAgentTab(agentIndex) {{
    var tabs = document.querySelectorAll(".agent-tab");
    if (agentIndex + 1 < tabs.length) {{
      var agentTab = tabs[agentIndex + 1];
      var agentLabel = agentTab.textContent || "Agent " + agentIndex;

      // Get agent description from flow data
      var desc = "";
      if (FLOW.agents && FLOW.agents[agentIndex]) {{
        desc = FLOW.agents[agentIndex].description || "";
        if (desc.length > 80) desc = desc.substring(0, 80) + "...";
      }}
      showFlowBanner("Subagent: " + agentLabel + (desc ? "  —  " + desc : ""));

      agentTab.click();

      // Reset search/filters, expand all messages, scroll to first
      document.getElementById("search-input").value = "";
      document.getElementById("type-filter").value = "all";
      document.getElementById("content-filter").value = "all";

      setTimeout(function() {{
        var panelId = agentTab.getAttribute("data-target");
        var panel = document.getElementById("panel-" + panelId);
        if (!panel) return;
        var msgs = panel.querySelectorAll(".message");
        for (var j = 0; j < msgs.length; j++) {{
          msgs[j].classList.remove("hidden");
          msgs[j].classList.add("highlight");
          // Auto-expand first 5 messages
          if (j < 5) {{
            msgs[j].querySelector(".msg-body").classList.add("expanded");
            var icon = msgs[j].querySelector(".msg-header span:last-child");
            if (icon) icon.textContent = "-";
          }}
        }}
        document.getElementById("match-count").textContent = msgs.length + " agent messages";
        if (msgs.length > 0) {{
          msgs[0].scrollIntoView({{ behavior: "smooth", block: "start" }});
        }}
      }}, 150);
    }}
  }}

  buildFlowDiagram();
  buildPanels();
  applyFilters();
}})();
</script>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"[session_analyzer] Report written to {output_path}", file=sys.stderr)
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill Tester - Session Analyzer")
    parser.add_argument("--project-dir", help="Claude project directory (auto-detected if omitted)")
    parser.add_argument("--session-id", help="Session UUID (latest if omitted)")
    parser.add_argument("--output", "-o", default="session_report.html", help="Output file path")
    parser.add_argument("--format", choices=["html", "json", "both"], default="html",
                        help="Output format")
    args = parser.parse_args()

    project_dir = args.project_dir
    if not project_dir:
        found = _find_project_dir()
        if found:
            project_dir = str(found)
        else:
            print("Could not auto-detect project directory. Use --project-dir.", file=sys.stderr)
            sys.exit(1)

    data = analyze_session(project_dir, args.session_id)

    if args.format in ("json", "both"):
        json_path = args.output.replace(".html", ".json") if args.output.endswith(".html") else args.output + ".json"
        summary = {
            "session": data["session"],
            "analyzed_at": data["analyzed_at"],
            "parent_stats": data["parent"]["stats"],
            "agents": [{"agent_id": a["agent_id"], "agent_type": a["agent_type"], "stats": a["stats"]} for a in data["agents"]],
            "totals": data["totals"],
        }
        Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        Path(json_path).write_text(json.dumps(summary, indent=2))
        print(f"[session_analyzer] JSON summary written to {json_path}", file=sys.stderr)
        print(json_path)

    if args.format in ("html", "both"):
        html_path = generate_html_report(data, args.output)
        print(html_path)


if __name__ == "__main__":
    main()
