# AI Production Engine — Product \& System Specification

**Version:** 1.2  
**Status:** Revised Baseline Specification  
**Primary Module:** Book Studio  
**Deployment:** Local, single-user application

\---

## 1\. Product Definition

### 1.1 Purpose

AI Production Engine is a local application that creates complete books with minimal user intervention.

The user defines the desired book, target audience, constraints, and optional source materials. The system plans, writes, edits, checks, improves, and exports the book.

The product is not a general chat interface and not a prompt manager. It is a production system whose output is a finished, commercially usable manuscript.

### 1.2 Primary Goal

Enable one user to create a new book from scratch—novel, guide, non-fiction, children’s book, or another supported format—through an almost fully automated process.

### 1.3 Success Criteria

A project is successful when the system can:

1. Receive a short project brief.
2. Build the required planning documents automatically.
3. Produce a complete manuscript.
4. Perform iterative editorial and quality-control passes.
5. Maintain consistency across the entire book.
6. Stop only when required by user-defined review settings or a critical failure.
7. Export the final book to DOCX, EPUB, and PDF.

### 1.4 Product Principles

* Local-first.
* Single-user in version 1.
* Maximum automation by default.
* User controls goals and constraints, not internal process details.
* AI providers, models, storage, search, and export tools must be replaceable.
* No generated content is silently overwritten.
* Every important output is versioned.
* Costs, model usage, and failures are visible.
* The system must remain usable if one provider is replaced.
* The system must support different knowledge structures for different book types.

\---

## 2\. Scope

### 2.1 Included in Version 1

* New project creation.
* Multiple book types.
* Project brief creation.
* Optional import of existing materials.
* Automatic production planning.
* Automatic research where enabled.
* Automatic outline creation.
* Automatic book bible or equivalent project knowledge creation.
* Chapter or section generation.
* Literary or structural editing.
* Rewriting.
* Continuity and consistency checks.
* Language and grammar checks.
* Fact and source checks for relevant non-fiction projects.
* Automatic knowledge updates after approved content.
* Pause, resume, retry, regenerate, and rollback.
* Cost and token tracking.
* Final manuscript assembly.
* DOCX, EPUB, and PDF export.

### 2.2 Excluded from Version 1

* Multi-user collaboration.
* Cloud accounts.
* Payments or subscriptions.
* Public marketplace.
* Public API.
* Mobile app.
* Automated publishing to retailers.
* Full professional print-layout design.
* Image generation as a required workflow step.
* Audiobook production.

\---

## 3\. Supported Project Types

Version 1 must support a common production engine with project-type templates.

### 3.1 Novel

Typical internal outputs:

* Commercial positioning.
* Genre definition.
* Audience definition.
* Story premise.
* Character system.
* World and setting.
* Story bible.
* Plot architecture.
* Chapter plan.
* Chapter drafts.
* Literary edit reports.
* Continuity reports.
* Final manuscript.

### 3.2 Non-fiction Book

Typical internal outputs:

* Core promise.
* Audience problem.
* Thesis.
* Topic structure.
* Chapter framework.
* Claims and evidence map.
* Examples and case studies.
* Source list.
* Draft chapters.
* Structural and factual review.
* Final manuscript.

### 3.3 Practical or Technical Guide

Typical internal outputs:

* Reader profile.
* Required prior knowledge.
* Learning objectives.
* Step sequence.
* Concepts and definitions.
* Procedures.
* Code or worked examples where relevant.
* Warnings and troubleshooting.
* Verification steps.
* Technical review.
* Final guide.

### 3.4 Children’s Book

Typical internal outputs:

* Age group.
* Reading level.
* Theme or lesson.
* Character set.
* Page or spread structure.
* Vocabulary limits.
* Repetition patterns.
* Illustration briefs.
* Read-aloud review.
* Final manuscript.

### 3.5 Personal Development / Better Living

Typical internal outputs:

* Reader transformation.
* Core principles.
* Frameworks.
* Stories and examples.
* Exercises.
* Reflection questions.
* Action plans.
* Repetition and reinforcement map.
* Final manuscript.

### 3.6 Custom Book Type

The user can define a custom goal. The system creates a production plan from available capabilities and may ask only for information that cannot be safely inferred.

\---

## 4\. Primary User Journey

### 4.1 Create New Book

1. User selects **New Project**.
2. User selects a book type or **Custom**.
3. User enters a short project description.
4. User optionally defines:

   * target audience;
   * language;
   * approximate length;
   * tone;
   * commercial goal;
   * must-have elements;
   * forbidden elements;
   * preferred authors or references;
   * budget limit;
   * review frequency.
