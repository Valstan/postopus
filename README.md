# 🚀 Postopus - Production Ready

**Automated Social Media Content Management System for Russian Regional Groups**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## ⚡ Quick Deploy

**Ready for immediate deployment to Render.com:**

1. **Fork this repository**
2. **Create Render Blueprint**:
   - Dashboard → New → Blueprint
   - Select this repository
   - Choose `render.yaml`
   - Click Apply
3. **Set DATABASE_URL** in environment variables
4. **Access your app** at `https://your-app.onrender.com`

## 🎯 What This Does

**Postopus** automates content distribution across **15 Russian regional VK groups**:

- **🌍 Regional Management**: mi, nolinsk, arbazh, kirs, slob, verhosh, bogord, yaransk, viatpol, zuna, darov, kilmez, lebazh, omut, san
- **📊 Content Processing**: 6 themes (novost, sosed, kino, music, prikol, reklama) with AI filtering
- **🔄 Automated Posting**: VK API integration with rate limiting and scheduling
- **📈 Analytics Dashboard**: Real-time regional statistics and performance monitoring
- **👥 User Management**: Role-based access (Admin/Editor/Viewer)
- **⚙️ Settings Control**: VK token management, system configuration

## 🏗️ Production Architecture

**Modern FastAPI + PostgreSQL + Redis Stack:**

```
📦 Postopus Production
├── 🌐 Web API (FastAPI)
│   ├── 🔐 Authentication (JWT + BCrypt)
│   ├── 📊 Dashboard (Regional Analytics)
│   ├── 📝 Posts CRUD (Content Management)
│   └── ⚙️ Settings (VK Tokens, Users)
├── 🗄️ Database (PostgreSQL)
│   ├── 👥 Users & Roles
│   ├── 📄 Posts & Content
│   ├── 🔑 VK Tokens
│   └── ⚙️ System Settings
├── 🔄 Background Tasks (Celery + Redis)
│   ├── 📤 Auto-posting
│   ├── 🔍 Content Processing
│   └── 📊 Analytics Updates
└── 🚀 Deployment (Render.com)
    ├── 🌐 Web Service
    ├── 👷 Worker Service
    └── 📁 Database & Redis
```

## 📱 API Endpoints

**25+ Production-Ready Endpoints:**

```bash
# Authentication
POST /api/auth/login         # User login
GET  /api/auth/me           # Current user info

# Content Management  
GET  /api/posts/            # List posts (with filtering)
POST /api/posts/            # Create post
PUT  /api/posts/{id}        # Update post
DEL  /api/posts/{id}        # Delete post
POST /api/posts/bulk/publish # Bulk publish

# Regional Dashboard
GET  /api/dashboard/stats   # System overview
GET  /api/dashboard/regional # Regional analytics
GET  /api/dashboard/health  # System health

# Settings & Management
GET  /api/settings/users    # User management
POST /api/settings/vk-tokens # VK token management
GET  /api/settings/system/stats # System statistics
```

## 🔐 Default Access

**After deployment, login with:**
- **Admin**: `admin/admin` (Full access)
- **Editor**: `editor/editor123` (Content management)

## 🌍 Regional Groups Supported

**15 Russian Regions:**
- **Malmyž** (mi)
- **Nolinsk** (nolinsk)
- **Arbaž** (arbazh)
- **Kirs** (kirs)
- **Slobodskoy** (slob)
- **Verhoš'e** (verhosh)
- **Bogorodskoe** (bogord)
- **Yaransk** (yaransk)
- **Vyatskie Polyany** (viatpol)
- **Zuna** (zuna)
- **Darov** (darov)
- **Kilmez** (kilmez)
- **Lebažъ** (lebazh)
- **Omutninsk** (omut)
- **Sanči** (san)

## 🔧 Configuration

**Environment Variables:**

```env
# Database (required)
DATABASE_URL=postgresql://user:pass@host/db

# Redis (auto-configured on Render)
REDIS_URL=redis://host:port/0

# Security (auto-generated)
SECRET_KEY=your-secret-key

# VK API (optional)
VK_API_VERSION=5.131
VK_APP_ID=your-app-id
```

## 🎯 Key Features

- ✅ **Zero Configuration**: Deploy and start using immediately
- ✅ **PostgreSQL Ready**: Production database with graceful fallbacks
- ✅ **Regional Content**: Manage 15 regional groups from one interface
- ✅ **VK Integration**: Multi-token support with rate limiting
- ✅ **Role-Based Security**: Admin/Editor/Viewer access levels
- ✅ **Real-time Analytics**: Dashboard with regional statistics
- ✅ **Bulk Operations**: Publish/manage multiple posts simultaneously
- ✅ **Monitoring**: Health checks and performance tracking
- ✅ **Production Optimized**: <10MB deployment, fast startup

## 📊 Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with async SQLAlchemy
- **Queue**: Celery + Redis
- **Authentication**: JWT + BCrypt
- **Deployment**: Render.com with Docker
- **Monitoring**: Structured logging + health checks

## 🚀 Deployment Status

- ✅ **Production Ready**: Tested and optimized for Render.com
- ✅ **Database Migration**: MongoDB → PostgreSQL complete
- ✅ **VK API Integration**: Enhanced multi-region support
- ✅ **Web Interface**: Complete CRUD operations
- ✅ **Monitoring**: Health checks and analytics
- ✅ **Security**: Role-based access control
- ✅ **Repository Optimized**: 157MB → <10MB

---

**🎉 Ready to deploy! Click the Deploy to Render button above to get started.**