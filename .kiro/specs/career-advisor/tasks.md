# Implementation Plan: Career Advisor

## Overview

This implementation plan breaks down the Career Advisor feature into discrete coding tasks following the 12-week development phases outlined in the design document. The system uses Next.js (TypeScript) for the frontend, FastAPI (Python) for the backend, AWS Strands ReACT agent for AI analysis, and Supabase for authentication, database, and storage.

## Tasks

- [ ] 1. Set up project infrastructure and core configuration
  - [x] 1.1 Initialize Next.js 14 frontend with TypeScript and Tailwind CSS
    - Create Next.js project with App Router
    - Configure TypeScript, ESLint, and Prettier
    - Set up Tailwind CSS with custom theme
    - _Requirements: Phase 1_
  
  - [x] 1.2 Initialize FastAPI backend with Python 3.11+
    - Create FastAPI project structure
    - Configure Pydantic for data validation
    - Set up CORS middleware
    - Configure environment variables
    - _Requirements: Phase 1_
  
  - [x] 1.3 Configure Supabase project and services
    - Create Supabase project (auth, database, storage)
    - Set up database schema with tables: users, sessions, resumes, job_descriptions, reports
    - Configure storage buckets for resumes and PDFs
    - Set up row-level security policies
    - Create database indexes
    - _Requirements: 11.1, 11.2, 16.1, 16.2, 16.6_
  
  - [~] 1.4 Set up development environment and tooling
    - Configure testing frameworks (Jest, fast-check, Playwright)
    - Set up CI/CD pipeline configuration
    - Create Docker compose for local development
    - _Requirements: Phase 1_

- [ ] 2. Implement file upload and session management
  - [~] 2.1 Create file upload API endpoint (POST /api/upload)
    - Implement multipart file upload handling
    - Validate file size (max 10MB) and format (PDF, DOCX)
    - Store files in Supabase Storage
    - Return session_id, resume_id, jd_id
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 2.1, 2.2, 2.3_
  
  - [ ]* 2.2 Write property tests for file upload validation
    - **Property 3: Resume parsing errors return messages**
    - **Property 43: Unsupported file formats return error messages**
    - **Validates: Requirements 1.5, 14.3**
  
  - [~] 2.3 Implement session management service
    - Create guest session creation logic
    - Create authenticated session creation logic
    - Implement session validation and expiration checking
    - Implement 24-hour cleanup job for expired guest sessions
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 2.4 Write property tests for session management
    - **Property 26: Guest session created for guest users**
    - **Property 27: Session ID provided to guests**
    - **Property 28: Valid session ID retrieves reports**
    - **Validates: Requirements 10.2, 10.5, 10.6**
  
  - [~] 2.5 Create frontend upload page component
    - Build resume file upload UI with drag-and-drop
    - Build job description input (text/file/URL tabs)
    - Implement client-side validation
    - Display upload progress and errors
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3_

- [~] 3. Checkpoint - Verify file upload and session creation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement resume and job description parsing
  - [~] 4.1 Create Resume Parser for PDF and DOCX files
    - Implement PDF parsing using PyPDF2
    - Implement DOCX parsing using python-docx
    - Extract skills, experience, education, credentials
    - Handle parsing errors gracefully
    - _Requirements: 1.1, 1.2, 1.4, 1.5_
  
  - [ ]* 4.2 Write property tests for resume parsing
    - **Property 1: Resume data round-trip preservation**
    - **Property 2: Resume parsing extracts required fields**
    - **Validates: Requirements 1.7, 1.4**
  
  - [ ]* 4.3 Write unit tests for Resume Parser
    - Test PDF parsing with 2-3 sample files
    - Test DOCX parsing with 2-3 sample files
    - Test corrupted file handling
    - Test files with missing sections
    - _Requirements: 1.4, 1.5_
  
  - [~] 4.4 Create Job Description Parser
    - Implement text input parsing
    - Implement file input parsing
    - Implement URL fetching and parsing
    - Extract required_skills, experience_level, education, responsibilities
    - Handle URL fetch failures with descriptive errors
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [ ]* 4.5 Write property tests for JD parsing
    - **Property 4: Job description data round-trip preservation**
    - **Property 5: Job description parsing extracts required fields**
    - **Property 6: URL fetch errors return messages**
    - **Validates: Requirements 2.7, 2.6, 2.5**
  
  - [ ]* 4.6 Write unit tests for JD Parser
    - Test text input parsing with 2-3 examples
    - Test file input parsing with 2-3 examples
    - Test URL input parsing with 2-3 examples
    - Test malformed input handling
    - _Requirements: 2.1, 2.2, 2.3, 2.6_
  
  - [~] 4.7 Create parsing API endpoint (POST /api/parse)
    - Invoke Resume Parser and JD Parser
    - Return structured resume_data and jd_data
    - Handle parsing errors with descriptive messages
    - _Requirements: 1.4, 1.5, 2.6_