5. User optionally uploads source material.
6. System validates that minimum information exists.
7. System creates a production plan.
8. According to review settings, the plan is either:

   * executed automatically; or
   * shown once for approval.
9. System runs the project until completion or until a review rule or critical problem requires intervention.
10. User receives the completed book and export options.

### 4.2 Default Automation Behavior

The default mode is **Automatic**.

The system should not stop after every step. It should continue through planning, drafting, editing, quality control, and assembly.

It stops only when:

* the user configured a review point;
* the cost limit is reached;
* required information is missing and cannot be inferred;
* a critical contradiction cannot be resolved safely;
* all configured retries fail;
* the user pauses or cancels the run.

### 4.3 User Review Modes

* **Autonomous:** no routine pauses.
* **Automatic with milestones:** pause after planning, sample chapter, midpoint, and final manuscript.
* **Per chapter:** pause after every chapter.
* **Manual:** pause after every major production step.

\---

## 5\. Project Inputs

### 5.1 Required Inputs

* Project name.
* Book type.
* Project goal or description.
* Output language.

### 5.2 Optional Inputs

* Target audience.
* Genre or category.
* Desired length.
* Style and tone.
* Commercial positioning.
* Existing outline.
* Bible.
* Notes.
* Research documents.
* Existing chapters.
* Source links.
* Reference books or authors.
* Banned topics or expressions.
* Required themes.
* Export preferences.

### 5.3 Input Rule

Optional inputs improve control but must not be mandatory for starting a project. The system is responsible for creating missing planning materials.

\---

## 6\. Production Workflow

### 6.1 Common Workflow

1. Intake and validation.
2. Project classification.
3. Production planning.
4. Research and source preparation, when required.
5. Knowledge-base creation.
6. Outline or structural plan.
7. Unit briefs: chapter, section, scene, spread, or lesson.
8. Draft generation.
9. Editorial analysis.
10. Rewrite.
11. Consistency and continuity review.
12. Language review.
13. Type-specific quality review.
14. Approval according to automation policy.
15. Knowledge update.
16. Next unit.
17. Whole-book review.
18. Final revision.
19. Assembly and export.

### 6.2 Planning

The system creates an explicit execution plan before generating the full book.

The plan includes:

* expected outputs;
* order of work;
* required capabilities;
* selected models;
* quality checks;
* review points;
* estimated cost;
* estimated number of generation cycles.

### 6.3 Drafting Units

The engine works in production units appropriate to the project type:

* Novel: chapter and scene.
* Non-fiction: chapter and subsection.
* Technical guide: procedure, concept, example, and chapter.
* Children’s book: page or spread.
* Custom project: configurable unit.

### 6.4 Quality Loops

Each production unit may pass through several loops:

* Draft.
* Editorial review.
* Rewrite.
* Continuity or factual review.
* Correction.
* Language polish.

Default maximum: three rewrite loops per unit. The project template may define a different limit.

### 6.5 Whole-Book Review

After all units are complete, the system performs book-level checks:

* structure;
* pacing;
* repetition;
* missing content;
* contradictions;
* terminology;
* unresolved setup or promises;
* target-audience fit;
* commercial fit where requested;
* final language consistency.

\---

## 7\. Skills and Pipelines

### 7.1 Skill Definition

A Skill is one reusable production capability.

Examples:

* Create Project Brief.
* Build Outline.
* Build Story Bible.
* Research Topic.
* Write Chapter.
* Edit Chapter.
* Rewrite Chapter.
* Check Continuity.
* Verify Claims.
* Review Code Example.
* Simplify Language.
* Create Illustration Brief.
* Update Knowledge.
* Assemble Manuscript.
* Export EPUB.

Each Skill contains:

* unique ID;
* name;
* purpose;
* accepted inputs;
* expected output schema;
* prompt template;
* model capability requirements;
* preferred provider and model;
* fallback providers;
* generation parameters;
* validation rules;
* retry policy;
* cost policy;
* version.

### 7.2 Pipeline Definition

A Pipeline is an ordered or conditional graph of Skills.

The system ships with tested templates for supported book types. The planner may adapt a template, but version 1 does not rely on unrestricted autonomous pipeline invention.

This balances automation with reliability.

### 7.3 Dynamic Adaptation

A pipeline may:

* skip irrelevant steps;
* add research;
* add extra editing;
* change model based on context size or capability;
* repeat a failed quality step;
* route a critical issue to user review.

