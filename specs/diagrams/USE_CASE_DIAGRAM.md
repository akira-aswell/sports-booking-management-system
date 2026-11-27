# Use case overview (actor-to-use-case map)

Mermaid flowchart notation is used for portability; this is a use-case overview rather than a formal UML diagram.

```mermaid
flowchart LR
 V[Visitor] --> A([UC-001 Register])
 V --> S([UC-003 Discover courts])
 V --> AV([UC-006 Availability])
 P[Player] --> L([UC-002 Authenticate])
 P --> B([UC-007 Create booking])
 P --> BC([UC-009 Cancel / reschedule])
 P --> PAY([UC-010 Demo payment])
 P --> TM([UC-012 Manage team])
 P --> REG([UC-013 Register team])
 O[Owner] --> CM([UC-004 Manage court])
 O --> OH([UC-005 Hours / maintenance])
 O --> REV([UC-008 Review booking])
 O --> PAY
 ORG[Organizer] --> REG
 ORG --> FIX([UC-014 Fixtures / scheduling])
 ORG --> SC([UC-015 Results / standings])
 AD[Admin] --> CAT([UC-016 Catalog])
 AD --> UA([UC-017 User admin])
 P --> N([UC-011 Notifications])
 O --> N
 ORG --> N
 AD --> N
```

Admin may also perform explicitly authorized operations in individual use cases. The diagram omits repeated login associations for readability; the access matrix defines precise permissions.
