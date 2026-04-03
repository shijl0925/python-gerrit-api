Second-round design optimization recommendations
===============================================

This note captures a deeper, design-level review of the current client structure.
The recommendations below are ordered by priority so they can be used as a follow-up
roadmap for larger refactors.

Priority 1
==========

Split resource handles from resource snapshots
----------------------------------------------

Many objects currently combine two roles at once:

* an operation entry point that can call additional Gerrit APIs
* a mutable container for data returned by one specific request

Because object construction often triggers a remote fetch, object lifecycle and data
hydration are tightly coupled. A future refactor should separate:

* **resource handles** for performing actions against Gerrit
* **resource snapshots** for representing a response payload at a point in time

This would reduce constructor side effects, make object state easier to reason about,
and avoid repeated tension between direct hydration and ``poll()``-driven refresh.

Consolidate error translation into shared layers
------------------------------------------------

``Requester`` already maps HTTP status codes to a common exception hierarchy, but many
resource modules still translate low-level request failures again in local ``try`` /
``except`` blocks.

A cleaner design is to define two explicit layers:

* **transport error translation** in the shared requester layer
* **domain error translation** only where a resource-specific exception is truly needed

This would remove duplicated status handling, keep exception semantics consistent
across modules, and make resource code more focused on Gerrit behavior instead of
request mechanics.

Standardize collection and entity return contracts
--------------------------------------------------

The current API mixes return styles:

* some ``list()`` and ``get()`` methods return raw ``dict`` / ``list`` data
* some return resource objects
* some perform an initial lookup and then construct an object that fetches again

The design should define a stable contract:

* collection objects are responsible for lookup and construction
* entity objects are responsible for operations on a single resource
* each method family should consistently return either raw data or typed objects

This would improve predictability for users and simplify testing because the same
method shape would not produce different object models in different modules.

Priority 2
==========

Introduce clearer data boundaries
---------------------------------

Large parts of the codebase use ``Any`` for method returns and attach response fields
to objects dynamically. That keeps the API flexible, but it also weakens static
analysis and makes response-shape regressions harder to catch.

An incremental improvement would be to add ``TypedDict`` definitions or lightweight
DTO-style models for the main resource families first, especially:

* changes
* projects
* reviewers
* accounts

This would make the data model more explicit without requiring an all-at-once rewrite.

Centralize endpoint and identifier encoding rules
-------------------------------------------------

Most endpoints are currently assembled through ad-hoc string concatenation, and
identifier encoding rules are spread across modules. That increases the chance of
inconsistent behavior for projects, changes, accounts, refs, and file paths.

The client should eventually expose shared helpers for:

* endpoint path construction
* resource identifier encoding
* query parameter normalization

This would reduce duplication and make URI handling easier to audit and extend.

Priority 3
==========

Evolve top-level client accessors into stable service facades
-------------------------------------------------------------

``GerritClient`` currently constructs fresh service objects for ``projects``,
``changes``, ``accounts``, ``groups``, and related accessors on each property access.
The current cost is small, but the pattern makes it harder to attach shared behavior
later, such as caching, instrumentation, or configurable policies.

Over time, these accessors should move toward stable service facade objects that can
own shared concerns while preserving the same high-level client experience.

Recommended follow-up for a third round
======================================

The next documentation round should focus on two more concrete design artifacts:

* an object-model refactoring roadmap
* an exception and return-value consistency specification
