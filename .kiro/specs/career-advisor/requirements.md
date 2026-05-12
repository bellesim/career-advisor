# Requirements Document

## Introduction

Career Advisor is an AI-powered web application that analyzes the gap between a candidate's current qualifications and a target role. The system accepts a resume and job description, conducts pre-analysis with clarifying questions, and produces structured reports including fit scores, gap analysis, strengths identification, and actionable 90-day improvement plans.

## Glossary

- **Career_Advisor**: The complete web application system
- **Resume_Parser**: Component that extracts structured data from resume files
- **JD_Parser**: Component that extracts structured data from job descriptions
- **Analysis_Engine**: AI-powered component using AWS Strands ReACT agent for gap analysis
- **Fit_Scorer**: Component that calculates fit scores across five categories
- **Report_Generator**: Component that produces structured analysis reports
- **Action_Plan_Generator**: Component that creates 90-day improvement plans
- **Auth_Service**: Supabase-based authentication service
- **Storage_Service**: Supabase storage for resumes and reports
- **Guest_User**: Unauthenticated user with session-based access (24-hour expiry)
- **Authenticated_User**: User with persistent account and saved reports
- **Fit_Score**: Numerical score (0-100) representing alignment between candidate and role
- **Gap_Category**: Classification of gaps as Critical, Moderate, or Nice-to-have
- **Sprint**: 30-day period within the 90-day action plan
- **Track**: One of three parallel improvement areas (Skills, Experience, Credentials)

## Requirements

### Requirement 1: Resume Upload and Parsing

**User Story:** As a candidate, I want to upload my resume in multiple formats, so that the system can analyze my qualifications.

#### Acceptance Criteria

1. THE Resume_Parser SHALL accept PDF format resume files
2. THE Resume_Parser SHALL accept DOCX format resume files
3. WHEN a resume file exceeds 10MB, THE Career_Advisor SHALL reject the upload with a descriptive error message
4. WHEN a valid resume is uploaded, THE Resume_Parser SHALL extract structured data including skills, experience, education, and credentials
5. WHEN resume parsing fails, THE Career_Advisor SHALL return an error message indicating the parsing failure reason
6. THE Storage_Service SHALL store uploaded resume files securely
7. FOR ALL valid resumes, parsing the resume then formatting it back SHALL preserve all extracted structured data (round-trip property)

### Requirement 2: Job Description Input

**User Story:** As a candidate, I want to provide job descriptions through multiple input methods, so that I can analyze any target role.

#### Acceptance Criteria

1. THE JD_Parser SHALL accept job descriptions as plain text input
2. THE JD_Parser SHALL accept job descriptions from uploaded files
3. THE JD_Parser SHALL accept job descriptions from URLs
4. WHEN a URL is provided, THE Career_Advisor SHALL fetch the job description content from the URL
5. WHEN URL fetching fails, THE Career_Advisor SHALL return an error message with the failure reason
6. WHEN a valid job description is provided, THE JD_Parser SHALL extract structured requirements including required skills, experience level, education, and responsibilities
7. FOR ALL valid job descriptions, parsing then formatting SHALL preserve all extracted structured requirements (round-trip property)

### Requirement 3: Pre-Analysis Clarifying Questions

**User Story:** As a candidate, I want the system to ask clarifying questions before analysis, so that the report is more accurate and personalized.

#### Acceptance Criteria

1. WHEN resume and job description are provided, THE Analysis_Engine SHALL generate up to 3 clarifying questions
2. THE Analysis_Engine SHALL generate questions that address ambiguities or missing information
3. THE Career_Advisor SHALL present clarifying questions to the user before generating the report
4. WHEN the user provides answers, THE Analysis_Engine SHALL incorporate the answers into the analysis
5. WHEN the user skips questions, THE Analysis_Engine SHALL proceed with analysis using available information

### Requirement 4: Fit Score Calculation

**User Story:** As a candidate, I want to see numerical fit scores across multiple categories, so that I can understand my alignment with the target role.

#### Acceptance Criteria

1. THE Fit_Scorer SHALL calculate an overall fit score between 0 and 100
2. THE Fit_Scorer SHALL calculate a Software & Technical Skills score with 30% weight
3. THE Fit_Scorer SHALL calculate a Domain Knowledge score with 20% weight
4. THE Fit_Scorer SHALL calculate an Experience Depth & Seniority score with 25% weight
5. THE Fit_Scorer SHALL calculate a Credentials & Education score with 10% weight
6. THE Fit_Scorer SHALL calculate a Soft Skills & Leadership score with 15% weight
7. THE Fit_Scorer SHALL compute the overall score as the weighted sum of category scores
8. FOR ALL valid inputs, the overall score SHALL equal the sum of (category_score × category_weight)
9. FOR ALL category scores, the score SHALL be between 0 and 100 inclusive
10. FOR ALL overall scores, the score SHALL be between 0 and 100 inclusive