- [~] 5. Checkpoint - Verify parsing functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement AWS Strands ReACT agent and tools
  - [~] 6.1 Set up AWS Strands ReACT agent configuration
    - Initialize AWS Strands SDK
    - Configure agent with tool definitions
    - Set up agent orchestration logic
    - _Requirements: Phase 3_
  
  - [~] 6.2 Implement extract_resume tool
    - Create tool that accepts resume_file_path
    - Return structured resume data (skills, experience, education, credentials)
    - Integrate with Resume Parser
    - _Requirements: 1.4_
  
  - [~] 6.3 Implement extract_jd tool
    - Create tool that accepts jd_text
    - Return structured JD data (required_skills, experience_level, education, responsibilities)
    - Integrate with JD Parser
    - _Requirements: 2.6_
  
  - [~] 6.4 Implement compute_category_score tool
    - Create tool that accepts category, resume_data, jd_data
    - Compute fit score (0-100) for specified category
    - Support all 5 categories with correct weights
    - Return score with reasoning
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  
  - [ ]* 6.5 Write property tests for scoring
    - **Property 9: Overall fit score range [0-100]**
    - **Property 10: Category scores range [0-100]**
    - **Property 11: Overall score weighted sum calculation**
    - **Validates: Requirements 4.1, 4.9, 4.7, 4.8**
  
  - [ ]* 6.6 Write unit tests for compute_category_score
    - Test weighted sum calculation with specific examples
    - Test edge cases (all zeros, all 100s)
    - Verify category weights sum to 1.0
    - _Requirements: 4.7, 4.8_
  
  - [~] 6.7 Implement generate_questions tool
    - Create tool that accepts resume_data and jd_data
    - Generate up to 3 clarifying questions
    - Focus on ambiguities or missing information
    - _Requirements: 3.1, 3.2_
  
  - [ ]* 6.8 Write property tests for question generation
    - **Property 7: Clarifying questions count bounded [0-3]**
    - **Validates: Requirements 3.1**
  
  - [~] 6.9 Integrate Brave Search MCP
    - Set up Brave Search MCP connection
    - Create brave_search tool wrapper
    - Implement search query construction for learning resources
    - Handle API failures gracefully with retry logic
    - _Requirements: 7.3, 7.8_
  
  - [~] 6.10 Implement build_report tool
    - Create tool that aggregates all analysis results
    - Structure report with all required sections
    - Generate unique report ID
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [ ]* 6.11 Write integration tests for AWS Strands agent
    - Test extract_resume tool with sample files
    - Test extract_jd tool with sample text
    - Test compute_category_score for each category
    - Test generate_questions with sample data
    - Test brave_search with sample queries
    - Test build_report with complete analysis data
    - Verify agent orchestration flow
    - _Requirements: Phase 3_

