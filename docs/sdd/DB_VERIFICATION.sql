-- Read-only PostgreSQL checks; run on a migrated disposable demo database.
SELECT version_num FROM alembic_version;
SELECT extname FROM pg_extension WHERE extname = 'btree_gist';
SELECT conname, pg_get_constraintdef(oid) AS definition
FROM pg_constraint WHERE conname IN ('no_active_allocation_overlap','ck_allocation_single_source','ck_bookings_valid_booking_period','ck_court_allocations_valid_allocation_period');

-- Expected zero: active same-court overlap.
SELECT a.id AS allocation_a, b.id AS allocation_b, a.court_id
FROM court_allocations a JOIN court_allocations b
ON a.court_id=b.court_id AND a.id<b.id
WHERE a.active AND b.active AND a.start_at<b.end_at AND b.start_at<a.end_at;
-- Expected zero: invalid source or period.
SELECT id FROM court_allocations
WHERE (booking_id IS NULL)=(match_id IS NULL) OR start_at>=end_at;
-- Expected zero: source court mismatch.
SELECT a.id FROM court_allocations a JOIN bookings b ON b.id=a.booking_id WHERE a.court_id<>b.court_id;
SELECT a.id FROM court_allocations a JOIN matches m ON m.id=a.match_id WHERE a.court_id IS DISTINCT FROM m.court_id;
-- Expected zero: active allocation for rejected/cancelled booking.
SELECT b.id FROM bookings b JOIN court_allocations a ON a.booking_id=b.id
WHERE b.status IN ('REJECTED','CANCELLED') AND a.active;
-- Expected zero: booking without payment or allocation (application invariant).
SELECT b.id FROM bookings b LEFT JOIN payments p ON p.booking_id=b.id LEFT JOIN court_allocations a ON a.booking_id=b.id WHERE p.id IS NULL OR a.id IS NULL;
-- Inspect actual demo rows; not a proof of concurrent behavior by itself.
SELECT b.id,b.court_id,b.status,p.status AS payment_status,a.start_at,a.end_at,a.active
FROM bookings b LEFT JOIN payments p ON p.booking_id=b.id LEFT JOIN court_allocations a ON a.booking_id=b.id ORDER BY b.id DESC LIMIT 30;