### Requirement 5: Gap Analysis

**User Story:** As a candidate, I want to see a structured analysis of my qualification gaps, so that I know what areas need improvement.

#### Acceptance Criteria

1. THE Analysis_Engine SHALL classify each identified gap as Critical, Moderate, or Nice-to-have
2. THE Analysis_Engine SHALL identify gaps in technical skills
3. THE Analysis_Engine SHALL identify gaps in domain knowledge
4. THE Analysis_Engine SHALL identify gaps in experience level
5. THE Analysis_Engine SHALL identify gaps in credentials and education
6. THE Analysis_Engine SHALL identify gaps in soft skills
7. WHEN a gap is classified as Critical, THE Report_Generator SHALL include it in the Critical Gaps section
8. WHEN a gap is classified as Moderate, THE Report_Generator SHALL include it in the Moderate Gaps section
9. WHEN a gap is classified as Nice-to-have, THE Report_Generator SHALL include it in the Nice-to-have Gaps section
10. FOR ALL identified gaps, each gap SHALL be assigned to exactly one category (Critical, Moderate, or Nice-to-have)

### Requirement 6: Strengths Identification

**User Story:** As a candidate, I want to see my strengths relative to the target role, so that I can leverage them in my application.

#### Acceptance Criteria

1. THE Analysis_Engine SHALL identify candidate strengths that align with job requirements
2. THE Analysis_Engine SHALL identify candidate strengths that exceed job requirements
3. THE Report_Generator SHALL include a Strengths section in the report
4. THE Report_Generator SHALL provide specific examples for each identified strength
5. WHEN no strengths are identified, THE Report_Generator SHALL include a message indicating limited alignment

### Requirement 7: 90-Day Action Plan Generation

**User Story:** As a candidate, I want a structured 90-day action plan, so that I have a clear roadmap for improvement.

#### Acceptance Criteria

1. THE Action_Plan_Generator SHALL create a plan with exactly 3 sprints of 30 days each
2. THE Action_Plan_Generator SHALL organize actions into 3 tracks: Skills, Experience, and Credentials
3. WHEN generating the action plan, THE Action_Plan_Generator SHALL use Brave Search MCP to find relevant learning resources
4. THE Action_Plan_Generator SHALL include specific, actionable items for each sprint and track
5. THE Action_Plan_Generator SHALL prioritize actions based on gap criticality
6. FOR ALL generated action plans, the total duration SHALL equal 90 days
7. FOR ALL generated action plans, each sprint SHALL contain at least one action item
8. THE Action_Plan_Generator SHALL include resource links for each recommended action

### Requirement 8: Report Generation and Structure

**User Story:** As a candidate, I want a comprehensive structured report, so that I have all analysis results in one place.

#### Acceptance Criteria

1. THE Report_Generator SHALL produce a report containing all analysis sections
2. THE Report_Generator SHALL include the overall fit score in the report
3. THE Report_Generator SHALL include all five category scores in the report
4. THE Report_Generator SHALL include the gap analysis section in the report
5. THE Report_Generator SHALL include the strengths section in the report
6. THE Report_Generator SHALL include the 90-day action plan in the report
7. THE Report_Generator SHALL include metadata: candidate name, target role, analysis date
8. THE Report_Generator SHALL generate a unique report ID for each analysis
9. WHEN a report is generated, THE Storage_Service SHALL persist the report data

### Requirement 9: PDF Export

**User Story:** As a candidate, I want to download my report as a PDF, so that I can save and share it offline.

#### Acceptance Criteria

1. THE Career_Advisor SHALL generate a PDF version of any completed report
2. THE Career_Advisor SHALL include all report sections in the PDF
3. THE Career_Advisor SHALL maintain formatting and readability in the PDF
4. WHEN a user requests PDF download, THE Career_Advisor SHALL deliver the PDF file within 10 seconds
5. THE Career_Advisor SHALL include charts and visual elements in the PDF

### Requirement 10: Guest User Sessions

**User Story:** As a guest user, I want to use the system without creating an account, so that I can try it quickly.

#### Acceptance Criteria

