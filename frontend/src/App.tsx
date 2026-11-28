import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import { Layout } from './components/Layout'
import { ErrorNotice, RequireRole } from './components/Ui'
import { AuthPage } from './pages/AuthPages'
import { BookingsPage } from './pages/BookingsPage'
import { CourtPage } from './pages/CourtPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { OwnerPage } from './pages/OwnerPage'
import { SearchPage } from './pages/SearchPage'
import { request } from './api'
import { useEffect, useState } from 'react'
import type { Sport } from './types'
// Sprint 1 catalog maintenance remains available without importing Sprint 3 AdminPage.
function Catalog(){
 const {token}=useAuth(); const [sports,setSports]=useState<Sport[]>([]);const [name,setName]=useState('');const [error,setError]=useState<string|null>(null);const [revision,setRevision]=useState(0)
 useEffect(()=>{request<Sport[]>('/sports/admin',{},token).then(setSports).catch(e=>setError(e.message))},[token,revision])
 async function save(path:string,method:string,body:object){try{setError(null);await request(path,{method,body:JSON.stringify(body)},token);setName('');setRevision(v=>v+1)}catch(e){setError(e instanceof Error?e.message:'Lỗi cập nhật')}}
 return <section className="container dashboard-page"><h1>Quản lý danh mục môn thể thao</h1><ErrorNotice message={error}/><form className="surface" onSubmit={e=>{e.preventDefault();void save('/sports','POST',{name})}}><label className="field"><span>Tên môn</span><input value={name} minLength={2} maxLength={100} required onChange={e=>setName(e.target.value)}/></label><button className="btn btn-primary">Thêm môn</button></form><div className="surface">{sports.map(s=><div className="sport-row" key={s.id}><div><strong>{s.name}</strong><small>{s.active?'Đang hoạt động':'Đã khóa'}</small></div><button className="btn btn-outline btn-small" onClick={()=>save(`/sports/${s.id}`,'PATCH',{active:!s.active})}>{s.active?'Khóa':'Bật lại'}</button></div>)}</div></section>
}
export function App(){return <BrowserRouter><AuthProvider><Routes><Route element={<Layout/>}>
 <Route path="/" element={<SearchPage/>}/><Route path="/courts/:id" element={<CourtPage/>}/>
 <Route path="/login" element={<AuthPage mode="login"/>}/><Route path="/register" element={<AuthPage mode="register"/>}/>
 <Route path="/bookings" element={<RequireRole roles={['PLAYER','ADMIN']}><BookingsPage/></RequireRole>}/>
 <Route path="/owner" element={<RequireRole roles={['OWNER','ADMIN']}><OwnerPage/></RequireRole>}/>
 <Route path="/owner/bookings" element={<RequireRole roles={['OWNER','ADMIN']}><BookingsPage mode="owner"/></RequireRole>}/>
 <Route path="/notifications" element={<RequireRole roles={['PLAYER','OWNER','ORGANIZER','ADMIN']}><NotificationsPage/></RequireRole>}/>
 <Route path="/admin" element={<RequireRole roles={['ADMIN']}><Catalog/></RequireRole>}/>
 <Route path="/organizer" element={<RequireRole roles={['ORGANIZER','ADMIN']}><div className="container dashboard-page"><h1>Giải đấu</h1><p>Nghiệp vụ tổ chức giải đấu thuộc Sprint 3.</p></div></RequireRole>}/>
 <Route path="*" element={<Navigate to="/" replace/>}/>
 </Route></Routes></AuthProvider></BrowserRouter>}
