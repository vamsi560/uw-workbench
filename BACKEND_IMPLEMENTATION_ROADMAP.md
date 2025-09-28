# Backend Implementation Roadmap for Frontend Enhancements

## Current State Analysis

### What We Have ✅
- Basic FastAPI application with email intake
- SQLAlchemy database with `Submission` and `WorkItem` models
- Basic CRUD operations for submissions
- Polling endpoint for real-time updates (`/api/workitems/poll`)
- WebSocket support (optional)
- LLM integration for data extraction

### What We Need 🎯
Based on the frontend enhancement guide, we need to implement significant backend changes to support:
- Advanced work item management
- Risk assessment system
- Comments and collaboration
- Smart assignment system
- Analytics dashboard
- Role-based access control

---

## Implementation Phases

### Phase 1: Core Data Model Extensions (Week 1-2)

#### 1.1 Database Schema Updates

**Extend Submission/WorkItem Models**:
```python
# models.py additions needed
class WorkItem(Base):
    # Existing fields...
    
    # New fields for cyber insurance
    risk_score = Column(Float, nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(Enum('Small', 'Medium', 'Large', 'Enterprise'))
    policy_type = Column(String(100), nullable=True)
    coverage_amount = Column(Float, nullable=True)
    
    # Risk categories (JSON field)
    risk_categories = Column(JSON, nullable=True)
    last_risk_assessment = Column(DateTime, nullable=True)
    
    # Status and priority enums
    status = Column(Enum('Pending', 'In Review', 'Approved', 'Rejected'))
    priority = Column(Enum('Low', 'Moderate', 'Medium', 'High', 'Critical'))
```

**New Tables Needed**:
```python
class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"))
    overall_risk_score = Column(Float, nullable=False)
    risk_categories = Column(JSON)  # technical, operational, financial, compliance
    risk_factors = Column(JSON)
    recommendations = Column(JSON)
    assessed_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"))
    author_id = Column(String(255))
    author_name = Column(String(255))
    content = Column(Text)
    is_urgent = Column(Boolean, default=False)
    mentions = Column(JSON)  # Array of user IDs
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    role = Column(Enum('Underwriter', 'Senior_Underwriter', 'Manager', 'Risk_Analyst'))
    specializations = Column(JSON)  # Array of specialization areas
    max_capacity = Column(Integer, default=25)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkItemHistory(Base):
    __tablename__ = "work_item_history"
    
    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"))
    action = Column(Enum('created', 'updated', 'assigned', 'commented', 'risk_assessed'))
    performed_by = Column(String(255))
    performed_by_name = Column(String(255))
    details = Column(JSON)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

#### 1.2 Database Migration Script
```python
# migration_script.py
def migrate_database():
    # Add new columns to existing tables
    # Create new tables
    # Set up indexes for performance
    pass
```

### Phase 2: Enhanced Work Item Management (Week 2-3)

#### 2.1 Update Work Items API

**Replace existing endpoints with enhanced versions**:

```python
# main.py - Enhanced work items endpoints

