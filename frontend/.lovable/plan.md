

# Stego-Hunter — Phase 1: Landing Page & Dashboard

## Overview
Building a premium cybersecurity platform for detecting steganographic malware. Phase 1 covers the app shell, landing page, and dashboard with a dark, high-tech aesthetic.

## Design System
- **Theme**: Deep dark mode (slate-950 base), glassmorphism cards with backdrop-blur
- **Colors**: Emerald green (safe/clean), Crimson red (threat/infected), Cyan/electric blue (primary actions & accents)
- **Typography**: Clean, modern, data-dense but breathable
- **Icons**: Lucide React throughout
- **Animations**: CSS-based smooth transitions for scanners, progress elements, and hover states

## Pages & Components

### 1. Landing Page (`/`)
- **Hero Section**: Bold headline about steganographic threats, animated mock terminal/scanner effect showing detection in action, two CTAs ("Start Scanning" → `/scan`, "View Documentation")
- **Threat Explainer**: Brief visual section explaining image & DNN steganography with icons
- **Features Grid**: 6 feature cards with glassmorphism styling — Image Scanning, DNN Analysis, Threat Neutralization, YARA Rules, Integrity Reports, Real-time Monitoring
- **Stats Bar**: Animated counters (e.g., "10M+ Images Scanned", "99.7% Detection Rate")
- **Footer**: Minimal with links

### 2. App Layout (Sidebar + Header)
- **Sidebar**: Collapsible dark sidebar with navigation to Dashboard, Image Scanner, DNN Analyzer, Neutralize, Reports, Admin
- **Header**: Top bar with sidebar trigger, search, and user avatar placeholder
- Active route highlighting using NavLink

### 3. Dashboard (`/dashboard`)
- **Metric Cards Row**: Total Scans, Threats Detected, Threats Neutralized, System Health — each with icon, value, and trend indicator
- **Recent Activity Table**: Mock data table showing recent scans with status badges (Clean/Infected/Pending)
- **Quick Action Cards**: Two prominent cards linking to Image Scanner and DNN Analyzer with descriptions and icons
- **Threat Distribution Chart**: Small donut or bar chart using Recharts showing threat types breakdown

### 4. Placeholder Pages
- Stub pages for `/scan`, `/dnn`, `/neutralize`, `/reports`, `/admin`, `/login`, `/register` with "Coming Soon" states
- Custom 404 page with cybersecurity theme

## Color Variables
Override the default theme with dark cybersecurity palette — slate-950 backgrounds, cyan-400 primary, emerald-500 safe, red-500 threat accents.

