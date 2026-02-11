# Slovenian Translation Guide

This guide might help you complete the Slovenian (sl) string translations for the CLARIN DSpace
repository. But note all this is a Claude Code experiment, so documentation may also be excessive
and wrong.

## Current Status (as of 2026-01-29)

✅ **Completed:**
- Slovenian translation file created: `src/assets/i18n/sl.json5`
- Language configuration updated in `config/config.yml`
- Slovenian (sl) set as active alongside English (en)

⚠️ **Remaining Work:**
- Review ~2,145 pending translation keys (out of ~3,100 total)

## Quick Start Guide

### 1. Set Up Translation Tools

Install dependencies and set your API key:

```bash
# Install Python dependencies
pip install anthropic json5 rapidfuzz

# Set your Claude API key
export ANTHROPIC_API_KEY="your-api-key"
```

Get your API key from: https://console.anthropic.com/

Get the git repository and translation branch:

```bash
git clone git@github.com:clarinsi/dspace-angular.git
git remote rename origin si
git checkout localisation
```

### 2. Run Machine Translation with DSpace 5 Reuse

```bash
# Preview what will happen (no API calls)
python scripts/translate-sl.py --stats-only

# Run full translation (overwrites everything)
python scripts/translate-sl.py

# Re-translate only PENDING keys (preserves DONE and IN_PROGRESS translations)
python scripts/translate-sl.py --update pending

# Adjust thresholds and re-translate pending
python scripts/translate-sl.py --high 0.95 --medium 0.80 --update pending
```

**Smart Translation Strategy:**
1. **First, try DSpace 5 reuse** - Fuzzy match each DSpace 7 English string with DSpace 5 translations
   - `≥ 90% match`: Use DSpace 5 translation, mark as `REVIEW: DONE` (high confidence)
   - `70-89% match`: Use DSpace 5 translation, mark as `REVIEW: PENDING`, include Claude alternative
   - `< 70% match`: Use Claude translation, include DSpace 5 as alternative
2. **Fallback to Claude API** - For new strings with no good DSpace 5 match

**Configurable Thresholds:**
- `--high` (default 0.90): Matches above this are marked DONE
- `--medium` (default 0.70): Matches above this use DSpace 5 but marked PENDING
- Use `--stats-only` to preview match distribution before committing

**Update Modes:**
- `--update all` (default): Full regeneration, overwrites everything
- `--update pending`: Only re-translate PENDING keys, preserve IN_PROGRESS + DONE
- `--update in-progress`: Re-translate PENDING + IN_PROGRESS, preserve DONE

**Benefits:**
- Reuses existing reviewed translations (~31% auto-approved from DSpace 5)
- Saves API costs (fewer Claude calls needed)
- Maintains terminology consistency for upgrading users
- Incremental updates preserve manual review work

### 3. Review Translations

**Check progress:**
```bash
python scripts/review-progress.py
```

**Find pending items:**
```bash
# All pending translations
grep -n "REVIEW: PENDING" src/assets/i18n/sl.json5

# Specific section (e.g., navigation)
grep -n "navigation.*REVIEW: PENDING" src/assets/i18n/sl.json5
```

**Update review status as you work:**
```json5
// Good translation → mark as DONE
"404.page-not-found": "stran ni bila najdena",  // REVIEW: DONE

// Needs attention → mark as IN_PROGRESS with optional note
"login.help": "Potrebujete pomoč pri prijavi?",  // REVIEW: IN_PROGRESS | note: too formal
```

### 4. Check and commit changes

```bash
python scripts/review-progress.py
git commit -m "<message>"
git push si localisation
```

## Translation File Location

**File:** `src/assets/i18n/sl.json5`

**Current State:** The file has been machine-translated with proper formatting. Each key has:
- English original as a comment above
- Slovenian translation as the value
- Review status marker (`REVIEW: DONE` or `REVIEW: PENDING`)

When reviewing, translate the **values** (right side) while keeping the **keys** (left side) unchanged.

### Proper Format with English Comments

According to DSpace standards, each translated key should include a comment with the original English text:

```json5
{
  // ✅ CORRECT - English original as comment, key unchanged, value translated
  // "404.page-not-found": "page not found",
  "404.page-not-found": "stran ni bila najdena",

  // ❌ WRONG - Don't translate the key
  "404.stran-ni-bila-najdena": "page not found",

  // ❌ WRONG - Missing English comment
  "404.page-not-found": "stran ni bila najdena",
}
```

This format:
- Helps translators see the original English context
- Enables automated synchronization when English files are updated
- Makes it easier to identify outdated translations

## Translation Strategy: Machine Translation + Human Review

This project uses a two-phase approach:

1. **Machine Translation (Automated)** - Use AI/machine translation for initial pass
2. **Human Review & Correction (Manual)** - Native speakers review and correct, focusing on:
   - Academic/technical terminology
   - CLARIN-specific terms
   - User-facing messages
   - Error messages