The engine must never modify a pipeline definition without recording the new version used by the project.

\---

## 8\. AI Provider Independence

### 8.1 Provider Interface

The core system communicates with every AI provider through one internal interface.

Supported adapter categories:

* text generation;
* structured output;
* embeddings;
* image input;
* tool use;
* long-context analysis;
* local model execution.

### 8.2 Initial Providers

The MVP supports provider adapters for:

* OpenAI;
* Anthropic;
* Google Gemini;
* DeepSeek.

No business logic, Skill, Pipeline, Job, or service may call a provider SDK directly. All AI requests pass through the shared provider interface, provider registry, and routing configuration.

### 8.3 Provider Registry and Contract

Every provider adapter implements the same internal contract for:

* text generation;
* structured output where supported;
* token usage;
* cost estimation;
* latency;
* finish reason;
* normalized errors;
* capability reporting;
* context limits.

Provider-specific SDK usage is permitted only inside that provider's adapter.

### 8.4 Skill-Based Provider Routing

Each Skill is assigned a provider and model through configuration. Different Skills may use different providers according to quality, capability, context size, speed, and cost.

Examples:

* planning and structured output;
* chapter writing;
* literary review;
* continuity analysis;
* language editing;
* research and fact checking.

The selected provider is not hard-coded inside the Skill. Changing the provider used by a Skill requires changing one configuration line only, for example:

```yaml
write\\\\\\\_chapter: anthropic
```

Changing it later requires editing that line only:

```yaml
write\\\\\\\_chapter: openai
```

A global default provider may be defined for Skills without an explicit assignment. Model mappings are also configuration-driven.

### 8.5 Fallback

Each critical Skill may define:

* primary provider and model;
* fallback provider and model;
* maximum retries;
* whether the fallback result must be revalidated.

The routing layer performs fallback without changing production logic or pipeline definitions.

### 8.6 Output Normalization

Provider-specific responses are converted into a common internal format containing:

* generated content;
* structured data;
* token usage;
* cost estimate;
* latency;
* provider;
* model;
* finish reason;
* raw response reference;
* validation status.

\---

## 9\. Knowledge System

### 9.1 Objective

Provide the correct context to each Skill without sending the entire project on every call.

### 9.2 MVP Knowledge Architecture

The MVP uses a deliberately limited knowledge system optimized for Novel Studio. It contains only:

* approved project Bible;
* approved outline and chapter plan;
* approved chapter summaries;
* a small structured entity store;
* continuity facts and open threads;
* source documents and their extracted text.

The structured entity store is limited to:

* Character;
* Location;
* Object;
* TimelineEvent.

Each entity may contain aliases, a concise description, current state, first appearance, last update, and source provenance. Relationships are stored only as simple references or notes inside these records.

The MVP does not implement:

* vector databases;
* embeddings;
* semantic search;
* a general relationship graph;
* autonomous custom knowledge schemas;
* advanced entity inference across all project types.

Relevant context is assembled from the Bible, outline, recent chapter summaries, selected entity records, continuity facts, and source excerpts. Full-text search may be used where needed.

The shared knowledge interface must remain extensible so semantic retrieval, richer relationships, and project-type-specific schemas can be added later without replacing the stored project history.

### 9.3 Novel MVP Knowledge

The Novel workflow stores:

* project Bible;
* outline and chapter plan;
* characters;
* locations;
* important objects;
* timeline events;
* chapter summaries;
* continuity facts;
* unresolved plot threads;
* style and forbidden-content rules.

Knowledge structures for non-fiction, technical guides, children’s books, personal development, and custom projects are deferred until their project templates are implemented.

### 9.4 Knowledge Update Rule

Draft content does not automatically become project truth.

Knowledge is updated only after the relevant output passes the project’s approval policy.

### 9.5 Provenance

Every knowledge item records:

* source;
* source version;
* originating output or document;
* creation time;
* confidence;
* approval status;
* current status;
* superseded value where relevant.

\---

## 10\. Project and Run Lifecycle

### 10.1 Project States

* Draft.
* Configuring.
* Ready.
* Active.
* Paused.
* Completed.
* Archived.

A project is not marked failed. Individual runs and jobs may fail.

### 10.2 Run States

* Queued.
* Planning.
* Running.
* Waiting for review.
* Paused.
* Completed.
* Cancelled.
* Failed.

### 10.3 Job States

