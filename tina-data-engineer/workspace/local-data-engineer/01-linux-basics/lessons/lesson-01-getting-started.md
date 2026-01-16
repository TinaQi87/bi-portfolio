# Lesson 1: Getting Started with Terminal

## What is the Terminal?

The terminal (also called command line or shell) is a text-based interface to your computer. Instead of clicking icons, you type commands.

**Why data engineers use it:**
- Servers don't have graphical interfaces
- Commands can be automated in scripts
- Much faster than clicking once you learn it
- You can work on remote machines via SSH

---

## Your First Terminal Session

### Access Your Terminal

```bash
# From your Mac terminal, access the Docker container
docker exec -it tina-devtools bash
```

You'll see a prompt like this:
```
root@abc123:/workspace#
```

This is your command prompt. It's waiting for you to type a command.

---

## Understanding the Prompt

```
root@abc123:/workspace#
│    │       │         │
│    │       │         └─ Prompt symbol (# means root user)
│    │       └─────────── Current directory
│    └─────────────────── Container/hostname
└──────────────────────── Username
```

**What this tells you:**
- You're logged in as `root` (administrator)
- You're in the `/workspace` directory
- You're ready to type commands

---

## Your First Commands

### 1. Print Working Directory (pwd)

```bash
pwd
```

**Output:**
```
/workspace
```

**What it does:** Shows where you are in the file system.

**Real-world use:** "Where am I? Did I navigate to the right folder?"

---

### 2. List Files (ls)

```bash
ls
```

**Output:**
```
local-data-engineer  sample_data.csv  test_processing.py
```

**What it does:** Shows files and folders in current directory.

**Try these variations:**
```bash
ls -l          # Long format (shows details)
ls -la         # Long format + hidden files
ls -lh         # Long format + human-readable sizes
```

**Example output of `ls -lh`:**
```
-rw-r--r-- 1 root root 250 Jan 14 09:30 sample_data.csv
drwxr-xr-x 2 root root 480 Jan 16 06:11 local-data-engineer
```

---

### 3. Echo (Print Text)

```bash
echo "Hello, Data Engineering!"
```

**Output:**
```
Hello, Data Engineering!
```

**What it does:** Prints text to the screen.

**Real-world use:** Testing, debugging scripts, creating simple files.

---

### 4. Clear Screen

```bash
clear
```

**What it does:** Clears the terminal screen (makes it easier to read).

**Shortcut:** Press `Ctrl + L`

---

### 5. Get Help

```bash
ls --help
```

**What it does:** Shows how to use a command.

**Try it:**
```bash
pwd --help
echo --help
```

**Another way to get help:**
```bash
man ls    # Manual page for ls (press 'q' to quit)
```

---

## Command Structure

Most commands follow this pattern:

```
command [options] [arguments]
```

**Examples:**
```bash
ls                    # Command only
ls -l                 # Command + option
ls -l /workspace      # Command + option + argument
ls -lh /workspace     # Command + multiple options + argument
```

---

## Practice Exercise 1: Basic Commands

Type each command and observe the output:

```bash
# 1. Where am I?
pwd

# 2. What's in this directory?
ls

# 3. Show details
ls -l

# 4. Show hidden files too
ls -la

# 5. Print a message
echo "I am learning Linux!"

# 6. Clear the screen
clear

# 7. Check the date
date

# 8. See who is logged in
whoami
```

---

## Useful Keyboard Shortcuts

| Shortcut | What it does |
|----------|--------------|
| `Ctrl + C` | Cancel current command |
| `Ctrl + L` | Clear screen |
| `Ctrl + D` | Exit terminal |
| `↑` (Up arrow) | Previous command |
| `↓` (Down arrow) | Next command |
| `Tab` | Auto-complete |

**Try this:**
```bash
# Type 'ec' then press Tab
ec[Tab]
# It completes to 'echo'
```

---

## Command History

The terminal remembers your commands:

```bash
# Press Up arrow to see previous commands
# Press Down arrow to go forward

# See all your command history
history

# Run a previous command by number
!5    # Runs command #5 from history
```

---

## Practice Exercise 2: Using History

```bash
# 1. Run several commands
pwd
ls
date
whoami

# 2. View your history
history

# 3. Press Up arrow to see previous commands
# 4. Press Up multiple times to go back further
# 5. Press Down to go forward
# 6. Press Enter to run a command again
```

---

## Common Mistakes & How to Fix Them

### Mistake 1: Typo in Command
```bash
pwdd
# Output: bash: pwdd: command not found
```
**Fix:** Check spelling, use Tab to auto-complete

### Mistake 2: Command Stuck/Frozen
**Fix:** Press `Ctrl + C` to cancel

### Mistake 3: Too Much Output
```bash
# If output is scrolling too fast
ls -la | less    # Use 'less' to scroll (press 'q' to quit)
```

---

## Real Data Engineer Scenario

**Situation:** You SSH into a production server to check a failed pipeline.

**What you do:**
```bash
# 1. Where am I?
pwd

# 2. What files are here?
ls -lh

# 3. Check the log file
ls -lh pipeline.log

# 4. When was it last updated?
ls -lh pipeline.log
# Output: -rw-r--r-- 1 root root 2.3M Jan 16 03:45 pipeline.log

# 5. The file was updated at 3:45 AM - that's when it failed!
```

---

## Key Takeaways

✅ The terminal is a text interface to your computer
✅ `pwd` shows where you are
✅ `ls` shows what's in a directory
✅ `echo` prints text
✅ Use `--help` to learn about commands
✅ Up/Down arrows navigate command history
✅ `Ctrl + C` cancels commands
✅ Tab completes commands and filenames

---

## Practice Challenge

Complete these tasks without looking at the notes:

1. Check your current directory
2. List all files with details
3. Print "Data Engineering is awesome!"
4. View your command history
5. Clear the screen
6. Check today's date
7. Find out your username

---

## Next Lesson

In Lesson 2, you'll learn to navigate the file system - moving between directories like a pro!

---

## Quick Reference

```bash
pwd              # Where am I?
ls               # What's here?
ls -lh           # Show details
echo "text"      # Print text
clear            # Clear screen
date             # Show date/time
whoami           # Show username
history          # Show command history
command --help   # Get help
```

**Remember:** Type commands yourself. Don't copy-paste. Muscle memory matters!
