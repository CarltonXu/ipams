export interface Subnet {
  name: string;
  subnet: string;
}

export interface ScheduleConfig {
  interval?: number;
  weekDays?: string[];
  monthDays?: string[];
  startTime?: Date;
  cron?: string;
}

export interface Schedule {
  type: '每分钟' | '每小时' | '每天' | '每周' | '每月' | '自定义';
  config: ScheduleConfig;
}

export interface Policy {
  id: string;
  name: string;
  description: string;
  subnets: Subnet[];
  schedule: Schedule;
  created_at: string;
  status: 'active' | 'inactive';
}