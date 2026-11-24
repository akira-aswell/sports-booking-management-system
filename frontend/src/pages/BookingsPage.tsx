import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { CalendarDays, CreditCard, RefreshCcw, ShieldCheck, XCircle } from 'lucide-react'
import { bookingStatus, dateVietnam, localVietnamInput, money, paymentStatus, request, toVietnamISO } from '../api'
import { useAuth } from '../auth'
import type { Booking } from '../types'
import { EmptyState, ErrorNotice, Loading } from '../components/Ui'

export function BookingCard({ booking: b, role = 'player', afterChange }: { booking: Booking; role?: 'player' | 'owner'; afterChange: () => void }) {
  const { token } = useAuth()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string|null>(null)
  const [edit, setEdit] = useState(false)
  const [reference, setReference] = useState('')
  const [start, setStart] = useState(localVietnamInput(b.start_at))
  const [end, setEnd] = useState(localVietnamInput(b.end_at))
  async function action(name: string, body?: object) {
    if ((name === 'cancel' || name === 'reject') && !window.confirm(`Bạn chắc chắn muốn ${name==='cancel'?'hủy':'từ chối'} đơn #${b.id}?`)) return
    setError(null);setBusy(true)
    try { await request(`/bookings/${b.id}/${name}`, {method:'POST', ...(body?{body:JSON.stringify(body)}:{})},token);setEdit(false);afterChange() }
    catch(e) { setError(e instanceof Error?e.message:'Không thể cập nhật đơn') }
    finally { setBusy(false) }
  }
  const canAct = b.status === 'PENDING' || b.status === 'CONFIRMED'
  return <article className="surface booking-card">
    <div className="booking-card-top"><div><span className="overline">ĐƠN #{b.id}</span><h3><Link to={`/courts/${b.court_id}`}>{b.court_name}</Link></h3><p>{role==='owner'?`Người đặt: ${b.player_name}`:'Đơn đặt sân của bạn'}</p></div>
      <span className={`status-tag ${b.status==='CONFIRMED'?'on':'off'}`}>{bookingStatus(b.status)}</span></div>
    <div className="booking-card-metrics"><span><CalendarDays size={15}/>{dateVietnam(b.start_at)} – {new Date(b.end_at).toLocaleTimeString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh',hour:'2-digit',minute:'2-digit'})}</span><strong>{money(b.total_amount)}</strong></div>
    <p className="payment-label"><CreditCard size={14}/>{paymentStatus(b.payment_status)} · Thanh toán mô phỏng, không chuyển tiền thật</p>
    {b.note&&<p className="booking-note">Ghi chú: {b.note}</p>}
    <ErrorNotice message={error}/>
    <div className="action-row">
      {role==='owner'&&b.status==='PENDING'&&<><button className="btn btn-primary btn-small" disabled={busy} onClick={()=>action('approve')}><ShieldCheck size={14}/>Duyệt</button><button className="btn btn-outline btn-small" disabled={busy} onClick={()=>action('reject')}><XCircle size={14}/>Từ chối</button></>}
      {role==='owner'&&b.status==='CONFIRMED'&&b.payment_status==='SUBMITTED'&&<button className="btn btn-primary btn-small" disabled={busy} onClick={()=>action('payment-confirm')}>Xác nhận đã nhận tiền (demo)</button>}
      {role==='player'&&canAct&&b.payment_status==='UNPAID'&&<button className="btn btn-outline btn-small" disabled={busy} onClick={()=>setEdit(!edit)}><RefreshCcw size={14}/>Đổi lịch</button>}
      {role==='player'&&b.status==='CONFIRMED'&&['UNPAID','SUBMITTED'].includes(b.payment_status)&&<form onSubmit={(e:FormEvent)=>{e.preventDefault();action('payment-submit',{reference})}} className="action-row"><input aria-label="Mã chuyển khoản demo" value={reference} required minLength={3} placeholder="Mã chuyển khoản demo" onChange={e=>setReference(e.target.value)} /><button className="btn btn-primary btn-small" disabled={busy}>Gửi xác nhận demo</button></form>}
      {canAct&&<button className="btn btn-ghost btn-small" disabled={busy} onClick={()=>action('cancel')}><XCircle size={14}/>Hủy đơn</button>}
    </div>
    {edit&&<form className="edit-booking-grid" onSubmit={(e:FormEvent)=>{e.preventDefault();action('reschedule',{start_at:toVietnamISO(start),end_at:toVietnamISO(end)})}}>
      <label className="field"><span>Bắt đầu mới (giờ Việt Nam)</span><input type="datetime-local" required value={start} onChange={e=>setStart(e.target.value)}/></label>
      <label className="field"><span>Kết thúc mới (giờ Việt Nam)</span><input type="datetime-local" required value={end} onChange={e=>setEnd(e.target.value)}/></label>
      <button className="btn btn-primary btn-small" disabled={busy}>Gửi yêu cầu đổi lịch</button>
    </form>}
  </article>
}

export function BookingsPage({ mode='player' }: { mode?:'player'|'owner' }) {
  const { token } = useAuth()
  const [items, setItems] = useState<Booking[]>([])
  const [loading,setLoading] = useState(true)
  const [error,setError] = useState<string|null>(null)
  const [version,setVersion] = useState(0)
  useEffect(()=>{let live=true;setLoading(true);request<Booking[]>(`/bookings?scope=${mode==='owner'?'owner':'mine'}`,{},token).then(v=>{if(live)setItems(v)}).catch(e=>{if(live)setError(e.message)}).finally(()=>{if(live)setLoading(false)});return ()=>{live=false}},[token,mode,version])
  return <div className="container dashboard-page"><div className="dash-heading"><div><span className="overline">{mode==='owner'?'CHỦ SÂN':'NGƯỜI CHƠI'} · QUẢN LÝ LỊCH</span><h1>{mode==='owner'?'Duyệt đơn đặt sân':'Đơn đặt sân của tôi'}</h1><p>{mode==='owner'?'Duyệt/từ chối đặt sân, xác minh thanh toán demo.':'Theo dõi, đổi lịch, hủy và gửi xác nhận thanh toán demo.'}</p></div><button className="btn btn-outline" onClick={()=>setVersion(v=>v+1)}><RefreshCcw size={16}/>Làm mới</button></div>
    <ErrorNotice message={error}/>{loading?<Loading/>:items.length===0?<EmptyState icon={<CalendarDays size={36}/>} title="Chưa có đơn đặt sân">Đơn đặt mới sẽ xuất hiện ở đây.</EmptyState>:<div className="booking-stack">{items.map(b=><BookingCard key={b.id} booking={b} role={mode} afterChange={()=>setVersion(v=>v+1)}/>)}</div>}
  </div>
}
