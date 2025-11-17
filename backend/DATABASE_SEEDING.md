# Database Seeding Guide

## Overview

The PsyProtocol platform includes a comprehensive database seeding script that populates the database with demo data for development and testing purposes.

## Files Created

- **`seed_database.py`** - Main seeding script
- **`scripts/reset_and_seed.sh`** - Convenience script to drop, recreate, and seed database
- **`DATABASE_SEEDING.md`** - This documentation

## What Gets Seeded

### 1. Demo Users (6 users)

| Email | Password | Role |
|-------|----------|------|
| `admin@psyprotocol.com` | `Admin123!` | Platform Admin |
| `director@psyprotocol.com` | `Director123!` | Medical Director |
| `therapist1@psyprotocol.com` | `Therapist123!` | Therapist (MD) |
| `therapist2@psyprotocol.com` | `Therapist123!` | Therapist (PhD) |
| `patient1@psyprotocol.com` | `Patient123!` | Patient |
| `patient2@psyprotocol.com` | `Patient123!` | Patient |

### 2. Demo Clinic

- **Name:** Center for Evidence-Based Therapies
- **Type:** Clinic
- **Address:** 123 Wellness St, San Francisco, CA 94102
- **License Numbers:** CA-MED-12345, DEA-XY9876543
- **Certifications:** MAPS, Johns Hopkins Psilocybin Research, State Schedule I Research License
- **Protocols Enabled:** All protocols

### 3. Therapist Profiles

- **Therapist 1 (MD):** Board-certified psychiatrist with psychedelic therapy certifications
- **Therapist 2 (PhD):** Licensed clinical psychologist with ketamine therapy certification

### 4. Patient Profiles

- **Patient 1:** 40-year-old with treatment-resistant depression
- **Patient 2:** 33-year-old with PTSD

### 5. Protocols from JSON (7 protocols)

All protocols loaded from `backend/examples/`:
- Psilocybin-Assisted Therapy for Treatment-Resistant Depression
- MDMA-Assisted Therapy for PTSD (MAPS Phase 3 Protocol)
- Ketamine Infusion Therapy for Treatment-Resistant Depression
- LSD Microdosing Protocol
- Testosterone Optimization Protocol
- FOLFOX Chemotherapy for Colorectal Cancer
- Autologous Bone Marrow Stem Cell Therapy for Knee Osteoarthritis

Each protocol includes:
- Full protocol metadata
- All protocol steps with proper sequencing
- Safety checks and contraindications
- Clinical scales and monitoring requirements

### 6. Sample Treatment Plans

- Active treatment plan (Patient 1 with Psilocybin protocol)
- Screening treatment plan (Patient 2 with MDMA protocol)
- Completed treatment plan (demonstration)

### 7. Sample Sessions

- Completed sessions with documentation
- Scheduled upcoming sessions
- Session documentation with vitals and notes

## Usage

### Option 1: Seed Only (Preserve Existing Data)

If you want to add demo data to an existing database:

```bash
cd backend
python seed_database.py
```

The script is **idempotent** - it checks for existing data and won't create duplicates. Safe to run multiple times.

### Option 2: Reset and Seed (Fresh Start)

To drop the database, recreate it, run migrations, and seed:

```bash
cd backend
./scripts/reset_and_seed.sh
```

**WARNING:** This will DELETE ALL existing data!

The script will prompt for confirmation before proceeding.

## Requirements

- PostgreSQL database must be accessible
- `.env` file must be properly configured with `DATABASE_URL`
- Alembic migrations must be available (for reset script)
- Python dependencies must be installed

## Script Features

### Idempotency
- Checks for existing users, clinics, protocols before creating
- Won't duplicate data if run multiple times
- Safe to run in development environments

### Error Handling
- Graceful error handling for missing files
- Transaction rollback on failures
- Informative error messages

### Progress Reporting
- Real-time progress messages
- Summary of what was created
- Clear success/failure indicators

### Data Validation
- Proper password hashing using Argon2
- Enum mapping for therapy types and evidence levels
- Foreign key relationships properly maintained

## Verification

After seeding, verify the data:

```bash
# Check user count
python -c "from app.database import SessionLocal; from app.models import User; db = SessionLocal(); print(f'Users: {db.query(User).count()}'); db.close()"

# Check protocols
python -c "from app.database import SessionLocal; from app.models import Protocol; db = SessionLocal(); print(f'Active Protocols: {db.query(Protocol).filter(Protocol.status==\"active\").count()}'); db.close()"

# Check treatment plans
python -c "from app.database import SessionLocal; from app.models import TreatmentPlan; db = SessionLocal(); print(f'Treatment Plans: {db.query(TreatmentPlan).count()}'); db.close()"
```

## Development Workflow

### Initial Setup
```bash
# Create database and run migrations
alembic upgrade head

# Seed with demo data
python seed_database.py
```

### Reset During Development
```bash
# Quick reset when you need fresh data
./scripts/reset_and_seed.sh
```

### Test API Endpoints

Once seeded, you can test with demo credentials:

```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@psyprotocol.com", "password": "Admin123!"}'

# Login as therapist
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "therapist1@psyprotocol.com", "password": "Therapist123!"}'

# Login as patient
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "patient1@psyprotocol.com", "password": "Patient123!"}'
```

## Customization

### Adding More Demo Data

Edit `seed_database.py` and add to the respective data arrays:

- `DEMO_USERS` - Add more user accounts
- `therapist_data` - Add more therapist profiles
- `patient_data` - Add more patient profiles
- `plan_data` - Add more treatment plans

### Adding More Protocols

Add JSON files to `backend/examples/` and update `PROTOCOL_FILES` array in `seed_database.py`.

## Troubleshooting

### "Database does not exist" Error
```bash
# Create database manually
createdb your_database_name

# Or use reset script which handles this
./scripts/reset_and_seed.sh
```

### "Permission denied" Error
```bash
# Make scripts executable
chmod +x seed_database.py
chmod +x scripts/reset_and_seed.sh
```

### Import Errors
```bash
# Ensure you're in the backend directory
cd backend

# Ensure dependencies are installed
pip install -r requirements.txt
```

### "Protocol file not found" Warning
- Check that JSON files exist in `backend/examples/`
- Verify file names match `PROTOCOL_FILES` array
- Script will skip missing files and continue

## Production Warning

**DO NOT run these scripts in production!**

These scripts are for development and testing only. Demo credentials use weak passwords and predictable data.

For production:
- Use strong, unique passwords
- Create users through proper admin interfaces
- Load protocols through validated admin workflows
- Never commit actual patient data

## Summary Output

After successful seeding, you'll see:

```
======================================================================
✓ Database seeding completed successfully!
======================================================================

Summary:
  - Users created: 6
  - Clinics created: 1
  - Therapist profiles: 2
  - Patient profiles: 2
  - Protocols loaded: 7
  - Treatment plans: 3
  - Treatment sessions: 8

Demo Login Credentials:
  Admin:     admin@psyprotocol.com / Admin123!
  Director:  director@psyprotocol.com / Director123!
  Therapist: therapist1@psyprotocol.com / Therapist123!
  Patient:   patient1@psyprotocol.com / Patient123!
======================================================================
```

## Additional Resources

- API Documentation: `THERAPIST_API_CURL_EXAMPLES.md`
- Admin API: `ADMIN_API_EXAMPLES.md`
- Protocol Examples: `examples/*.json`

## Support

For issues or questions about database seeding:
1. Check this documentation
2. Review script output for error messages
3. Verify database connectivity and migrations
4. Check Python logs for detailed error traces
