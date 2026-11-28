import { useEffect, useState } from 'react'
import { Bell, CheckCircle } from 'lucide-react'
import { dateVietnam, request } from '../api'
import { useAuth } from '../auth'
import type { NotificationItem } from '../types'
import { EmptyState, ErrorNotice, Loading } from '../components/Ui'
export function NotificationsPage(){
 const {token}=useAuth();const [items,setItems]=useState<NotificationItem[]>([]);const [error,setError]=useState<string|null>(null);const [loading,setLoading]=useState(true)
 useEffect(()=>{let live=true;setLoading(true);setError(null);request<NotificationItem[]>('/notifications',{},token).then(v=>{if(live)setItems(v)}).catch(e=>{if(live)setError(e.message)}).finally(()=>{if(live)setLoading(false)});return()=>{live=false}},[token])
 async function read(id:number){try{await request(`/notifications/${id}/read`,{method:'POST'},token);setItems(v=>v.map(x=>x.id===id?{...x,read:true}:x))}catch(e){setError(e instanceof Error?e.message:'Không thể cập nhật')}}
 return <div className="container dashboard-page"><div className="dash-heading"><div><h1>Thông báo của bạn</h1><p>Đơn đặt sân, duyệt đơn và thanh toán mô phỏng.</p></div><Bell size={26}/></div><ErrorNotice message={error}/>{loading?<Loading/>:!items.length?<EmptyState icon={<Bell size={32}/>} title="Không có thông báo"/>:<div className="booking-stack">{items.map(n=><article key={n.id} className={`surface notification-item ${n.read?'is-read':''}`}><div><strong>{n.title}</strong><p>{n.message}</p><small>{dateVietnam(n.created_at)}</small></div>{!n.read&&<button className="btn btn-outline btn-small" onClick={()=>read(n.id)}><CheckCircle size={15}/>Đã đọc</button>}</article>)}</div>}</div>
}