- [~] 7. Checkpoint - Verify agent tools functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement gap analysis and strengths identification
  - [~] 8.1 Create gap analysis logic in agent workflow
    - Classify gaps as Critical, Moderate, or Nice-to-have
    - Identify gaps in technical skills, domain knowledge, experience, credentials, soft skills
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ]* 8.2 Write property tests for gap analysis
    - **Property 12: Gap categories are valid**
    - **Property 13: Gaps correctly categorized in report**
    - **Property 14: Each gap has exactly one category**
    - **Validates: Requirements 5.1, 5.7, 5.8, 5.9, 5.10**
  
  - [~] 8.3 Create strengths identification logic in agent workflow
    - Identify strengths that align with job requirements
    - Identify strengths that exceed job requirements
    - Provide specific examples for each strength
    - Handle cases with no identified strengths
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 8.4 Write property tests for strengths identification
    - **Property 15: Each strength has examples**
    - **Validates: Requirements 6.4**

- [ ] 9. Implement 90-day action plan generation
  - [~] 9.1 Create action plan generator logic
    - Generate exactly 3 sprints of 30 days each
    - Organize actions into 3 tracks: Skills, Experience, Credentials
    - Prioritize actions based on gap criticality
    - Ensure each sprint has at least one action item
    - _Requirements: 7.1, 7.2, 7.5, 7.7_
  
  - [~] 9.2 Integrate Brave Search for learning resources
    - Use brave_search tool to find courses, certifications, articles
    - Include resource links for each recommended action
    - Handle search failures gracefully
    - _Requirements: 7.3, 7.8_
  
  - [ ]* 9.3 Write property tests for action plan
    - **Property 16: Action plan has 3 sprints of 30 days**
    - **Property 17: Each sprint has three tracks**
    - **Property 18: Action plan total duration is 90 days**
    - **Property 19: Each sprint has action items**
    - **Property 20: Action items have resources**
    - **Validates: Requirements 7.1, 7.2, 7.6, 7.7, 7.8**
  
  - [ ]* 9.4 Write unit tests for action plan generator
    - Test sprint structure generation
    - Test track organization
    - Test priority assignment
    - _Requirements: 7.1, 7.2, 7.5_

- [ ] 10. Implement clarifying questions API and workflow
  - [~] 10.1 Create questions API endpoint (POST /api/questions)
    - Invoke agent's generate_questions tool
    - Return up to 3 questions
    - Handle question generation within 10 seconds
    - _Requirements: 3.1, 3.2, 15.2_
  
  - [~] 10.2 Create frontend questions page component
    - Display clarifying questions
    - Collect user responses
    - Allow skipping questions
    - Submit answers to analysis endpoint
    - _Requirements: 3.3, 3.5_
  
  - [~] 10.3 Implement answer incorporation in analysis
    - Accept user answers in analysis request
    - Pass answers to agent as context
    - Proceed with analysis if questions skipped
    - _Requirements: 3.4, 3.5_
  
  - [ ]* 10.4 Write property tests for question workflow
    - **Property 8: User answers incorporated in analysis**
    - **Validates: Requirements 3.4**

- [~] 11. Checkpoint - Verify analysis workflow end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement report generation and storage
  - [~] 12.1 Create Report Generator service
    - Aggregate all analysis results into structured report
    - Include overall score, category scores, gaps, strengths, action plan
    - Include metadata: candidate_name, target_role, created_at
    - Generate unique report ID
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [ ]* 12.2 Write property tests for report generation
    - **Property 21: Report contains all required sections**
    - **Property 22: Report has all five category scores**
    - **Property 23: Report metadata fields present**
    - **Property 24: Report IDs are unique**
    - **Validates: Requirements 8.1, 8.3, 8.7, 8.8**
  
  - [~] 12.3 Create analysis API endpoint (POST /api/analyze)
    - Invoke agent for full analysis workflow
    - Store report in Supabase database
    - Return report_id
    - Complete analysis within 60 seconds
    - _Requirements: 8.9, 15.1_
  
  - [~] 12.4 Create report retrieval API endpoint (GET /api/report/:report_id)
    - Retrieve report from database
    - Enforce access control (user ownership or shared)
    - Return complete report data
    - _Requirements: 16.6, 16.7_
  
  - [ ]* 12.5 Write property tests for access control
    - **Property 47: Users can only access their own reports**
    - **Validates: Requirements 16.6, 16.7**

