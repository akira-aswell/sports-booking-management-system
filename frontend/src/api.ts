export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message) }
}

export async function request<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    }
  })
  if (response.status === 204) return undefined as T
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const message = data?.detail
    throw new ApiError(response.status,
      typeof message === 'string' ? message : Array.isArray(message)
        ? message.map((m: { msg?: string }) => m.msg || 'Dữ liệu không hợp lệ').join('; ')
        : `Lỗi HTTP ${response.status}`)
  }
  return data as T
}

export const money = (amount: string | number) => new Intl.NumberFormat('vi-VN').format(Number(amount)) + 'đ'
export const shortTime = (iso: string) => new Intl.DateTimeFormat('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(iso))
export const dateVietnam = (iso: string) => new Intl.DateTimeFormat('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', dateStyle: 'short', timeStyle: 'short' }).format(new Date(iso))
export const tomorrowVietnam = () => new Date(Date.now() + 7 * 3600_000 + 24 * 3600_000).toISOString().slice(0, 10)

export const toVietnamISO = (localDateTime: string) => `${localDateTime}:00+07:00`
export const localVietnamInput = (iso: string) => new Date(new Date(iso).getTime() + 7 * 3600_000).toISOString().slice(0, 16)
export const tomorrowEveningInput = () => `${tomorrowVietnam()}T18:00`
export const bookingStatus = (s: string) => ({PENDING:'Chờ duyệt', CONFIRMED:'Đã duyệt', CANCELLED:'Đã hủy', REJECTED:'Bị từ chối'}[s] || s)
export const paymentStatus = (s: string) => ({UNPAID:'Chưa thanh toán',SUBMITTED:'Chờ xác minh (demo)',PAID:'Đã xác nhận (demo)',REFUND_REVIEW:'Cần xử lý hoàn tiền'}[s] || s)
export const tournamentStatus = (s: string) => ({OPEN:'Đang nhận đội',IN_PROGRESS:'Đang thi đấu',COMPLETED:'Đã kết thúc',CANCELLED:'Đã hủy'}[s] || s)
