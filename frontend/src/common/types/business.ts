/** 业务实体类型定义，与后端响应字段对应（snake_case）。 */

export interface User {
  id: number
  username: string
  nickname: string
  avatar: string
  phone: string
  student_no: string
  credit_score: number
  role: number
  status: number
  created_at?: string
}

export interface Category {
  id: number
  name: string
  icon: string
  sort: number
}

export interface GoodsItem {
  id: number
  title: string
  description: string
  original_price: number
  sell_price: number
  condition_level: number
  images: string[]
  status: number
  view_count: number
  category_id: number
  category_name: string
  seller_id: number
  seller_nickname: string
  seller_avatar: string
  created_at?: string
}

export interface SellerBrief {
  id: number
  nickname: string
  avatar: string
  credit_score: number
}

export interface GoodsDetail extends GoodsItem {
  seller?: SellerBrief
  is_favorited: boolean
  ai_suggest_price?: number
  related: GoodsItem[]
}

export interface BargainRecord {
  id: number
  product_id: number
  product_title: string
  product_image: string
  buyer_id: number
  buyer_nickname: string
  seller_id: number
  seller_nickname: string
  round: number
  offer_price: number | null
  role: string
  message: string
  status: number
  created_at?: string
}

export interface BargainSession {
  product_id: number
  product_title: string
  product_image: string
  sell_price: number
  buyer_id: number
  buyer_nickname: string
  seller_id: number
  seller_nickname: string
  records: BargainRecord[]
  pending_record_id: number | null
  turn: string
}

export interface Order {
  id: number
  order_no: string
  product_id: number
  product_title: string
  product_image: string
  buyer_id: number
  buyer_nickname: string
  seller_id: number
  seller_nickname: string
  deal_price: number
  status: number
  address: string
  remark: string
  has_review: boolean
  created_at?: string
}

export interface Review {
  id: number
  order_id: number
  reviewer_id: number
  reviewer_nickname: string
  reviewer_avatar: string
  target_id: number
  rating: number
  content: string
  tags: string[]
  created_at?: string
}

export interface Conversation {
  peer_id: number
  peer_nickname: string
  peer_avatar: string
  product_id: number | null
  last_content: string
  last_time?: string
  unread_count: number
}

export interface ChatMessage {
  id: number
  sender_id: number
  sender_nickname: string
  sender_avatar: string
  receiver_id: number
  product_id: number | null
  content: string
  msg_type: number
  is_read: boolean
  created_at?: string
}

export interface AiCopyResult {
  title: string
  description: string
  source: string
}

export interface AiEstimateResult {
  suggested_price: number
  price_low: number
  price_high: number
  source: string
  reason: string
}

export interface AiBargainResult {
  reply: string
  counter_price: number | null
  source: string
}
