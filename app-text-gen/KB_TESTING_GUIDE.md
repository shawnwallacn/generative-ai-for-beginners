# Phase 3: Knowledge Base Testing Guide

Follow these steps to test the Knowledge Base functionality:

## Setup

1. Make sure the app is running in your terminal
2. You should see the app welcome message and command options

## Test Workflow

### Step 1: Create a Collection

```
Type: kb
Select: 1 (Create collection)
Collection name: 6502-docs
Description: Documentation about 6502 microprocessor
```

Expected: You should see `✓ Collection '6502-docs' created`

### Step 2: Add a Document

```
Select: 2 (Add document to collection)
```

You'll see available collections. Select the one you just created.

```
File path: sample_kb_document.md
Document title (optional): 6502 Microprocessor Guide
Select strategy (1-3): 1 (Paragraphs - default)
```

Expected:
```
✓ Document added: 6502 Microprocessor Guide
  - Chunks: X
  - Total words: X
  - Document ID: doc_6502-docs_0_TIMESTAMP
```

### Step 3: View Collections

```
Select: 3 (List collections)
```

You should see your collection listed with its description.

### Step 4: View Documents

```
Select: 4 (List documents)
Select: 1 (Select your collection)
```

You should see your document listed with its chunk count and word count.

### Step 5: View Statistics

```
Select: 5 (View collection stats)
Select: 1 (Select your collection)
```

You should see stats like:
- Collection name and description
- Document count: 1
- Total chunks: X
- Total words: X
- Created timestamp

### Step 6: View Overall Stats

```
Select: 6 (View KB stats)
```

You should see:
- Collections: 1
- Documents: 1
- Total chunks: X
- Total words: X
- Indexed documents: 0/1 (will show as "Not indexed" until we integrate indexing in Phase 3b)

### Step 7: Test Multiple Documents

Go back (Select 0) and repeat the workflow:
- Create another collection (e.g., "python-docs")
- Add another document
- View the increased statistics

### Step 8: Return to Main Menu

```
Select: 0 (Back to main menu)
```

## Expected Behavior

✅ Collections created successfully
✅ Documents added and chunked
✅ Correct document counts and word counts displayed
✅ Statistics accurately calculated
✅ File structure created (knowledge_base/ directory)
✅ KB index saved (knowledge_base/kb_index.json)

## Troubleshooting

If you see errors:
- **File not found**: Make sure you use the correct path to the document
- **Collection not found**: Create a collection first before adding documents
- **No content to index**: Try with a larger document
- **Parse errors**: Ensure the file format is supported (TXT, MD, PDF)

## Next Steps

Once KB management is working, Phase 3b will:
1. Index KB documents with embeddings
2. Include KB results in RAG context
3. Add KB search command
4. Integrate KB into automatic context retrieval

Let me know what you see! 🚀

