import type { ReactNode } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'
import { AlertCircle, LockKeyhole } from 'lucide-react'
import { useAuth } from '../auth'
import type { Role } from '../types'

export function Loading({message='Đang tải dữ liệu...'}:{message?:string}) {
  return <div className="notice"><span className="loading-spinner"/>{message}</div>
}
export function ErrorNotice({message}:{message:string|null}) {
  return message ? <div className="error-notice" role="alert"><AlertCircle size={17}/>{message}</div> : null
}
export function EmptyState({icon,title,children}:{icon:ReactNode;title:string;children?:ReactNode}) {
  return <div className="empty-state">{icon}<h3>{title}</h3><p>{children}</p></div>
}
export function RequireRole({roles,children}:{roles:Role[];children:ReactNode}) {
  const {user,loading}=useAuth(); const loc=useLocation()
  if(loading) return <Loading/>
  if(!user) return <Navigate to="/login" replace state={{from:loc.pathname}}/>
  if(!roles.includes(user.role)) return <div className="container restricted"><LockKeyhole size={42}/><h2>Không có quyền truy cập</h2><Link to="/">Về trang chủ</Link></div>
  return <>{children}</>
}
