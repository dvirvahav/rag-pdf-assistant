# RAG PDF Assistant - Frontend

A modern, mobile-responsive React application that provides a ChatGPT-like interface for asking questions about PDF documents using Retrieval-Augmented Generation (RAG).

## 🚀 Features

- **📱 Mobile-First Design**: Fully responsive interface that works perfectly on all devices
- **📄 PDF Upload**: Drag-and-drop file upload with progress tracking
- **💬 ChatGPT-like Interface**: Familiar conversation interface with message bubbles
- **⚡ Real-time Updates**: Live status updates during document processing
- **🔄 Async Processing**: Non-blocking PDF processing with job status polling
- **🎨 Modern UI**: Clean, professional design with Tailwind CSS

## 🛠️ Tech Stack

- **React 19** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Lucide React** for icons

## 📋 Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see main project README)

## 🚀 Getting Started

### Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5173`

### Production Build

1. **Build for production:**
   ```bash
   npm run build
   ```

2. **Preview production build:**
   ```bash
   npm run preview
   ```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   │   ├── FileUpload.tsx      # PDF upload component
│   │   ├── UploadStatus.tsx    # Upload progress display
│   │   ├── Message.tsx         # Individual chat message
│   │   ├── MessageInput.tsx    # Message input field
│   │   └── ChatInterface.tsx   # Main chat container
│   ├── services/       # API services
│   │   └── api.ts             # Backend API client
│   ├── types/          # TypeScript type definitions
│   │   └── index.ts           # Shared types
│   ├── App.tsx         # Main application component
│   ├── main.tsx        # Application entry point
│   └── index.css       # Global styles with Tailwind
├── public/             # Static assets
├── .env.development    # Development environment variables
├── .env.production     # Production environment variables
├── Dockerfile          # Docker build configuration
├── nginx.conf          # Nginx configuration for production
├── package.json        # Dependencies and scripts
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

Create `.env.development` and `.env.production` files:

```env
# Development
VITE_API_URL=http://localhost:8000

# Production
VITE_API_URL=https://api.yourdomain.com
```

### Backend API

The frontend expects the following API endpoints:

- `POST /documents/upload` - Upload PDF file
- `GET /documents/job/{job_id}` - Check upload status
- `POST /query/ask` - Ask questions about processed documents

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Build production image
docker build -t rag-pdf-frontend .

# Run container
docker run -p 80:80 rag-pdf-frontend
```

### Using Docker Compose

Add to your main `docker-compose.yml`:

```yaml
frontend:
  build: ./frontend
  ports:
    - "3000:80"
  environment:
    - VITE_API_URL=http://backend:8000
  depends_on:
    - backend
```

## 📱 Mobile Responsiveness

The application is designed mobile-first with:

- **Responsive breakpoints**: Mobile (320px+), Tablet (768px+), Desktop (1024px+)
- **Touch-friendly interactions**: Large buttons, swipe gestures
- **Optimized layouts**: Single column on mobile, multi-column on larger screens
- **Performance**: Lazy loading, code splitting, optimized assets

## 🔍 Development Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

## 📄 License

MIT License - see the main project LICENSE file for details.
