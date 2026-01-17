
export enum AppView {
  LANDING = 'landing',
  COURSE = 'course',
  CHECKOUT = 'checkout',
  LOGIN = 'login',
  DASHBOARD = 'dashboard',
  ABOUT = 'about'
}

export interface User {
  name: string;
  avatar: string;
  enrolledCourses: number;
}

export interface Course {
  id: string;
  title: string;
  progress: number;
  image: string;
  instructor: string;
  duration: string;
}
