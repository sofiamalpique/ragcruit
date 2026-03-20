const API_BASE_URL = import.meta.env.DEV ? "" : "http://localhost:8000";


export type CandidateCreatePayload = {
  full_name: string;
  email: string;
  phone: string | null;
  location: string | null;
  summary: string | null;
  years_experience: number | null;
  skills: string[];
};

export type CandidateRead = {
  id: number;
  full_name: string;
  email: string;
  phone: string | null;
  location: string | null;
  summary: string | null;
  years_experience: number | null;
};

export type CandidateSearchPayload = {
  query_text: string;
  limit: number;
};

export type CandidateSearchResult = {
  candidate: CandidateRead;
  similarity_score: number;
};

export type CandidateSearchResponse = {
  results: CandidateSearchResult[];
};

export type JobCreatePayload = {
  title: string;
  company_name: string | null;
  location: string | null;
  description: string;
  requirements: string | null;
  min_years_experience: number | null;
};

export type JobRead = {
  id: number;
  title: string;
  company_name: string | null;
  location: string | null;
  description: string;
  requirements: string | null;
  min_years_experience: number | null;
};

export type JobMatchPayload = {
  limit: number;
};

export type JobMatchResult = {
  candidate: CandidateRead;
  similarity_score: number;
};

export type JobMatchResponse = {
  results: JobMatchResult[];
};


async function apiRequest<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;

    try {
      const errorBody = (await response.json()) as { detail?: string };
      if (typeof errorBody.detail === "string" && errorBody.detail.trim() !== "") {
        message = errorBody.detail;
      }
    } catch {
      // Keep the fallback message when the response body is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}


export function createCandidate(
  payload: CandidateCreatePayload,
): Promise<CandidateRead> {
  return apiRequest<CandidateRead>("/candidates", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export function searchCandidates(
  payload: CandidateSearchPayload,
): Promise<CandidateSearchResponse> {
  return apiRequest<CandidateSearchResponse>("/candidates/search", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export function createJob(payload: JobCreatePayload): Promise<JobRead> {
  return apiRequest<JobRead>("/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export function listJobs(): Promise<JobRead[]> {
  return apiRequest<JobRead[]>("/jobs", {
    method: "GET",
  });
}


export function matchJob(
  jobId: number,
  payload: JobMatchPayload,
): Promise<JobMatchResponse> {
  return apiRequest<JobMatchResponse>(`/jobs/${jobId}/match`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
