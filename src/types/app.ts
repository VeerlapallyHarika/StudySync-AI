export interface ScoreItem {
  subject: string
  score: number
}

export interface GroupMember {
  name: string
  strength: string
  weakness: string
}

export interface StudyGroup {
  name: string
  members: GroupMember[]
  overallStrengths: string[]
}

export interface StatCard {
  label: string
  value: string
  note?: string
}
