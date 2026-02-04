"""Claude Skills installer for PyFlightProfiler."""

import shutil
from pathlib import Path


def get_skills_source_dir() -> Path:
    """Get the skills directory from the installed package."""
    return Path(__file__).parent / "skills"


def get_skills_target_dir() -> Path:
    """Get the Claude commands directory."""
    return Path.home() / ".claude" / "commands"


def install_skills():
    """Install Claude skills to ~/.claude/commands/"""
    source_dir = get_skills_source_dir()
    target_dir = get_skills_target_dir()
    
    if not source_dir.exists():
        print(f"Error: Skills directory not found: {source_dir}")
        return False
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    installed = []
    for skill_file in source_dir.glob("*.md"):
        shutil.copy2(skill_file, target_dir / skill_file.name)
        installed.append(skill_file.name)
    
    if installed:
        print(f"Installed {len(installed)} skill(s) to {target_dir}")
        for name in installed:
            print(f"  /{name.replace('.md', '')}")
        return True
    else:
        print("No skills found.")
        return False


def uninstall_skills():
    """Remove Claude skills from ~/.claude/commands/"""
    source_dir = get_skills_source_dir()
    target_dir = get_skills_target_dir()
    
    if not source_dir.exists():
        return
    
    removed = []
    for skill_file in source_dir.glob("*.md"):
        dest = target_dir / skill_file.name
        if dest.exists():
            dest.unlink()
            removed.append(skill_file.name)
    
    print(f"Removed {len(removed)} skill(s)" if removed else "No skills to remove.")
