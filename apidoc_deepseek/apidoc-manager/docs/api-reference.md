# Server API Reference

Base URL
text
http://localhost:8000/api/v1
Endpoints
Specifications
Method	Path	Description
GET	/specs	List specifications
POST	/specs	Create specification
GET	/specs/{id}	Get specification
DELETE	/specs/{id}	Delete specification
Versions
Method	Path	Description
GET	/specs/{id}/versions	List versions
POST	/specs/{id}/versions	Create version
DELETE	/specs/{id}/versions/{v}	Delete version
Search
http
GET /specs/search?q=query&page=1&per_page=20
Diff
http
POST /specs/{id}/diff
{"version1": "1.0.0", "version2": "1.1.0"}
Import/Export
http
POST /specs/import
GET /specs/{id}/export?format=json
Health
http
GET /health
GET /health/readiness
Metrics
http
GET /metrics
