# Requirements Specification

## Document Information
- **Project:** {{project_name}}
- **Version:** {{version}}
- **Date:** {{date}}
- **Status:** {{status}}

## 1. Introduction

{{introduction}}

## 2. System Overview

{{system_overview}}

## 3. Requirements by Block

{{#each blocks}}
### 3.{{@index}}. {{block_name}}

{{block_description}}

#### Functional Requirements
| ID | Statement | Priority | V&V Method | Parent Need |
|----|-----------|----------|------------|-------------|
{{#each functional_requirements}}
| {{id}} | {{statement}} | {{priority}} | {{vv_method}} | {{parent_need}} |
{{/each}}

#### Performance Requirements
| ID | Statement | Priority | V&V Method | Parent Need |
|----|-----------|----------|------------|-------------|
{{#each performance_requirements}}
| {{id}} | {{statement}} | {{priority}} | {{vv_method}} | {{parent_need}} |
{{/each}}

#### Interface Requirements
| ID | Statement | Priority | V&V Method | Parent Need |
|----|-----------|----------|------------|-------------|
{{#each interface_requirements}}
| {{id}} | {{statement}} | {{priority}} | {{vv_method}} | {{parent_need}} |
{{/each}}

#### Constraint Requirements
| ID | Statement | Priority | V&V Method | Parent Need |
|----|-----------|----------|------------|-------------|
{{#each constraint_requirements}}
| {{id}} | {{statement}} | {{priority}} | {{vv_method}} | {{parent_need}} |
{{/each}}

#### Quality Requirements
| ID | Statement | Priority | V&V Method | Parent Need |
|----|-----------|----------|------------|-------------|
{{#each quality_requirements}}
| {{id}} | {{statement}} | {{priority}} | {{vv_method}} | {{parent_need}} |
{{/each}}

{{/each}}

## 4. TBD/TBR Items

{{tbd_tbr_table}}

## Appendix: Full Attribute Details

See JSON registries for complete INCOSE A1-A13 attributes.