@app.get("/api/workitems", response_model=WorkItemListResponse)
async def get_work_items(
    search: str = None,
    priority: str = None,
    status: str = None,
    assigned_to: str = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Enhanced work items with filtering, search, and pagination"""
    pass

@app.get("/api/workitems/{id}", response_model=WorkItemDetailResponse)
async def get_work_item_details(id: int, db: Session = Depends(get_db)):
    """Get detailed work item with all related data"""
    pass

@app.put("/api/workitems/{id}", response_model=WorkItemResponse)
async def update_work_item(
    id: int,
    updates: WorkItemUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update work item with history tracking"""
    pass
```

#### 2.2 Update Response Models

```python
# models.py - New response models
class WorkItemListResponse(BaseModel):
    workItems: List[WorkItemSummary]
    total: int
    pagination: PaginationInfo

class WorkItemDetailResponse(BaseModel):
    workItem: WorkItemDetail
    riskAssessment: Optional[RiskAssessmentDetail]
    comments: List[CommentDetail]
    assignmentHistory: List[AssignmentRecord]
    history: List[HistoryRecord]
```

### Phase 3: Risk Assessment System (Week 3-4)

#### 3.1 Risk Assessment Endpoints

```python
@app.get("/api/workitems/{id}/risk-assessment")
async def get_risk_assessment(id: int, db: Session = Depends(get_db)):
    """Get current risk assessment for work item"""
    pass

@app.post("/api/workitems/{id}/risk-assessment")
async def create_risk_assessment(
    id: int,
    assessment: RiskAssessmentRequest,
    db: Session = Depends(get_db)
):
    """Create new risk assessment"""
    pass

@app.put("/api/workitems/{id}/risk-assessment")
async def update_risk_assessment(
    id: int,
    assessment: RiskAssessmentUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update existing risk assessment"""
    pass
```

#### 3.2 Risk Calculation Engine

```python
# risk_engine.py
class RiskCalculationEngine:
    def calculate_overall_risk(self, factors: Dict) -> float:
        """Calculate overall risk score based on multiple factors"""
        pass
    
    def analyze_risk_categories(self, work_item: WorkItem) -> Dict:
        """Analyze technical, operational, financial, compliance risks"""
        pass
    
    def generate_recommendations(self, assessment: RiskAssessment) -> List[Dict]:
        """Generate risk mitigation recommendations"""
        pass
```

### Phase 4: Comments and Collaboration (Week 4-5)

#### 4.1 Comments System

```python
@app.get("/api/workitems/{id}/comments")
async def get_comments(id: int, db: Session = Depends(get_db)):
    """Get all comments for a work item"""
    pass

@app.post("/api/workitems/{id}/comments")
async def create_comment(
    id: int,
    comment: CommentRequest,
    db: Session = Depends(get_db)
):
    """Create new comment with mention support"""
    pass

@app.get("/api/users/search")
async def search_users(query: str, db: Session = Depends(get_db)):
    """Search users for @mentions"""
    pass
```

### Phase 5: Smart Assignment System (Week 5-6)

#### 5.1 Assignment Intelligence

```python
@app.get("/api/underwriters/recommendations")
async def get_assignment_recommendations(
    work_item_id: int,
    db: Session = Depends(get_db)
):
    """Get intelligent underwriter recommendations"""
    pass

@app.post("/api/workitems/{id}/assign")
async def assign_work_item(
    id: int,
    assignment: AssignmentRequest,
    db: Session = Depends(get_db)
):
    """Assign work item to underwriter"""
    pass

@app.get("/api/underwriters/{id}/workload")
async def get_underwriter_workload(id: str, db: Session = Depends(get_db)):
    """Get current workload for underwriter"""
    pass
```

#### 5.2 Assignment Algorithm

```python
# assignment_engine.py
class AssignmentEngine:
    def recommend_underwriters(self, work_item: WorkItem) -> List[RecommendationScore]:
        """Score and rank underwriters for assignment"""
        pass
    
    def calculate_workload_balance(self, underwriter_id: str) -> WorkloadMetrics:
        """Calculate current workload and capacity"""
        pass
```

### Phase 6: Analytics Dashboard (Week 6-7)

#### 6.1 Analytics Endpoints

```python
@app.get("/api/analytics/cyber-risk-by-industry")
async def get_cyber_risk_by_industry(db: Session = Depends(get_db)):
    """Analytics for cyber risk distribution by industry"""
    pass

@app.get("/api/analytics/policy-coverage-distribution")
async def get_policy_coverage_distribution(db: Session = Depends(get_db)):
    """Analytics for policy coverage types"""
    pass

@app.get("/api/analytics/work-item-status-distribution")
async def get_work_item_status_distribution(db: Session = Depends(get_db)):
    """Analytics for work item status distribution"""
    pass

@app.get("/api/analytics/risk-score-distribution")
async def get_risk_score_distribution(db: Session = Depends(get_db)):
    """Analytics for risk score distribution"""
    pass
```

### Phase 7: Authentication & Authorization (Week 7-8)

#### 7.1 User Management System

```python
# auth.py
class AuthenticationService:
    def authenticate_user(self, token: str) -> User:
        """Authenticate user from JWT token"""
        pass
    
    def authorize_action(self, user: User, action: str, resource: str) -> bool:
        """Check if user has permission for action"""
        pass

# Middleware for role-based access
def require_role(allowed_roles: List[str]):
    def decorator(func):
        # Role checking logic
        pass
    return decorator
```

### Phase 8: Performance & Optimization (Week 8-9)

#### 8.1 Caching Layer

```python
# cache.py
import redis
from functools import wraps

def cache_result(expiry_seconds: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Redis caching logic
            pass
        return wrapper
    return decorator
```

#### 8.2 Database Optimization

```sql
-- Create performance indexes
CREATE INDEX idx_workitems_status ON work_items(status);
CREATE INDEX idx_workitems_priority ON work_items(priority);
CREATE INDEX idx_workitems_assigned_to ON work_items(assigned_to);
CREATE INDEX idx_workitems_created_at ON work_items(created_at);
CREATE INDEX idx_comments_work_item_id ON comments(work_item_id);
CREATE INDEX idx_risk_assessments_work_item_id ON risk_assessments(work_item_id);
```

### Phase 9: Testing & Documentation (Week 9-10)

#### 9.1 API Testing

```python
# tests/test_workitems.py
def test_work_item_filtering():
    """Test work item filtering functionality"""
    pass

def test_risk_assessment_calculation():
    """Test risk assessment calculation"""
    pass

def test_assignment_recommendations():
    """Test underwriter recommendation algorithm"""
    pass
```

#### 9.2 API Documentation

```python
# Update OpenAPI documentation
app = FastAPI(
    title="Cyber Insurance Underwriting Workbench API",
    description="Comprehensive API for cyber insurance underwriting",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
```

---

## Integration with Current Polling System

Your current polling endpoint `/api/workitems/poll` should be enhanced to support the new data structure:

```python
@app.get("/api/workitems/poll")
async def poll_workitems(
    since: str = None,
    limit: int = 50,
    user_id: str = None,  # Filter by assigned user
    db: Session = Depends(get_db)
):
    """Enhanced polling with new work item structure"""
    # Query with new fields including risk_score, priority, etc.
    # Return enhanced work item structure
    pass
```

---

## Migration Strategy

### Step 1: Backup Current Data
```bash
# Backup current database
pg_dump your_database > backup_before_migration.sql
```

### Step 2: Gradual Migration
1. Add new tables without breaking existing functionality
2. Gradually migrate data from `submissions` to enhanced `work_items`
3. Update endpoints one by one
4. Maintain backward compatibility during transition

### Step 3: Frontend Integration Points
The enhanced polling endpoint should return data in this format to match frontend expectations:

```json
{
  "items": [
    {
      "id": 123,
      "submission_id": 456,
      "submission_ref": "uuid-string",
      "title": "Cyber Insurance Application - TechCorp Inc",
      "description": "Healthcare technology company seeking cyber coverage",
      "priority": "High",
      "status": "Pending",
      "assignedTo": "underwriter@company.com",
      "riskScore": 75,
      "riskCategories": {
        "technical": 80,
        "operational": 65,
        "financial": 70,
        "compliance": 85
      },
      "industry": "Healthcare Technology",
      "companySize": "Medium",
      "coverageAmount": 5000000,
      "commentsCount": 3,
      "hasUrgentComments": true,
      "created_at": "2025-09-28T10:15:00Z",
      "updated_at": "2025-09-28T11:30:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2025-09-28T11:30:00Z"
}
```

---

## Immediate Next Steps

1. **This Week**: Start with Phase 1 - extend the database schema
2. **Add new models** to `models.py` and `database.py`
3. **Create migration script** to safely update existing data
4. **Test the polling endpoint** with new data structure
5. **Update frontend environment variables** to point to new enhanced endpoints

The current polling system will continue to work during the migration, ensuring no downtime for your frontend.