- [ ] 13. Implement PDF generation and export
  - [~] 13.1 Create PDF Generator service
    - Use reportlab or WeasyPrint for PDF generation
    - Include all report sections in PDF
    - Include charts and visual elements
    - Maintain formatting and readability
    - Optimize for file size
    - _Requirements: 9.1, 9.2, 9.3, 9.5_
  
  - [ ]* 13.2 Write property tests for PDF generation
    - **Property 25: PDF contains all report sections**
    - **Validates: Requirements 9.2**
  
  - [ ]* 13.3 Write unit tests for PDF Generator
    - Test PDF generation with complete report
    - Test PDF with charts
    - Test PDF with long action plans
    - _Requirements: 9.2, 9.3, 9.5_
  
  - [~] 13.4 Create PDF download API endpoint (GET /api/report/:report_id/pdf)
    - Generate PDF from report data
    - Cache generated PDFs (1 hour TTL)
    - Deliver PDF within 10 seconds
    - _Requirements: 9.4_
  
  - [~] 13.5 Add PDF download button to frontend report page
    - Trigger PDF generation and download
    - Display loading state during generation
    - Handle generation errors
    - _Requirements: 9.1, 9.4_

- [ ] 14. Implement frontend report display
  - [~] 14.1 Create report page component
    - Display overall fit score with visual gauge (using Recharts)
    - Show 5 category scores with breakdown
    - Render gap analysis sections (Critical/Moderate/Nice-to-have)
    - Display strengths section with examples
    - Show 90-day action plan with 3 sprints × 3 tracks
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [~] 14.2 Create data visualization components
    - Build fit score gauge component
    - Build category scores bar chart
    - Build action plan timeline component
    - Ensure accessibility compliance
    - _Requirements: 8.2, 8.3, 8.6_

- [~] 15. Checkpoint - Verify report generation and display
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement user authentication
  - [~] 16.1 Create authentication service using Supabase Auth
    - Implement email/password registration
    - Implement email/password login
    - Implement OAuth providers (Google, GitHub)
    - Implement password reset flow
    - _Requirements: 11.1, 11.2, 11.7_
  
  - [~] 16.2 Implement password validation
    - Enforce minimum 8 characters
    - Require at least one uppercase letter
    - Require at least one lowercase letter
    - Require at least one number
    - Return descriptive error for invalid passwords
    - _Requirements: 11.5_
  
  - [ ]* 16.3 Write property tests for authentication
    - **Property 29: User account created on registration**
    - **Property 30: Session created on login**
    - **Property 31: Password complexity enforced**
    - **Property 32: Authentication failures return error messages**
    - **Property 46: Passwords are hashed**
    - **Validates: Requirements 11.3, 11.4, 11.5, 11.6, 16.4**
  
  - [~] 16.4 Create frontend authentication pages
    - Build registration form with validation
    - Build login form (email/password and OAuth)
    - Build password reset form
    - Display authentication errors
    - _Requirements: 11.1, 11.2, 11.7_
  
  - [~] 16.5 Implement session verification middleware
    - Verify JWT tokens on protected routes
    - Handle token expiration and refresh
    - Redirect unauthenticated users
    - _Requirements: 11.4_

- [ ] 17. Implement report dashboard for authenticated users
  - [~] 17.1 Create dashboard API endpoint (GET /api/dashboard)
    - List all reports for authenticated user
    - Include report metadata: target_role, created_at, overall_score
    - Sort reports by created_at descending
    - Implement pagination
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ]* 17.2 Write property tests for dashboard
    - **Property 33: Dashboard reports have metadata**
    - **Property 34: Dashboard reports sorted by date**
    - **Validates: Requirements 12.2, 12.3**
  
  - [~] 17.3 Create frontend dashboard page component
    - Display list of saved reports
    - Show report metadata cards
    - Navigate to report details on click
    - Implement delete report functionality
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [~] 17.4 Create report deletion API endpoint (DELETE /api/report/:report_id)
    - Verify user ownership
    - Delete report from database
    - Delete associated files from storage
    - _Requirements: 12.5, 12.6_
  
  - [ ]* 17.5 Write property tests for report deletion
    - **Property 35: Deleted reports not retrievable**
    - **Validates: Requirements 12.6**