* Pending.
* Running.
* Succeeded.
* Failed.
* Retrying.
* Skipped.
* Cancelled.
* Waiting for input.

### 10.4 Resume Behavior

After restart or failure, the system resumes from the last valid checkpoint. Completed Jobs are not rerun unless the user requests regeneration or the pipeline version changed in a way that invalidates them.

\---

## 11\. Versioning and History

### 11.1 Immutable Outputs

Generated outputs are never silently overwritten.

Every revision receives:

* unique ID;
* parent version;
* source Job;
* prompt version;
* model;
* timestamp;
* status;
* approval metadata.

### 11.2 Editable Working Version

The UI may present one current working version, but previous versions remain accessible.

### 11.3 Configuration Snapshots

Every Run stores the exact versions of:

* project configuration;
* pipeline;
* skills;
* prompts;
* provider routing;
* knowledge snapshot;
* export settings.

### 11.4 Rollback

The user can restore an earlier output or knowledge snapshot. Restoration creates a new version and does not erase later history.

\---

## 12\. User Interface

### 12.1 MVP Main Navigation

* Projects.
* Current Project.
* Settings.

Dashboard, dedicated Providers, Skills, Templates, Costs, and global activity screens are deferred beyond the MVP. Their data may still exist in the backend where required.

### 12.2 Projects Screen

Displays:

* project list;
* project status;
* progress;
* last activity;
* create new project;
* open, rename, duplicate, archive, and restore actions.

### 12.3 New Project Wizard

The MVP wizard includes:

1. Project name and Novel selection.
2. Goal, premise, audience, language, approximate length, tone, and constraints.
3. Optional Bible, outline, chapters, notes, and source files.
4. Automation mode and review points.
5. Budget and active model settings with automatic defaults.
6. Summary and start.

Advanced settings remain collapsed by default.

### 12.4 Current Project Screen

The project screen combines the essential project functions into one view with four sections:

* Overview;
* Plan and Sources;
* Manuscript;
* Activity and Reviews.

### 12.5 Overview Section

Shows:

* project objective;
* current stage;
* progress;
* next action;
* word count;
* total cost;
* warnings;
* start, pause, resume, and cancel controls.

### 12.6 Plan and Sources Section

Provides:

* current approved production plan;
* Bible and outline status;
* imported sources;
* source role;
* add or replace source;
* approve planning milestone when required.

Previous versions remain stored but do not require a dedicated version-management screen in the MVP.

### 12.7 Manuscript Section

Provides:

* chapter list and status;
* current chapter content;
* basic editing;
* approve;
* reject;
* regenerate;
* view previous versions through a simple history list;
* export manuscript.

Advanced visual comparison, side-by-side diff, and content locking UI are deferred. The backend still preserves immutable versions.

### 12.8 Activity and Reviews Section

Provides a concise combined view of:

* current Skill or Job;
* completed and queued steps;
* failures and retries;
* review reason;
* system recommendation;
* approve, edit, regenerate, or ignore once;
* current tokens and cost.

A full log viewer, audit viewer, detailed cost dashboard, and standalone run monitor are deferred.

### 12.9 Settings Screen

Provides:

* API keys for configured providers;
* default provider;
* provider and model mapping per Skill;
* fallback mapping for critical Skills;
* default budget;
* default automation mode;
* local storage and backup settings.

Provider routing is controlled entirely through configuration. Changing the provider used by any Skill requires changing one configuration line, without modifying business logic or pipeline code.

## 13\. Functional Requirements

### 13.1 Project Management

The user can:

* create;
* rename;
* duplicate;
* archive;
* restore;
* import;
* export an entire project package;
* permanently delete only after explicit confirmation.

### 13.2 Source Management

The system can:

* import DOCX, PDF, TXT, Markdown, EPUB, and supported image files;
* preserve original files;
* extract text and metadata;
* create versioned replacements;
* tag and classify sources;
* mark a source as authoritative, reference-only, inspiration, or prohibited imitation.

### 13.3 Planning

The system can:

* classify the project;
* detect missing information;
* generate a complete production plan;
* estimate length and cost;
* generate project-specific planning assets;
* revise the plan without deleting earlier versions.

### 13.4 Generation

The system can:

* generate complete books incrementally;
* maintain target length;
* use unit briefs;
* preserve style rules;
* avoid banned content;
* use approved sources;
* regenerate selected units without rerunning the whole project.

### 13.5 Editing

The system can:

* identify structural, literary, factual, technical, continuity, and language problems;
* distinguish mandatory corrections from optional suggestions;
* apply revisions;
* compare before and after;
* limit rewrite loops;
* escalate unresolved conflicts.

