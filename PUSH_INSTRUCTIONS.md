# How to Upload Changes to GitHub

## Step-by-Step Instructions

### Step 1: Check Your Changes
```bash
cd "/Users/amirkhabaza/Downloads/Quick/CSE 108/lab-8-course-registration-project-fall-2025-main"
git status
```

### Step 2: Add All Changes
```bash
git add .
```
This stages all modified and new files for commit.

### Step 3: Commit Your Changes
```bash
git commit -m "feat: Add security, validation, and UI enhancements

- Implemented password hashing for all user types
- Added course capacity checking
- Added schedule conflict detection
- Added drop course functionality
- Enhanced days and dates display
- Fixed password hash recognition (scrypt format)
- Updated database schema with start_date and end_date"
```

### Step 4: Pull Latest Changes (if needed)
```bash
git pull origin main
```
This ensures you have the latest changes from the repository. If there are conflicts, resolve them first.

### Step 5: Push to GitHub
```bash
git push origin main
```

**When prompted:**
- **Username**: Your GitHub username
- **Password**: Use your **Personal Access Token** (not your GitHub password)

---

## If You Get Permission Errors

### Create a Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: "Course Registration Project"
4. Select scope: `repo` (full control)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)
7. Use this token as your password when pushing

---

## Quick Command Sequence

Copy and paste these commands one by one:

```bash
# Navigate to project
cd "/Users/amirkhabaza/Downloads/Quick/CSE 108/lab-8-course-registration-project-fall-2025-main"

# Check status
git status

# Add all changes
git add .

# Commit with message
git commit -m "feat: Add security, validation, and UI enhancements

- Password hashing for all user types
- Course capacity checking
- Schedule conflict detection
- Drop course functionality
- Enhanced days and dates display
- Fixed password hash recognition"

# Pull latest (if needed)
git pull origin main

# Push to GitHub
git push origin main
```

---

## Verify Your Push

After pushing, check the repository:
https://github.com/eduardocastellon/lab-8-course-registration-project-fall-2025

You should see your new commit in the commit history.

---

## Troubleshooting

### If you get "non-fast-forward" error:
```bash
git pull origin main --rebase
git push origin main
```

### If you get authentication errors:
- Make sure you're using a Personal Access Token, not your password
- Clear cached credentials: `git credential-osxkeychain erase` (then enter host=github.com)

### If you have merge conflicts:
1. Resolve conflicts in the files
2. `git add .` (to mark conflicts as resolved)
3. `git commit` (to complete the merge)
4. `git push origin main`

