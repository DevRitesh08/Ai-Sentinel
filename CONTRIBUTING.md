# Contributing

Thanks for helping build AI Trust Sentinel.

## What We Value

- Clear, measurable improvements over vague feature creep
- Trustworthy docs that match the code
- Small PRs with obvious user or maintainer value
- Good demos, good tests, and good naming

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

## Validation Before A PR

Run backend smoke tests from the repo root:

```bash
python -m unittest discover -s backend/tests -v
```

If you are working on live integrations, also run:

```bash
python test_keys.py
```

Then from `frontend/`:

```bash
npm run build
```

## PR Guidelines

- Keep the scope tight.
- Explain the user-facing impact in the PR description.
- Include screenshots or terminal output for UI and DX changes.
- Add or update tests when behavior changes.
- Update the README or roadmap if the product story changes.

## Good First Contributions

- Improve source ranking and claim classification quality
- Add screenshots, GIFs, and launch assets
- Add more backend tests
- Improve deployment docs
- Add benchmark datasets and eval scripts

## Things To Avoid

- Hardcoding personal API endpoints or credentials
- Shipping docs that promise features the repo does not have
- Bundling large unrelated refactors into one PR
