export interface Education {
  school: string;
  major: string;
  degree: string;
  graduation_time: string;
}

export interface ResumeProfile {
  name: string;
  phone: string;
  email: string;
  city: string;
  education: Education[];
  skills: string[];
}

export interface ScoreResult {
  overall_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  comment: string;
  interview_questions: string[];
}
