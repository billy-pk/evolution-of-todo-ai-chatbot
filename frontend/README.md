# Frontend Setup - Phase 2 Todo Application

This is the frontend for the full-stack todo application built with Next.js, React, and TailwindCSS with Better Auth for authentication.

## Tech Stack
- Next.js 16+ (App Router)
- React 19+
- TypeScript
- TailwindCSS
- Better Auth

## Setup Instructions

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
# or
pnpm install
```

### 3. Environment Configuration
Create a `.env.local` file based on `.env.local.example`:
```bash
cp .env.local.example .env.local
```

Update the `.env.local` file with your actual configuration:
- `NEXT_PUBLIC_API_URL`: Your backend API URL (e.g., http://localhost:8000)
- `BETTER_AUTH_SECRET`: Same secret as backend for JWT validation

### 4. Start Development Server
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Frontend will be available at: http://localhost:3000

## Project Structure
- `app/`: Next.js App Router pages and layouts
- `components/`: Reusable UI components
- `lib/`: API client, auth configuration, and utilities
- `public/`: Static assets

## Key Features
- Authentication with Better Auth
- Task management (CRUD operations)
- Responsive UI with TailwindCSS
- JWT-based authentication flow

## Common Commands
```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Integration with Backend
This frontend communicates with the backend API at the configured `NEXT_PUBLIC_API_URL`. All authenticated requests automatically include the JWT token in the Authorization header.

## Responsive Design Testing (T075-T076)

The application is fully responsive and should be tested across different viewport sizes to ensure proper layout adaptation.

### Mobile Viewport Testing (T075)
Test the application on mobile devices and small screens (320px - 768px width):

**Browser DevTools Method:**
1. Open Chrome/Firefox DevTools (F12)
2. Click the device toolbar icon (Toggle device toolbar)
3. Select a mobile device preset or set custom dimensions:
   - **320px** - iPhone SE (smallest supported)
   - **375px** - iPhone 12/13
   - **390px** - iPhone 14 Pro
   - **414px** - iPhone 14 Plus
   - **768px** - iPad portrait

**What to verify on mobile:**
- ✅ Navbar shows hamburger menu (instead of full navigation)
- ✅ TaskForm inputs and buttons stack vertically
- ✅ TaskItem buttons stack vertically
- ✅ Text sizes are legible (smaller responsive sizes apply)
- ✅ Touch targets are at least 44x44px
- ✅ No horizontal scrolling
- ✅ Content padding adapts (p-3, p-4)

### Desktop Viewport Testing (T076)
Test the application on desktop screens (768px - 2560px width):

**Browser DevTools Method:**
1. Open Chrome/Firefox DevTools (F12)
2. Set responsive mode with custom dimensions:
   - **1024px** - Small laptop
   - **1440px** - Standard desktop
   - **1920px** - Full HD
   - **2560px** - 2K/QHD

**What to verify on desktop:**
- ✅ Navbar shows full navigation (no hamburger menu)
- ✅ TaskForm inputs and buttons are side-by-side
- ✅ TaskItem buttons are side-by-side
- ✅ Text sizes are larger and more readable
- ✅ Layout uses available space efficiently
- ✅ Content is centered with max-width constraints
- ✅ Padding and spacing are generous (p-4, p-6)

### Responsive Breakpoints
The application uses TailwindCSS breakpoints:
- `sm:` - 640px and up
- `md:` - 768px and up
- `lg:` - 1024px and up
- `xl:` - 1280px and up
- `2xl:` - 1536px and up

### Testing Checklist
- [ ] Test on real mobile device (iOS/Android)
- [ ] Test on tablet (iPad/Android tablet)
- [ ] Test on desktop browser (Chrome, Firefox, Safari)
- [ ] Verify all interactive elements are accessible via touch
- [ ] Verify all text is readable at all sizes
- [ ] Test orientation changes (portrait ↔ landscape)
- [ ] Verify no content overflow or clipping