This approach provides fast initial results while ensuring quality through human review.

## Translation Workflow

### Step 1: Prepare Translation Environment

```bash
# Create a backup
cp src/assets/i18n/sl.json5 src/assets/i18n/sl.json5.backup

# Validate JSON5 format (optional)
yarn install
```

### Step 2: Run Machine Translation

Use the provided translation script to translate keys from English to Slovenian:

```bash
# Preview match distribution first (recommended)
python scripts/translate-sl.py --stats-only

# Run full translation (first time or regeneration)
python scripts/translate-sl.py

# Or re-translate only pending items (preserves reviewed work)
python scripts/translate-sl.py --update pending
```

This will generate/update `src/assets/i18n/sl.json5` with:
- English original as comments
- Machine-translated Slovenian text
- Review markers: `// REVIEW: DONE` (high-confidence) or `// REVIEW: PENDING`

### Step 3: Translation Guidelines

**Key Principles:**
1. **Don't translate the keys** - Only translate values (right side of `:`)
2. **Preserve placeholders** - Keep `{{variable}}`, `{0}`, `{1}` exactly as-is
3. **Maintain HTML tags** - Keep `<a>`, `<strong>`, `<br>` etc. in translations
4. **Preserve line breaks** - Use `\n` where present in English
5. **Keep technical terms** - Words like "DSpace", "Handle", "DOI" stay in English

**Examples:**

```json5
// Placeholders - keep {{username}} intact
// "user.greeting": "Welcome, {{username}}!",
"user.greeting": "Dobrodošli, {{username}}!",  // ✅ Correct

// HTML tags - preserve structure
// "item.download": "Click <a href='{{url}}'>here</a> to download",
"item.download": "Kliknite <a href='{{url}}'>tukaj</a> za prenos",  // ✅ Correct

// Technical terms - keep as-is (Handle unchanged)
// "item.handle": "Handle: {{handle}}",
"item.handle": "Handle: {{handle}}",  // ✅ Correct
```

### Step 4: Review Workflow

After machine translation, review translations incrementally. The inline review markers track progress.

**Review Process:**

1. **Check current progress:**
   ```bash
   python scripts/review-progress.py
   ```

2. **Find pending translations** (by priority or section):
   ```bash
   # All pending items
   grep -n "REVIEW: PENDING" src/assets/i18n/sl.json5

   # Pending items in specific section (e.g., navigation)
   grep -n "navigation.*REVIEW: PENDING" src/assets/i18n/sl.json5
   ```

3. **Review and update status:**
   ```json5
   // Before review
   // "404.page-not-found": "page not found",
   "404.page-not-found": "stran ni byla najdena",  // REVIEW: PENDING

   // After review - translation is good
   // "404.page-not-found": "page not found",
   "404.page-not-found": "stran ni bila najdena",  // REVIEW: DONE

   // Needs attention or being worked on
   // "404.help": "We can't find the page...",
   "404.help": "Ne moremo najti strani...",  // REVIEW: IN_PROGRESS | note: too literal
   ```

4. **Track progress regularly:**
   ```bash
   python scripts/review-progress.py
   ```

**Review Status Values (in order of priority):**

| Status | Meaning | When `--update` re-translates |
|--------|---------|------------------------------|
| `PENDING` | Not yet reviewed | `pending`, `in-progress`, `all` |
| `IN_PROGRESS` | Being worked on or needs attention | `in-progress`, `all` |
| `DONE` | Reviewed and approved | `all` only |

You can add optional notes: `// REVIEW: IN_PROGRESS | note: check terminology`

**Tips for Team Review:**
- Divide work by sections (navigation, search, admin, etc.)
- Use git branches for parallel work: `git checkout -b review/navigation`
- Communicate which sections team members are working on
- Merge completed sections regularly

### Step 5: CLARIN-Specific Terminology

Standardize these terms across all translations:

| English | Slovenian (Suggested) | Notes |
|---------|----------------------|-------|
| Repository | Repozitorij | Standard term |
| Collection | Zbirka | |
| Community | Skupnost | |
| Item | Objekt / Predmet | Choose one consistently |
| License | Licenca | |
| Download | Prenos | |
| Upload | Nanos | |
| Bitstream | Bitstream | Keep in English |
| Handle | Handle | Keep in English |
| Metadata | Metapodatki | |
| Submission | Oddaja | |
| Workflow | Potek dela | |

**Note:** Consult with Slovenian librarians/academics for standard terminology in your domain.

## Useful Commands

