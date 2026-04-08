# Real Estate AI Platform with VR & Vastu Chatbot

A production-grade real estate platform featuring AI-powered recommendations, 360° virtual tours, advanced property search, and an intelligent Vastu Shastra chatbot.

## 🎯 Key Features

- **Smart Property Browsing**: Filter by location, BHK, property type, and budget
- **AI Recommendations**: Collaborative filtering for personalized property suggestions  
- **360° Virtual Tours**: Capture and view panoramic room images using WebRTC + OpenCV stitching
- **Vastu Chatbot**: NLP-powered guidance on Vastu Shastra with semantic matching and fallback suggestions
- **Property Submission**: Sellers can list properties with detailed information and 360° room images
- **Advanced Filtering**: Dynamic filter options based on available properties
- **Production-Grade Architecture**: Environment-based configuration, structured logging, error handling

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Django 6.0.3, DRF | Web framework & REST API |
| **Database** | SQLite3 | Data persistence |
| **Frontend** | HTML5, CSS3, Vanilla JS | UI/UX |
| **ML/AI** | scikit-learn, pandas | Recommendations & chatbot |
| **Image Processing** | OpenCV | 360° panorama stitching |
| **Configuration** | python-decouple | Environment management |
| **Logging** | Python logging | Structured application logs |

## 📁 Project Structure

```
real-estate-ai-project/
├── core/                           # Shared utilities & config
│   ├── constants.py               # Centralized constants (avoid hardcoding)
│   ├── exceptions.py              # Custom exception classes
│   └── logging_config.py          # Logging setup
├── EYproject/                      # Django project config
│   ├── settings.py                # Environment-based settings
│   ├── urls.py
│   └── wsgi.py
├── listings/                       # Property listings app
│   ├── models.py                  # Property model
│   ├── views.py                   # Listing API & pages
│   ├── serializers.py
│   └── management/
│       └── commands/
│           └── seed_properties.py
├── recommendation/                 # AI & Chatbot
│   ├── views.py                   # Recommendation & chat APIs
│   ├── vastu_chatbot.py          # NLP chatbot logic
│   ├── train_model.py            # ML model training
│   ├── vastu_data.json           # Q&A knowledge base
│   └── ml_model/
│       ├── predict.py            # ML inference
│       └── models/               # Serialized models (.pkl files)
├── templates/                      # Django HTML templates
├── static/                         # Frontend assets (CSS, JS)
├── logs/                          # Application logs
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── manage.py
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip & virtualenv

### Installation

1. **Clone & Navigate**
   ```bash
   cd real-estate-ai-project
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env  # Create your .env file
   # Edit .env with your settings
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py seed_properties  # Optional: seed sample data
   ```

6. **Run Server**
   ```bash
   python manage.py runserver
   ```

   Access at: **http://127.0.0.1:8000/**

## 🧭 API Endpoints

### Property APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/properties/` | Get filtered properties with pagination |
| GET | `/api/properties/<id>/` | Get single property details |
| GET | `/api/filter-options/` | Get valid filter values (cities, BHK, types, budgets) |
| POST | `/api/properties/360/update/` | Update 360° room images |

### Recommendation APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recommend/` | Get AI recommendations |
| GET | `/api/recommend/options/` | Get valid filter options |

### Chatbot API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vastu-chat/` | Chat with Vastu guidance bot |

### UI Pages
| URL | Purpose |
|-----|---------|
| `/` | Homepage |
| `/home/` | Home page |
| `/discover/` | Property discovery & filtering |
| `/property/<id>/` | Property detail page |
| `/virtual-tour/` | Virtual tour (redirects to first property) |
| `/virtual-tour/<id>/` | Specific property 360° tour |
| `/ai-advisor/` | AI recommendation form |
| `/sell/` | Property submission form |
| `/capture360/` | 360° image capture tool |

## 📝 Usage Examples

### Get Properties with Filters
```bash
curl "http://127.0.0.1:8000/api/properties/?city=Mumbai&budget=20to50&bhk=2%20BHK"
```

### Get AI Recommendations
```bash
curl -X POST http://127.0.0.1:8000/api/recommend/ \
  -H "Content-Type: application/json" \
  -d '{"city": "Mumbai", "bhk": "2 BHK", "type": "Apartment", "budget": 80}'
```

### Chat with Vastu Bot
```bash
curl -X POST http://127.0.0.1:8000/vastu-chat/ \
  -H "Content-Type: application/json" \
  -d '{"query": "what is best for north facing house?"}'
```

## 🔧 Configuration

