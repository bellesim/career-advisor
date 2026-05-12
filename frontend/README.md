# Career Advisor Frontend

This is the frontend application for Career Advisor, an AI-powered web application that analyzes the gap between a candidate's qualifications and target job requirements.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Linting**: ESLint
- **Formatting**: Prettier

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm

### Installation

```bash
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### Building for Production

```bash
npm run build
npm start
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Run ESLint and fix issues
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages and layouts
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # Reusable React components (to be added)
├── lib/                   # Utility functions and helpers (to be added)
├── public/                # Static assets
├── .eslintrc.json        # ESLint configuration
├── .prettierrc.json      # Prettier configuration
├── tailwind.config.ts    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```
