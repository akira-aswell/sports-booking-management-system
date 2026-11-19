import { ArrowRight, BadgeCheck, CalendarDays, ChevronLeft, ChevronRight, Filter, MapPin, Search, ShieldCheck, SlidersHorizontal, Wallet } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { money, request } from '../api'
import type { CourtList, Sport } from '../types'
import { EmptyState, ErrorNotice, Loading } from '../components/Ui'

const locations = ['', 'Cầu Giấy', 'Hai Bà Trưng', 'Hoàng Mai', 'Tây Hồ', 'Đống Đa', 'Thanh Xuân', 'Ba Đình', 'Nam Từ Liêm', 'Long Biên', 'Hà Đông']

export function SearchPage() {
  const [sports, setSports] = useState<Sport[]>([])
  const [courts, setCourts] = useState<CourtList | null>(null)
  const [q, setQ] = useState('')
  const [sport, setSport] = useState('')
  const [district, setDistrict] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [applied, setApplied] = useState({ q: '', sport: '', district: '', maxPrice: '' })
  const [page, setPage] = useState(0)
  const [busy, setBusy] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => { request<Sport[]>('/sports').then(setSports).catch(e => setError(e.message)) }, [])
  useEffect(() => {
    setBusy(true); setError(null)
    const p = new URLSearchParams({ limit: '6', offset: String(page * 6) })
    if (applied.q) p.set('q', applied.q)
    if (applied.sport) p.set('sport_id', applied.sport)
    if (applied.district) p.set('district', applied.district)
    if (applied.maxPrice) p.set('max_price', applied.maxPrice)
    request<CourtList>(`/courts?${p.toString()}`).then(setCourts).catch(e => setError(e.message)).finally(() => setBusy(false))
  }, [applied, page])

  function searchCourts(e: FormEvent) {
    e.preventDefault(); setPage(0); setApplied({ q, sport, district, maxPrice })
  }

  return <>
    <section className="hero"><div className="container hero-layout">
      <div className="hero-copy"><span className="eyebrow"><span className="eyebrow-dot" /> Nền tảng thể thao phong trào</span>
        <h1>Tìm sân lý tưởng.<br/><em>Chơi hết mình.</em></h1>
        <p>Khám phá sân thể thao theo môn, khu vực và giá thuê. Chọn lịch trống, đặt sân, quản lý đội và tổ chức giải đấu trên cùng một nền tảng.</p>
        <div className="hero-points"><span><BadgeCheck size={16} /> Thông tin minh bạch</span><span><CalendarDays size={16} /> Đặt sân theo khung giờ</span></div>
      </div>
      <div className="hero-art" aria-label="Minh họa sân thể thao"><div className="court-art"><div className="court-line horizontal"/><div className="court-line vertical"/><div className="court-circle"/><span className="court-ball">⚽</span><span className="court-ribbon">COURT FINDER</span></div><div className="art-tag"><ShieldCheck size={20}/><div><strong>SPORTS, MADE SIMPLE</strong><small>Hệ thống quản lý sân thể thao</small></div></div></div>
    </div></section>

    <section className="search-wrapper container"><form onSubmit={searchCourts} className="search-panel"><div className="search-title"><SlidersHorizontal size={20}/><strong>Tìm sân phù hợp</strong><span>Điền tiêu chí để lọc danh sách</span></div>
      <div className="search-fields">
        <label className="field"><span>Tên sân hoặc địa chỉ</span><div className="input-with-icon"><Search size={17}/><input value={q} onChange={e => setQ(e.target.value)} placeholder="Ví dụ: Sân bóng Minh Khai" /></div></label>
        <label className="field"><span>Môn thể thao</span><select value={sport} onChange={e => setSport(e.target.value)}><option value="">Tất cả các môn</option>{sports.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
        <label className="field"><span>Khu vực</span><select value={district} onChange={e => setDistrict(e.target.value)}>{locations.map((s,i) => <option key={i} value={s}>{s || 'Tất cả khu vực'}</option>)}</select></label>
        <label className="field"><span>Giá tối đa / giờ</span><select value={maxPrice} onChange={e => setMaxPrice(e.target.value)}><option value="">Không giới hạn</option><option value="150000">150.000đ</option><option value="250000">250.000đ</option><option value="350000">350.000đ</option></select></label>
        <button className="btn btn-primary search-submit" type="submit"><Filter size={17}/> Tìm sân</button>
      </div></form></section>

    <section className="container results-section"><div className="section-heading"><div><span className="overline">KHÁM PHÁ SÂN</span><h2>Sân thể thao dành cho bạn</h2><p>{courts ? `${courts.total} sân phù hợp với bộ lọc` : 'Đang tìm sân...'}</p></div><span className="tag muted">SÂN THỂ THAO · ĐẶT LỊCH TRỰC TUYẾN</span></div>
      <ErrorNotice message={error}/>
      {busy ? <Loading/> : courts && courts.items.length > 0 ? <>
        <div className="court-grid">{courts.items.map((c,i) => <article className="court-card" key={c.id}>
          <div className={`card-scene scene-${i % 4}`}><span className="scene-icon">{c.sport.name === 'Cầu lông' ? '🏸' : c.sport.name === 'Tennis' ? '🎾' : c.sport.name === 'Bóng rổ' ? '🏀' : c.sport.name === 'Pickleball' ? '🏓' : '⚽'}</span><span className="card-tag">{c.sport.name}</span></div>
          <div className="court-card-body"><h3>{c.name}</h3><div className="location-line"><MapPin size={15}/>{c.address}</div><div className="card-meta"><span><ShieldCheck size={15}/> {c.district}</span><span><CalendarDays size={15}/> Xem khung giờ</span></div>
            <div className="card-bottom"><div><small>Giá từ</small><strong>{money(c.price_per_hour)}<small> / giờ</small></strong></div><Link to={`/courts/${c.id}`} className="btn btn-outline btn-small">Chi tiết <ArrowRight size={15}/></Link></div>
          </div></article>)}</div>
        {courts.total > 6 && <div className="pagination"><button disabled={page === 0} onClick={() => setPage(n => n-1)} className="btn btn-outline btn-small"><ChevronLeft size={15}/> Trước</button><span>Trang {page+1} / {Math.ceil(courts.total/6)}</span><button disabled={(page+1)*6 >= courts.total} onClick={() => setPage(n => n+1)} className="btn btn-outline btn-small">Sau <ChevronRight size={15}/></button></div>}
      </> : !error && <EmptyState icon={<Wallet size={34}/>} title="Không tìm thấy sân phù hợp">Thử thay đổi môn thể thao, khu vực hoặc mức giá.</EmptyState>}
    </section>
    <section className="info-strip container"><div><ShieldCheck size={22}/><strong>Quyền truy cập rõ ràng</strong><span>4 vai trò phân tách ở Backend</span></div><div><CalendarDays size={22}/><strong>Lịch sân không trùng nhau</strong><span>Kiểm tra booking và lịch thi đấu</span></div><div><MapPin size={22}/><strong>Tìm sân theo nhu cầu</strong><span>Lọc theo môn, khu vực và giá</span></div></section>
    <div className="container sprint-note"><strong>Lưu ý phiên bản:</strong> Bản đầy đủ cho phép đặt sân, duyệt đơn và tổ chức giải. Mọi thanh toán trong hệ thống là mô phỏng phục vụ demo, không sử dụng tiền thật.</div>
  </>
}
