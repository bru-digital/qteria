# Changelog

All notable changes to Stack-Driven will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Comprehensive usage documentation (issue #62)
  - COMMAND-REFERENCE.md - Complete reference for all 25 commands
  - TROUBLESHOOTING.md - Common errors and solutions
  - FAQ.md - Comprehensive frequently asked questions
  - CONTRIBUTING.md - Contribution guidelines
  - GLOSSARY.md - Framework terminology definitions
  - QUICK-REFERENCE.md - One-page cheat sheet
  - .github/ templates for issues and pull requests

---

## [2.0.0] - 2025-11-10

### Major Changes - v2.0: Generative Cascade

**Breaking Change:** Stack-Driven v2.0 transforms from a prescriptive template collection into a **generative cascade** where AI analyzes YOUR specific user journey and recommends optimal decisions.

**Previous approach (v1.x):** Prescribed "use Next.js, FastAPI, and PostgreSQL" for everyone

**New approach (v2.0):** "Tell me about your users, and I'll recommend the optimal stack for YOUR journey"

### Added

**Core Cascade Expansion (14 sessions):**
- Session 7: `/design-database-schema` - Complete database schema with ERD and migrations
- Session 8: `/generate-api-contracts` - OpenAPI specifications and endpoint definitions
- Session 9: `/create-test-strategy` - Comprehensive testing strategy (unit, integration, E2E)
- Session 12: `/scaffold-project` - Working development environment with actual code files
- Session 13: `/plan-deployment` - Deployment strategy and CI/CD pipeline
- Session 14: `/design-observability` - Monitoring, alerting, and observability strategy

**Post-Cascade Extensions (8 sessions):**
- Session 15: `/discover-naming` - Brand name generation and evaluation
- Session 16: `/define-messaging` - Brand messaging framework
- Session 17: `/design-brand-identity` - Logo, visual system, brand guidelines
- Session 18: `/create-content-guidelines` - Content style guide and microcopy
- Session 19: `/design-user-experience` - Detailed UX research, flows, wireframes
- Session 20: `/setup-analytics` - Analytics implementation plan
- Session 21: `/design-growth-strategy` - Growth strategy with acquisition channels
- Session 22: `/create-financial-model` - Financial modeling and unit economics

**Meta Commands:**
- `/cascade-status` - Check cascade progress and next steps
- `/run-cascade` - Automatically execute cascade sequentially

**Development Commands:**
- `/review-code` - Comprehensive code review framework

**Essentials Templates:**
- Created "essentials" versions of long documents for token optimization
- `11-product-strategy-essentials.md`
- `07-database-schema-essentials.md`
- `08-api-contracts-essentials.md`
- `09-test-strategy-essentials.md`
- AI reads essentials versions in downstream sessions to reduce context

**Template Numbering System:**
- Implemented consistent numbering (00-22) across all templates
- Core sessions: 00-14
- Post-cascade extensions: 15-22
- See `templates/README.md` for complete guide

**Documentation:**
- PHILOSOPHY.md - Framework philosophy and core axioms
- IMPLEMENTATION-PROMPT.md - Detailed guide for contributors
- templates/README.md - Template numbering and organization guide
- Enhanced README.md with complete cascade overview
- GETTING-STARTED.md improvements

**Examples:**
- `examples/compliance-saas/` - Complete cascade demonstration
- Shows journey-driven tech stack selection
- Demonstrates generative approach

### Changed

**Session Reordering:**
- Session 2: Product Strategy (was pre-cascade, now reads journey)
- Session 5: Brand Strategy (moved from pre-cascade to post-Session 4)
- All commands now read user journey as input
- Complete philosophy alignment: User journey ALWAYS comes first

**Command Improvements:**
- All commands now include:
  - Decision trees for complex choices
  - "What We DIDN'T Choose" sections
  - Quality checklists
  - Examples from compliance-saas
  - AI agent guidelines for edge cases

**Output Files:**
- Moved from `.stack-driven/` to `product-guidelines/` (more intuitive)
- Standardized file naming convention (XX-name.md)
- All outputs remain gitignored (each user generates own cascade)

**Framework Positioning:**
- Emphasis on generative (not prescriptive) approach
- "Different journeys → different stacks" messaging
- Clear separation: Core cascade (14) vs Post-cascade extensions (8)

### Removed

**Pre-Cascade Commands (moved to post-cascade):**
- Commands no longer run before understanding users
- All branding/strategy commands now read journey first
- Maintains philosophy: User journey is the foundation

**Prescriptive Elements:**
- Removed generic "best practices" templates
- Removed one-size-fits-all tech stack recommendations
- Replaced with journey-driven analysis

### Fixed

- Philosophy consistency: All commands now trace back to user journey
- Cascade flow: Clear dependencies between sessions
- Template structure: Consistent format across all templates
- File numbering: Resolved conflicts and gaps in numbering system

---

## [1.0.0] - 2024-XX-XX

### Added

**Initial Release:**
- Core 6-session cascade:
  1. `/refine-journey` - User journey definition
  2. `/choose-tech-stack` - Technology selection
  3. `/generate-strategy` - Mission, metrics, monetization, architecture
  4. `/create-brand-strategy` - Brand foundation
  5. `/create-design` - Design system
  6. `/generate-backlog` - Feature backlog
  7. `/create-gh-issues` - GitHub integration

**Foundation:**
- Templates for all core sessions
- Example implementation (compliance-saas)
- Basic documentation (README, GETTING-STARTED)
- `.stack-driven/` output directory structure

**Philosophy:**
- User-first approach
- Cascading decisions
- Journey → Strategy → Execution flow

---

## Version History Overview

| Version | Date | Key Changes |
|---------|------|-------------|
| **2.0.0** | 2025-11-10 | Generative cascade, 14 core sessions, 8 post-cascade extensions, essentials templates, complete philosophy alignment |
| **1.0.0** | 2024-XX-XX | Initial release, 6 core sessions, basic cascade |

---

## Migration Guides

### Migrating from v1.x to v2.0

**What changed:**
1. **More sessions:** 6 → 14 core sessions
2. **Output directory:** `.stack-driven/` → `product-guidelines/`
3. **File numbering:** Updated numbering system
4. **New capabilities:** Database schema, API contracts, testing, scaffolding, deployment, observability

**Migration steps:**

**Option 1: Start Fresh (Recommended)**
```bash
# Backup old cascade
mv .stack-driven .stack-driven.v1.backup

# Create new directory
mkdir product-guidelines

# Run v2.0 cascade
/refine-journey
# ... continue with new sessions
```

**Option 2: Migrate Existing Files**
```bash
# Move files to new directory
mkdir product-guidelines
mv .stack-driven/* product-guidelines/

# Renumber if needed (check templates/README.md)
# Fill in missing sessions (7-14)
/design-database-schema
/generate-api-contracts
# ... etc
```

**What you need to do:**
- Re-run complete cascade (recommended for best results)
- Or supplement existing cascade with new sessions (7-14)
- Update any automation that references `.stack-driven/`

**Breaking changes:**
- Output directory changed
- File numbering updated
- Some commands moved in cascade order
- New required inputs for some commands

**Benefits:**
- Complete production-ready system
- Better philosophy alignment
- More comprehensive outputs
- Token-optimized with essentials templates

---

## Roadmap

### Planned for v2.1

**Enhanced Examples:**
- Mobile app example (React Native / Flutter)
- Real-time collaboration app (WebSockets)
- E-commerce marketplace
- Developer tools / CLI

**Improved Commands:**
- More decision trees
- Better error handling
- Enhanced validation

**Documentation:**
- Video tutorials
- Interactive guides
- More case studies

**Integrations:**
- Notion integration
- Jira/Linear export
- Figma plugin (future)

### Planned for v2.2+

**AI Enhancements:**
- Multi-model support
- Cost optimization
- Faster execution

**Community Features:**
- Showcase of completed cascades
- Template marketplace
- Custom command sharing

**Advanced Features:**
- Team collaboration workflows
- Version control integration
- Analytics and tracking

### Under Consideration

- Web UI / dashboard
- VS Code extension
- Mobile app for cascade management
- Advanced customization options
- Multi-language support

---

## Contributing to Changelog

When submitting PRs, add your changes under `[Unreleased]` section:

```markdown
## [Unreleased]

### Added
- Your new feature (#PR-NUMBER)

### Changed
- Your improvements (#PR-NUMBER)

### Fixed
- Your bug fixes (#PR-NUMBER)
```

Maintainers will organize and version changes during release.

---

## Versioning Philosophy

**Major version (X.0.0):**
- Breaking changes
- Fundamental architecture changes
- Major new capabilities

**Minor version (2.X.0):**
- New features
- New commands/sessions
- Backwards-compatible enhancements

**Patch version (2.0.X):**
- Bug fixes
- Documentation updates
- Minor improvements
- No breaking changes

---

## Getting Release Notifications

**Watch the repository:**
1. Go to https://github.com/bru-digital/stack-driven
2. Click "Watch" → "Custom" → "Releases"
3. Get notified of new versions

**Check regularly:**
- GitHub Releases page
- This CHANGELOG.md file

---

## Support for Old Versions

**v2.x (current):**
- ✅ Actively maintained
- ✅ Bug fixes and improvements
- ✅ New features

**v1.x (legacy):**
- ⚠️ Security fixes only
- ⚠️ No new features
- ⚠️ Migrate to v2.0 recommended

**v0.x (deprecated):**
- ❌ No longer supported
- ❌ Migrate to v2.0 required

---

## License

Stack-Driven is released under the Apache License 2.0.

See [LICENSE](LICENSE) file for details.

---

**Last Updated:** 2025-11-14
**Current Version:** 2.0.0
**Status:** Active Development

For questions about changes, see [FAQ.md](FAQ.md) or open an [issue](../../issues).