### 13.6 Continuity and Consistency

The system can detect:

* contradictions;
* timeline conflicts;
* location conflicts;
* character inconsistency;
* unresolved plot setup;
* terminology drift;
* repeated content;
* broken references;
* unsupported claims;
* inconsistent code or technical versions.

### 13.7 Cost Control

The user can define:

* project budget;
* run budget;
* provider preference;
* quality versus cost priority;
* stop threshold;
* warning threshold.

The system records estimated and actual costs per provider, model, Skill, Job, Run, and Project.

### 13.8 Export

The system can export:

* full manuscript;
* selected chapters;
* planning documents;
* review reports;
* project archive;
* DOCX;
* EPUB;
* PDF;
* Markdown.

\---

## 14\. Error Handling

### 14.1 Retry Policy

Errors are classified as:

* temporary provider error;
* rate limit;
* timeout;
* invalid structured output;
* context limit;
* safety refusal;
* authentication error;
* budget limit;
* local storage error;
* validation failure;
* unrecoverable content conflict.

Each category has a configurable response.

### 14.2 Automatic Recovery

Possible recovery actions:

* retry same model;
* retry with adjusted parameters;
* split context;
* use fallback model;
* re-run validation;
* restore last checkpoint;
* pause for user action.

### 14.3 Critical Failures

The system must stop and request action when:

* API credentials are invalid;
* the configured budget is exhausted;
* local storage is unavailable;
* an authoritative source conflict cannot be resolved;
* all fallbacks fail;
* continuing may corrupt project history.

\---

## 15\. Security and Privacy

* API keys are stored locally using operating-system secure storage where available.
* Keys are never written to project files or logs.
* Project data remains local unless sent to a configured provider.
* Before using a provider, the system shows which data categories may be transmitted.
* Logs redact secrets.
* Project exports exclude API keys and private global settings.
* The user may disable selected providers for sensitive projects.
* Local backups are configurable.

\---

## 16\. Storage Architecture

### 16.1 Initial Implementation

* SQLite for metadata and structured records.
* Local filesystem for documents and large outputs.
* Markdown or JSON for portable configuration and selected human-readable artifacts.

### 16.2 Abstraction Rule

Business logic does not depend directly on SQLite or filesystem paths.

Storage is accessed through repositories and adapters so that future implementations may use PostgreSQL, object storage, a vector database, or another solution.

### 16.3 Project Package

A project can be exported as a portable package containing:

* project metadata;
* source references or copies;
* configuration snapshots;
* knowledge snapshots;
* manuscript versions;
* reviews;
* run history;
* exports;
* checksums and manifest.

\---

## 17\. Core Data Entities

All primary entities use UUIDs.

### 17.1 MVP Entities

* Workspace.
* Project.
* SourceAsset.
* AssetVersion.
* KnowledgeDocument.
* KnowledgeEntity.
* KnowledgeSnapshot.
* SkillVersion.
* PipelineVersion.
* Run.
* Job.
* JobAttempt.
* OutputVersion.
* ReviewRequest.
* ReviewDecision.
* PromptVersion.
* ProviderConfiguration.
* ModelConfiguration.
* UsageRecord.
* CostRecord.
* Export.
* AuditEvent.
* ProjectSetting.
* GlobalSetting.

`KnowledgeEntity` supports only Character, Location, Object, and TimelineEvent in the Novel MVP.

Separate definition and version tables may be used where technically necessary, but the MVP must avoid duplicating entities that can be represented safely through versioned records. Rich `KnowledgeLink`, generic `ProjectType`, and advanced provider-management entities are deferred until their related functionality is implemented.

\---

## 18\. API and Service Boundaries

The local application exposes an internal API used by the web UI.

Primary service areas:

* Projects.
* Sources.
* Planning.
* Pipelines.
* Runs.
* Jobs.
* Reviews.
* Manuscript.
* Knowledge.
* Providers.
* Skills.
* Costs.
* Exports.
* Settings.

Long-running work is executed by a background worker and persists independently of the browser session.

\---

## 19\. Non-Functional Requirements

### 19.1 Reliability

* A system restart must not lose completed work.
* Every long-running operation must have checkpoints.
* Jobs must be idempotent where possible.
* Partial provider responses must not be accepted as successful without validation.

### 19.2 Performance

* Dashboard loads within two seconds for normal local projects.
* Project navigation remains responsive while Jobs run.
* Large manuscripts are loaded by section rather than as one UI document.

