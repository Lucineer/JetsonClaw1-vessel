# Fork-and-Ship as Pedagogy

## Overview

Fork-and-ship is an educational model where students fork a repository, complete assignments within it, and "ship" (submit/merge) their work. It leverages real Git workflows as a teaching tool, giving students production-grade version control experience.

## Why It Works

### Authentic Learning
- Students use the same tools professionals use (Git, PRs, code review)
- Work is public/persistent — not lost in an LMS submission box
- Builds a portfolio that outlasts the course
- Teach Git by doing Git, not by reading about Git

### Feedback Loops
- PR reviews mirror professional code review
- Inline comments are more contextual than a rubric score
- Iterative: students can push fixes and request re-review
- History is preserved — students can see their own progression

### Motivation
- Public repos create accountability and pride
- Shipping real code is more motivating than homework points
- Community: students can see (and learn from) each other's approaches
- Transition to open source contribution is seamless

## Existing Implementations

### GitHub Classroom
- Free for education, integrates with Canvas/Blackboard/Moodle
- Creates per-student or per-team repos from a template
- Supports individual and group assignments
- Automated testing via GitHub Actions on PR
- rubric-based grading integration
- **Limitation**: No built-in AI-assisted review or adaptive difficulty

### GitLab Education
- Similar to GitHub Classroom but with GitLab's CI/CD pipeline
- More flexible for self-hosted institutions
- Stronger CI/CD integration for automated testing

### Replit
- Browser-based, zero setup required
- Built-in collaboration, Git integration
- Lower barrier to entry than raw Git
- Good for introductory courses

### MIT's 6.00.1 / 6.006 (and similar)
- Use Git repos for homework submission
- Automated test suites validate correctness
- TAs review code quality in addition to correctness

## Design Patterns for Fork-and-Ship

### The Template Repo Pattern
1. Instructor creates a template repo with:
   - Starter code (scaffolding, boilerplate)
   - Test suite (visible and hidden tests)
   - README with instructions
   - CI configuration (runs tests on push/PR)
   - `.github/PULL_REQUEST_TEMPLATE.md`

2. Students fork and:
   - Clone locally or work in browser
   - Implement solutions
   - Push and open PR (or merge to main for simpler workflows)
   - CI runs automatically — instant feedback

### The Branch-Based Pattern
- Students work on branches (`homework-1`, `homework-2`)
- Each branch is reviewed and merged
- Main branch represents their "shipped" portfolio
- Good for progressive assignments that build on each other

### The Collaboration Pattern
- Students are assigned to teams
- Each team forks a group repo
- Git workflow teaches collaboration (branches, merge conflicts, code review)
- PRs require at least one team member review

## Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Academic integrity (copying) | Hidden tests, similarity detection (MOSS), oral defense component |
| Git is hard for beginners | GitHub Desktop, IDE integration, scaffolded first assignment |
| Grading at scale | Automated tests for correctness, AI for style/readability, TAs for edge cases |
| Late submissions | Git timestamps are immutable — use branch protection and deadlines |
| Accessibility | Replit/browser-based for students without dev machines |

## Actionable Recommendations for Cocapn

1. **Build fork-and-ship into the core workflow**: When a student starts a project, fork from a template. When they submit, open a PR. The PR is the submission artifact.

2. **Automated review pipeline**: On PR open:
   - Run test suite (correctness)
   - Run linter/formatter (style)
   - Run security scanner (dependencies)
   - AI generates review comments with explanations
   - Teacher gets a summary with highlights

3. **Progressive branching**: Start students on a `main` branch. As they learn Git, introduce feature branches, PRs, and eventually collaborative workflows. Git mastery is a hidden curriculum.

4. **Portfolio generation**: At course end, the student's repo IS their portfolio. Auto-generate a summary page showing their best work, progression, and skills demonstrated.

5. **Peer review rounds**: After AI review, optionally enable peer review. Students review each other's PRs using a rubric. This teaches code review skills and exposes them to different approaches.

6. **Cheating detection**: Use AST-level similarity detection (not just text diff). AI can flag suspicious patterns. Combine with oral defense for high-stakes assignments.

## Research Gaps

- Limited empirical research on fork-and-ship's effectiveness vs traditional LMS submission
- Optimal balance of automation vs human review in educational code review
- Long-term impact on career readiness and open source contribution rates
- Effectiveness across different CS education levels (intro vs advanced)
