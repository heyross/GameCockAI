# Next Session Prompt - Critical Bug Fixes Required

## Current Critical Issues

The GameCock AI application has **CRITICAL BUGS** that prevent core functionality from working. The main application cannot find companies or add them to the target list, which are essential features.

## Immediate Priority: Fix Core Application Functionality

### 1. **CRITICAL: Fix Company Search and Addition**
- **Problem**: Main app cannot find companies or add them to target list
- **Impact**: Core functionality is broken
- **Status**: Must be fixed before any new features

### 2. **CRITICAL: Consolidate Duplicate Files**
- **Problem**: Two `processor.py` files exist:
  - `GameCockAI/processor.py` (complete, 2000+ lines)
  - `GameCockAI/src/processor.py` (incomplete, 200 lines)
- **Solution**: Integrate complete processor.py into src/processor.py
- **Impact**: Import conflicts causing application failures

### 3. **CRITICAL: Fix Import System**
- **Problem**: Import errors due to duplicate files and path conflicts
- **Solution**: Update all imports to use src/ modules consistently
- **Impact**: Application cannot start properly

## Current File Structure Issues

```
GameCockAI/
├── processor.py          # COMPLETE VERSION (2000+ lines) - KEEP THIS CONTENT
├── src/
│   ├── processor.py      # INCOMPLETE VERSION (200 lines) - REPLACE WITH ABOVE
│   └── [other modules]
└── [other files]
```

## Required Actions (In Order)

### Step 1: Consolidate Processor Files
1. **Read** `GameCockAI/processor.py` (complete version)
2. **Read** `GameCockAI/src/processor.py` (incomplete version)
3. **Replace** `GameCockAI/src/processor.py` with complete content from `GameCockAI/processor.py`
4. **Delete** `GameCockAI/processor.py` (duplicate)

### Step 2: Fix Import System
1. **Update** `GameCockAI/main.py` imports to use `from src.processor import ...`
2. **Update** all other files that import from processor
3. **Test** that imports work correctly

### Step 3: Test Core Functionality
1. **Run** `python main.py` to test application startup
2. **Test** company search functionality
3. **Test** adding companies to target list
4. **Verify** all core workflows work end-to-end

### Step 4: Clean Up
1. **Remove** any remaining duplicate files
2. **Verify** all imports use src/ modules consistently
3. **Test** complete application functionality

## Key Files to Focus On

- `GameCockAI/main.py` - Main application entry point
- `GameCockAI/processor.py` - Complete processor (source of truth)
- `GameCockAI/src/processor.py` - Target for integration
- `GameCockAI/company_manager.py` - Company search functionality
- `GameCockAI/company_data.py` - Target list management

## Testing Requirements

After fixes, verify:
1. Application starts without import errors
2. Company search works (find companies by name/ticker)
3. Companies can be added to target list
4. All core workflows function properly
5. No duplicate files remain

## Important Notes

- **DO NOT** start new feature development until core bugs are fixed
- **DO NOT** create new files until existing issues are resolved
- **PRIORITIZE** functionality over new features
- **TEST** everything thoroughly after each fix
- **KEEP** the complete processor.py content (2000+ lines)
- **REPLACE** the incomplete src/processor.py with complete content

## Success Criteria

- Application starts without errors
- Company search functionality works
- Companies can be added to target list
- All imports use src/ modules consistently
- No duplicate files exist
- Core workflows function end-to-end

## Next Steps After Fixes

Once core functionality is restored:
1. Implement comprehensive testing
2. Build features from brainstorm.md one at a time
3. Add integration testing and documentation
4. Follow the build/test/commit checklist from brainstorm.md

---

**CRITICAL**: Fix the core application bugs first. Do not proceed with new features until the application can find companies and add them to the target list.