1. THE Career_Advisor SHALL allow guest users to create reports without authentication
2. THE Career_Advisor SHALL create a session for each guest user
3. THE Career_Advisor SHALL store guest user reports for 24 hours
4. WHEN 24 hours elapse, THE Career_Advisor SHALL delete guest user session data
5. THE Career_Advisor SHALL provide a session identifier to guest users for accessing their reports
6. WHEN a guest user returns with a valid session identifier within 24 hours, THE Career_Advisor SHALL retrieve their reports

### Requirement 11: User Authentication

**User Story:** As a candidate, I want to create an account, so that I can save my reports permanently.

#### Acceptance Criteria

1. THE Auth_Service SHALL support email and password registration
2. THE Auth_Service SHALL support OAuth authentication providers
3. WHEN a user registers, THE Auth_Service SHALL create a persistent user account
4. WHEN a user logs in, THE Auth_Service SHALL verify credentials and create an authenticated session
5. THE Auth_Service SHALL enforce password complexity requirements: minimum 8 characters, at least one uppercase, one lowercase, one number
6. WHEN authentication fails, THE Auth_Service SHALL return a descriptive error message
7. THE Auth_Service SHALL support password reset functionality

### Requirement 12: Report Dashboard

**User Story:** As an authenticated user, I want to view all my saved reports, so that I can track my progress over time.

#### Acceptance Criteria

1. THE Career_Advisor SHALL display a dashboard listing all reports for authenticated users
2. THE Career_Advisor SHALL display report metadata: target role, creation date, overall fit score
3. THE Career_Advisor SHALL sort reports by creation date with most recent first
4. WHEN a user selects a report, THE Career_Advisor SHALL display the full report details
5. THE Career_Advisor SHALL allow users to delete their own reports
6. WHEN a user deletes a report, THE Career_Advisor SHALL remove the report from storage permanently

### Requirement 13: Shareable Report Links

**User Story:** As an authenticated user, I want to generate shareable links for my reports, so that I can share them with recruiters or mentors.

#### Acceptance Criteria

1. THE Career_Advisor SHALL generate a unique public URL for each report when sharing is enabled
2. THE Career_Advisor SHALL allow users to enable or disable sharing for each report
3. WHEN sharing is enabled, THE Career_Advisor SHALL make the report accessible via the public URL without authentication
4. WHEN sharing is disabled, THE Career_Advisor SHALL return an access denied error for the public URL
5. THE Career_Advisor SHALL allow users to revoke shared links at any time
6. WHEN a shared link is revoked, THE Career_Advisor SHALL immediately deny access to the public URL
7. THE Career_Advisor SHALL display view count for shared reports

### Requirement 14: Data Validation and Error Handling

**User Story:** As a user, I want clear error messages when something goes wrong, so that I can correct issues and proceed.

#### Acceptance Criteria

1. WHEN invalid input is provided, THE Career_Advisor SHALL return a descriptive error message indicating the validation failure
2. WHEN a required field is missing, THE Career_Advisor SHALL return an error message specifying the missing field
3. WHEN an unsupported file format is uploaded, THE Career_Advisor SHALL return an error message listing supported formats
4. WHEN a system error occurs, THE Career_Advisor SHALL log the error details for debugging
5. WHEN a system error occurs, THE Career_Advisor SHALL return a user-friendly error message without exposing internal details
6. THE Career_Advisor SHALL validate all user inputs before processing
7. FOR ALL error responses, the response SHALL include an error code and human-readable message

### Requirement 15: Performance and Scalability

**User Story:** As a user, I want fast report generation, so that I can get results quickly.

#### Acceptance Criteria

1. WHEN a report is requested, THE Career_Advisor SHALL generate the complete report within 60 seconds
2. WHEN clarifying questions are generated, THE Analysis_Engine SHALL return questions within 10 seconds
3. THE Career_Advisor SHALL support concurrent report generation for multiple users
4. THE Career_Advisor SHALL handle at least 100 concurrent users without performance degradation
5. WHEN the system is under load, THE Career_Advisor SHALL queue requests and process them in order

### Requirement 16: Data Privacy and Security

**User Story:** As a user, I want my resume and personal data to be secure, so that my privacy is protected.

#### Acceptance Criteria

1. THE Storage_Service SHALL encrypt all resume files at rest
2. THE Career_Advisor SHALL transmit all data over HTTPS
3. THE Career_Advisor SHALL not share user data with third parties without explicit consent
4. THE Auth_Service SHALL hash all passwords using a secure hashing algorithm
5. WHEN a user deletes their account, THE Career_Advisor SHALL permanently delete all associated data within 30 days
6. THE Career_Advisor SHALL implement role-based access control ensuring users can only access their own reports
7. WHEN accessing reports, THE Career_Advisor SHALL verify the requesting user has permission to view the report
