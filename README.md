# Career Advisor

An AI-powered web application that analyzes the gap between a candidate's qualifications and target job requirements. The system provides comprehensive career guidance through resume analysis, job description parsing, AI-driven gap analysis, and actionable 90-day improvement plans.

## Project Structure

```
career-advisor/
├── frontend/              # Next.js 14 frontend application
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components (to be added)
│   └── ...
├── backend/              # FastAPI backend service (to be added)
└── .kiro/                # Kiro spec files
    └── specs/
        └── career-advisor/
```

## Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Linting**: ESLint + Prettier

### Backend (Planned)
- **Framework**: FastAPI
- **Language**: Python
- **AI**: AWS Strands ReACT Agent
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Authentication**: Supabase Auth

## Getting Started

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

For more details, see the [frontend README](./frontend/README.md).

## Features

- **Resume Upload**: Support for PDF and DOCX formats
- **Job Description Input**: Text, file upload, or URL
- **AI-Powered Analysis**: Gap analysis using AWS Strands ReACT agent
- **Fit Scoring**: Five-category scoring system
- **90-Day Action Plans**: Structured improvement roadmap
- **Guest & Authenticated Access**: Try without signup or save reports
- **PDF Export**: Download reports for offline use
- **Report Sharing**: Generate shareable links

## Development Status

✅ **Phase 1: Project Setup**
- [x] Initialize Next.js 14 frontend with TypeScript and Tailwind CSS

🔄 **Phase 2: Frontend Development** (In Progress)
- [ ] Create UI components
- [ ] Implement upload and input pages
- [ ] Build report display pages
- [ ] Add authentication flows

⏳ **Phase 3: Backend Development** (Planned)
- [ ] Set up FastAPI service
- [ ] Implement resume and JD parsers
- [ ] Configure AWS Strands ReACT agent
- [ ] Set up Supabase integration

⏳ **Phase 4: Integration & Testing** (Planned)
- [ ] Connect frontend to backend
- [ ] End-to-end testing
- [ ] Performance optimization

## License

Private project
