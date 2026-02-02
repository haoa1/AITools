# TODO for AITools Project

## Completed Features ✅

### Markdown Module (Completed)
- ✅ Created markdown module based on git module template
- ✅ Implemented 8 core functions:
  1. `read_markdown_file` - Read markdown files
  2. `write_markdown_file` - Write markdown files
  3. `parse_markdown` - Parse markdown structure
  4. `convert_markdown_to_html` - Convert to HTML
  5. `extract_toc_from_markdown` - Extract table of contents
  6. `extract_code_blocks_from_markdown` - Extract code blocks
  7. `merge_markdown_files` - Merge multiple markdown files
  8. `validate_markdown_syntax` - Validate markdown syntax
- ✅ Split into multiple files (all under 1000 lines):
  - `markdown_base.py` - Base definitions and helpers
  - `markdown_io.py` - File I/O operations
  - `markdown_parse.py` - Parsing and HTML conversion
  - `markdown_extract.py` - Extraction functions
  - `markdown_merge.py` - Merge functionality
  - `markdown_validation.py` - Validation functionality
  - `markdown.py` - Main module interface
- ✅ All functions tested and working

### Markdown Module Integration (Completed)
- ✅ Added `tools` and `TOOL_CALL_MAP` definitions to markdown.py
- ✅ Updated markdown/__init__.py to export tools and TOOL_CALL_MAP
- ✅ Integrated markdown module into main.py load_manual_imports()
- ✅ Verified all 8 markdown tools are loaded (157 total tools)
- ✅ Created integration tests confirming functionality
- ✅ No additional dependencies needed (uses only Python stdlib)

## Next Atomic Features 🚀

### Phase 1: Module Improvements (Priority)

1. **Add markdown to PDF conversion**
   - Create `markdown_to_pdf` function
   - Support styling options
   - Include table of contents generation
   - Add page numbering and headers/footers

2. **Enhance markdown parsing with advanced features**
   - Add support for tables (proper parsing)
   - Add support for footnotes
   - Add support for definition lists
   - Add support for task lists

3. **Add markdown template system**
   - Create template engine for markdown
   - Support variables and conditionals
   - Add includes/partials support

### Phase 2: New Modules Development

4. **Create CSV module** (similar to markdown module)
   - Read/write CSV files
   - Parse CSV data
   - Convert to/from JSON
   - Filter and sort operations
   - CSV validation

5. **Create JSON module** (similar to markdown module)
   - Read/write JSON files
   - Validate JSON syntax
   - Pretty formatting
   - JSON schema validation
   - JSON merge and diff operations

6. **Create YAML module** (similar to markdown module)
   - Read/write YAML files
   - Validate YAML syntax
   - Convert to/from JSON
   - YAML schema validation

### Phase 3: Integration Features

7. **Add markdown to documentation generator**
   - Generate API documentation from markdown
   - Create navigation menus
   - Support search functionality
   - Generate PDF/HTML output

8. **Add markdown blog system**
   - Create blog post templates
   - Generate RSS feeds
   - Add tag/category support
   - Create archive pages

## Technical Debt & Improvements

### Code Quality
- [ ] Add comprehensive unit tests for all modules
- [ ] Add integration tests
- [ ] Add type hints coverage
- [ ] Add documentation strings for all functions

### Performance
- [ ] Optimize markdown parsing for large files
- [ ] Add caching for frequently accessed files
- [ ] Implement streaming for large markdown files

### Security
- [ ] Add input validation and sanitization
- [ ] Prevent path traversal attacks
- [ ] Validate file sizes before processing

## Notes

- Each feature should be atomic and completable
- Keep files under 1000 lines
- Follow git module structure as template
- Use `optimize_feature_context` after each feature
- Update TODO.md after feature completion

## Current Priority

**Next atomic feature:** Add markdown to PDF conversion function

This feature is:
1. Atomic and completable
2. Builds on existing markdown module
3. Adds significant value
4. Follows the module pattern

---

*Last updated: 2026-02-02*
*Next feature: markdown to PDF conversion*