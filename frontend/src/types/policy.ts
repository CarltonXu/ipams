export interface Subnet {
  id: string;
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
  strategies: string;
  start_time: string;
  threads: number;
  created_at: string;
  subnets: Subnet[];
  status: 'active' | 'inactive';
}