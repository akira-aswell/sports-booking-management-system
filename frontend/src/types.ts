export type Role = 'PLAYER' | 'OWNER' | 'ORGANIZER' | 'ADMIN'
export interface User { id:number; full_name:string; email:string; role:Role }
export interface AuthResult { access_token:string; token_type:string; user:User }
export interface Sport { id:number; name:string; active:boolean }
export interface Court { id:number; owner_id:number; sport_id:number; sport:Sport; name:string; address:string; district:string; description:string; price_per_hour:string; min_duration_minutes:number; buffer_minutes:number; active:boolean }
export interface OperatingHour { id:number; weekday:number; open_time:string; close_time:string }
export interface Maintenance { id:number; start_at:string; end_at:string; reason:string }
export interface CourtDetail extends Court { operating_hours:OperatingHour[]; maintenance_windows:Maintenance[] }
export interface CourtList { items:Court[]; total:number }
export interface Slot { start_at:string; end_at:string; available:boolean; reason:string|null }
export interface Availability { court_id:number; date:string; duration_minutes:number; note:string; slots:Slot[] }
export type CourtInput = Pick<Court,'name'|'sport_id'|'address'|'district'|'description'|'price_per_hour'|'min_duration_minutes'|'buffer_minutes'|'active'>
export type BookingStatus = 'PENDING'|'CONFIRMED'|'CANCELLED'|'REJECTED'
export interface Booking { id:number; court_id:number; player_id:number; start_at:string; end_at:string; status:BookingStatus; total_amount:string; note:string; created_at:string; court_name:string; player_name:string; payment_status:string }
export interface NotificationItem { id:number; title:string; message:string; read:boolean; created_at:string }
// Contracts reserved for Sprint 3; no corresponding routes are enabled here.
export interface TeamMember { id:number; name:string; jersey_number:number|null }
export interface Team { id:number; captain_id:number; captain_name:string; name:string; description:string; members:TeamMember[] }
export interface Tournament { id:number; organizer_id:number; sport_id:number; sport_name:string; organizer_name:string; name:string; description:string; format:'ROUND_ROBIN'|'KNOCKOUT'; status:'OPEN'|'IN_PROGRESS'|'COMPLETED'|'CANCELLED'; max_teams:number; approved_teams:number; starts_at:string; ends_at:string; location:string }
export interface Registration { id:number; tournament_id:number; team_id:number; team_name:string; status:string }
export interface Match { id:number; tournament_id:number; home_team_id:number; away_team_id:number; home_team_name:string; away_team_name:string; round_number:number; court_id:number|null; court_name:string|null; start_at:string|null; end_at:string|null; home_score:number|null; away_score:number|null; status:string }
export interface Standing { team_id:number; team_name:string; played:number; won:number; drawn:number; lost:number; goals_for:number; goals_against:number; goal_difference:number; points:number }
export interface AdminUser extends User { active:boolean }
export interface AdminOverview { users:number; courts:number; bookings:number; confirmed_bookings:number; tournaments:number; matches:number; demo_paid_amount:string; payment_note:string }
