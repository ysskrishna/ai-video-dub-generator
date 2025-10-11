const API_BASE_URL = "http://localhost:8085/api/v1/video";

export interface Language {
  [key: string]: string;
}

export interface LanguagesResponse {
  languages: Language;
  total_count: number;
}

export interface CreateJobRequest {
  video_url: string;
  target_language: string;
}

export interface CreateJobResponse {
  job_id: number;
  status: string;
  target_language: string;
  message: string;
}

export interface JobStatus {
  job_id: number;
  video_url: string;
  target_language: string;
  status: "pending" | "processing" | "completed" | "failed";
  error_code: string | null;
  created_at: string;
  updated_at: string;
}

export const api = {
  async getLanguages(): Promise<LanguagesResponse> {
    const response = await fetch(`${API_BASE_URL}/languages`);
    if (!response.ok) throw new Error("Failed to fetch languages");
    return response.json();
  },

  async createJob(data: CreateJobRequest): Promise<CreateJobResponse> {
    const response = await fetch(`${API_BASE_URL}/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to create job");
    return response.json();
  },

  async getJobStatus(jobId: number): Promise<JobStatus> {
    const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
    if (!response.ok) throw new Error("Failed to fetch job status");
    return response.json();
  },

  async getAllJobs(): Promise<JobStatus[]> {
    const response = await fetch(`${API_BASE_URL}/jobs`);
    if (!response.ok) throw new Error("Failed to fetch jobs");
    return response.json();
  },

  getDownloadUrl(jobId: number): string {
    return `${API_BASE_URL}/download/${jobId}`;
  },
};
