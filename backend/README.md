# StudySync AI Backend

Django + DRF backend for the StudySync AI admin module, wired to a
scikit-learn K-Means grouping pipeline.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API runs on `http://localhost:8000`. The Vite dev server connects to it
via `VITE_API_BASE_URL` (default `http://localhost:8000`). CORS is enabled for
`http://localhost:5173`.

## API surface

| Method | Path                        | Purpose                          |
| ------ | --------------------------- | -------------------------------- |
| POST   | `/api/admin/login/`         | Admin login (`admin@studysync.ai` / `admin123`) |
| GET    | `/api/admin/dashboard/`     | Dashboard statistics             |
| GET    | `/api/students/`            | Student directory                |
| POST   | `/api/students/register/`   | Register a student               |
| POST   | `/api/students/login/`      | Student login                    |
| POST   | `/api/groups/generate/`     | Run the AI grouping pipeline     |
| GET    | `/api/groups/`              | List generated groups            |
| GET    | `/api/groups/<id>/`         | Single group detail              |
| DELETE | `/api/groups/`              | Delete all groups                |
| GET    | `/api/reports/`             | Report history + latest payload  |
| POST   | `/api/reports/export/`      | Export report (`format`: csv/excel/pdf) |
| GET    | `/api/dashboard/statistics/`| Legacy alias of the dashboard    |

All response payloads use the camelCase shapes the React admin module consumes
(`AdminStudent`, `AdminGroup`, `AdminDashboardData`, `ReportData`).

## ML pipeline

`backend/ml/` holds the modular, reusable grouping engine:

- `feature_engineering.py` — score normalisation and fixed-order feature vectors
- `strength_analysis.py` — strength / weakness detection, subject coverage
- `clustering.py` — scikit-learn `KMeans` + complementary matching
- `group_balancer.py` — near-equal group sizes + complementary skill score
- `recommendation.py` — team leader suggestion + learning recommendations
- `utils.py` — shared constants and score helpers

The generation flow (orchestrated in `api/services.py::generate_groups`):

```
retrieve students
  -> preprocess academic scores
  -> detect strengths
  -> detect weaknesses
  -> create feature vectors
  -> run K-Means clustering
  -> apply complementary matching
  -> balance group sizes
  -> store generated groups
  -> return groups + summary
```

Complementary matching rules:

- Experts in the same subject are spread across different groups.
- Every group aims for one expert per core subject when the population allows.
- Group sizes are balanced to within one member of the mean.

## Tests

```bash
python manage.py test
```

The suite covers ML module behaviour, the full generation pipeline and every
API endpoint.
