# Troubleshooting Guide

Common issues and solutions when using Stack-Driven.

---

## Table of Contents

1. [Installation & Setup Issues](#installation--setup-issues)
2. [Cascade Execution Issues](#cascade-execution-issues)
3. [File and Output Issues](#file-and-output-issues)
4. [Command-Specific Issues](#command-specific-issues)
5. [GitHub Integration Issues](#github-integration-issues)
6. [Regeneration and Updates](#regeneration-and-updates)
7. [Performance and Token Issues](#performance-and-token-issues)
8. [Getting Help](#getting-help)

---

## Installation & Setup Issues

### Issue: Commands not recognized

**Symptom:** When you type `/refine-journey`, nothing happens or you get "command not found"

**Causes:**
- Not in a directory with `.claude/commands/` folder
- Using wrong AI assistant
- Commands folder not properly set up

**Solutions:**

1. **Verify you're in the Stack-Driven directory:**
   ```bash
   pwd
   # Should show: .../stack-driven

   ls .claude/commands/
   # Should list command files
   ```

2. **Ensure you're using Claude Code or compatible AI assistant:**
   - Stack-Driven uses Claude Code slash commands
   - Other AI assistants may not support this format
   - Check your assistant's documentation

3. **Verify command files exist:**
   ```bash
   ls -la .claude/commands/ | grep refine-journey
   ```

   If missing, you may have an incomplete installation.

---

### Issue: `product-guidelines/` directory doesn't exist

**Symptom:** Commands say they can't write to `product-guidelines/`

**Solution:**

Create the directory manually:

```bash
mkdir -p product-guidelines
```

The directory is gitignored by default (each user generates their own cascade).

---

## Cascade Execution Issues

### Issue: "Cannot find input file from previous session"

**Symptom:**
```
Error: Cannot read product-guidelines/00-user-journey.md
Please complete Session 1 first
```

**Causes:**
- Skipped a required session
- File was deleted or moved
- Wrong directory

**Solutions:**

1. **Check cascade status:**
   ```bash
   /cascade-status
   ```

   This will show which sessions are complete and which are missing.

2. **Run the missing session:**
   ```bash
   # If journey is missing:
   /refine-journey
   ```

3. **Verify file exists:**
   ```bash
   ls -la product-guidelines/
   ```

4. **If file was deleted, re-run that session:**
   ```bash
   # Re-run the missing session
   /refine-journey  # or whichever session is missing
   ```

---

### Issue: Session generates incomplete output

**Symptom:** Output file exists but is missing sections or appears truncated

**Causes:**
- AI response was interrupted
- Token limit reached
- Network issue during generation

**Solutions:**

1. **Re-run the session:**
   ```bash
   # Simply run the same command again
   /generate-strategy
   ```

   The cascade will regenerate the file.

2. **Check file manually:**
   ```bash
   cat product-guidelines/03-mission.md
   ```

   If incomplete, delete and re-run:
   ```bash
   rm product-guidelines/03-mission.md
   /generate-strategy
   ```

3. **For very long outputs, check if essentials file was created:**
   ```bash
   # Some sessions create both full and essentials versions
   ls product-guidelines/*essentials.md
   ```

---

### Issue: "Cascading updates not working"

**Symptom:** Updated Session 1 (journey) but Session 3 (tech stack) still uses old journey

**Cause:** Sessions don't auto-regenerate - you must manually re-run downstream sessions

**Solution:**

After updating any session, re-run all downstream sessions:

```bash
# Updated journey
/refine-journey

# Now re-run everything after it:
/create-product-strategy
/choose-tech-stack
/generate-strategy
# ... etc
```

Or use automated cascade:
```bash
/run-cascade  # Will regenerate from current point
```

---

### Issue: "Don't know which session to run next"

**Symptom:** Completed a session but unsure what comes next

**Solution:**

Always run `/cascade-status` to see your progress:

```bash
/cascade-status
```

This shows:
- ✅ Completed sessions
- ⏹️ Not started sessions
- ➡️ Recommended next step

Each session also tells you the next command in its output.

---

## File and Output Issues

### Issue: Can't find output files

**Symptom:** Session says it completed but you don't see the file

**Solutions:**

1. **Check the correct directory:**
   ```bash
   ls -la product-guidelines/
   ```

   All outputs go to `product-guidelines/`, not the root directory.

2. **Check for hidden files:**
   ```bash
   ls -laR product-guidelines/
   ```

3. **Verify the file was created with correct name:**
   ```bash
   # Session 1 creates:
   ls product-guidelines/00-user-journey.md

   # Session 4 creates multiple files:
   ls product-guidelines/03-mission.md
   ls product-guidelines/04-*.md
   ```

4. **If file is genuinely missing, re-run the session.**

---

### Issue: Output file has incorrect format

**Symptom:** File exists but sections are missing or format is wrong

**Causes:**
- Template was updated and you have old version
- Generation was interrupted
- Custom modifications broke structure

**Solutions:**

1. **Delete and regenerate:**
   ```bash
   rm product-guidelines/06-design-system.md
   /create-design
   ```

2. **Compare with template:**
   ```bash
   cat templates/06-design-system-template.md
   ```

   Your output should match this structure.

3. **Check examples:**
   ```bash
   cat examples/compliance-saas/design/06-design-system.md
   ```

---

### Issue: Files have wrong numbering

**Symptom:** Expected `07-database-schema.md` but got different number

**Cause:** Template numbering was updated in v2.0

**Solution:**

Check `templates/README.md` for current numbering system:

```bash
cat templates/README.md
```

The framework uses consistent numbering:
- Core sessions: 00-14
- Post-cascade: 15-22

If you have old files with different numbers, you can:
1. Use them as-is (AI reads content, not numbers)
2. Rename to match new numbering
3. Regenerate with latest cascade

---

## Command-Specific Issues

### Issue: `/choose-tech-stack` recommends tech I don't know

**Symptom:** AI recommends Python but your team only knows JavaScript

**Solution:**

Provide constraints when running the command:

```bash
/choose-tech-stack

# When asked, specify:
"Our team only knows JavaScript/TypeScript.
Please recommend a JavaScript-based stack."
```

You can also manually edit the output:
```bash
# Edit the tech stack file
vim product-guidelines/02-tech-stack.md

# Update to your preferred stack
# Then continue cascade - future sessions will use your choices
```

---

### Issue: `/generate-backlog` creates too many stories

**Symptom:** Generated 50 stories but you only want to focus on 10

**Solution:**

1. **Focus on P0 stories only:**
   ```bash
   ls product-guidelines/10-backlog/P0-*.md
   ```

   These are critical for MVP. P1 and P2 can wait.

2. **Delete low-priority stories you won't build:**
   ```bash
   rm product-guidelines/10-backlog/P2-*.md
   ```

3. **Re-run with explicit constraint:**
   ```bash
   /generate-backlog

   # Specify: "Generate only 15 stories, focusing on MVP"
   ```

---

### Issue: `/create-gh-issues` fails

**Symptom:**
```
Error: gh: command not found
```
or
```
Error: Not authenticated with GitHub
```

**Solutions:**

1. **Install GitHub CLI:**
   ```bash
   # macOS
   brew install gh

   # Linux
   sudo apt install gh

   # Windows
   winget install GitHub.cli
   ```

2. **Authenticate:**
   ```bash
   gh auth login
   ```

   Follow prompts to authenticate.

3. **Verify authentication:**
   ```bash
   gh auth status
   ```

4. **Check you're in a git repository:**
   ```bash
   git status
   ```

   If not, initialize:
   ```bash
   git init
   gh repo create
   ```

5. **If authentication fails, manually create issues:**
   - Go to your GitHub repository
   - Create issues manually from `product-guidelines/10-backlog/*.md` files

---

### Issue: `/scaffold-project` generates wrong framework files

**Symptom:** Generated Next.js files but you chose FastAPI

**Cause:** Scaffold reads `02-tech-stack.md` - check if tech stack is correct

**Solutions:**

1. **Verify tech stack file:**
   ```bash
   cat product-guidelines/02-tech-stack.md
   ```

   Ensure it lists your chosen technologies.

2. **If tech stack is wrong, update it:**
   ```bash
   /choose-tech-stack  # Re-run with correct choices
   ```

3. **Regenerate scaffold:**
   ```bash
   rm -rf product-guidelines/12-project-scaffold/
   /scaffold-project
   ```

---

## GitHub Integration Issues

### Issue: Push fails with permission error

**Symptom:**
```
Error: Permission denied (publickey)
```

**Solution:**

Set up SSH keys for GitHub:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

Add the public key to GitHub:
1. Go to GitHub Settings > SSH and GPG keys
2. Click "New SSH key"
3. Paste your public key

Or use HTTPS instead:
```bash
git remote set-url origin https://github.com/username/repo.git
```

---

### Issue: Issues created multiple times

**Symptom:** Ran `/create-gh-issues` twice and now have duplicate issues

**Solution:**

1. **Delete duplicate issues manually in GitHub UI**

2. **Or use GitHub CLI:**
   ```bash
   # List all issues
   gh issue list

   # Delete specific issue
   gh issue delete ISSUE_NUMBER
   ```

3. **Prevent duplicates:**
   - Check existing issues before running command
   - Use `/cascade-status` to track what's been done

---

## Regeneration and Updates

### Issue: "How do I update just one section?"

**Symptom:** Want to change monetization strategy but keep rest of Session 4

**Solutions:**

**Option 1: Edit file directly**
```bash
vim product-guidelines/04-monetization.md
```

**Option 2: Regenerate just that session**
```bash
# Regenerate all Session 4 files
/generate-strategy

# Specify: "Keep mission, metrics, architecture the same.
#          Only update monetization to [new strategy]"
```

**Option 3: Split into separate sessions**
- Session 4 generates 4 files
- Edit the specific file you want to change
- Downstream sessions will read the updated version

---

### Issue: "Journey evolved, how do I update everything?"

**Symptom:** User research changed your understanding of the journey

**Solution:**

Cascade update (manual):

```bash
# 1. Update journey
/refine-journey

# 2. Regenerate everything downstream
/create-product-strategy
/choose-tech-stack
/generate-strategy
/create-brand-strategy
/create-design
/design-database-schema
/generate-api-contracts
/create-test-strategy
/generate-backlog
```

Or automated:
```bash
# Update journey
/refine-journey

# Auto-regenerate rest
/run-cascade
```

**Warning:** This regenerates ALL files. Back up any manual edits first:
```bash
cp -r product-guidelines product-guidelines.backup
```

---

### Issue: "Can I keep some outputs and regenerate others?"

**Symptom:** Happy with tech stack but want to regenerate design system

**Solution:**

Yes - just re-run specific sessions:

```bash
# Keep: journey, product strategy, tech stack, strategy, brand
# Regenerate: design system only

/create-design
```

AI will read the existing previous session files and regenerate just the design system.

If downstream sessions depend on design (like backlog), re-run those too:
```bash
/create-design
/generate-backlog  # Update backlog with new design components
```

---

## Performance and Token Issues

### Issue: "Session is very slow"

**Symptom:** Session takes 10+ minutes or appears stuck

**Causes:**
- Large context (many previous sessions to read)
- Complex requirements
- AI service slowdown

**Solutions:**

1. **Use essentials templates:**
   - Sessions 2, 7, 8, 9 create "essentials" versions
   - These are optimized for AI reading
   - Automatically used by downstream sessions

2. **Wait it out:**
   - Complex sessions (generate-backlog, scaffold-project) can take time
   - This is normal for generating 50 user stories or complete scaffolds

3. **Check AI service status:**
   - If consistently slow, check if AI service is experiencing issues

---

### Issue: "Token limit exceeded"

**Symptom:**
```
Error: Maximum token limit exceeded
```

**Causes:**
- Too many previous sessions to read
- Very large output being generated

**Solutions:**

1. **Use essentials templates (automatic):**
   - Framework already uses essentials for long documents
   - Session 2 creates `11-product-strategy-essentials.md`
   - Downstream sessions read essentials instead of full version

2. **Reduce backlog size:**
   ```bash
   /generate-backlog

   # Specify: "Generate 20 stories instead of 50"
   ```

3. **Split large sessions:**
   - Generate backlog in phases (P0, then P1, then P2)

---

## Getting Help

### Still stuck?

1. **Check documentation:**
   - `README.md` - Framework overview
   - `GETTING-STARTED.md` - Quick start guide
   - `COMMAND-REFERENCE.md` - All commands
   - `FAQ.md` - Common questions
   - `PHILOSOPHY.md` - Framework principles

2. **Check cascade status:**
   ```bash
   /cascade-status
   ```

3. **Review your files:**
   ```bash
   ls -la product-guidelines/
   cat product-guidelines/00-user-journey.md
   ```

4. **Open an issue:**
   - Go to GitHub repository
   - Click "Issues" > "New Issue"
   - Describe your problem with:
     - What command you ran
     - What you expected
     - What actually happened
     - Relevant output files or errors

5. **Check examples:**
   ```bash
   ls examples/compliance-saas/
   ```

   Compare your outputs with the example implementation.

---

## Common Error Messages

### "File not found: product-guidelines/XX-*.md"

**Meaning:** Previous session hasn't been completed

**Fix:** Run the missing session first (check `/cascade-status`)

---

### "Invalid format in XX-*.md"

**Meaning:** File exists but doesn't match expected template

**Fix:** Delete and regenerate:
```bash
rm product-guidelines/XX-*.md
/[command-that-generates-it]
```

---

### "GitHub authentication required"

**Meaning:** Not logged into GitHub CLI

**Fix:**
```bash
gh auth login
```

---

### "Template not found"

**Meaning:** Framework files may be corrupt or incomplete

**Fix:**
```bash
# Verify templates exist
ls templates/

# If missing, reinstall or clone repository again
```

---

### "Cascade loop detected"

**Meaning:** Somehow session is trying to read a file it generates (should never happen)

**Fix:** Report this as a bug - include:
- Which command you ran
- Contents of `product-guidelines/` directory

---

## Recovery Procedures

### "I want to start over completely"

```bash
# Backup existing work
mv product-guidelines product-guidelines.backup

# Create fresh directory
mkdir product-guidelines

# Start from Session 1
/refine-journey
```

---

### "I want to reset just one session"

```bash
# Delete that session's outputs
rm product-guidelines/06-design-system.md

# Regenerate
/create-design
```

---

### "Files are corrupted or unreadable"

```bash
# Restore from backup (if you made one)
cp -r product-guidelines.backup product-guidelines

# Or regenerate from scratch
rm -rf product-guidelines/
mkdir product-guidelines
/cascade-status  # See what to rebuild
```

---

## Debugging Tips

### Enable verbose output

When reporting issues, gather detailed information:

```bash
# List all generated files
find product-guidelines -type f -name "*.md" | sort

# Check file sizes (detect truncated files)
du -h product-guidelines/*.md

# View cascade status
/cascade-status
```

---

### Verify cascade integrity

```bash
# Check all core session files exist
ls product-guidelines/00-user-journey.md
ls product-guidelines/01-product-strategy.md
ls product-guidelines/02-tech-stack.md
ls product-guidelines/03-mission.md
ls product-guidelines/04-*.md
ls product-guidelines/05-brand-strategy.md
ls product-guidelines/06-design-system.md
# ... etc
```

---

### Check for partial outputs

```bash
# Count lines in output files
wc -l product-guidelines/*.md

# Very small files (<50 lines) might be incomplete
```

---

## Preventive Measures

### Before starting cascade

1. **Ensure stable environment:**
   - Good internet connection
   - Sufficient disk space
   - Up-to-date AI assistant

2. **Create backup directory:**
   ```bash
   # Store manual notes separately
   mkdir notes/
   ```

3. **Use version control:**
   ```bash
   git init
   git add product-guidelines/
   git commit -m "Session X complete"
   ```

---

### During cascade

1. **Save progress frequently:**
   - Each session creates files
   - Consider git commits after each session

2. **Review outputs:**
   - Don't blindly run next session
   - Verify output quality
   - Edit if needed

3. **Track status:**
   - Run `/cascade-status` regularly
   - Know where you are in cascade

---

### After cascade

1. **Backup everything:**
   ```bash
   tar -czf stack-driven-backup.tar.gz product-guidelines/
   ```

2. **Version control:**
   ```bash
   git add product-guidelines/
   git commit -m "Complete cascade"
   ```

3. **Export critical docs:**
   - Copy files you'll reference frequently
   - Print or PDF mission, metrics, architecture

---

## Known Limitations

1. **No automatic regeneration:**
   - Updating Session 1 doesn't auto-update Session 3
   - You must manually re-run downstream sessions

2. **No undo:**
   - Once file is regenerated, previous version is gone
   - Solution: Use version control (git)

3. **GitHub CLI required for `/create-gh-issues`:**
   - Can't push to GitHub without `gh` command
   - Alternative: Manually create issues from backlog files

4. **Large context can be slow:**
   - Sessions 10+ read many previous files
   - This is intentional (quality over speed)
   - Essentials templates help but don't eliminate slowness

---

## Quick Diagnostics Checklist

When something goes wrong:

- [ ] Am I in the `stack-driven` directory?
- [ ] Does `.claude/commands/` exist?
- [ ] Does `product-guidelines/` exist?
- [ ] Did I run previous sessions?
- [ ] Did previous session complete successfully?
- [ ] Did I check `/cascade-status`?
- [ ] Are files actually missing or just in unexpected location?
- [ ] Did I customize something that broke the cascade?
- [ ] Is this a known limitation (see above)?
- [ ] Have I checked the error message carefully?

---

**Last Updated:** 2025-11-14
**Version:** 2.0.0

For additional help, see:
- **FAQ.md** - Common questions
- **COMMAND-REFERENCE.md** - Command details
- **README.md** - Framework overview
