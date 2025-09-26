# Engineering Log Intelligence - Frontend

This is the Vue.js frontend application for the Engineering Log Intelligence System.

## 🚀 Features

- **Vue.js 3** with Composition API
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Vue Router** for navigation
- **Pinia** for state management
- **Axios** for API communication
- **Chart.js** for data visualization (coming soon)

## 🛠️ Development Setup

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3001`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## 📁 Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets
│   │   └── css/         # Global styles
│   ├── components/      # Vue components
│   │   ├── common/      # Reusable components
│   │   └── layout/      # Layout components
│   ├── router/          # Vue Router configuration
│   ├── stores/          # Pinia stores
│   ├── views/           # Page components
│   ├── App.vue          # Root component
│   └── main.js          # Application entry point
├── public/              # Public assets
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── README.md           # This file
```

## 🎨 Styling

This project uses **Tailwind CSS** for styling. Key features:

- **Utility-first** CSS framework
- **Custom color palette** for the application
- **Responsive design** with mobile-first approach
- **Custom components** and utilities
- **Dark mode support** (ready for implementation)

### Custom CSS Classes

- `.btn` - Button base styles
- `.btn-primary`, `.btn-secondary`, etc. - Button variants
- `.card` - Card component styles
- `.input` - Input field styles
- `.badge` - Badge component styles
- `.status-indicator` - Status indicator styles

## 🔧 State Management

The application uses **Pinia** for state management with the following stores:

- **Auth Store** - User authentication and authorization
- **System Store** - System health and status
- **Notification Store** - Application notifications

## 🧭 Navigation

The application uses **Vue Router** with the following routes:

- `/` - Redirects to dashboard
- `/dashboard` - Main dashboard
- `/logs` - Log analysis
- `/ab-testing` - A/B testing management
- `/monitoring` - System monitoring
- `/settings` - Application settings
- `/login` - User login

## 🔌 API Integration

The frontend communicates with the backend API through:

- **Axios** for HTTP requests
- **Automatic token refresh** for authentication
- **Error handling** with user-friendly messages
- **Loading states** for better UX

## 📱 Responsive Design

The application is fully responsive and works on:

- **Desktop** (1024px+)
- **Tablet** (768px - 1023px)
- **Mobile** (320px - 767px)

## 🚀 Deployment

The frontend is designed to be deployed on **Vercel** alongside the backend:

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

## 🧪 Testing

Testing setup (coming soon):

- **Unit tests** with Vitest
- **Component tests** with Vue Test Utils
- **E2E tests** with Playwright

## 📚 Learning Resources

For beginners learning Vue.js and frontend development:

- [Vue.js Official Guide](https://vuejs.org/guide/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)

## 🤝 Contributing

1. Follow the existing code style
2. Use meaningful commit messages
3. Test your changes thoroughly
4. Update documentation as needed

## 📄 License

MIT License - see LICENSE file for details
