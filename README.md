# Weather API Wrapper (Flask)

A simple Flask service that wraps the Visual Crossing Weather API and adds basic caching.


Created for https://roadmap.sh/projects/weather-api-wrapper-service

___

## Setup

1. Create virtualenv and install dependencies:

   ```bash
   pip install -r requirements.txt
   
2. Create ```.env``` in the orijext root:
```text
VISUAL_CROSSING_API_KEY=your_real_key_here
VISUAL_CROSSING_BASE_URL=https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline
CACHE_TTL_SECONDS=600
FLASK_ENV=development
REDIS_URL=redis://localhost:6379/0
```
3. Run the app:
```bash
python -m --app app run
```
The API will be available at http://127.0.0.1:5000/

___

## Testing

Run the automated tests:

```bash
pytest
