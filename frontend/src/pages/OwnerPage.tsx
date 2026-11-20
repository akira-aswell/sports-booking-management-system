import { ArrowLeft, BadgeCheck, CalendarClock, Clock3, Edit3, Plus, Save, ShieldCheck, Trash2, Wrench } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { money, request } from '../api'
import { useAuth } from '../auth'
import type { CourtDetail, CourtInput, Sport } from '../types'
import { EmptyState, ErrorNotice, Loading } from '../components/Ui'

const blankCourt: CourtInput = { name: '', sport_id: 0, address: '', district: '', description: '', price_per_hour: '150000', min_duration_minutes: 60, buffer_minutes: 0, active: true }
const weekdays = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật']

export function OwnerPage() {
  const { token } = useAuth()
  const [courts, setCourts] = useState<CourtDetail[]>([])
  const [sports, setSports] = useState<Sport[]>([])
  const [editing, setEditing] = useState<CourtDetail | 'new' | null>(null)
  const [selected, setSelected] = useState<CourtDetail | null>(null)
  const [form, setForm] = useState<CourtInput>(blankCourt)
  const [hours, setHours] = useState<Record<number, { enabled: boolean; open_time: string; close_time: string }>>({})
  const [maintenance, setMaintenance] = useState({ start_at: '', end_at: '', reason: 'Bảo trì sân' })
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function reload() {
    const [c, s] = await Promise.all([
      request<CourtDetail[]>('/courts/mine', {}, token), request<Sport[]>('/sports')
    ])
    setCourts(c); setSports(s)
    if (selected) setSelected(c.find(item => item.id === selected.id) ?? null)
  }
  useEffect(() => {
    Promise.all([request<CourtDetail[]>('/courts/mine', {}, token), request<Sport[]>('/sports')])
      .then(([c,s]) => { setCourts(c); setSports(s) })
      .catch(e => setError(e.message)).finally(() => setLoading(false))
  }, [token])

  function openCreate() { setForm({...blankCourt, sport_id: sports[0]?.id ?? 0}); setEditing('new'); setSelected(null); setError(null); setSuccess(null) }
  function openEdit(c: CourtDetail) { setForm({ name:c.name, sport_id:c.sport_id, address:c.address, district:c.district, description:c.description, price_per_hour:c.price_per_hour, min_duration_minutes:c.min_duration_minutes, buffer_minutes:c.buffer_minutes, active:c.active }); setEditing(c); setSelected(null); setError(null); setSuccess(null) }
  function openSettings(c: CourtDetail) {
    setEditing(null); setSelected(c); setError(null); setSuccess(null)
    const map: Record<number, { enabled: boolean; open_time: string; close_time: string }> = {}
    for (let i=0; i<7; i++) { const h = c.operating_hours.find(v=>v.weekday===i); map[i] = { enabled:!!h, open_time:h?.open_time.slice(0,5) ?? '06:00', close_time:h?.close_time.slice(0,5) ?? '22:00' } }
    setHours(map)
  }
  async function submitCourt(e: FormEvent) {
    e.preventDefault(); if (!editing) return
    setError(null); setBusy(true)
    try {
      await request(editing === 'new' ? '/courts' : `/courts/${editing.id}`, {method: editing === 'new' ? 'POST' : 'PATCH', body:JSON.stringify(form)}, token)
      await reload(); setEditing(null); setSuccess('Đã lưu thông tin sân thành công.')
    } catch (e) { setError(e instanceof Error ? e.message : 'Không thể lưu sân') }
    finally { setBusy(false) }
  }
  async function saveHours() {
    if (!selected) return
    setError(null); setBusy(true)
    try {
      const payload = Object.entries(hours).filter(([, h]) => h.enabled).map(([weekday,h]) => ({weekday:Number(weekday), open_time:h.open_time, close_time:h.close_time}))
      await request(`/courts/${selected.id}/hours`, {method:'PUT', body:JSON.stringify(payload)}, token)
      await reload(); setSuccess('Đã cập nhật giờ hoạt động.')
    } catch(e) { setError(e instanceof Error ? e.message : 'Không thể cập nhật lịch') }
    finally { setBusy(false) }
  }
  async function addMaintenance(e: FormEvent) {
    e.preventDefault(); if (!selected) return
    setError(null); setBusy(true)
    try {
      await request(`/courts/${selected.id}/maintenance`, {method:'POST', body:JSON.stringify({start_at:new Date(maintenance.start_at).toISOString(), end_at:new Date(maintenance.end_at).toISOString(), reason:maintenance.reason})}, token)
      await reload(); setMaintenance({start_at:'',end_at:'',reason:'Bảo trì sân'}); setSuccess('Đã thêm lịch bảo trì.')
    } catch(e) { setError(e instanceof Error ? e.message : 'Không thể thêm lịch bảo trì') }
    finally { setBusy(false) }
  }
  async function removeMaintenance(id:number) {
    if (!selected || !window.confirm('Xóa khoảng bảo trì này?')) return
    setError(null)
    try { await request(`/courts/${selected.id}/maintenance/${id}`, {method:'DELETE'}, token); await reload(); setSuccess('Đã xóa lịch bảo trì.') }
    catch(e) { setError(e instanceof Error ? e.message : 'Không thể xóa lịch bảo trì') }
  }

  return <div className="container dashboard-page"><div className="dash-heading"><div><span className="overline">BẢNG ĐIỀU KHIỂN CHỦ SÂN</span><h1>Quản lý sân thể thao</h1><p>Thêm/sửa sân, cấu hình giờ hoạt động và bảo trì.</p></div>{editing || selected ? <button className="btn btn-outline" onClick={() => { setEditing(null); setSelected(null); setError(null) }}><ArrowLeft size={17}/> Danh sách sân</button> : <button className="btn btn-primary" onClick={openCreate}><Plus size={18}/> Thêm sân mới</button>}</div>
    <ErrorNotice message={error}/>{success && <div className="success-notice"><BadgeCheck size={18}/>{success}</div>}
    {loading ? <Loading/> : editing ? <form className="surface admin-form" onSubmit={submitCourt}><h2>{editing === 'new' ? 'Thêm sân mới' : 'Sửa thông tin sân'}</h2><div className="form-grid">
      <label className="field"><span>Tên sân *</span><input required minLength={3} value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label>
      <label className="field"><span>Môn thể thao *</span><select required value={form.sport_id || ''} onChange={e=>setForm({...form,sport_id:Number(e.target.value)})}><option value="">Chọn môn</option>{sports.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
      <label className="field"><span>Địa chỉ *</span><input required value={form.address} onChange={e=>setForm({...form,address:e.target.value})}/></label>
      <label className="field"><span>Khu vực / quận *</span><input required value={form.district} onChange={e=>setForm({...form,district:e.target.value})}/></label>
      <label className="field"><span>Giá thuê mỗi giờ (VND) *</span><input type="number" required min={1} step="1000" value={form.price_per_hour} onChange={e=>setForm({...form,price_per_hour:e.target.value})}/></label>
      <label className="field"><span>Thời lượng tối thiểu</span><select value={form.min_duration_minutes} onChange={e=>setForm({...form,min_duration_minutes:Number(e.target.value)})}>{[30,60,90,120,150,180,210,240].map(v=><option key={v} value={v}>{v} phút</option>)}</select></label>
      <label className="field"><span>Nghỉ giữa lượt</span><select value={form.buffer_minutes} onChange={e=>setForm({...form,buffer_minutes:Number(e.target.value)})}>{[0,30,60,90,120].map(v=><option key={v} value={v}>{v} phút</option>)}</select></label>
      <label className="field toggle"><input type="checkbox" checked={form.active} onChange={e=>setForm({...form,active:e.target.checked})}/><span>Sân đang hoạt động</span></label>
      <label className="field full-span"><span>Mô tả</span><textarea rows={3} value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label></div>
      <div className="form-actions"><button type="button" onClick={()=>setEditing(null)} className="btn btn-outline">Hủy</button><button disabled={busy} className="btn btn-primary" type="submit"><Save size={17}/>{busy?'Đang lưu...':'Lưu sân'}</button></div>
    </form> : selected ? <div className="owner-settings"><div className="surface"><h2><CalendarClock size={21}/> Giờ hoạt động — {selected.name}</h2><p className="subtle">Bỏ chọn những ngày sân đóng cửa. Một khung giờ mở cửa mỗi ngày.</p><div className="weekly-config">{weekdays.map((day,i)=><div className="weekly-row" key={day}><label className="check-row"><input type="checkbox" checked={hours[i]?.enabled??false} onChange={e=>setHours({...hours,[i]:{...hours[i],enabled:e.target.checked}})}/>{day}</label><input type="time" disabled={!hours[i]?.enabled} value={hours[i]?.open_time || '06:00'} onChange={e=>setHours({...hours,[i]:{...hours[i],open_time:e.target.value}})}/><span>đến</span><input type="time" disabled={!hours[i]?.enabled} value={hours[i]?.close_time || '22:00'} onChange={e=>setHours({...hours,[i]:{...hours[i],close_time:e.target.value}})}/></div>)}</div><button className="btn btn-primary" onClick={saveHours} disabled={busy}><Save size={16}/> Lưu giờ hoạt động</button></div>
      <div className="surface"><h2><Wrench size={21}/> Bảo trì / tạm đóng</h2><form onSubmit={addMaintenance} className="maintenance-form"><label className="field"><span>Bắt đầu</span><input required type="datetime-local" value={maintenance.start_at} onChange={e=>setMaintenance({...maintenance,start_at:e.target.value})}/></label><label className="field"><span>Kết thúc</span><input required type="datetime-local" value={maintenance.end_at} onChange={e=>setMaintenance({...maintenance,end_at:e.target.value})}/></label><label className="field full-span"><span>Lý do</span><input required value={maintenance.reason} onChange={e=>setMaintenance({...maintenance,reason:e.target.value})}/></label><button disabled={busy} className="btn btn-outline" type="submit"><Plus size={16}/> Thêm lịch bảo trì</button></form>
      {selected.maintenance_windows.length ? <div className="maintenance-list">{selected.maintenance_windows.map(m=><div key={m.id}><span>{new Date(m.start_at).toLocaleString('vi-VN')} – {new Date(m.end_at).toLocaleString('vi-VN')} · {m.reason}</span><button className="icon-button" title="Xóa" onClick={()=>removeMaintenance(m.id)}><Trash2 size={16}/></button></div>)}</div> : <p className="subtle">Chưa có lịch bảo trì.</p>}</div></div>
    : courts.length ? <div className="owner-court-list">{courts.map(c=><div className="surface owner-court-row" key={c.id}><div className="owner-icon">🏟️</div><div className="owner-main"><div className="owner-row-title"><h3>{c.name}</h3><span className={`status-tag ${c.active?'on':'off'}`}>{c.active?'Đang hoạt động':'Tạm ẩn'}</span></div><p>{c.sport.name} · {c.district} · {money(c.price_per_hour)}/giờ</p><p className="subtle">{c.address}</p></div><div className="owner-actions"><button className="btn btn-outline btn-small" onClick={()=>openEdit(c)}><Edit3 size={15}/> Sửa sân</button><button className="btn btn-primary btn-small" onClick={()=>openSettings(c)}><Clock3 size={15}/> Giờ / Bảo trì</button><Link to={`/courts/${c.id}`} className="btn btn-ghost btn-small">Xem</Link></div></div>)}</div>
    : <EmptyState icon={<ShieldCheck size={36}/>} title="Bạn chưa có sân nào">Bấm "Thêm sân mới" để tạo sân đầu tiên.</EmptyState>}
  </div>
}
