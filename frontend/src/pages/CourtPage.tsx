import { ArrowLeft, CalendarDays, Clock3, Info, MapPin, ShieldCheck, Wallet, Wrench } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../auth'
import { dateVietnam, money, request, shortTime, tomorrowVietnam } from '../api'
import type { Availability, CourtDetail } from '../types'
import { ErrorNotice, Loading } from '../components/Ui'

const weekdays = ['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ nhật']

export function CourtPage() {
  const { id } = useParams()
  const { token, user } = useAuth()
  const [chosen, setChosen] = useState<{start_at:string;end_at:string}|null>(null)
  const [bookingBusy,setBookingBusy] = useState(false)
  const [booked,setBooked] = useState<number|null>(null)
  const [note,setNote] = useState('')
  const [reload,setReload] = useState(0)
  const [court, setCourt] = useState<CourtDetail | null>(null)
  const [availability, setAvailability] = useState<Availability | null>(null)
  const [date, setDate] = useState(tomorrowVietnam())
  const [duration, setDuration] = useState(60)
  const [error, setError] = useState<string|null>(null)
  const [loading, setLoading] = useState(true)
  const [slotLoading, setSlotLoading] = useState(true)

  useEffect(() => {
    setLoading(true); setError(null)
    request<CourtDetail>(`/courts/${id}`).then(c => { setCourt(c); setDuration(c.min_duration_minutes) }).catch(e => setError(e.message)).finally(() => setLoading(false))
  }, [id])
  useEffect(() => {
    if (!court) return
    setChosen(null);setSlotLoading(true); setError(null)
    request<Availability>(`/courts/${id}/availability?date=${date}&duration_minutes=${duration}`)
      .then(setAvailability).catch(e => setError(e.message)).finally(() => setSlotLoading(false))
  }, [id, date, duration, court, reload])

  async function book() {
    if (!chosen || !court || !token) return
    setBookingBusy(true);setError(null);setBooked(null)
    try {
      const data = await request<{id:number}>('/bookings', {method:'POST',body:JSON.stringify({...chosen,court_id:court.id,note})}, token)
      setBooked(data.id);setChosen(null);setReload(n=>n+1)
    } catch(e){setError(e instanceof Error?e.message:'Không thể tạo đơn đặt sân')}
    finally {setBookingBusy(false)}
  }

  if (loading) return <div className="container page-space"><Loading /></div>
  if (!court) return <div className="container page-space"><ErrorNotice message={error}/><Link to="/">Về danh sách sân</Link></div>

  return <div className="container detail-page"><Link className="back-link" to="/"><ArrowLeft size={16}/> Quay lại tìm sân</Link>
    <div className="detail-head"><div><span className="overline">CHI TIẾT SÂN THỂ THAO</span><h1>{court.name}</h1><p><MapPin size={17}/>{court.address}</p></div><span className="pill"><ShieldCheck size={16}/>{court.sport.name}</span></div>
    <div className="detail-layout"><div className="detail-primary"><div className="detail-cover"><span>{court.sport.name === 'Cầu lông' ? '🏸' : court.sport.name === 'Tennis' ? '🎾' : court.sport.name === 'Pickleball' ? '🏓' : '⚽'}</span><strong>{court.district}</strong></div>
      <div className="surface"><h2>Thông tin sân</h2><p>{court.description || 'Sân thể thao đang hoạt động.'}</p><div className="facts"><div><Wallet size={18}/><span>Giá thuê mỗi giờ</span><strong>{money(court.price_per_hour)}</strong></div><div><Clock3 size={18}/><span>Thời gian tối thiểu</span><strong>{court.min_duration_minutes} phút</strong></div><div><CalendarDays size={18}/><span>Thời gian nghỉ giữa lượt</span><strong>{court.buffer_minutes} phút</strong></div></div></div>
      <div className="surface"><h2>Giờ mở cửa hàng tuần</h2><div className="hour-list">{weekdays.map((day, i) => { const h = court.operating_hours.find(item => item.weekday === i); return <div key={day}><span>{day}</span><strong>{h ? `${h.open_time.slice(0, 5)} – ${h.close_time.slice(0, 5)}` : 'Đóng cửa'}</strong></div> })}</div></div>
      {court.maintenance_windows.length > 0 && <div className="surface"><h2><Wrench size={19}/> Lịch bảo trì</h2>{court.maintenance_windows.map(m => <div className="maintenance-line" key={m.id}>{dateVietnam(m.start_at)} – {dateVietnam(m.end_at)} · {m.reason}</div>)}</div>}
    </div>
    <aside className="surface slot-panel"><div className="slot-title"><CalendarDays size={21}/><h2>Tra cứu khung giờ</h2></div><div className="beta-alert"><Info size={16}/><span>Khung giờ có kiểm tra đơn đã giữ chỗ, lịch thi đấu và bảo trì. Đơn mới sẽ chờ chủ sân duyệt.</span></div>
      <label className="field"><span>Ngày muốn chơi</span><input type="date" value={date} min={new Date(Date.now() + 7*3600_000).toISOString().slice(0,10)} onChange={e => setDate(e.target.value)} /></label>
      <label className="field"><span>Thời lượng</span><select value={duration} onChange={e => setDuration(Number(e.target.value))}>{[30,60,90,120,150,180,210,240].filter(v => v>=court.min_duration_minutes).map(v => <option key={v} value={v}>{v} phút</option>)}</select></label>
      {slotLoading ? <Loading/> : availability?.slots.length ? <div className="slot-grid">{availability.slots.map((slot, i) => <button type="button" disabled={!slot.available} onClick={()=>{setChosen({start_at:slot.start_at,end_at:slot.end_at});setBooked(null)}} className={`slot-chip ${slot.available ? 'slot-free' : 'slot-blocked'} ${chosen?.start_at===slot.start_at?'slot-selected':''}`} key={i} title={slot.reason || 'Còn trống'}><strong>{shortTime(slot.start_at)}</strong><span>{slot.available ? 'Chọn giờ này' : slot.reason}</span></button>)}</div> : <div className="no-slots">Sân không mở cửa trong ngày này.</div>}
      {chosen&&<div className="booking-checkout"><h3>Khung giờ đã chọn</h3><p>{shortTime(chosen.start_at)} – {shortTime(chosen.end_at)} · <strong>{money(Number(court.price_per_hour)*duration/60)}</strong></p><label className="field"><span>Ghi chú (không bắt buộc)</span><input value={note} maxLength={500} onChange={e=>setNote(e.target.value)} placeholder="Ghi chú cho chủ sân..." /></label>{user?.role==='PLAYER'||user?.role==='ADMIN'?<button disabled={bookingBusy} onClick={book} className="btn btn-primary full-btn">{bookingBusy?'Đang gửi...':'Xác nhận đặt sân — chờ duyệt'}</button>:<Link className="btn btn-primary full-btn" to="/login">Đăng nhập bằng tài khoản người chơi</Link>}</div>}
      {booked&&<div className="success-notice"><ShieldCheck size={16}/>Đã tạo đơn #{booked} thành công. <Link to="/bookings">Xem đơn của tôi</Link></div>}
      <div className="sprint-locked"><ShieldCheck size={18}/><span>Hệ thống ngăn đặt trùng lịch. Thanh toán tại đây chỉ là mô phỏng.</span></div>
    </aside></div>
  </div>
}
