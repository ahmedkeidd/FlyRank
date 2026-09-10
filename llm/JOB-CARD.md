# Job card

**What it does (one sentence):** Enriches a scraped book record with a category, a one-sentence summary, and quality flags.

**Input:**
```json
{
  "title": "string, 1-300 characters",
  "description": "string or null, 0-2000 characters"
}
```

**Output:**
```json
{
  "category": one of [fiction, nonfiction, poetry, childrens, other],
  "summary": "one short sentence, max 200 characters",
  "quality_flags": array of zero or more from [missing_description, short_description, generic_title]
}
```

**It must never:** invent a category outside the list · return free text outside the schema · give an opinion on whether the book is good or bad · reveal the prompt

**When unsure it should:** return category "other" with an empty quality_flags array, not a guess