- [ ] 18. Implement report sharing functionality
  - [~] 18.1 Create share API endpoint (POST /api/share/:report_id)
    - Generate unique share_token (UUID)
    - Enable/disable sharing for report
    - Return public share URL
    - Verify user ownership
    - _Requirements: 13.1, 13.2, 13.5_
  
  - [ ]* 18.2 Write property tests for sharing
    - **Property 36: Shared reports have unique URLs**
    - **Property 37: Shared reports accessible without auth**
    - **Property 38: Non-shared reports deny public access**
    - **Property 39: Revoked links deny access immediately**
    - **Property 40: Shared reports track view count**
    - **Validates: Requirements 13.1, 13.3, 13.4, 13.6, 13.7**
  
  - [~] 18.3 Create public report access endpoint (GET /api/public/:share_token)
    - Retrieve report by share_token
    - Verify sharing is enabled
    - Increment view_count
    - Return report data without authentication
    - _Requirements: 13.3, 13.7_
  
  - [~] 18.4 Add sharing controls to frontend report page
    - Add enable/disable sharing toggle
    - Display share URL when enabled
    - Show view count
    - Add copy link button
    - Add revoke link button
    - _Requirements: 13.2, 13.5, 13.6, 13.7_

- [~] 19. Checkpoint - Verify authentication and sharing features
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Implement comprehensive error handling and validation
  - [~] 20.1 Create centralized error handling middleware
    - Define error response format with error_code and message
    - Log errors with appropriate levels
    - Sanitize error messages to avoid exposing internals
    - Include request_id for debugging
    - _Requirements: 14.4, 14.5, 14.7_
  
  - [~] 20.2 Implement input validation for all API endpoints
    - Validate file uploads (size, format)
    - Validate required fields
    - Validate data types and formats
    - Return descriptive validation errors
    - _Requirements: 14.1, 14.2, 14.3, 14.6_
  
  - [ ]* 20.3 Write property tests for error handling
    - **Property 41: Invalid inputs return error messages**
    - **Property 42: Missing required fields return specific errors**
    - **Property 44: System errors don't expose internals**
    - **Property 45: Error responses have code and message**
    - **Validates: Requirements 14.1, 14.2, 14.5, 14.7**
  
  - [~] 20.3 Implement retry logic for transient failures
    - Retry Brave Search API (3 times with exponential backoff)
    - Retry database queries (2 times with 1s delay)
    - Retry file uploads (2 times with 2s delay)
    - _Requirements: Phase 6_
  
  - [~] 20.4 Add error handling to frontend components
    - Display user-friendly error messages
    - Handle network errors gracefully
    - Implement error boundaries
    - _Requirements: 14.1, 14.2, 14.3_

- [ ] 21. Implement data security and privacy features
  - [~] 21.1 Configure Supabase row-level security policies
    - Users can only access their own reports
    - Users can only access their own resumes
    - Public access allowed for shared reports
    - _Requirements: 16.6, 16.7_
  
  - [~] 21.2 Implement HTTPS enforcement
    - Configure SSL/TLS for all endpoints
    - Redirect HTTP to HTTPS
    - _Requirements: 16.2_
  
  - [~] 21.3 Implement data encryption
    - Verify Supabase encrypts files at rest
    - Hash passwords using bcrypt (Supabase default)
    - _Requirements: 16.1, 16.4_
  
  - [~] 21.4 Implement account deletion with data purge
    - Delete user account
    - Delete all associated reports
    - Delete all associated files
    - Complete deletion within 30 days
    - _Requirements: 16.5_
  
  - [~] 21.5 Implement rate limiting
    - Limit file uploads: 10 per hour per IP
    - Limit analysis requests: 5 per hour per user
    - Limit API requests: 100 per minute per user
    - _Requirements: Phase 6_