```bash
# Progress report
python scripts/review-progress.py

# Preview translation stats (no API calls)
python scripts/translate-sl.py --stats-only

# Re-translate only pending items
python scripts/translate-sl.py --update pending

# Count translations by status
grep -c "REVIEW: DONE" src/assets/i18n/sl.json5
grep -c "REVIEW: PENDING" src/assets/i18n/sl.json5
grep -c "REVIEW: IN_PROGRESS" src/assets/i18n/sl.json5

# Find items needing attention
grep -n "REVIEW: IN_PROGRESS" src/assets/i18n/sl.json5
grep -n "REVIEW: PENDING" src/assets/i18n/sl.json5

# Find specific sections
grep -n "navigation.*REVIEW: PENDING" src/assets/i18n/sl.json5
grep -n "admin.*REVIEW: PENDING" src/assets/i18n/sl.json5
```

## Translation Scripts

Two scripts are provided to manage the translation workflow:

### 1. Translation Script (`scripts/translate-sl.py`)

Generates machine-translated file with review markers using DSpace 5 reuse + Claude API.

**Location:** `scripts/translate-sl.py`

**Features:**
- Fuzzy-matches DSpace 7 English with DSpace 5 translations
- Falls back to Claude API for new/changed strings
- Configurable confidence thresholds
- Incremental update mode (preserves reviewed translations)
- Stats-only mode to preview before running
- Progress indicator and cost estimates

**Command-Line Options:**
```
--high FLOAT      High confidence threshold (default: 0.90)
                  Matches >= this use DSpace 5 and are marked DONE
--medium FLOAT    Medium confidence threshold (default: 0.70)
                  Matches >= this use DSpace 5 but marked PENDING
--update MODE     What to update: 'pending', 'in-progress', or 'all'
                  - pending: only re-translate PENDING keys
                  - in-progress: re-translate PENDING + IN_PROGRESS
                  - all: full regeneration (default)
--stats-only      Show match distribution without translating
```

**Usage Examples:**
```bash
# Install dependencies
pip install anthropic json5 rapidfuzz

# Set API key
export ANTHROPIC_API_KEY="your-api-key"

# Preview match distribution (no API calls, no changes)
python scripts/translate-sl.py --stats-only

# Full translation (first run or complete regeneration)
python scripts/translate-sl.py

# Re-translate only pending items with adjusted thresholds
python scripts/translate-sl.py --high 0.95 --medium 0.80 --update pending

# Re-translate pending + in-progress items
python scripts/translate-sl.py --update in-progress
```

**Model Used:** Claude 3 Haiku (`claude-3-haiku-20240307`) - fast and cost-effective

### 2. Progress Tracking Script (`scripts/review-progress.py`)

Analyzes the translation file and generates a progress report.

**Location:** `scripts/review-progress.py`

**Features:**
- Counts translations by review status
- Shows completion percentage
- Progress bar visualization
- Lists items in progress
- Suggests next actions

**Usage:**
```bash
# View progress report
python scripts/review-progress.py

# Export stats as JSON (for automation)
python scripts/review-progress.py --json
```

**Example Output:**
```
╔════════════════════════════════════════════════════════════════╗
║       Slovenian Translation Review Progress Report            ║
╚════════════════════════════════════════════════════════════════╝

📊 Overall Progress: 30.8% complete

   [███████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 953/3098

📈 Detailed Status:

   Total keys:         3098
   ✅ Done:             953 (30.8%)
   ⏳ Pending:         2145 (69.2%)
   🔄 In Progress:        0 ( 0.0%)
```

## Priority Review Areas

After machine translation, review in this order for quickest user-visible results:

### Phase 1: Core UI (High Priority)
- `navigation.*` - Main navigation
- `menu.*` - Menu items
- `search.*` - Search interface
- `login.*` - Authentication
- `404.*`, `401.*`, `403.*`, `500.*` - Error pages
- `form.*` - Form labels and buttons

### Phase 2: Item Display (Medium Priority)
- `item.*` - Item page elements
- `collection.*` - Collection pages
- `community.*` - Community pages
- `browse.*` - Browse interface
- `file.*` - File download/display

### Phase 3: CLARIN Features (Medium Priority)
- `clarin.license.*` - License system
- `clarin.submission.*` - Submission forms
- `clarin.auth.*` - AAI/Shibboleth

### Phase 4: Admin & Advanced (Lower Priority)
- `admin.*` - Admin interface
- `workflow.*` - Workflow system
- `statistics.*` - Statistics
- `curation.*` - Curation tasks

## Review Guidelines

When reviewing machine-translated content, focus on:

1. **CLARIN.SI terminology:** Ensure consistency with existing Slovenian CLARIN documentation
2. **Library standards:** Reference Slovenian national library terminology
3. **Context accuracy:** Machine translation may miss context - verify technical terms make sense
4. **Natural language flow:** Adjust phrasing to sound natural in Slovenian
5. **Academic language:** Ensure appropriate register for academic/research context

## Useful Resources

- **DSpace 7 i18n docs:** https://wiki.lyrasis.org/pages/viewpage.action?pageId=117735441
- **JSON5 syntax:** https://json5.org/
