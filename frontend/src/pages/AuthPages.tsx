import { ArrowRight, LockKeyhole, Mail, ShieldCheck, UserRound } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { request } from '../api'
import { useAuth } from '../auth'
import { ErrorNotice } from '../components/Ui'
import type { AuthResult } from '../types'

export function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const { user, setSession } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<'PLAYER' | 'OWNER'>('PLAYER')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  if (user) return <Navigate to="/" replace />

  async function submit(e: FormEvent) {
    e.preventDefault(); setError(null); setBusy(true)
    try {
      const result = await request<AuthResult>(`/auth/${mode}`, {
        method: 'POST', body: JSON.stringify(mode === 'register'
          ? { full_name: fullName, email, password, role } : { email, password })
      })
      setSession(result)
      const fallback = result.user.role === 'OWNER' ? '/owner' : result.user.role === 'ADMIN' ? '/admin' : result.user.role === 'ORGANIZER' ? '/organizer' : '/'
      const from = (location.state as { from?: string } | null)?.from
      navigate(from && from !== '/login' && from !== '/register' ? from : fallback, { replace: true })
    } catch (e) { setError(e instanceof Error ? e.message : 'Đã xảy ra lỗi') }
    finally { setBusy(false) }
  }

  return <section className="auth-screen"><div className="container auth-grid"><div className="auth-decoration"><span className="eyebrow">DAT SÂN PLATFORM</span><h1>Thể thao kết nối<br/>từ một cú chạm.</h1><p>Đăng nhập để quản lý sân, tổ chức hoạt động và khám phá những không gian thể thao gần bạn.</p><div className="auth-big-icon">⚽</div><span className="auth-protection"><ShieldCheck size={18}/> Xác thực JWT và phân quyền phía máy chủ</span></div>
    <form className="auth-card" onSubmit={submit}><span className="overline">CHÀO MỪNG ĐẾN VỚI DATSÂN</span><h2>{mode === 'login' ? 'Đăng nhập' : 'Tạo tài khoản'}</h2><p>{mode === 'login' ? 'Tiếp tục với tài khoản của bạn.' : 'Tham gia hệ thống thể thao phong trào.'}</p>
      <ErrorNotice message={error} />
      {mode === 'register' && <><label className="field"><span>Họ và tên</span><div className="input-with-icon"><UserRound size={17}/><input required minLength={2} maxLength={120} value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Nguyễn Văn A" /></div></label><label className="field"><span>Vai trò</span><select value={role} onChange={e => setRole(e.target.value as 'PLAYER'|'OWNER')}><option value="PLAYER">Người chơi</option><option value="OWNER">Chủ sân</option></select></label></>}
      <label className="field"><span>Email</span><div className="input-with-icon"><Mail size={17}/><input required type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="email@example.com" /></div></label>
      <label className="field"><span>Mật khẩu</span><div className="input-with-icon"><LockKeyhole size={17}/><input required type="password" minLength={mode === 'register' ? 8 : undefined} value={password} onChange={e => setPassword(e.target.value)} placeholder="Nhập mật khẩu" /></div></label>
      <button className="btn btn-primary full-btn" disabled={busy} type="submit">{busy ? 'Đang xử lý...' : mode === 'login' ? 'Đăng nhập' : 'Đăng ký'} <ArrowRight size={17}/></button>
      <div className="auth-switch">{mode === 'login' ? <>Chưa có tài khoản? <Link to="/register">Đăng ký ngay</Link></> : <>Đã có tài khoản? <Link to="/login">Đăng nhập</Link></>}</div>
      {mode === 'login' && <div className="demo-box"><strong>Tài khoản demo (chỉ môi trường development)</strong><p>Chủ sân: <code>owner@demo.example.com</code></p><p>Người chơi: <code>player@demo.example.com</code></p><p>Admin: <code>admin@demo.example.com</code></p><p>BTC: <code>organizer@demo.example.com</code></p><p>Mật khẩu chung: <code>Demo123!</code></p></div>}
    </form>
  </div></section>
}