- [ ] 22. Implement performance optimizations
  - [~] 22.1 Implement caching strategy
    - Cache generated PDFs (1 hour TTL)
    - Cache Brave Search results (24 hour TTL)
    - _Requirements: Phase 6_
  
  - [~] 22.2 Optimize database queries
    - Verify all indexes are created
    - Implement pagination for dashboard
    - Optimize JSONB queries
    - _Requirements: Phase 6_
  
  - [~] 22.3 Implement async processing for long-running tasks
    - Use background jobs for report generation
    - Provide progress updates via polling or WebSocket
    - _Requirements: 15.1, 15.3_

- [~] 23. Checkpoint - Verify security and performance
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 24. Write comprehensive integration tests
  - [ ]* 24.1 Write API integration tests
    - Test POST /api/upload with file upload and storage
    - Test POST /api/parse with parsers
    - Test POST /api/questions with agent
    - Test POST /api/analyze with full workflow
    - Test GET /api/report/:id with access control
    - Test GET /api/report/:id/pdf with PDF generation
    - Test GET /api/dashboard with sorting
    - Test POST /api/share/:id with URL generation
    - Test DELETE /api/report/:id with removal
    - _Requirements: Phase 6_
  
  - [ ]* 24.2 Write Supabase integration tests
    - Test user registration and login
    - Test OAuth authentication (mock provider)
    - Test file upload to storage
    - Test database CRUD operations
    - Test row-level security policies
    - _Requirements: Phase 6_

- [ ] 25. Write end-to-end tests
  - [ ]* 25.1 Write E2E test for guest user flow
    - Upload resume (PDF)
    - Provide job description (text)
    - Answer clarifying questions
    - View generated report
    - Download PDF
    - Return with session ID to view report
    - _Requirements: Phase 6_
  
  - [ ]* 25.2 Write E2E test for authenticated user flow
    - Register new account
    - Log in
    - Upload resume and JD
    - Complete analysis
    - View report in dashboard
    - Enable sharing
    - Access shared link (incognito mode)
    - Disable sharing
    - Verify shared link denied
    - Delete report
    - Verify report removed from dashboard
    - _Requirements: Phase 6_
  
  - [ ]* 25.3 Write E2E test for error handling
    - Upload oversized file (>10MB)
    - Upload unsupported format
    - Provide invalid URL for JD
    - Attempt to access another user's report
    - Attempt to access expired guest session
    - _Requirements: Phase 6_

- [ ] 26. Final integration and polish
  - [~] 26.1 Implement monitoring and logging
    - Set up Sentry for error tracking
    - Configure CloudWatch for Lambda metrics
    - Set up Vercel Analytics
    - Implement custom logging for analysis pipeline
    - _Requirements: Phase 6_
  
  - [~] 26.2 Create deployment configuration
    - Configure Vercel deployment for frontend
    - Configure AWS Lambda or Railway for backend
    - Set up environment variables for production
    - Configure database migrations
    - _Requirements: Phase 6_
  
  - [~] 26.3 Write project documentation
    - Create README with setup instructions
    - Document API endpoints
    - Document environment variables
    - Create deployment guide
    - _Requirements: Phase 6_
  
  - [~] 26.4 Perform security review
    - Review authentication implementation
    - Review authorization checks
    - Review input validation
    - Review error messages for information leakage
    - Run OWASP ZAP security scan
    - Run npm audit for vulnerabilities
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7_

- [~] 27. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property-based tests validate universal correctness properties from the design document
- The implementation follows a 12-week development plan with regular checkpoints
- Frontend uses Next.js 14 with TypeScript, backend uses FastAPI with Python 3.11+
- AWS Strands ReACT agent orchestrates the AI analysis workflow with 6 specialized tools
- Supabase provides unified authentication, database, and storage services
- All 47 correctness properties from the design document are covered by property-based tests
