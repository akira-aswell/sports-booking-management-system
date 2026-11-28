import { useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { CalendarDays, Bell, ClipboardList, LayoutDashboard, LogOut, MapPin, Menu, ShieldCheck, X } from 'lucide-react'
import { useAuth } from '../auth'
export function Layout(){
  const {user,logout}=useAuth();const [open,setOpen]=useState(false)
  return <div className="app-shell"><header className="site-header"><div className="container nav-row"><Link to="/" className="brand"><span className="brand-emblem"><CalendarDays size={21}/></span>Dat<span>Sân</span><small>SPRINT 2</small></Link>
  <button className="hamburger" aria-label="Mở menu" onClick={()=>setOpen(v=>!v)}>{open?<X/>:<Menu/>}</button>
  <nav className={`nav-links ${open?'show':''}`} aria-label="Điều hướng" onClick={()=>setOpen(false)}>
    <NavLink to="/"><MapPin size={16}/>Tìm sân</NavLink>
    {(user?.role==='PLAYER'||user?.role==='ADMIN')&&<NavLink to="/bookings"><ClipboardList size={16}/>Đơn của tôi</NavLink>}
    {(user?.role==='OWNER'||user?.role==='ADMIN')&&<><NavLink to="/owner"><LayoutDashboard size={16}/>Quản lý sân</NavLink><NavLink to="/owner/bookings"><ClipboardList size={16}/>Duyệt đơn</NavLink></>}
    {user?.role==='ADMIN'&&<NavLink to="/admin"><ShieldCheck size={16}/>Danh mục môn</NavLink>}
    {user&&<NavLink to="/notifications"><Bell size={16}/>Thông báo</NavLink>}
    <div className="nav-account">{user?<><span className="user-badge">{user.full_name}</span><button className="btn btn-ghost btn-small" onClick={logout}><LogOut size={15}/>Đăng xuất</button></>:<><Link className="btn btn-ghost btn-small" to="/login">Đăng nhập</Link><Link className="btn btn-primary btn-small" to="/register">Tạo tài khoản</Link></>}</div>
  </nav></div></header><main className="main-content"><Outlet/></main><footer className="site-footer"><div className="container footer-row"><strong>DatSân · Sprint 2</strong><span>Demo học tập · Thanh toán mô phỏng</span></div></footer></div>
}
