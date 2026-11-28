"""Sprint 2 integration entrypoint; Sprint 3 routers are intentionally not mounted."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, sports, courts, bookings, notifications
from app.core.config import settings

app = FastAPI(title='DatSan API — Sprint 2', version='0.2.0', description='Court reservations and simulated payment. Local educational demo.')
app.add_middleware(CORSMiddleware, allow_origins=[s.strip() for s in settings.cors_origins.split(',') if s.strip()], allow_credentials=False, allow_methods=['GET','POST','PUT','PATCH','DELETE'], allow_headers=['Authorization','Content-Type'])
for module in (auth, sports, courts, bookings, notifications):
    app.include_router(module.router, prefix='/api')

@app.get('/api/health', tags=['System'])
def health():
    return {'status':'ok','version':'0.2.0','booking_engine':'enabled','payments':'DEMO_ONLY'}
