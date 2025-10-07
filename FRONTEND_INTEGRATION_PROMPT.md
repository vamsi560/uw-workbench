# Frontend Integration Prompt for Underwriter Dashboard

## Context
We have implemented a comprehensive underwriter dashboard backend with advanced analytics, risk scoring, and portfolio management capabilities. The backend extends our existing insurance underwriting workbench with intelligent decision support tools designed specifically for insurance underwriters.

## What We Need to Build (Frontend)

### 1. Main Underwriter Dashboard
**API Endpoint:** `GET /api/dashboard/underwriter/{underwriter_id}?timeframe=week`

Create a comprehensive dashboard that displays:

**KPI Cards (Top Row):**
- Active Submissions (with trend indicators)
- Pending Reviews (with SLA alerts) 
- Quotes Issued (with conversion rates)
- Average Processing Time (with target comparison)
- SLA Performance (with percentage and trend)
- Portfolio Premium (with growth indicators)
- Average Risk Score (with industry benchmark)

Each KPI card should show:
- Current value with appropriate formatting (count, percentage, currency, days)
- Trend indicator (up/down/stable with color coding)
- Percentage change from previous period
- Small sparkline chart if possible

**Work Queue Section (Main Content):**
Four columns showing different work item categories:
- **Urgent Items** (red badge, high priority items)
- **Pending Review** (yellow badge, items assigned to me)
- **Awaiting Info** (blue badge, waiting for broker response)
- **Ready to Quote** (green badge, complete and low-risk items)

Each work item card should display:
- Company name and submission reference
- Industry and risk score (with color coding)
- Coverage amount and policy type
- Days since submission with SLA indicator
- Priority badge and urgent comment indicator

**Team Metrics Panel (Right Sidebar):**
- Team average risk score
- Items completed this week
- Pending assignments (unassigned items)
- Team capacity utilization meter
- Average cycle time

### 2. Enhanced Submission Detail View
**API Endpoint:** `GET /api/dashboard/submission/{work_item_id}/detail`

Create a comprehensive submission analysis page with multiple sections:

**Company Intelligence Panel:**
- Company profile (name, industry, size, employees, revenue)
- Cybersecurity posture (security measures, data types, certifications) 
- Financial health indicators (credit rating, years in business, trends)

**Risk Assessment Dashboard:**
- Overall risk score with gauge visualization
- Risk category breakdown (Technical, Operational, Financial, Compliance)
- Detailed risk factors list with impact levels and mitigation recommendations
- Industry benchmark comparison
- Confidence score indicator

**Automated Recommendations Card:**
- Recommended action (Approve/Decline/Request Info/Refer) with confidence level
- Reasoning bullets with clear explanations
- Suggested policy conditions if applicable
- Estimated premium range with market positioning

**Policy Details Section:**
- Coverage type and limits breakdown
- Policy components (first-party, third-party, etc.)
- Suggested exclusions and endorsements
- Premium calculation factors

**Communication Hub:**
- Broker correspondence thread
- Internal comments and notes
- Information request history
- Action buttons for sending requests

### 3. Portfolio Analytics Dashboard
**API Endpoint:** `GET /api/dashboard/analytics/portfolio?timeframe=month`

Build an analytics dashboard with:

**Performance Overview:**
- Key metrics tiles showing portfolio totals
- Trend charts for submission volume, approval rates, processing times
- Goal vs actual progress bars

**Risk Distribution Charts:**
- Pie chart showing low/medium/high risk distribution
- Industry breakdown with risk scores (horizontal bar chart)
- Coverage type distribution (donut chart)
- Risk score histogram

**Benchmarking Section:**
- Industry comparison tables showing our performance vs benchmarks
- Competitive positioning charts
- Percentile ranking indicators

**Insights & Recommendations:**
- AI-generated insights about portfolio performance
- Actionable recommendations for improvement
- Alerts for concentration risks or performance issues

### 4. Work Queue Management Interface
**API Endpoint:** `GET /api/dashboard/work-queue/{underwriter_id}`

Create an enhanced work queue with:

**Advanced Filtering:**
- Priority dropdown (Critical, High, Medium, Low)
- Status multi-select (Pending, In Review, etc.)
- Industry filter with checkboxes
- Risk score range slider (0-100)
- Coverage amount range filter
- Date range picker

**Sortable Columns:**
- Company Name
- Industry
- Risk Score (with color coding)
- Coverage Amount
- Days Pending
- Priority
- Status

**Bulk Actions:**
- Select multiple items
- Bulk assignment to underwriters
- Bulk status updates
- Export to CSV

**Real-time Updates:**
- WebSocket integration for live updates
- New item notifications
- Status change alerts

### 5. Risk Assessment Interface
**API Endpoint:** `POST /api/dashboard/work-item/{work_item_id}/risk-assessment`

Build a risk assessment display with:

**Risk Score Visualization:**
- Large gauge chart showing overall score (0-100)
- Color coding: Green (0-40), Yellow (41-70), Red (71-100)
- Risk level indicator (Low/Medium/High/Critical)