All configuration uses environment variables via `.env` file:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_URL=sqlite:///db.sqlite3

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:8000

# Logging
LOGGING_LEVEL=INFO

# File uploads
MAX_IMAGE_SIZE_MB=5
MAX_PROPERTY_IMAGES=10

# ML models
ML_MODEL_DIR=./recommendation/ml_model
ML_MODEL_NAME=collaborative_filter_v1

# Security (for production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

## 📊 Key Improvements (Professional Grade Refactor)

### Phase 1 & 2: Configuration & Code Quality ✅
- ✅ **Centralized Constants** (`core/constants.py`) - No more hardcoded values
- ✅ **Environment Variables** - Using `python-decouple` for secure configuration
- ✅ **Structured Logging** - Replaced `print()` with Python logging module
- ✅ **Custom Exceptions** (`core/exceptions.py`) - Proper error handling
- ✅ **Path Fixes** - Cross-platform compatible paths (removed absolute `/home/claude/` paths)
- ✅ **Import Fixes** - Proper relative imports, removed sys.path hacks
- ✅ **DRY Principle** - Extracted duplicate city/budget lists to constants

### Upcoming Improvements
- **Phase 3**: Folder restructuring & app renaming
- **Phase 4**: API documentation & deployment guides
- Security hardening for production
- Database query optimization & pagination
- Async task queue for image stitching (Celery)
- Caching layer (Redis) for recommendations
- API authentication & rate limiting
- Comprehensive test suite

## 🧠 Chatbot Intelligence

The Vastu chatbot uses a multi-level matching strategy for robust query handling:

1. **Exact Match**: Direct lookup after normalization
2. **Substring Match**: Question contains user query
3. **Token Overlap**: Semantic word-level matching
4. **TF-IDF Similarity**: Vectorized semantic search
5. **Fallback Suggestions**: Top 3 similar questions when no match found

**Supported Features:**
- Case-insensitive matching
- Spelling correction (e.g., "magara" → "makara")
- Whitespace normalization
- Punctuation handling
- 274+ Vastu Q&A pairs

**Example Queries:**
- "north facing house"
- "is north-facing good?"
- "magara rasi"
- "kumbha rasi advantage"
- "best direction for open ground"

## 🔐 Security Notes

### Current Setup (Development)
- DEBUG mode enabled for development
- SQLite for simplicity
- CORS allows localhost

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Switch to PostgreSQL for database
- [ ] Enable HTTPS (`SECURE_SSL_REDIRECT=True`)
- [ ] Set secure cookie flags
- [ ] Whitelist CORS origins
- [ ] Add authentication layer
- [ ] Implement rate limiting
- [ ] Set up monitoring & logging

## 📋 Database

### Models Structure
**Property Model**: 
- Title, Location, City, Price (display + numeric)
- BHK, Type, Area, Floor, Facing
- Description, Amenities
- 360° Views: living_room, kitchen, bedroom, bathroom
- Badge, Active status, Timestamps

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🤖 ML Recommendations

**Method**: Collaborative Filtering with Cosine Similarity

**Features Used**:
- City (encoded)
- BHK (encoded)
- Property Type (encoded)
- Price (normalized)
- Area (normalized)
- Floor (processed)

**Training**:
```bash
python recommendation/train_model.py
```

Generates 6 serialized models in `recommendation/ml_model/`:
- `le_city.pkl`, `le_bhk.pkl`, `le_type.pkl` (label encoders)
- `scaler.pkl` (feature normalization)
- `feature_matrix.pkl` & `similarity_matrix.pkl` (pre-computed scores)
- `properties_df.pkl` (properties lookup)

## 📸 360° Virtual Tours

**Capture Flow**:
1. User uploads property
2. Redirects to `/capture360/?property_id=<id>`
3. Uses WebRTC to access camera
4. Captures 4+ frames per room
5. OpenCV stitches frames into panorama
6. Saves base64-encoded panorama to DB
7. Displays in Three.js viewer

**Supported Rooms**:
- Living Room 🛋️
- Kitchen 🍳
- Bedroom 🛏️
- Bathroom 🚿

## 📞 Support & Documentation

- **Issues**: Check Django logs in `logs/application.log`
- **API Testing**: Use curl or Postman
- **Database**: SQLite file at `db.sqlite3`

## 📄 License

MIT License - See LICENSE file for details

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [scikit-learn ML](https://scikit-learn.org/)
- [OpenCV Image Processing](https://opencv.org/)
- [python-decouple Configuration](https://github.com/HenryBrunner/python-decouple) 