### 19.3 Maintainability

* Provider adapters are isolated.
* Prompts are versioned outside core code.
* Skills are configurable.
* Project templates are data-driven.
* Automated tests cover pipeline state transitions and recovery.

### 19.4 Portability

The first supported environment is Windows desktop using a local web application. The architecture should remain portable to macOS and Linux.

\---

## 20\. MVP Definition

The MVP is complete when the user can:

1. Create a Novel project.
2. Enter a short brief and optional Bible or outline.
3. Select an automation mode.
4. Start a run.
5. Have the system automatically create planning materials if missing.
6. Generate chapters sequentially.
7. Run literary editing, rewriting, continuity, and language review.
8. Update project knowledge after approved chapters.
9. Pause and resume without losing state.
10. View costs and failures.
11. Review and edit chapters.
12. Export the complete manuscript to DOCX and EPUB.

### 20.1 MVP Technical Limits

* Single user.
* Local filesystem.
* SQLite.
* No cloud synchronization.
* OpenAI, Anthropic, Google Gemini, and DeepSeek provider adapters are supported.
* Provider and model selection are configured per Skill.
* Changing the provider for a Skill requires changing one configuration line only.
* Novel Studio first.
* Other project types implemented after the Novel workflow is proven, while preserving the generic core interfaces.

\---

## 21\. Development Order

### Phase 1 — Stable Foundation

* Finalize domain schema.
* Project and source storage.
* Provider interface and registry.
* OpenAI, Anthropic, Google Gemini, and DeepSeek adapters.
* Skill-based provider and model routing through configuration.
* Configurable cross-provider fallback for critical Skills.
* Prompt and Skill versioning.
* Run and Job engine.
* Background worker.
* Audit and cost records.

### Phase 2 — Novel Studio MVP

* New Project wizard.
* Planning pipeline.
* Story Bible and outline generation.
* Chapter brief generation.
* Chapter writing.
* Literary review.
* Rewrite.
* Continuity check.
* Language check.
* Knowledge update.
* Manuscript view.

### Phase 3 — Reliability

* Resume and recovery.
* Provider retry and fallback reliability.
* Capability and cost-aware routing validation.
* Budget controls.
* Version comparison.
* Review workflows.
* Whole-book quality pass.

### Phase 4 — Export

* DOCX.
* EPUB.
* PDF.
* Project package.

### Phase 5 — Additional Book Types

* Non-fiction.
* Practical and technical guides.
* Children’s books.
* Personal development.
* Custom templates.

\---

## 22\. Acceptance Scenario

The following scenario must work end to end:

1. User creates a project named “New Gothic Romance”.
2. User selects Novel, English, dark gothic romance, target audience women aged 20–40, approximately 80,000 words.
3. User provides a two-paragraph premise and no outline.
4. User selects Autonomous mode with review after the planning stage and final manuscript only.
5. System creates commercial positioning, characters, Bible, plot structure, and chapter plan.
6. User approves the plan.
7. System writes the entire book chapter by chapter.
8. Every chapter passes editing, rewriting, continuity, and language checks.
9. Approved chapter knowledge is added to the project memory.
10. The system performs a whole-book review and final revision.
11. User receives a complete manuscript, production report, total cost, and DOCX/EPUB exports.
12. All intermediate versions and logs remain available.

\---

## 22.1 MVP Simplification Decisions

The following decisions override broader version 1 requirements where they conflict:

* The MVP supports OpenAI, Anthropic, Google Gemini, and DeepSeek through isolated adapters.
* Each Skill may use a different configured provider and model. Changing the provider for a Skill requires changing one configuration line only.
* Critical Skills may define cross-provider fallback through configuration.
* The Novel knowledge system is limited to Bible, outline, chapter summaries, continuity facts, source excerpts, and four entity types.
* Semantic search, embeddings, a relationship graph, and generic project-type knowledge schemas are deferred.
* The MVP UI is limited to Projects, Current Project, and Settings, with essential project functions combined into those screens.
* Advanced administration, visualization, comparison, audit, cost, provider, Skill, Template, and Run Monitor screens are deferred.
* Immutable versioning, recovery, cost recording, and audit data remain backend requirements even when they do not have dedicated MVP screens.

## 23\. Final Product Rule

Every future feature must be evaluated against the primary objective:

> Does this help the system produce a complete, high-quality book with less user intervention, greater reliability, or lower cost?

Features that do not materially support this objective are deferred until the core production engine is proven.