**Category Breakdown:**
- Four progress bars for Technical, Operational, Financial, Compliance
- Each with score out of 100 and color coding
- Expandable sections showing contributing factors

**Risk Factors List:**
- Categorized list of identified risk factors
- Impact level badges (Low/Medium/High)
- Score impact indicators (+/- points)
- Mitigation recommendations in tooltips

**Industry Benchmark:**
- Comparison chart showing our score vs industry average
- Percentile ranking indicator
- Context about industry-specific risks

### 6. Assignment Recommendations
**API Endpoint:** `GET /api/dashboard/assignment/recommendations/{work_item_id}`

Create an assignment wizard with:

**Recommended Underwriters:**
- Cards showing top 5 recommended underwriters
- Recommendation score (0-100) with reasoning
- Expertise match indicators
- Current workload meters
- Estimated processing time

**Underwriter Details:**
- Name, role, and specializations
- Industry expertise badges
- Success rate and performance metrics
- Current capacity utilization

**Assignment Actions:**
- One-click assignment buttons
- Custom assignment with reason field
- Notification settings for assigned underwriter

### 7. Team Performance Dashboard
**API Endpoint:** `GET /api/dashboard/team/metrics?timeframe=week`

Build a team overview showing:

**Team Statistics:**
- Total active submissions across team
- Average processing time
- Team capacity utilization
- Items pending assignment

**Individual Performance Cards:**
- Each underwriter's key metrics
- Workload indicators
- Performance trends
- Availability status

**Comparative Charts:**
- Processing time comparison (bar chart)
- Approval rate comparison
- Risk score averages
- Productivity rankings

## UI/UX Guidelines

### Color Scheme for Risk Levels:
- **Low Risk (0-40):** Green (#10B981)
- **Medium Risk (41-70):** Yellow (#F59E0B) 
- **High Risk (71-85):** Orange (#EF4444)
- **Critical Risk (86-100):** Red (#DC2626)

### Priority Indicators:
- **Critical:** Red badge with urgent icon
- **High:** Orange badge
- **Medium:** Yellow badge  
- **Low:** Green badge

### Status Colors:
- **Pending:** Blue
- **In Review:** Yellow
- **Approved:** Green
- **Rejected:** Red
- **Awaiting Info:** Purple

### Key Interactions Needed:

1. **Real-time Updates:** Implement WebSocket connections for live dashboard updates
2. **Filtering & Search:** Advanced filtering with multiple criteria
3. **Drill-down Navigation:** Click on metrics to see detailed breakdowns
4. **Export Functionality:** CSV/PDF export for reports and analysis
5. **Responsive Design:** Mobile-friendly layout for field underwriters
6. **Keyboard Shortcuts:** Power user shortcuts for common actions

### Data Refresh Strategy:
- Dashboard KPIs: Refresh every 5 minutes
- Work queue: Real-time updates via WebSocket
- Analytics: Refresh when timeframe changes
- Risk assessments: On-demand calculation

### Error Handling:
- Graceful loading states for all API calls
- Error messages with retry options
- Offline capability where possible
- Progressive loading for large datasets

## Sample API Responses

### Dashboard KPIs Response:
```json
{
  "underwriter_id": "john.doe@company.com",
  "underwriter_name": "John Doe",
  "kpis": {
    "active_submissions": {
      "name": "Active Submissions",
      "value": 45,
      "previous_value": 38,
      "trend": "up",
      "percentage_change": 18.4,
      "unit": "count"
    },
    "pending_reviews": {
      "name": "Pending Reviews", 
      "value": 12,
      "trend": "stable",
      "unit": "count"
    }
  },
  "work_queue": {
    "urgent": [...],
    "pending_review": [...],
    "awaiting_info": [...],
    "ready_to_quote": [...]
  }
}
```

### Risk Assessment Response:
```json
{
  "overall_score": 67.5,
  "technical_score": 72.0,
  "operational_score": 58.0,
  "financial_score": 45.0,
  "compliance_score": 85.0,
  "risk_level": "High",
  "confidence_score": 87.5,
  "industry_benchmark": 55.0,
  "risk_factors": [
    {
      "category": "technical",
      "factor": "Limited Security Controls",
      "impact_level": "High",
      "score_impact": 15,
      "description": "Basic security measures in place",
      "mitigation_recommendation": "Implement advanced threat detection"
    }
  ]
}
```

## Integration Points

### WebSocket Events:
```javascript
// Subscribe to real-time updates
websocket.on('work_item_updated', (data) => {
  // Update work queue in real-time
});

websocket.on('new_submission', (data) => {
  // Show notification and update counters
});
```

### API Error Handling:
```javascript
// Standardized error handling
try {
  const response = await fetch('/api/dashboard/underwriter/123');
  if (!response.ok) throw new Error(response.statusText);
  const data = await response.json();
} catch (error) {
  showErrorMessage('Failed to load dashboard data', error.message);
}
```

This comprehensive frontend implementation will provide underwriters with the intelligent, data-driven tools they need while maintaining an intuitive and efficient user experience. The backend APIs are ready and waiting for these frontend components to be built.