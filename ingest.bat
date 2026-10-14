@echo off
rem Compile pending raw/ files into wiki/ with Claude Code (/ingest skill in .claude/skills)
cd /d "%~dp0"
where claude >nul 2>nul || (echo Claude Code CLI not found - https://claude.com/claude-code & pause & exit /b 1)
claude "/ingest"
