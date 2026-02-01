# WuWei Development Log

A running record of TDD-driven development decisions. Each entry captures: what test was written, what design decision it forced, and what emerged from the process.

Built with Claude Code (Opus 4.5) as a pair programming partner.

---

## 2026-02-01 — Project Setup

### What happened
- Created CLAUDE.md (project context) and SPEC.md (full technical specification)
- Initialized git repo, connected to GitHub (github.com/mattyray/thewuwei)
- Set up .gitignore for Django/Next.js/Docker stack

### Design decisions
- **Multi-tenancy approach:** Simple user-scoped queries (every model gets a `user` ForeignKey, every query filters by `request.user`). No tenant abstraction needed — this is a personal practice app, not a team tool.
- **TDD strategy:** Tests drive design at every layer — model tests force schema decisions, API tests force auth/scoping, agent tool tests force interface design. Multi-tenancy is tested at every layer, not bolted on.

### Key insight
> The multi-tenancy guarantee isn't an afterthought — it's baked in because we test for it at every layer. The test that user_a can't see user_b's journal entry drives the `get_queryset` implementation in every viewset.

---

<!-- New entries will be added above this line -->
