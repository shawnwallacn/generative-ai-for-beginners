# Privacy Settings Implementation Guide

## Understanding Conversation History vs Saved Conversations

There's an important distinction that needs to be clear:

### **Conversation History** (In-Memory)
- Shows messages from CURRENT SESSION ONLY
- Stored in memory while app is running
- **NOT affected by privacy settings** (needed for context and RAG)
- Lost when you close the app
- Used by: `history` command

### **Saved Conversations** (Persisted to Disk)
- Saved to `conversations/` folder as JSON files
- Persisted across sessions
- **CONTROLLED BY privacy settings** ✅
- Can be loaded later with `load` command

## How Privacy Settings Work

### **What Privacy Settings Control:**

1. **`auto_save_conversations`**
   - Controls: Whether `save` command actually saves to disk
   - Prompt: "Override and save anyway?" (when OFF)
   - Default: ON

2. **`auto_save_feedback`**
   - Controls: Whether `rate` command saves feedback
   - Prompt: "Override and save feedback anyway?" (when OFF)
   - Default: ON

3. **`auto_save_snippets`**
   - Controls: Whether code snippets are extracted and saved
   - Affects: `extract_code_snippet` function call
   - Default: ON

4. **`auto_save_summaries`**
   - Controls: Whether summaries are created and saved
   - Affects: `create_summary` function call
   - Default: ON

5. **`track_usage_stats`**
   - Controls: Whether API usage is tracked
   - Affects: `record_request` function calls
   - Default: ON

6. **`privacy_mode`** (Master Toggle)
   - When ON: ALL auto-save features disabled
   - Equivalent to: Turning OFF all of 1-5 above
   - Default: OFF

### **What Privacy Settings DON'T Control:**

❌ **Conversation History** - Always available in memory (needed for RAG/context)
❌ **Profiles** - Always saved (needed for app to work)
❌ **Knowledge Base** - Always saved (user explicitly added them)
❌ **Settings** - Always saved (needed to persist user preferences)

---

## Testing Privacy Settings

### **Test 1: Turn Off Conversation Saving**

```bash
# Start app
python src/app.py

# Set privacy
Enter your prompt (or command): privacy
2  # Disable auto-save conversations

# Have a conversation
Enter your prompt (or command): What is Python?
[AI generates response]

# Check history (in-memory, always shows)
Enter your prompt (or command): history
→ Shows current session messages ✓

# Try to save
Enter your prompt (or command): save
→ Prompts: "Override and save anyway? (yes/no):"
→ If you type 'no': Not saved ✓
→ If you type 'yes': Saved despite privacy setting ✓

# Verify file wasn't created (if you said no)
Check: conversations/ folder should be empty
```

### **Test 2: Enable Privacy Mode**

```bash
Enter your prompt (or command): privacy
6  # Enable Privacy Mode

# All auto-save should now be disabled
# Trying `save`, `rate`, etc. will prompt to override
```

### **Test 3: Disable Privacy Mode & Save**

```bash
Enter your prompt (or command): privacy
6  # Disable Privacy Mode (turn it back OFF)

# Now `save` should work without prompting
Enter your prompt (or command): save
→ Saves immediately without prompt ✓
```

---

## Current Implementation Status

### ✅ Implemented:
- [x] Privacy Settings Menu
- [x] Settings Persistence (saved to `settings/privacy_settings.json`)
- [x] Privacy checks in `save_current_conversation()`
- [x] Privacy checks in `rate_last_response()`
- [x] Privacy Mode (master toggle)

### 🔄 In Progress:
- [ ] Function calling privacy checks (snippets/summaries)
- [ ] Usage stats privacy checks
- [ ] Auto-save on response generation

### ⏳ Future:
- [ ] Automatic data cleanup/deletion
- [ ] Data export functionality
- [ ] Cookie/session management
- [ ] GDPR-style data requests

---

## Important Note About Conversation History

The in-memory conversation history is **NOT saved to disk** automatically. It only exists:

1. **During your current session** - displayed by `history` command
2. **In memory** - used for RAG context and streaming
3. **Until you exit the app** - then it's lost

This is **intentional and good** because:
- Gives users control - they must explicitly `save` if they want persistence
- Respects privacy - only what user chooses to save is persisted
- Protects memory - don't accumulate data unless user wants it

---

## How to Actually Test Privacy Enforcement

### **Full Test Flow:**

```bash
# 1. Start fresh
rm settings/privacy_settings.json  # Remove old settings
python src/app.py

# 2. Chat
Enter your prompt (or command): Hello, what's AI?
[AI responds]

# 3. Check history works
Enter your prompt (or command): history
→ Shows: [USER]: Hello, what's AI?
→ Shows: [ASSISTANT]: [response]

# 4. Disable auto-save
Enter your prompt (or command): privacy
1  # Turn OFF auto-save conversations
0  # Back to main menu

# 5. Try to save
Enter your prompt (or command): save
→ Prompts: "⚠️  Auto-save conversations is currently DISABLED..."
→ "Override and save anyway? (yes/no):"
→ Enter: no
→ Result: "Save cancelled." ✓

# 6. Verify no file was created
Check: ls conversations/
→ Should be empty or only show old files

# 7. Re-enable and save
Enter your prompt (or command): privacy
1  # Turn ON auto-save conversations
0  # Back to main menu

Enter your prompt (or command): save
→ No warning prompt
→ Saves normally ✓
```

---

## Architecture Notes

### **Privacy Settings Module** (`src/privacy_settings.py`):
- `PrivacySettings` class manages all settings
- Loads/saves from `settings/privacy_settings.json`
- Provides interactive menu
- Shows data locations and collection info

### **Integration Points** (`src/app.py`):
- `save_current_conversation()` - checks `auto_save_conversations`
- `rate_last_response()` - checks `auto_save_feedback`
- Future: Function calling - check `auto_save_snippets` and `auto_save_summaries`
- Future: Usage tracking - check `track_usage_stats`

### **Privacy Settings File** (`settings/privacy_settings.json`):
```json
{
  "auto_save_conversations": false,
  "auto_save_feedback": true,
  "auto_save_snippets": true,
  "auto_save_summaries": true,
  "track_usage_stats": true,
  "privacy_mode": false,
  "last_updated": "2025-12-29T14:35:22.123456"
}
```

---

## Conclusion

Privacy settings now work to:

✅ **Give users control** over what data is persisted  
✅ **Show clear prompts** when settings block saves  
✅ **Allow overrides** for intentional saves despite settings  
✅ **Persist preferences** across sessions  
✅ **Provide transparency** about what's collected  

The conversation history shown by `history` command is separate from saved conversations - it's in-memory only and not affected by privacy settings (because it's needed for RAG/context during the current session).

