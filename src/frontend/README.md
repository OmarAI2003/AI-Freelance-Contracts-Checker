# Frontend - User Interface

**Developer**: Developer 4 (Integration Lead)  
**Component**: Web Application  
**Timeline**: Day 4 (Oct 18, 2025)

---

## 📋 Overview

This folder contains the **Frontend Website** where freelancers interact with ContractGuard AI.

### Purpose
Simple, intuitive website for freelancers to upload contracts and receive AI-powered analysis.

### Key Features
- **Drag-and-drop upload**: PDF/DOCX contract files
- **Real-time progress**: Loading animation while agents work
- **Tabbed results view**:
  - Analysis (risks & scores)
  - Explanations (plain English)
  - Negotiation (counter-proposals)
  - Full Report (downloadable PDF)
- **Mobile responsive**: Works on all devices
- **Professional design**: Clean, trustworthy UI

---

## 🛠️ Technologies Used

- **HTML5 + CSS3**: Modern, responsive design
- **Vanilla JavaScript**: No framework dependencies
- **AWS S3**: Static website hosting
- **CloudFront**: Global CDN (optional)
- **API Gateway**: Backend integration

---

## 📁 Files (To Be Created)

- `index.html` - Main website page
- `styles.css` - CSS styling
- `app.js` - Frontend logic & API calls
- `assets/` - Images, icons, fonts
- `README.md` - Deployment instructions

---

## 🎨 Design

**Color Scheme**:
- Primary: #2563EB (blue - trust)
- Success: #10B981 (green - safe)
- Warning: #F59E0B (orange - caution)
- Danger: #EF4444 (red - reject)

**Layout**:
1. Hero section with upload form
2. Loading animation with agent status
3. Tabbed results display
4. Download full report button

---

## 🚀 Deployment

**Option 1**: AWS S3 + CloudFront
```bash
aws s3 sync . s3://contractguard-frontend --acl public-read
```

**Option 2**: Local testing
```bash
python -m http.server 8000
```

**Website URL**: `https://contractguard-frontend.s3.amazonaws.com/index.html`

---

## 📖 Documentation

See `/docs/DEV4_INTEGRATION.md` for frontend implementation details.
