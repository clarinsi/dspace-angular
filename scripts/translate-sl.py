#!/usr/bin/env python3
"""
Machine Translation Script for Slovenian (sl.json5) with DSpace 5 Reuse

This script translates the English translation file to Slovenian using:
1. DSpace 5 translations (fuzzy matched) - preferred when available
2. Claude API - fallback for new strings

Fuzzy matching thresholds:
- >= 0.90: High confidence - use DSpace 5, mark as REVIEW: OPTIONAL
- 0.70-0.89: Medium confidence - use DSpace 5, mark as REVIEW: RECOMMENDED
- < 0.70: Low confidence - use Claude, show DSpace 5 as alternative, mark as REVIEW: NECESSARY

Usage:
  1. Install dependencies: pip install anthropic json5 rapidfuzz lxml
  2. Set your API key: export ANTHROPIC_API_KEY="your-api-key"
  3. Run: python scripts/translate-sl.py

Requirements:
  - anthropic>=0.18.0
  - json5
  - rapidfuzz
  - lxml
"""

import argparse
import json5
import os
import re
import sys
from pathlib import Path
from anthropic import Anthropic
from rapidfuzz import fuzz, process
import xml.etree.ElementTree as ET

# Paths relative to project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
EN_PATH = PROJECT_ROOT / 'src' / 'assets' / 'i18n' / 'en.json5'
SL_PATH = PROJECT_ROOT / 'src' / 'assets' / 'i18n' / 'sl.json5'
DSPACE5_EN_PATH = PROJECT_ROOT / 'tmp' / 'messages_en.xml'
DSPACE5_SL_PATH = PROJECT_ROOT / 'tmp' / 'messages_sl.xml'
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Fuzzy matching thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.90
MEDIUM_CONFIDENCE_THRESHOLD = 0.70

# Claude API configuration
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # Fast and cost-effective


def j5(val):
    """json5.dumps with proper UTF-8 (no \\uXXXX escapes for diacritics)."""
    return json5.dumps(val, ensure_ascii=False)


def parse_dspace5_messages(xml_path):
    """
    Parse DSpace 5 XML message file.

    Returns:
        dict: {key: message_text}
    """
    messages = {}

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for message in root.findall('message'):
            key = message.get('key')
            text = message.text
            if key and text:
                messages[key] = text.strip()

        return messages

    except Exception as e:
        print(f"⚠️  Warning: Could not parse {xml_path}: {e}")
        return {}


def load_dspace5_translations():
    """
    Load DSpace 5 English and Slovenian translations.

    Returns:
        tuple: (en_messages, sl_messages) as dicts
    """
    print("\nLoading DSpace 5 translations...")

    en_messages = parse_dspace5_messages(DSPACE5_EN_PATH)
    sl_messages = parse_dspace5_messages(DSPACE5_SL_PATH)

    print(f"  Loaded {len(en_messages)} English messages from DSpace 5")
    print(f"  Loaded {len(sl_messages)} Slovenian messages from DSpace 5")

    return en_messages, sl_messages


def find_best_dspace5_match(text, dspace5_en, dspace5_sl, medium_threshold=None):
    """
    Find the best matching DSpace 5 translation using fuzzy matching.

    Args:
        text: DSpace 7 English text to match
        dspace5_en: DSpace 5 English messages {key: text}
        dspace5_sl: DSpace 5 Slovenian messages {key: text}
        medium_threshold: Minimum match score (0.0-1.0). Defaults to MEDIUM_CONFIDENCE_THRESHOLD.

    Returns:
        tuple: (slovenian_text, match_score, matched_key) or (None, 0, None)
    """
    if medium_threshold is None:
        medium_threshold = MEDIUM_CONFIDENCE_THRESHOLD

    if not dspace5_en or not dspace5_sl:
        return None, 0, None

    # Build a reverse lookup: text -> key for DSpace 5 English
    text_to_key = {text: key for key, text in dspace5_en.items()}

    # Find best match using token_sort_ratio (handles word reordering better)
    result = process.extractOne(
        text,
        text_to_key.keys(),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=medium_threshold * 100
    )

    if result:
        matched_text, score, _ = result
        matched_key = text_to_key[matched_text]

        # Check if we have Slovenian translation for this key
        if matched_key in dspace5_sl:
            slovenian = dspace5_sl[matched_key]
            return slovenian, score / 100, matched_key

    return None, 0, None


def translate_with_claude(text):
    """
    Translate text using Claude API.

    Args:
        text: English text to translate

    Returns:
        str: Translated Slovenian text

    Raises:
        Exception: If API call fails
    """
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Translate the following English text to Slovenian for a digital repository interface.

CRITICAL RULES:
1. Preserve ALL placeholders exactly as-is: {{{{variable}}}}, {{0}}, {{1}}, etc.
2. Preserve ALL HTML tags exactly as-is: <a>, <strong>, <br>, etc.
3. Keep technical terms in English: DSpace, Handle, DOI, Bitstream, Metadata
4. Keep \\n (newline) characters exactly as-is
5. Use formal/professional tone appropriate for academic/library context
6. Return ONLY the translated text, no explanations

English text to translate:
{text}

Slovenian translation:"""

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text.strip()

    except Exception as e:
        raise Exception(f"Translation API error: {str(e)}")


def parse_existing_statuses(sl_path=None):
    """Parse existing sl.json5 to extract review statuses per key."""
    if sl_path is None:
        sl_path = SL_PATH
    if not Path(sl_path).exists():
        return {}

    with open(sl_path, 'r', encoding='utf-8') as f:
        content = f.read()

    statuses = {}
    review_re = re.compile(
        r'^\s*"([^"]+)":\s*".*",?\s*//\s*REVIEW:\s*(\w[\w_-]*)',
        re.MULTILINE
    )
    plain_re = re.compile(
        r'^\s*"([^"]+)":\s*".*",?\s*$',
        re.MULTILINE
    )

    for m in review_re.finditer(content):
        key = m.group(1)
        status = m.group(2).upper().replace('-', '_')
        statuses[key] = {'status': status}

    for m in plain_re.finditer(content):
        key = m.group(1)
        if key not in statuses:
            statuses[key] = {'status': None}

    return statuses


def stats_only_mode(high_threshold, medium_threshold):
    """Show match distribution without translating or calling the API."""
    print("Loading English translation file...")
    if not EN_PATH.exists():
        print(f"Error: English file not found at {EN_PATH}")
        sys.exit(1)

    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en = json5.load(f)

    entries = list(en.items())
    print(f"Found {len(entries)} translation keys in DSpace 7\n")
    dspace5_en, dspace5_sl = load_dspace5_translations()

    stats = {'high': 0, 'medium': 0, 'low': 0, 'no_match': 0, 'non_string': 0}
    for key, value in entries:
        if not isinstance(value, str):
            stats['non_string'] += 1
            continue
        _, score, _ = find_best_dspace5_match(
            value, dspace5_en, dspace5_sl, medium_threshold=0.01
        )
        if score >= high_threshold:
            stats['high'] += 1
        elif score >= medium_threshold:
            stats['medium'] += 1
        elif score > 0:
            stats['low'] += 1
        else:
            stats['no_match'] += 1

    total = len(entries)
    print('\n' + '=' * 70)
    print('Match Distribution (DSpace 5 fuzzy matching)')
    print('=' * 70)
    print(f'\n  Total keys: {total}')
    print(f'\n  High confidence  (>= {high_threshold:.0%}): {stats["high"]:5d}  '
          f'({stats["high"]/total*100:5.1f}%)  -> reuse DSpace 5, mark OPTIONAL')
    print(f'  Medium confidence ({medium_threshold:.0%}-{high_threshold:.0%}): {stats["medium"]:5d}  '
          f'({stats["medium"]/total*100:5.1f}%)  -> reuse DSpace 5, mark RECOMMENDED')
    print(f'  Low confidence   (< {medium_threshold:.0%}): {stats["low"]:5d}  '
          f'({stats["low"]/total*100:5.1f}%)  -> use Claude API')
    print(f'  No match at all        : {stats["no_match"]:5d}  '
          f'({stats["no_match"]/total*100:5.1f}%)  -> use Claude API')
    if stats['non_string'] > 0:
        print(f'  Non-string values      : {stats["non_string"]:5d}  (skipped)')

    claude_needed = stats['low'] + stats['no_match'] + stats['medium']
    estimated_cost = claude_needed * 0.00008
    print(f'\n  DSpace 5 reuse (no API): {stats["high"]}')
    print(f'  Claude API calls needed: {claude_needed}')
    print(f'  Estimated API cost:      ${estimated_cost:.2f}')
    print()


def translate_file(high_threshold=HIGH_CONFIDENCE_THRESHOLD,
                   medium_threshold=MEDIUM_CONFIDENCE_THRESHOLD,
                   update_mode='all'):
    """Generate translated JSON5 file with DSpace 5 reuse and Claude fallback."""
    print("Loading English translation file...")

    if not EN_PATH.exists():
        print(f"❌ Error: English file not found at {EN_PATH}")
        sys.exit(1)

    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en = json5.load(f)

    entries = list(en.items())
    print(f"Found {len(entries)} translation keys in DSpace 7\n")

    # Load DSpace 5 translations
    dspace5_en, dspace5_sl = load_dspace5_translations()

    # Load existing statuses and translations for --update mode
    existing = {}
    existing_translations = {}
    if update_mode != 'all':
        existing = parse_existing_statuses()
        if existing and SL_PATH.exists():
            with open(SL_PATH, 'r', encoding='utf-8') as f:
                existing_translations = json5.load(f)
            print(f"Loaded {len(existing)} existing translation statuses from sl.json5")
        else:
            print("No existing statuses found - will translate all keys")

    # Determine which statuses to skip
    if update_mode == 'necessary':
        skip_statuses = {'OPTIONAL', 'RECOMMENDED'}
    elif update_mode == 'recommended':
        skip_statuses = {'OPTIONAL'}
    else:
        skip_statuses = set()

    print(f"\nStarting translation process...\n")
    print(f"Strategy:")
    print(f"  1. Try DSpace 5 fuzzy match (>= {medium_threshold:.0%})")
    print(f"  2. Fall back to Claude API if no good match")
    if update_mode != 'all':
        print(f"  Update mode: {update_mode} (skipping: {', '.join(sorted(skip_statuses))})")
    print()

    # Statistics
    stats = {
        'total': len(entries),
        'dspace5_high': 0,
        'dspace5_medium': 0,
        'claude_primary': 0,
        'claude_only': 0,
        'skipped': 0,
        'errors': 0
    }

    output_lines = ['{']

    for i, (key, value) in enumerate(entries):
        if not isinstance(value, str):
            print(f"⚠️  Skipping non-string value for key '{key}'")
            continue

        # Skip keys preserved from previous run
        if key in existing and existing[key]['status'] in skip_statuses:
            stats['skipped'] += 1
            if key in existing_translations:
                existing_val = existing_translations[key]
                existing_status = existing[key]['status']
                output_lines.append(f'  // {j5(key)}: {j5(value)},')
                output_lines.append(
                    f'  {j5(key)}: {j5(existing_val)},  '
                    f'// REVIEW: {existing_status} | preserved'
                )
                output_lines.append('')
            continue

        try:
            # Try DSpace 5 match first
            dspace5_translation, match_score, matched_key = find_best_dspace5_match(
                value, dspace5_en, dspace5_sl, medium_threshold=medium_threshold
            )

            if match_score >= high_threshold:
                # High confidence - use DSpace 5, mark as OPTIONAL
                translation = dspace5_translation
                source = 'dspace5'
                review_status = 'OPTIONAL'
                stats['dspace5_high'] += 1

                # Format output
                output_lines.append(f'  // {j5(key)}: {j5(value)},')
                output_lines.append(
                    f'  {j5(key)}: {j5(translation)},  '
                    f'// REVIEW: {review_status} | source: {source} (match: {match_score:.2f})'
                )
                output_lines.append('')

            elif match_score >= medium_threshold:
                # Medium confidence - use DSpace 5, review recommended
                translation = dspace5_translation
                source = 'dspace5'
                review_status = 'RECOMMENDED'
                stats['dspace5_medium'] += 1

                # Get Claude translation as alternative
                try:
                    claude_alt = translate_with_claude(value)
                    output_lines.append(f'  // {j5(key)}: {j5(value)},')
                    output_lines.append(f'  // ALT (claude): {j5(claude_alt)}')
                    output_lines.append(
                        f'  {j5(key)}: {j5(translation)},  '
                        f'// REVIEW: {review_status} | source: {source} (match: {match_score:.2f})'
                    )
                    output_lines.append('')
                except:
                    # If Claude fails, just use DSpace 5 without alternative
                    output_lines.append(f'  // {j5(key)}: {j5(value)},')
                    output_lines.append(
                        f'  {j5(key)}: {j5(translation)},  '
                        f'// REVIEW: {review_status} | source: {source} (match: {match_score:.2f})'
                    )
                    output_lines.append('')

            elif dspace5_translation is not None:
                # Low confidence - use Claude, show DSpace 5 as alternative
                translation = translate_with_claude(value)
                source = 'claude'
                review_status = 'NECESSARY'
                stats['claude_primary'] += 1

                output_lines.append(f'  // {j5(key)}: {j5(value)},')
                output_lines.append(
                    f'  // ALT (dspace5, {match_score:.2f}): {j5(dspace5_translation)}'
                )
                output_lines.append(
                    f'  {j5(key)}: {j5(translation)},  '
                    f'// REVIEW: {review_status} | source: {source}'
                )
                output_lines.append('')

            else:
                # No DSpace 5 match - use Claude only
                translation = translate_with_claude(value)
                source = 'claude'
                review_status = 'NECESSARY'
                stats['claude_only'] += 1

                output_lines.append(f'  // {j5(key)}: {j5(value)},')
                output_lines.append(
                    f'  {j5(key)}: {j5(translation)},  '
                    f'// REVIEW: {review_status} | source: {source}'
                )
                output_lines.append('')

            # Progress indicator
            processed = i + 1
            if processed % 50 == 0:
                percent = (processed / len(entries)) * 100
                print(f"Progress: {processed}/{len(entries)} ({percent:.1f}%)")
                print(f"  DSpace5 high: {stats['dspace5_high']}, "
                      f"medium: {stats['dspace5_medium']}, "
                      f"Claude: {stats['claude_primary'] + stats['claude_only']}, "
                      f"skipped: {stats['skipped']}")

        except Exception as e:
            print(f"❌ Error translating key '{key}': {str(e)}")
            stats['errors'] += 1

            # On error, add original English with error marker
            output_lines.append(f'  // {j5(key)}: {j5(value)},')
            output_lines.append(
                f'  {j5(key)}: {j5(value)},  '
                f'// REVIEW: NECESSARY | ERROR: Translation failed'
            )
            output_lines.append('')

    # Remove trailing comma from last entry and close
    if output_lines[-1] == '':
        output_lines.pop()
    if output_lines[-1].endswith(','):
        output_lines[-1] = output_lines[-1][:-1]

    output_lines.append('}')

    # Write to file
    print("\nWriting translated file...")
    with open(SL_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    # Summary
    print('\n' + '='*70)
    print('✅ Translation complete!')
    print('='*70)
    print(f'\n📊 Statistics:')
    print(f'   Total keys: {stats["total"]}')
    if stats['skipped'] > 0:
        print(f'   Skipped (--update {update_mode}): {stats["skipped"]}')
    print(f'\n   DSpace 5 translations:')
    print(f'     High confidence (>={high_threshold:.0%}): {stats["dspace5_high"]} '
          f'({stats["dspace5_high"]/stats["total"]*100:.1f}%)')
    print(f'     Medium confidence ({medium_threshold:.0%}-{high_threshold:.0%}): '
          f'{stats["dspace5_medium"]} ({stats["dspace5_medium"]/stats["total"]*100:.1f}%)')
    print(f'   Claude API translations:')
    print(f'     Primary (with DSpace 5 alt): {stats["claude_primary"]} '
          f'({stats["claude_primary"]/stats["total"]*100:.1f}%)')
    print(f'     Only Claude (no match): {stats["claude_only"]} '
          f'({stats["claude_only"]/stats["total"]*100:.1f}%)')
    print(f'\n   Errors: {stats["errors"]}')

    # Cost estimate
    claude_calls = stats['claude_primary'] + stats['claude_only'] + stats['dspace5_medium']
    estimated_cost = claude_calls * 0.00008  # Rough estimate
    print(f'\n💰 Estimated Claude API cost: ${estimated_cost:.2f}')
    print(f'   Savings from DSpace 5 reuse: ~${(stats["dspace5_high"] * 0.00008):.2f}')

    print(f'\n📁 Output: {SL_PATH}')
    print('\n📝 Next steps:')
    print('   1. Review translations: grep "REVIEW: NECESSARY" src/assets/i18n/sl.json5')
    print('   2. Check progress: python scripts/review-progress.py')
    print('   3. After reviewing a translation, update its marker to REVIEW: OPTIONAL')
    print('   4. Also check RECOMMENDED items (medium-confidence DSpace 5 matches)')


def main():
    parser = argparse.ArgumentParser(
        description='Translate DSpace 7 English strings to Slovenian using '
                    'DSpace 5 fuzzy matching and Claude API fallback.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  %(prog)s --stats-only            Show match distribution (no API key needed)
  %(prog)s                         Full regeneration (needs ANTHROPIC_API_KEY)
  %(prog)s --update necessary      Only translate keys with NECESSARY status
  %(prog)s --high 0.85 --medium 0.60  Use custom thresholds"""
    )
    parser.add_argument(
        '--high', type=float, default=HIGH_CONFIDENCE_THRESHOLD,
        metavar='FLOAT',
        help=f'High confidence threshold (default: {HIGH_CONFIDENCE_THRESHOLD})'
    )
    parser.add_argument(
        '--medium', type=float, default=MEDIUM_CONFIDENCE_THRESHOLD,
        metavar='FLOAT',
        help=f'Medium confidence threshold (default: {MEDIUM_CONFIDENCE_THRESHOLD})'
    )
    parser.add_argument(
        '--update', choices=['necessary', 'recommended', 'all'], default='all',
        help='Which keys to re-translate: necessary (skip OPTIONAL/RECOMMENDED), '
             'recommended (skip OPTIONAL), all (regenerate everything, default)'
    )
    parser.add_argument(
        '--stats-only', action='store_true',
        help='Show match distribution without translating or calling API'
    )

    args = parser.parse_args()

    if not (0.0 < args.medium < args.high <= 1.0):
        parser.error(f'Thresholds must satisfy 0 < medium ({args.medium}) < high ({args.high}) <= 1.0')

    if args.stats_only:
        stats_only_mode(high_threshold=args.high, medium_threshold=args.medium)
    else:
        translate_file(
            high_threshold=args.high,
            medium_threshold=args.medium,
            update_mode=args.update,
        )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n⚠️  Translation interrupted by user')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Fatal error: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
